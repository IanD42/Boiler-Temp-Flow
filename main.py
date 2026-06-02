import machine, onewire, ds18x20, ssd1306
import time
import _thread
from machine import Pin, SoftI2C
import wifi
import mqtt
import ntptime  # Added for getting time from NTP server

# Constants
BOOT_DELAY = 1  # Hardware initialization delay
SAMPLING_INTERVAL = 15000  # 15-second sampling window (ms)
TEMP_CONVERSION_DELAY = 750  # Time required for temperature conversion (ms)
DISPLAY_UPDATE_INTERVAL = 0.1  # Display refresh rate (s)
SCROLL_SPEED = 10  # Speed of scrolling text (pixels per update)

# Graph Config
GRAPH_MIN = 15  # Min temperature
GRAPH_MAX = 70  # Max temperature
TEMP_RANGE = GRAPH_MAX - GRAPH_MIN
Y_GRAPH_TOP = 10  # Pixel Y for GRAPH_MAX
Y_GRAPH_BOTTOM = 60  # Pixel Y for GRAPH_MIN

# Data buffer (1 hour @ 15s intervals)
BUFFER_SIZE = 240
temperature_data = [[None, None] for _ in range(BUFFER_SIZE)]
data_index = 0
data_lock = _thread.allocate_lock()

# Hardware Setup
time.sleep(BOOT_DELAY)  
i2c = SoftI2C(scl=Pin(22), sda=Pin(21))
display = ssd1306.SSD1306_I2C(128, 64, i2c)
ow = onewire.OneWire(Pin(4))
ds = ds18x20.DS18X20(ow)
sensors = ds.scan()

def read_temperatures():
    """Reads temperatures from all sensors and returns a dictionary of lists."""
    samples = {i: [] for i in range(len(sensors))}
    
    start_time = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), start_time) < SAMPLING_INTERVAL:
        try:
            ds.convert_temp()
            time.sleep_ms(TEMP_CONVERSION_DELAY)
            for i, sensor in enumerate(sensors):
                temp = ds.read_temp(sensor)
                if temp is not None:
                    samples[i].append(temp)
        except Exception as e:
            print("Sensor error:", e)
    
    return {i: sum(v) / len(v) if v else None for i, v in samples.items()}

def core0_task():
    """Temperature sampling, data storage, and MQTT publishing."""
    global data_index
    wifi.connect_wifi()  # Ensure ESP32 connects to WiFi

    # Sync clock via NTP now that WiFi is up (was failing at import time, before network)
    try:
        ntptime.settime()
    except Exception as e:
        print("⚠ NTP time sync failed:", e)

    mqtt_client = mqtt.connect_mqtt()  # Connect to MQTT broker
    if mqtt_client is None:
        print("⚠ MQTT connection failed. Retrying in 10 seconds...")
    time.sleep(10)

    while True:
        new_data = read_temperatures()

        with data_lock:
            for i in range(len(sensors)):
                temperature_data[data_index][i] = new_data.get(i, None)
            data_index = (data_index + 1) % BUFFER_SIZE

        # Extract latest temperatures
        current_t1 = new_data.get(0, None)
        current_t2 = new_data.get(1, None)

        # Publish to MQTT if valid data is available
        if current_t1 is not None and current_t2 is not None:
            mqtt.publish_temperature(current_t1, current_t2)
        time.sleep(SAMPLING_INTERVAL / 1000)  # Wait for next cycle

def draw_graph(current_data, current_idx):
    """Draws temperature graph on OLED display."""
    display.fill(0)

    # Scale markers
    display.text(f"{GRAPH_MAX}C", 1, Y_GRAPH_TOP - -2, 1)
    display.text(f"{GRAPH_MIN}C", 1, Y_GRAPH_BOTTOM - 8, 1)
    display.hline(0, Y_GRAPH_TOP, 128, 2)    
    display.hline(0, Y_GRAPH_BOTTOM, 128, 2)

    # Plot temperature data
    for sensor_num in range(len(sensors)):
        prev_x, prev_y = None, None
        for i in range(128):
            idx = (current_idx - 128 + i) % BUFFER_SIZE
            temp = current_data[idx][sensor_num]
            if temp is not None:
                y_offset = int((max(GRAPH_MIN, min(GRAPH_MAX, temp)) - GRAPH_MIN) / TEMP_RANGE * (Y_GRAPH_BOTTOM - Y_GRAPH_TOP))
                y = Y_GRAPH_BOTTOM - y_offset
                if prev_x is not None:
                    if sensor_num == 0 or i % 2 == 0:
                        display.line(prev_x, prev_y, i, y, 1)
                prev_x, prev_y = i, y
            else:
                prev_x, prev_y = None, None

def core1_task():
    """Display temperature graph and scrolling text on OLED."""
    scroll_pos = 60  # Start position for scrolling text

    while True:
        with data_lock:
            current_data = list(temperature_data)  # Safer shallow copy
            current_idx = data_index

        draw_graph(current_data, current_idx)

        # Current temperature display
        current_t1 = current_data[(current_idx - 1) % BUFFER_SIZE][0]
        current_t2 = current_data[(current_idx - 1) % BUFFER_SIZE][1]

        # Get current date and time
        now = time.localtime()
        date_time_str = "{:02d}/{:02d}/{:02d} {:02d}:{:02d}:{:02d}".format(now[2], now[1], now[0]%100, now[3], now[4], now[5])
        
 # Construct the scrolling text with T1, T2, and date/time
        scroll_text = f"Flow={current_t1:.0f}C Rtn={current_t2:.0f}C {date_time_str}" if current_t1 is not None and current_t2 is not None else f"{date_time_str} "

        # Draw the scrolling text
        display.text(scroll_text, scroll_pos, 1, 1)
        
        scroll_pos -= SCROLL_SPEED
        if scroll_pos < -len(scroll_text) * 8:
            scroll_pos = 128

        display.show()
        time.sleep(DISPLAY_UPDATE_INTERVAL)

# Start system
_thread.start_new_thread(core1_task, ())
core0_task()
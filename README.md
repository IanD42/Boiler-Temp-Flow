# Boiler Temp Flow

An **ESP32** (MicroPython) project that monitors the **Flow** and **Return** temperatures of a
gas hot-water boiler using two **DS18B20 (Dallas) probes**. Readings are shown on an attached
**OLED display** as a rolling 60-minute graph with scrolling date/time, and are published over
**MQTT** to a home-automation broker (e.g. Home Assistant).

## Features

- 🌡️ **Dual DS18B20 probes** on a single OneWire bus — Flow and Return temperatures.
- 📈 **Rolling 60-minute graph** on the OLED (240 samples @ 15 s intervals).
- 🕒 **NTP-synced clock** — scrolling date/time and live readings across the top of the display.
- 📡 **MQTT publishing** of both temperatures for logging/automation.
- 🔁 **Auto-reconnect** for both WiFi and MQTT.
- 🧵 **Dual-core operation** — sampling/MQTT on one core, display rendering on the other.

## Hardware

| Component            | Detail                                              |
| -------------------- | --------------------------------------------------- |
| Microcontroller      | ESP32                                               |
| Temperature sensors  | 2 × DS18B20 (Dallas) on OneWire                      |
| Display              | SSD1306 OLED, 128 × 64, I²C                          |

### Wiring

| Signal              | ESP32 Pin |
| ------------------- | --------- |
| DS18B20 data        | GPIO 4    |
| OLED SCL            | GPIO 22   |
| OLED SDA            | GPIO 21   |

> The DS18B20 data line needs a **4.7 kΩ pull-up resistor** to 3.3 V. Both probes share the
> single OneWire bus on GPIO 4.

## Software / Dependencies

- **MicroPython** firmware flashed to the ESP32.
- Built-in modules: `machine`, `onewire`, `ds18x20`, `network`, `ntptime`, `_thread`.
- `umqtt.simple` — MQTT client (install via `mip`/`upip`, or bundle with the firmware).
- `ssd1306.py` — OLED driver (included in this repo).

## Project Files

| File              | Purpose                                                            |
| ----------------- | ------------------------------------------------------------------ |
| `boot.py`         | Runs on boot; connects to WiFi.                                    |
| `main.py`         | Main app: sampling, graph rendering, MQTT publishing.              |
| `wifi.py`         | WiFi connect / reconnect helpers.                                  |
| `mqtt.py`         | MQTT connect / publish helpers.                                    |
| `ssd1306.py`      | SSD1306 OLED driver.                                               |
| `config.py`       | Your WiFi / MQTT settings (edit before use).                       |
| `webrepl_cfg.py`  | WebREPL password — **kept local, not in this repo** (gitignored).  |

## Setup

1. **Flash MicroPython** to the ESP32 and install the `umqtt.simple` dependency.
2. **Edit `config.py`** with your own credentials and broker details:
   ```python
   WIFI_SSID = "your-ssid"
   WIFI_PASSWORD = "your-wifi-password"

   MQTT_BROKER = "192.168.1.224"   # your broker IP
   MQTT_PORT = 1883
   MQTT_USER = "your-mqtt-user"
   MQTT_PASSWORD = "your-mqtt-password"
   MQTT_CLIENT_ID = "boiler-sensor"   # required by mqtt.py — add this

   MQTT_TOPIC_T1 = "home/boiler/temperature1"
   MQTT_TOPIC_T2 = "home/boiler/temperature2"
   ```
   > ⚠️ `mqtt.py` references `config.MQTT_CLIENT_ID`, so make sure that line is present.
3. **Upload all `.py` files** to the ESP32 (e.g. with `mpremote`, `ampy`, or Thonny).
4. **Reset the board.** `boot.py` connects to WiFi, then `main.py` starts sampling and drawing.

## How It Works

- Every **15 seconds**, both probes are sampled (averaged over the window) and stored in a
  240-slot circular buffer — exactly **one hour** of history.
- The OLED plots the last 128 samples as two lines (Flow and Return) between the configured
  graph bounds (`GRAPH_MIN = 15 °C`, `GRAPH_MAX = 70 °C`).
- A header line scrolls the current Flow/Return readings and the NTP date/time.
- Each new reading is published to the two MQTT topics for downstream logging/automation.

## Configuration Tuning

In `main.py`:

| Constant            | Default | Meaning                                  |
| ------------------- | ------- | ---------------------------------------- |
| `SAMPLING_INTERVAL` | 15000   | Sampling window in ms.                   |
| `BUFFER_SIZE`       | 240     | Samples retained (240 × 15 s = 1 hour).  |
| `GRAPH_MIN` / `MAX` | 15 / 70 | Graph temperature range (°C).            |

## License

No license specified yet. Add one (e.g. MIT) if you intend others to reuse this code.

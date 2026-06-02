import network
import time
import config

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if wlan.isconnected():
        print("✅ Already connected:", wlan.ifconfig())
        return True

    print(f"🔄 Connecting to WiFi: {config.WIFI_SSID}...")
    wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)

    # Retry mechanism
    timeout = 30  # Max wait time in seconds
    while not wlan.isconnected() and timeout > 0:
        print(f"⏳ Waiting for WiFi... {timeout}s left")
        time.sleep(1)
        timeout -= 1

    if wlan.isconnected():
        print("✅ Connected! IP:", wlan.ifconfig()[0])
        return True
    else:
        print("❌ WiFi connection failed. Retrying in 10 seconds...")
        time.sleep(10)
        return connect_wifi()  # Recursive retry

def is_wifi_connected():
    """Check if WiFi is connected and reconnect if needed."""
    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected():
        print("⚠ WiFi lost! Reconnecting...")
        return connect_wifi()
    return True

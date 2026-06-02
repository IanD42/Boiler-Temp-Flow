import config
from umqtt.simple import MQTTClient
import time

mqtt_client = None  # Global MQTT client

def connect_mqtt():
    """Connect to MQTT broker with retry logic."""
    global mqtt_client
    while True:
        try:
            print("🔄 Connecting to MQTT...")
            mqtt_client = MQTTClient(config.MQTT_CLIENT_ID, config.MQTT_BROKER, 
                                     port=config.MQTT_PORT, 
                                     user=config.MQTT_USER, 
                                     password=config.MQTT_PASSWORD,
                                     keepalive=60)
            mqtt_client.connect()
            print("✅ Connected to MQTT Broker!")
            return mqtt_client
        except Exception as e:
            print(f"❌ MQTT connection failed: {e}. Retrying in 10s...")
            time.sleep(10)  # Wait before retrying

def is_mqtt_connected():
    """Check if MQTT is still connected."""
    try:
        mqtt_client.ping()  # Keep connection alive
        return True
    except:
        print("⚠ MQTT lost! Reconnecting...")
        return connect_mqtt()

def publish_temperature(t1, t2):
    """Publish temperature readings to MQTT."""
    if is_mqtt_connected():
        try:
            mqtt_client.publish(config.MQTT_TOPIC_T1, str(t1))
            mqtt_client.publish(config.MQTT_TOPIC_T2, str(t2))
            print(f"📡 Sent -> T1: {t1}°C, T2: {t2}°C")
        except Exception as e:
            print(f"⚠ MQTT Publish Error: {e}")

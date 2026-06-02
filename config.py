# WiFi Configuration
WIFI_SSID = "XXXXX"       #Replace woth your SSID
WIFI_PASSWORD = "XXXXXX"  #Replace with your wifi password

# MQTT Configuration
MQTT_BROKER = "192.168.1.224"
MQTT_PORT = 1883
MQTT_USER = "XXXXX"       # Replace woth your MQTT User name as defined in HA
MQTT_PASSWORD = "XXXXXX"  # Replace woth your MQTT User password as defined in HA
MQTT_TOPIC_TEMP1 = "home/temperature/sensor1"
MQTT_TOPIC_TEMP2 = "home/temperature/sensor2"

# Sensor Configuration (optional)
SENSOR_ADDRESSES = [
    "28-XXXXXXXXXXXX",  # Replace with actual sensor 1 address
    "28-XXXXXXXXXXXX"   # Replace with sensor 2 address
]

# MQTT Topics
MQTT_TOPIC_T1 = "home/boiler/temperature1"
MQTT_TOPIC_T2 = "home/boiler/temperature2"



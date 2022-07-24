import time

import dht
from machine import Pin
from umqtt.simple import MQTTClient

# Connection config
MQTT_CLIENT_NAME = "esp"
MQTT_BROKER_ADDR = "192.168.1.20"
MQTT_KEEPALIVE = 60

# Device config
DEVICE_ID = 0
SENSOR_PIN = 4

# topics
esp_id = f"esp{DEVICE_ID}"
topic_hum = f"{esp_id}/sensor/hum"
topic_temp = f"{esp_id}/sensor/temp"
topic_led = f"{esp_id}/actuator/led"
topics_to_subscribe = []


def callback(topic, msg):
    print(topic)
    print(msg)


def publish_measurements(mqtt: MQTTClient) -> None:

    print("Publishing sensor data to ", topic_hum, topic_temp)

    pin = Pin(SENSOR_PIN, Pin.IN, Pin.PULL_UP)
    sensor = dht.DHT11(pin)
    sensor.measure()

    humidity = sensor.humidity()
    temperature = sensor.temperature()
    print("hum", humidity)
    print("temp", temperature)
    mqtt.publish(topic_hum, str(humidity))
    mqtt.publish(topic_temp, str(temperature))


def connect_mqtt() -> MQTTClient:
    mqtt = MQTTClient(MQTT_CLIENT_NAME, MQTT_BROKER_ADDR, keepalive=MQTT_KEEPALIVE)

    print("Connecting to broker...")
    mqtt.connect()
    print("Connected to broker.")

    mqtt.set_callback(callback)

    for topic in topics_to_subscribe:
        mqtt.subscribe(topic)

    return mqtt


def main():

    print("Starting!!")
    mqtt = connect_mqtt()

    while True:
        time.sleep(1)
        publish_measurements(mqtt)


if __name__ == "__main__":
    main()

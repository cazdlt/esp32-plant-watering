import time

import dht
from machine import Pin
from lib.mqtt_manager import MQTTManager
from umqtt.simple import MQTTClient

# Device config
DEVICE_ID = 0
DEVICE_NAME = f"esp{DEVICE_ID}"

# Connection config
MQTT_CLIENT_NAME = DEVICE_NAME
MQTT_BROKER_ADDR = "192.168.1.20"
MQTT_KEEPALIVE = 60

# Topics
topic_hum = f"{DEVICE_NAME}/sensor/hum"
topic_temp = f"{DEVICE_NAME}/sensor/temp"
topic_led = f"{DEVICE_NAME}/actuator/led"
topic_health_check = f"{DEVICE_NAME}/health_check"
topics_to_subscribe = [topic_led, topic_health_check]

# Pins
SENSOR_PIN_NUMBER = 4
sensor_pin = Pin(SENSOR_PIN_NUMBER, Pin.IN, Pin.PULL_UP)
led_pin = Pin(2, Pin.OUT)


def led_callback(message: str):
    if message == "on":
        print("Turning on LED")
        led_pin.on()
    elif message == "off":
        print("Turning off LED")
        led_pin.off()
    else:
        print("Invalid message for led controller:", message)


def health_check_callback(message: str):
    print("Hola mamá")


def callback(topic: bytes, message: bytes):
    topic = topic.decode("utf-8")
    message = message.decode("utf-8")

    try:
        topic_callbacks = {
            topic_led: led_callback,
            topic_health_check: health_check_callback,
        }
        topic_callbacks[topic](message)
    except KeyError:
        print("Unknown action for topic", topic)
        print("Message:", message)


def get_measurements(sensor: dht.DHT11):

    try:
        sensor.measure()
        humidity = sensor.humidity()
        temperature = sensor.temperature()
    except Exception as e:
        print("Error while reading sensor measurements", e)
        humidity = temperature = -1
    return humidity, temperature


def publish_measurements(sensor: dht.DHT11, mqtt: MQTTClient) -> None:

    print("Reading sensor data...")
    humidity, temperature = get_measurements(sensor)

    print("Sending humidity", humidity, "to", topic_hum)
    mqtt.publish(topic_hum, str(humidity))

    print("Sending temperature", temperature, "to", topic_temp)
    mqtt.publish(topic_temp, str(temperature))


def subscribe_to_topics(mqtt: MQTTClient, topics: list[str], callback):
    mqtt.set_callback(callback)

    for topic in topics:
        print("Subscribing to", topic)
        mqtt.subscribe(topic)


def initialize_sensor():

    sensor = dht.DHT11(sensor_pin)
    return sensor


def main():

    print("Starting!!")
    sensor = initialize_sensor()

    with MQTTManager(MQTT_CLIENT_NAME, MQTT_BROKER_ADDR) as mqtt:
        subscribe_to_topics(mqtt, topics_to_subscribe, callback)

        while True:
            print()
            mqtt.check_msg()
            publish_measurements(sensor, mqtt)
            time.sleep(1)


if __name__ == "__main__":
    main()

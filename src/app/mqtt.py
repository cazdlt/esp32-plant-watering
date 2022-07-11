import time

import dht
from machine import Pin
from umqtt.simple import MQTTClient

MQTT_CLIENT_NAME = "esp"
MQTT_BROKER_ADDR = "192.168.1.20"
MQTT_KEEPALIVE = 60
TOPIC_HUM = "esp/hum"
TOPIC_TEMP = "esp/temp"
SENSOR_PIN = 4

def main():

    pin = Pin(SENSOR_PIN, Pin.IN, Pin.PULL_UP)
    sensor = dht.DHT11(pin)
    mqttc = MQTTClient(MQTT_CLIENT_NAME, MQTT_BROKER_ADDR, keepalive=MQTT_KEEPALIVE)

    print("Starting!!")

    print("Connecting...")
    mqttc.connect()
    print("Connected. Publishing sensor data to ", TOPIC_HUM, TOPIC_TEMP)


    while True:
        time.sleep(1)
        sensor.measure()

        humidity = sensor.humidity()
        temperature = sensor.temperature()
        print("hum", humidity)
        print("temp", temperature)
        mqttc.publish(TOPIC_HUM, str(humidity))
        mqttc.publish(TOPIC_TEMP, str(temperature))


if __name__ == "__main__":
    main()

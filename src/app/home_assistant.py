import time

import dht
import lib.home_assistant as ha
from lib.mqtt_manager import MQTTManager
from lib.sensor import SensorProtocol
from machine import Pin

# Device config
DEVICE_ID = 0
DEVICE_NAME = f"esp{DEVICE_ID}"

# Connection config
MQTT_CLIENT_NAME = DEVICE_NAME
MQTT_BROKER_ADDR = "192.168.1.20"

# Topics
BASE_TOPIC = "home"
topic_sensors = f"{BASE_TOPIC}/{DEVICE_NAME}/sensors"
topic_led = f"{BASE_TOPIC}/{DEVICE_NAME}/actuator/led"
topic_health_check = f"{BASE_TOPIC}/{DEVICE_NAME}/health_check"

# Pins
SENSOR_PIN_NUMBER = 4
LED_PIN_NUMBER = 2
led_pin = Pin(LED_PIN_NUMBER, Pin.OUT)


class DHT11Sensor(SensorProtocol):
    def __init__(self):
        sensor_pin = Pin(SENSOR_PIN_NUMBER, Pin.IN, Pin.PULL_UP)
        self.sensor = dht.DHT11(sensor_pin)

    def get_measurements(self) -> dict:
        try:
            self.sensor.measure()
            humidity = self.sensor.humidity()
            temperature = self.sensor.temperature()
        except Exception as e:  # type: ignore
            print("Error while reading sensor measurements", e)
            raise Exception("Error while reading DHT measurements")  # type: ignore

        return {"humidity": humidity, "temperature": temperature}


def main():
    print("Starting!!")

    sensor = DHT11Sensor()

    temp = ha.Sensor(
        device_id=DEVICE_NAME,
        name="temperature",
        device_class="temperature",
        value_attribute="temperature",
        unit_of_measurement="C",
    )
    hum = ha.Sensor(
        device_id=DEVICE_NAME,
        name="humidity",
        device_class="humidity",
        value_attribute="humidity",
        unit_of_measurement="%",
    )
    sensors = ha.MultiSensor(
        (temp, hum),
        state_topic=topic_sensors,
        sensor=sensor,
    )

    with MQTTManager(MQTT_CLIENT_NAME, MQTT_BROKER_ADDR) as mqtt:
        sensors.initialize(mqtt)

        while True:
            print()
            mqtt.check_msg()
            sensors.send_states()
            time.sleep(5)


if __name__ == "__main__":
    main()

import time

import dht
import lib.home_assistant as ha
from lib.mqtt_manager import MQTTManager
from machine import Pin

# Device config
DEVICE_ID = 0
DEVICE_NAME = f"esp{DEVICE_ID}"

# Connection config
MQTT_CLIENT_NAME = DEVICE_NAME
MQTT_BROKER_ADDR = "192.168.1.20"

# Topics
topic_sensors = f"home/{DEVICE_NAME}/sensors"
topic_led = f"home/{DEVICE_NAME}/actuator/led"
topic_health_check = f"home/{DEVICE_NAME}/health_check"

# Pins
SENSOR_PIN_NUMBER = 4
sensor_pin = Pin(SENSOR_PIN_NUMBER, Pin.IN, Pin.PULL_UP)
led_pin = Pin(2, Pin.OUT)


def initialize_sensor():
    sensor = dht.DHT11(sensor_pin)
    return sensor


def get_measurements(sensor: dht.DHT11):
    try:
        sensor.measure()
        humidity = sensor.humidity()
        temperature = sensor.temperature()
    except Exception as e:  # type: ignore
        print("Error while reading sensor measurements", e)
        raise Exception("Error while reading DHT measurements")  # type: ignore

    return {"humidity": humidity, "temperature": temperature}


def main():
    print("Starting!!")

    sensor = initialize_sensor()

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
        get_measurements_fn=lambda: get_measurements(sensor),
    )

    with MQTTManager(MQTT_CLIENT_NAME, MQTT_BROKER_ADDR) as mqtt:
        sensors.initialize(mqtt)

        while True:
            print()
            mqtt.check_msg()
            sensors.send_states(mqtt)
            time.sleep(5)


if __name__ == "__main__":
    main()

import time

import dht
from machine import Pin
from lib.mqtt_manager import MQTTManager
from umqtt.simple import MQTTClient
import json

# Device config
DEVICE_ID = 0
DEVICE_NAME = f"esp{DEVICE_ID}"

# Connection config
MQTT_CLIENT_NAME = DEVICE_NAME
MQTT_BROKER_ADDR = "192.168.1.20"
MQTT_KEEPALIVE = 60

# Topics
HA_BASE = "homeassistant"
topic_sensors = f"home/{DEVICE_NAME}/sensors"
topic_led = f"home/{DEVICE_NAME}/actuator/led"
topic_health_check = f"home/{DEVICE_NAME}/health_check"

# Pins
SENSOR_PIN_NUMBER = 4
sensor_pin = Pin(SENSOR_PIN_NUMBER, Pin.IN, Pin.PULL_UP)
led_pin = Pin(2, Pin.OUT)


class Sensor:
    def __init__(self, sensor):
        self.sensor = sensor

    def measure(self):
        raise Exception("Must be implemented")


class HAEntity:
    def __init__(self, component_type: str, name: str):
        self.component_type = component_type
        self.name = name
        self.object_id = f"{DEVICE_NAME}_{name}"
        self.unique_id = f"{self.component_type}.{self.object_id}"
        self.base_topic = f"{HA_BASE}/{component_type}/{self.object_id}"
        self.discovery_topic = f"{self.base_topic}/config"
        self.availability_topic = f"{self.base_topic}/status"
        self._status = "online"
        self.mqtt = None

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, new_status):
        old_status = self._status
        self._status = new_status
        if old_status != new_status:
            self.notify_status(self.mqtt)

    def initialize(self, mqtt: MQTTClient):
        self.mqtt = mqtt
        self.notify_status(mqtt)
        self.send_discovery_message(mqtt)

    def send_discovery_message(self, mqtt: MQTTClient):
        pass

    def notify_status(self, mqtt: MQTTClient):
        print("Setting", self.unique_id, "status as", self.status)
        mqtt.publish(self.availability_topic, self.status)


class HASensor(HAEntity):
    def __init__(
        self,
        name: str,
        device_class: str,
        get_measure_fn=None,
        state_topic: str = None,
        value_attribute: str = None,
    ):
        super().__init__("sensor", name)
        self.device_class = device_class
        self.state_topic = state_topic
        self.value_attribute = value_attribute
        self.get_measure = get_measure_fn

    @property
    def value_template(self):
        return f"{{{{ value_json.{self.value_attribute} }}}}"

    def send_discovery_message(self, mqtt: MQTTClient):
        assert self.state_topic is not None, "no state topic specified"
        message = {
            "name": self.name,
            "device_class": self.device_class,
            "object_id": self.object_id,
            "state_topic": self.state_topic,
            "unique_id": self.unique_id,
            "availability_topic": self.availability_topic,
        }

        if self.value_attribute is not None:
            message["value_template"] = self.value_template

        print("Sending discovery message:", message, "to", self.discovery_topic)
        mqtt.publish(self.discovery_topic, json.dumps(message), retain=True)

    def send_state(self, mqtt: MQTTClient):
        assert self.get_measure is not None, "no measure function specified"
        try:
            value = self.get_measure()
        except Exception as e:  # type: ignore
            self.status = "offline"
            print("Error getting measurements:", str(e))
            return
        message = str(value)
        print("Sending measurement:", message, "to", self.state_topic)
        mqtt.publish(self.state_topic, message)


class HAMultiSensor:
    def __init__(self, ha_sensors, state_topic: str, get_measurements_fn):
        self.sensors = ha_sensors
        self.state_topic = state_topic
        self.get_measurements = get_measurements_fn

    def initialize(self, mqtt: MQTTClient):
        for sensor in self.sensors:
            sensor.state_topic = self.state_topic
            sensor.initialize(mqtt)

    def update_sensors_status(self, new_status):
        for sensor in self.sensors:
            sensor.status = new_status

    def send_states(self, mqtt: MQTTClient):
        try:
            measurements = self.get_measurements()
        except Exception as e:  # type: ignore
            self.update_sensors_status("offline")
            print("Error getting measurements:", str(e))
            return
        print("Sending measurements:", measurements, "to", self.state_topic)
        self.update_sensors_status("online")
        mqtt.publish(self.state_topic, json.dumps(measurements))


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

    temp = HASensor(
        name="temperature",
        device_class="temperature",
        value_attribute="temperature",
    )
    hum = HASensor(
        name="humidity",
        device_class="humidity",
        value_attribute="humidity",
    )
    sensors = HAMultiSensor(
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

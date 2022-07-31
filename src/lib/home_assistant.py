import json

from umqtt.simple import MQTTClient

from lib.models import SensorProtocol

HA_BASE = "homeassistant"


class Entity:
    def __init__(self, device_id: str, component_type: str, name: str):
        self.component_type = component_type
        self.name = name
        self.object_id = f"{device_id}_{name}"
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
            self.notify_status()

    def initialize(self, mqtt: MQTTClient):
        self.mqtt = mqtt
        self.notify_status()
        self.send_discovery_message()

    def send_discovery_message(self):
        pass

    def notify_status(self):
        print("Setting", self.unique_id, "status as", self.status)
        self.mqtt.publish(self.availability_topic, self.status)


class Sensor(Entity):
    def __init__(
        self,
        device_id: str,
        name: str,
        device_class: str,
        sensor: SensorProtocol = None,
        state_topic: str = None,
        value_attribute: str = None,
        unit_of_measurement: str = None,
    ):
        super().__init__(device_id, "sensor", name)
        self.device_class = device_class
        self.state_topic = state_topic
        self.value_attribute = value_attribute
        self.sensor = sensor
        self.unit_of_measurement = unit_of_measurement

    @property
    def value_template(self):
        return f"{{{{ value_json.{self.value_attribute} }}}}"

    def send_discovery_message(self):
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

        if self.unit_of_measurement is not None:
            message["unit_of_measurement"] = self.unit_of_measurement

        print("Sending discovery message:", message, "to", self.discovery_topic)
        self.mqtt.publish(self.discovery_topic, json.dumps(message), retain=True)

    def send_state(self):
        assert self.sensor is not None, "no measure function specified"
        try:
            value = self.sensor.get_measurements()
        except Exception as e:  # type: ignore
            self.status = "offline"
            print("Error getting measurements:", str(e))
            return
        message = str(value)
        print("Sending measurement:", message, "to", self.state_topic)
        self.mqtt.publish(self.state_topic, message)


class MultiSensor:
    def __init__(self, ha_sensors, state_topic: str, sensor: SensorProtocol):
        self.ha_sensors = ha_sensors
        self.sensor = sensor
        self.state_topic = state_topic
        self.mqtt = None

    def initialize(self, mqtt: MQTTClient):
        self.mqtt = mqtt
        for sensor in self.ha_sensors:
            sensor.state_topic = self.state_topic
            sensor.initialize(mqtt)

    def update_sensors_status(self, new_status):
        for sensor in self.ha_sensors:
            sensor.status = new_status

    def send_states(self):
        try:
            measurements = self.sensor.get_measurements()
        except Exception as e:  # type: ignore
            self.update_sensors_status("offline")
            print("Error getting measurements:", str(e))
            return
        print("Sending measurements:", measurements, "to", self.state_topic)
        self.update_sensors_status("online")
        self.mqtt.publish(self.state_topic, json.dumps(measurements))

import json

from lib.models import SensorProtocol, SwitchProtocol
from lib.mqtt_manager import MQTTHelper

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
        self.command_topic = None
        self.command_callback = None

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, new_status):
        old_status = self._status
        self._status = new_status
        if old_status != new_status:
            self.notify_status()

    def initialize(self, mqtt: MQTTHelper):
        self.mqtt = mqtt
        self.send_discovery_message()
        self.notify_status()
        self.subscribe_to_command_topic()

    def subscribe_to_command_topic(self):
        if self.command_topic is not None and self.command_callback is not None:
            self.mqtt.subscribe_with_callback(self.command_topic, self.command_callback)

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

    def initialize(self, mqtt: MQTTHelper):
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


class Switch(Entity):
    def __init__(
        self,
        device_id: str,
        name: str,
        state_topic: str,
        command_topic: str,
        switch: SwitchProtocol,
        value_attribute: str = None,
        device_class: str = "switch",
        payload_off: str = "OFF",
        payload_on: str = "ON",
    ):
        super().__init__(device_id, "switch", name)
        self.device_class = device_class
        self.state_topic = state_topic
        self.command_topic = command_topic
        self.payload_off = payload_off
        self.payload_on = payload_on
        self.switch = switch
        self.command_callback = self.switch.callback
        self.value_attribute = value_attribute
        self.switch.register(self)

    def initialize(self, mqtt: MQTTHelper):
        super().initialize(mqtt)
        self.notify_state(self.switch.state)

    def notify_state(self, new_state):
        print(f"Notifying {self.unique_id} state as {new_state}")
        self.mqtt.publish(self.state_topic, new_state)

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
            "command_topic": self.command_topic,
            "unique_id": self.unique_id,
            "availability_topic": self.availability_topic,
            "payload_off": self.payload_off,
            "payload_on": self.payload_on,
        }

        if self.value_attribute is not None:
            message["value_template"] = self.value_template

        print("Sending discovery message:", message, "to", self.discovery_topic)
        self.mqtt.publish(self.discovery_topic, json.dumps(message), retain=True)

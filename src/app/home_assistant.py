import time

import dht
import lib.home_assistant as ha
from lib.mqtt_manager import MQTTHelper, MQTTManager
from lib.models import SensorProtocol
from machine import Pin
import json
from umqtt.simple import MQTTClient

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


class SwitchProtocol:
    def __init__(self):
        self.ha_switch = None

    @property
    def state(self):
        pass

    @state.setter
    def state(self):
        pass

    def callback(self, message):
        pass

    def register(self, ha_switch: "HASwitch"):
        self.ha_switch = ha_switch

    def notify_state(self, new_state):
        if self.ha_switch is not None:
            self.ha_switch.notify_state(new_state)


class Led(SwitchProtocol):
    def __init__(self):
        super().__init__()
        self.pin = Pin(LED_PIN_NUMBER, Pin.OUT)

    @property
    def state(self):
        return str(self.pin.value())

    @state.setter
    def state(self, new_state):
        old_state = self.pin.value()
        self.pin.value(new_state)
        new_state = self.pin.value()
        if new_state != old_state:
            self.notify_state(self.state)

    def callback(self, message):
        try:
            print("Setting LED to", message)
            self.state = int(message)
        except ValueError:  # type: ignore
            print(
                f"Failed setting {message} as LED state, please check that it is a valid state."
            )


class HASwitch(ha.Entity):
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


def main():
    print("Starting!!")

    sensor = DHT11Sensor()
    led = Led()

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

    ha_led = HASwitch(
        device_id=DEVICE_NAME,
        name="led",
        state_topic=topic_led,
        command_topic=topic_led,
        payload_on="1",
        payload_off="0",
        switch=led,
    )

    with MQTTManager(MQTT_CLIENT_NAME, MQTT_BROKER_ADDR) as mqtt:

        print("initializing")
        sensors.initialize(mqtt)
        ha_led.initialize(mqtt)
        print("finished initializing")

        print("starting main loop")
        while True:
            mqtt.check_msg()
            sensors.send_states()
            time.sleep(5)


if __name__ == "__main__":
    main()

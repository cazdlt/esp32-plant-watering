import dht
import lib.home_assistant as ha
from lib.models import SensorProtocol, SwitchProtocol
from lib.mqtt_manager import MQTTManager
from machine import Pin, Timer

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


class Led(SwitchProtocol):
    def __init__(self):
        super().__init__()
        self.pin = Pin(LED_PIN_NUMBER, Pin.OUT)

    @property
    def state(self) -> str:
        return str(self.pin.value())

    @state.setter
    def state(self, new_state: str):
        self.pin.value(int(new_state))

    def callback(self, message):
        try:
            print("Setting LED to", message)
            self.state = message
        except ValueError:  # type: ignore
            self.notify_state(self.state)
            print(f"Failed setting {message} as LED state, check that it is valid.")


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

    ha_led = ha.Switch(
        device_id=DEVICE_NAME,
        name="led",
        state_topic=topic_led,
        command_topic=topic_led,
        payload_on="1",
        payload_off="0",
        switch=led,
    )

    sensor_timer = Timer(0)
    check_message_timer = Timer(1)

    with MQTTManager(MQTT_CLIENT_NAME, MQTT_BROKER_ADDR) as mqtt:

        print("initializing")
        sensors.initialize(mqtt)
        ha_led.initialize(mqtt)
        print("finished initializing")

        try:
            print("initializing timers")
            sensor_timer.init(period=5000, callback=lambda _: sensors.send_states())
            check_message_timer.init(period=100, callback=lambda _: mqtt.check_msg())
            while True:
                pass
        except Exception as e:  # type: ignore
            print(e)
        finally:
            print("deactivating timers")
            sensor_timer.deinit()
            check_message_timer.deinit()

            print("deactivating entities")
            sensors.update_sensors_status("offline")
            ha_led.status = "offline"


if __name__ == "__main__":
    main()

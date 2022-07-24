from umqtt.simple import MQTTClient


class MQTTManager:
    """Context manager for handling MQTT connections"""

    def __init__(self, client_name, broker_address, keepalive=60):
        self.client_name = client_name
        self.broker_address = broker_address
        self.keepalive = keepalive

    def __enter__(self):

        print(f"Connecting to broker as {self.client_name}...")
        self.mqtt = MQTTClient(
            self.client_name,
            self.broker_address,
            keepalive=self.keepalive,
        )
        self.mqtt.connect()
        print(f"Connected")
        return self.mqtt

    def __exit__(self, *args):
        print("Disconnecting from broker")
        self.mqtt.disconnect()
        print("Disconnected")

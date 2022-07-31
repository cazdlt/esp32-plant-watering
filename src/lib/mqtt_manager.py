from umqtt.simple import MQTTClient


class MQTTHelper(MQTTClient):
    def __init__(
        self,
        client_id,
        server,
        port=0,
        user=None,
        password=None,
        keepalive=0,
        ssl=False,
        ssl_params={},
    ) -> None:
        super().__init__(
            client_id, server, port, user, password, keepalive, ssl, ssl_params
        )
        self.callbacks = {}

        def callback(topic: bytes, message: bytes):
            topic = topic.decode("utf-8")
            message = message.decode("utf-8")
            self.callbacks[topic](message)

        self.set_callback(callback)

    def subscribe_with_callback(self, topic, callback):
        self.callbacks[topic] = callback
        super().subscribe(topic)


class MQTTManager:
    """Context manager for handling MQTT connections"""

    def __init__(self, client_name, broker_address, keepalive=60):
        self.client_name = client_name
        self.broker_address = broker_address
        self.keepalive = keepalive

    def __enter__(self):

        print(f"Connecting to broker as {self.client_name}...")
        self.mqtt = MQTTHelper(
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

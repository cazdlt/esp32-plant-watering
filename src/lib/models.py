class SensorProtocol:
    def get_measurements(self):
        pass


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

    def register(self, ha_switch):
        self.ha_switch = ha_switch

    def notify_state(self, new_state):
        if self.ha_switch is not None:
            self.ha_switch.notify_state(new_state)

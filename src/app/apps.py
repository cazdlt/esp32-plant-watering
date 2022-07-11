from . import mqtt, blynk
from enum import Enum, auto

class App(Enum):
    BLYNK = auto()
    MQTT = auto()

def run_app(app: App):
    apps = {
        App.BLYNK: blynk.main,
        App.MQTT: mqtt.main,
    }
    return apps[app]()
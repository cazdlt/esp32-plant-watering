from . import mqtt
from . import home_assistant


def run_app(app: str):
    apps = {
        "mqtt": mqtt.main,
        "ha": home_assistant.main
    }
    assert app in apps.keys(), f"{app} is not a valid app"
    return apps[app]()

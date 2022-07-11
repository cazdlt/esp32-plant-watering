from . import mqtt, blynk


def run_app(app: str):
    apps = {
        "blynk": blynk.main,
        "mqtt": mqtt.main,
    }
    assert app in apps.keys(), f"{app} is not a valid app"
    return apps[app]()
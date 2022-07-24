from . import mqtt


def run_app(app: str):
    apps = {
        "mqtt": mqtt.main,
    }
    assert app in apps.keys(), f"{app} is not a valid app"
    return apps[app]()

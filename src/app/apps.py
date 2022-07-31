from . import home_assistant, mqtt, playground


def run_app(app: str):
    apps = {
        "mqtt": mqtt.main,
        "ha": home_assistant.main,
        "playground": playground.main,
    }
    assert app in apps.keys(), f"{app} is not a valid app"
    return apps[app]()

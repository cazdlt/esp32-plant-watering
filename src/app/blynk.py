import random

import config
from lib import blynklib

blynk = blynklib.Blynk(config.BLYNK_AUTH_TOKEN)


@blynk.handle_event("read V0")
def read_virtual_pin_handler(pin):
    sensor_data = random.uniform(0, 10)
    print("sensor value", sensor_data)
    blynk.virtual_write(pin, sensor_data)


def main():
    while True:
        blynk.run()


if __name__ == "__main__":
    main()

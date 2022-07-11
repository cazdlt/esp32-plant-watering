import blynklib_mp as blynklib
import random
import time
import config

blynk = blynklib.Blynk(config.BLYNK_AUTH_TOKEN)

@blynk.handle_event('read V0')
def read_virtual_pin_handler(pin):
    
    sensor_data = random.uniform(0,10)
    blynk.virtual_write(pin, sensor_data)
        
def main():
    while True:
        blynk.run()
        time.sleep_ms(1000)

if __name__ == "__main__":
    main()
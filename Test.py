import time

import LightControl as lc
from neopixel import *

def main():
    lights = lc.LEDString(count=50)

    print("Red")
    lights.light_up(0, Color(255, 0, 0))
    time.sleep(2)

    print("Green")
    lights.light_up(0, Color(0, 255, 0))

    time.sleep(2)

    print("Blue")
    lights.light_up(0, Color(0, 0, 255))

    time.sleep(2)

    lights.turn_all_off()

if __name__ == "__main__":
    main()
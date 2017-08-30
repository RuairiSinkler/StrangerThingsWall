import time

import LightControl as lc
from neopixel import *

def main():
    lights = lc.LEDString(count=50)
    lights.light_up(0, Color(255, 0, 0))

if __name__ == "__main__":
    main()
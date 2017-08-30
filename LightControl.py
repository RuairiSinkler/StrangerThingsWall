import time

import neopixel as np

class LEDString:

    # LED strip configuration:
    LED_COUNT      = 16      # Number of LED pixels.
    LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
    LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
    LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
    LED_INVERT = False  # True to invert the signal (when using NPN transistor level shift)
    LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
    LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
    LED_STRIP      = np.ws.WS2811_STRIP_RGB   # Strip type and colour ordering

    def __init__(self, **cnf):
        # Create NeoPixel object with appropriate configuration.
        count = cnf.get("count", self.LED_COUNT)
        pin = cnf.get("pin", self.LED_PIN)
        freq_hz = cnf.get("freq_hz", self.LED_FREQ_HZ)
        dma = cnf.get("dma", self.LED_DMA)
        invert = cnf.get("invert", self.LED_INVERT)
        brightness = cnf.get("brightness", self.LED_BRIGHTNESS)
        channel = cnf.get("channel", self.LED_CHANNEL)
        strip = cnf.get("strip", self.LED_STRIP)
        self.strip = np.Adafruit_NeoPixel(count, pin, freq_hz, dma, invert, brightness, channel, strip)
        # Intialize the library (must be called once before other functions).
        self.strip.begin()

    def activate(self, led_no, colour):
        self.strip.setPixelColor(led_no, colour)

    def show(self):
        self.strip.show()

    def light_up(self, led_no, colour):
        self.activate(led_no, colour)
        self.strip.show()

    def turn_all_off(self):
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, 0)
        self.strip.show()
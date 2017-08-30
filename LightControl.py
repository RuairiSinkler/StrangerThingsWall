import time

import neopixel as np

class LEDString:

    # LED strip configuration:
    LED_COUNT      = 50      # Number of LED pixels.
    LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
    LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
    LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
    LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
    LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
    LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
    LED_STRIP      = np.ws.WS2811_STRIP_GRB   # Strip type and colour ordering

    def __init__(self, **cnf):
        # Create NeoPixel object with appropriate configuration.
        count = cnf.get("count", self.LED_COUNT)
        pin = cnf.get("pin", self.LED_PIN)
        freq_hz = cnf.get("freq_hz", self.LED_FREQ_HZ)
        dma = cnf.get("dma", self.LED_DMA)
        brightness = cnf.get("brightness", self.LED_BRIGHTNESS)
        invert = cnf.get("invert", self.LED_INVERT)
        channel = cnf.get("channel", self.LED_CHANNEL)
        strip = cnf.get("strip", self.LED_STRIP)
        self.strip = np.Adafruit_NeoPixel(count, pin, freq_hz, dma, brightness, invert, channel, strip)
        # Intialize the library (must be called once before other functions).
        self.strip.begin()

    def light_up(self, led_no, colour):
        self.strip.setPixelColor(led_no, colour)
        self.strip.show()
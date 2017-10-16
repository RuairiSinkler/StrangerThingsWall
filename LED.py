
class LED:

    def __init__(self, name, strip, number, colour):
        self.name = name
        self.strip = strip
        self.number = number
        self.colour = colour

    def activate(self):
        self.strip.setPixelColor(self.number, self.colour)

    def light_up(self):
        self.activate(self.number, self.colour)
        self.show()

    def activate_colour(self, colour):
        self.strip.setPixelColor(self.number, colour)

    def show(self):
        self.strip.show()

    def light_up_colour(self, colour):
        self.activate(self.number, colour)
        self.show()
import time
import random

import neopixel as np
import LightControl as lc

class Wall:

    def __init__(self, lights):

        self.lights = lights
        self.MAX_WORD_LENGTH = 20
        self.ALLOWED_CHARACTERS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ ")

        white = np.Color(255, 255, 255)
        dark_blue = np.Color(0, 0, 170)
        purple = np.Color(100, 0, 100)
        cyan = np.Color(50, 220, 220)
        light_blue = np.Color(0, 150, 200)
        yellow = np.Color(255, 200, 0)
        pink = np.Color(255, 50, 255)

        self.LETTER_COLOUR = {"A" : white, "B" : dark_blue, "C" : purple, "D" : cyan, "E" : light_blue, "F" : yellow,
                              "G" : pink, "H" : cyan,
                              "I" : cyan, "J" : pink, "K" : light_blue, "L" : cyan, "M" : yellow, "N" : pink,
                              "O" : purple, "P" : cyan, "Q" : pink,
                              "R" : cyan, "S" : white, "T" : yellow, "U" : light_blue, "V" : pink, "W" : light_blue,
                              "X" : yellow, "Y" : pink, "Z" : pink}

        self.LETTER_LED = {}

        file = open("leds.txt", "r")
        file_output = file.readlines()
        for line in file_output:
            letter = line[:line.index(":")]
            number = int(line[line.index(":") + 1:])
            self.LETTER_LED[letter] = number

        self.words = []

        file = open("words.txt", "r")
        file_output = file.readlines()
        for line in file_output:
            line = line.upper().rstrip()
            #print(line)
            #print(self.word_is_ok(line))
            if self.word_is_ok(line):
                self.words.append(line)

    def word_is_ok(self, word):
        word = word.upper()
        #print(len(word) < self.MAX_WORD_LENGTH)
        #print(set(word).issubset(self.ALLOWED_CHARACTERS))
        return set(word).issubset(self.ALLOWED_CHARACTERS) and len(word) < self.MAX_WORD_LENGTH

    def light_letter(self, letter):
        led = self.LETTER_LED.get(letter)
        colour = self.LETTER_COLOUR.get(letter)
        self.lights.activate(led, colour)

    def display_word(self, word):
        letters = list(word.upper())
        for letter in letters:
            if not(letter == " "):
                self.light_letter(letter)
                self.lights.show()
            time.sleep(1)
            self.lights.turn_all_off()
            time.sleep(1)

    def random_word(self):
        self.display_word(random.choice(self.words))
        self.flicker()

    def flicker(self, repetitions=10):
        for i in range(repetitions):
            self.turn_letters_on()
            time.sleep(0.2)
            self.lights.turn_all_off()
            time.sleep(0.2)

    def turn_letters_on(self):
        for letter in self.LETTER_LED:
            self.light_letter(letter)
        self.lights.show()

    def turn_all_off(self):
        self.lights.turn_all_off()

def main():
    lights = lc.LEDString(count=50)
    wall = Wall(lights)
    for i in range(9):
        wall.random_word()
    wall.turn_letters_on()
    time.sleep(10)
    wall.turn_all_off()

if __name__ == "__main__":
    main()
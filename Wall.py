import time

import neopixel as np
import LightControl as lc

LETTER_LED = {"A" : 0, "B" : 1, "C" : 2, "D" : 3, "E" : 4, "F" : 5, "G" : 6, "H" : 7,
              "I" : 17, "J" : 16, "K" : 15, "L" : 14, "M" : 13, "N" : 12, "O" : 11, "P" : 10, "Q" : 9,
              "R" : 19, "S" : 20, "T" : 21, "U" : 22, "V" : 23, "W" : 24, "X" : 25, "Y" : 26, "Z" : 27}

white = np.Color(255, 255, 255)
dark_blue = np.Color(0, 0, 170)
purple = np.Color(130, 0, 130)
cyan = np.Color(50, 220, 220)
light_blue = np.Color(0, 150, 200)
yellow = np.Color(255, 200, 0)
pink = np.Color(220, 0, 220)


LETTER_COLOUR = {"A" : white, "B" : dark_blue, "C" : purple,
                 "D" : cyan, "E" : light_blue, "F" : yellow,
                 "G" : pink, "H" : cyan,
                 "I" : cyan, "J" : pink, "K" : light_blue,
                 "L" : cyan, "M" : yellow, "N" : pink,
                 "O" : purple, "P" : cyan, "Q" : pink,
                 "R" : cyan, "S" : white, "T" : yellow,
                 "U" : light_blue, "V" : pink, "W" : light_blue,
                 "X" : yellow, "Y" : pink, "Z" : pink}

def light_letter(lights, letter):
    led = LETTER_LED.get(letter)
    colour = LETTER_COLOUR.get(letter)
    lights.activate(led, colour)

def display_word(lights, word):
    letters = list(word.upper())
    for letter in letters:
        if not(letter == " "):
            light_letter(lights, letter)
            lights.show()
        time.sleep(1)
        lights.turn_all_off()
        time.sleep(1)

def flicker(lights, repetitions=10):
    for i in range(repetitions):
        turn_all_on(lights)
        time.sleep(0.2)
        lights.turn_all_off()
        time.sleep(0.2)

def turn_all_on(lights):
    for letter in LETTER_LED:
        light_letter(lights, letter)
    lights.show()

def main():
    lights = lc.LEDString(count=50)
    display_word(lights, "run")
    flicker(lights)
    turn_all_on(lights)

if __name__ == "__main__":
    main()
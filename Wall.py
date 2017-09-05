import time
import random
import configparser
import queue
import threading
import twitter

import neopixel as np
import LightControl as lc

class Wall:

    def __init__(self, lights):

        self.lights = lights
        self.queued_words = queue.Queue()
        self.running = True
        self.inputs_required = True
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

        config = configparser.ConfigParser()
        config.read("wall.ini")

        self.LETTER_LED = {}

        options = config.options("LED Numbers")
        for option in options:
            letter = option.upper().rstrip()
            number = config.getint("LED Numbers", option)
            #print(letter, number, type(letter), type(number))
            self.LETTER_LED[letter] = number

        self.words = []

        words = config.get("Words", "words").split(",")
        for word in words:
            word = word.upper().rstrip()
            #print(line)
            #print(self.word_is_ok(line))
            #print(word)
            if self.word_is_ok(word):
                self.words.append(word)

        #Twitter setup
        consumer_key = config.get("Twitter", "consumer_key")
        consumer_secret = config.get("Twitter", "consumer_secret")
        access_token = config.get("Twitter", "access_token")
        access_token_secret = config.get("Twitter", "access_token_secret")
        self.api = twitter.Api(consumer_key=consumer_key,
                               consumer_secret=consumer_secret,
                               access_token_key=access_token,
                               access_token_secret=access_token_secret,
                               sleep_on_rate_limit=True)


    def run(self):
        inputs = threading.Thread(target=self.get_console_inputs)
        inputs.start()
        while self.running:
            if self.queued_words.empty():
                self.queue_random_word()
            self.display_queued_word()
            self.flicker()

    def get_console_inputs(self):
        while self.inputs_required:
            word = input("> ")
            if self.word_is_ok(word):
                print("Word added to queue")
                self.queued_words.put(word)
            else:
                print("Sorry, not a valid input")

    def get_twitter_inputs(self):
        latest_id = None
        while True:
            results = self.api.GetHomeTimeline(since_id=latest_id)
            for status in results:
                latest_id = 0
                word = status["text"]
                if self.word_is_ok(word):
                    print("Word added to queue")
                    self.queued_words.put(word)
                else:
                    print("Sorry, not a valid input")
                latest_id = max(latest_id, status["id"])
            time.sleep(60)


    def word_is_ok(self, word):
        word = word.upper()
        #print(len(word) < self.MAX_WORD_LENGTH)
        #print(set(word).issubset(self.ALLOWED_CHARACTERS))
        return set(word).issubset(self.ALLOWED_CHARACTERS) and len(word) < self.MAX_WORD_LENGTH

    def light_letter(self, letter):
        led = self.LETTER_LED.get(letter.upper())
        #print(led, type(led))
        colour = self.LETTER_COLOUR.get(letter.upper())
        self.lights.activate(led, colour)

    def display_word(self, word):
        letters = list(word.upper())
        for letter in letters:
            if not(letter == " "):
                self.light_letter(letter)
                self.lights.show()
            time.sleep(1)
            self.lights.turn_all_off()
            time.sleep(0.5)

    def display_queued_word(self):
        word = self.queued_words.get()
        self.display_word(word)

    def queue_random_word(self):
        self.queued_words.put(random.choice(self.words))

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
    try:
        lights = lc.LEDString(count=50)
        wall = Wall(lights)
        wall.run()
    finally:
        wall.running = False
        wall.inputs_required = False
        wall.turn_all_off()

if __name__ == "__main__":
    main()
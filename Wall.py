import time
import random
import configparser
import queue
import threading
import twitter

import neopixel as np
import LightControl as lc
import LED

class Wall:

    def __init__(self):

        self.init_time = int(time.time())
        self.queued_words = queue.Queue()
        self.running = True
        self.inputs_required = True
        self.MAX_WORD_LENGTH = 60
        self.ALLOWED_CHARACTERS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ ")
        self.letters = ["A", "B", "C", "D", "E", "F", "G", "H",
                        "I", "J", "K", "L", "M", "N", "O", "P", "Q",
                        "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]

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

        self.animations = [self.flicker, self.trail_letters, self.twinkle, self.fade_in_and_out]

        self.LETTER_LED = {}
        self.pin18 = lc.LEDString(count=config.getint("Strip Lengths", "pin18"))
        self.pin12 = lc.LEDString(count=config.getint("Strip Lengths", "pin12"), pin=12)

        options = config.options("LED Pin and Numbers")
        for option in options:
            letter = option.upper().rstrip()
            numbers = config.get("LED Pin and Numbers", option).split(",")
            pin = int(numbers[0])
            number = int(numbers[1])
            #print(letter, number, type(letter), type(number))
            strip = None
            if pin == 18:
                strip = self.pin18
            elif pin == 12:
                strip = self.pin12
            self.LETTER_LED[letter] = LED.LED(letter, strip, number, self.LETTER_COLOUR.get(letter))

        #q = self.LETTER_LED.get("Q")
        #i = self.LETTER_LED.get("I")
        #strip = i.strip
        #self.top_row = [x for x in range(0, q)]
        #self.middle_row = [x for x in range(i, q - 1, -1)]
        #self.bottom_row = [x for x in range(i + 1, strip.numPixels + 1)]

        self.blacklist = []

        try:
            blacklist = config.get("Words", "blacklist").split(",")
            for word in blacklist:
                #print("blacklist word", word)
                word = word.upper().rstrip()
                # print(line)
                # print(self.word_is_ok(line))
                # print(word)
                self.blacklist.append(word)
        except configparser.NoOptionError:
            self.blacklist = []

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
        self.consumer_key = config.get("Twitter", "consumer_key")
        self.consumer_secret = config.get("Twitter", "consumer_secret")
        self.access_token = config.get("Twitter", "access_token")
        self.access_token_secret = config.get("Twitter", "access_token_secret")
        self.api = twitter.Api(consumer_key=self.consumer_key,
                               consumer_secret=self.consumer_secret,
                               access_token_key=self.access_token,
                               access_token_secret=self.access_token_secret,
                               sleep_on_rate_limit=True)


    def run(self):
        console_inputs = threading.Thread(target=self.get_console_inputs)
        console_inputs.start()
        twitter_inputs = threading.Thread(target=self.get_twitter_inputs)
        twitter_inputs.start()
        while self.running:
            if self.queued_words.empty():
                self.queue_random_word()
            self.display_queued_word()
            random.choice(self.animations)()

    def get_console_inputs(self):
        while self.inputs_required:
            word = input("> ")
            if self.word_is_ok(word):
                print("Word added to queue")
                self.queued_words.put(word)
            else:
                print("Sorry, not a valid input")

    def get_twitter_inputs(self):
        latest_id = 0
        while True:
            try:
                print("Checking Twitter")
                results = self.api.GetMentions(count=200, since_id=latest_id)
                for status in results:
                    print("Checking tweet: {}".format(status.text))
                    if self.status_is_ok(status):
                        at_symbol = status.text.index("@")
                        mention = status.text.index(" ")
                        hashtag = status.text.index("#")

                        #Mention will be at end of tweet e.g. "hello @user #strangestthings"
                        word = status.text[:at_symbol].upper().rstrip()

                        #Mention will be at beginning of tweet e.g. "@user hello #strangestthings"
                        #status_is_ok also needs changing if this is used: mention_at_start check to be changed
                        #word = status.text[mention:hashtag].upper().rstrip()

                        if self.word_is_ok(word):
                            print("Twitter word added to queue: {}".format(word))
                            self.queued_words.put(word)
                            self.api.PostUpdate("Thank you @{}! Your message has been sent to the Upside Down!".format(status.user.screen_name), in_reply_to_status_id=status.id)
                        else:
                            print("Twitter word rejected")
                    else:
                        print("Status rejected")
                    latest_id = max(latest_id, status.id)
                    print()
                print("Twitter Check Sleeping")
                time.sleep(20)
            except Exception as e:
                print("Error getting tweets, retrying in 60 seconds")
                #self.api = twitter.Api(consumer_key=self.consumer_key,
                                       #consumer_secret=self.consumer_secret,
                                       #access_token_key=self.access_token,
                                       #access_token_secret=self.access_token_secret,
                                       #sleep_on_rate_limit=True)
                time.sleep(60)


    def status_is_ok(self, status):
        strangestthings = twitter.Hashtag(text="strangestthings")
        StrangestThings = twitter.Hashtag(text="StrangestThings")
        Strangestthings = twitter.Hashtag(text="Strangestthings")
        strangestThings = twitter.Hashtag(text="strangestThings")
        STRANGESTTHINGS = twitter.Hashtag(text="STRANGESTTHINGS")
        hashtags = [strangestthings, StrangestThings, Strangestthings, strangestThings, STRANGESTTHINGS]
        hashtag_present = False
        for hashtag in hashtags:
            if hashtag in status.hashtags:
                hashtag_present = True
        new_enough = status.created_at_in_seconds > self.init_time
        mention_at_start = status.text.index("@") == 0
        return new_enough and hashtag_present and not(mention_at_start)

    def check_blacklist(self, word):
        for item in self.blacklist:
            if item in word:
                return False
        return True

    def word_is_ok(self, word):
        word = word.upper().rstrip()
        #print(len(word) < self.MAX_WORD_LENGTH)
        #print(set(word).issubset(self.ALLOWED_CHARACTERS))
        characters_ok = set(word).issubset(self.ALLOWED_CHARACTERS)
        length_ok = len(word) < self.MAX_WORD_LENGTH
        blacklist_ok = self.check_blacklist(word)
        all_ok = characters_ok and length_ok and blacklist_ok
        return all_ok

    def light_letter(self, letter):
        led = self.LETTER_LED.get(letter.upper())
        #print(led, type(led))
        led.activate()

    def show(self, letter):
        led = self.LETTER_LED.get(letter.upper())
        # print(led, type(led))
        led.show()

    def show_all(self):
        self.pin18.show()
        self.pin12.show()

    def set_brightness_all(self, brightness):
        self.pin18.set_brightness(brightness)
        self.pin12.set_brightness(brightness)

    def turn_all_off(self):
        self.pin18.turn_all_off()
        self.pin12.turn_all_off()

    def display_word(self, word):
        letters = list(word.upper())
        for letter in letters:
            if not(letter == " "):
                self.light_letter(letter)
                self.show(letter)
            time.sleep(0.75)
            self.turn_all_off()
            time.sleep(0.25)

    def display_queued_word(self):
        word = self.queued_words.get()
        self.display_word(word)

    def queue_random_word(self):
        self.queued_words.put(random.choice(self.words))

    def flicker(self, repetitions=5):
        for i in range(repetitions):
            self.turn_letters_on()
            time.sleep(0.2)
            self.turn_all_off()
            time.sleep(0.2)

    def trail_letters(self, repetitions=1):
        for i in range(repetitions):
            for letter in self.letters:
                if letter != " ":
                    self.light_letter(letter)
                    self.show(letter)
                    time.sleep(0.02)
                    self.turn_all_off()
                    time.sleep(0.02)
            for letter in reversed(self.letters):
                if letter != " ":
                    self.light_letter(letter)
                    self.show(letter)
                    time.sleep(0.02)
                    self.turn_all_off()
                    time.sleep(0.02)

    def twinkle(self, repetitions=5):
        for i in range(repetitions):
            for letter in range(0, len(self.letters), 2):
                self.light_letter(self.letters[letter])
            self.show_all()
            time.sleep(0.2)
            self.turn_all_off()
            for letter in range(1, len(self.letters), 2):
                self.light_letter(self.letters[letter])
            self.show_all()
            time.sleep(0.2)
            self.turn_all_off()

    def fade_in_and_out(self, repetitions=1):
        for i in range(repetitions):
            self.fade_in()
            self.fade_out()

    def fade_in(self, repetitions=1):
        for i in range(repetitions):
            for letter in self.letters:
                self.light_letter(letter)
            for brightness in range(255):
                self.set_brightness_all(brightness)
                self.show_all()
                time.sleep(0.005)
        self.set_brightness_all(255)

    def fade_out(self, repetitions=1):
        for i in range(repetitions):
            for letter in self.letters:
                self.light_letter(letter)
            for brightness in range(255):
                self.set_brightness_all(255-brightness)
                self.show_all()
                time.sleep(0.005)
        self.turn_all_off()
        self.set_brightness_all(255)

    def turn_letters_on(self):
        for letter in self.LETTER_LED:
            self.light_letter(letter)
        self.show_all()

    def test_animations(self):
        for animation in self.animations:
            animation()

def main():
    try:
        wall = Wall()
        wall.test_animations()
        wall.run()
    finally:
        wall.running = False
        wall.inputs_required = False
        wall.turn_all_off()

if __name__ == "__main__":
    main()
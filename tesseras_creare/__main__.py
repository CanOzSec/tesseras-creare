import string
import itertools
import argparse
import sys
from os import path, remove

# Default write buffer 256 MiB
WRITE_BUFFER_LEN = 256 * 1024 * 1024 
BATCH_LEN = 256 * 1024 * 1024 // 10

patterns = [
    ["word", "year", "special char"],
    ["word", "year", "special char", "special char"],
    ["word", "special char", "year"],
    ["word", "special char", "year", "special char"],
    ["word", "special char", "(00-99)"],
    ["word", "special char", "(00-99)", "special char"],
    ["word", "special char", "keywalk"],
    ["word", "(00-99)", "special char"],
    ["word", "(00-99)", "special char", "special char"],
    ["word", "word", "special char"],
    ["word", "word", "year", "special char"],
    ["word", "word", "(00-99)", "special char"],
    ["word", "special char", "word"],
    ["word", "year", "word", "special char"],
    ["word", "keywalk", "special char"],
    ["keywalk", "word", "special char"],
    ["keywalk", "special char"]
]


leetMapping = {
    "a":["a", "4", "@"],
    "b":["b", "8"],
    "c":["c", "<", "{"],
    "d":["d"],
    "e":["e", "3"],
    "f":["f"],
    "g":["g", "6", "9"],
    "h":["h", "#"],
    "i":["i", "1"],
    "j":["j"],
    "k":["k"],
    "l":["l", "1"],
    "m":["m"],
    "n":["n"],
    "o":["o", "0"],
    "p":["p"],
    "q":["q","9"],
    "r":["r"],
    "s":["s", "$","5"],
    "t":["t", "7"],
    "u":["u"],
    "v":["v"],
    "w":["w", "VV"],
    "x":["x", "><"],
    "y":["y"],
    "z":["z", "2"]
}


class PasswordGuesser:
    def __init__(self, words, leetMode, passSizeMin, yearMin, yearMax, stdout):
        self.words = words
        self.leetMode = leetMode if leetMode != None else False
        self.passSizeMin = passSizeMin if passSizeMin != None else 8
        self.yearMin = yearMin if yearMin != None else 1980
        self.yearMax = yearMax if yearMax != None else 2030
        self.stdout = stdout
        self.count = 0
        self.replacements = {
            "word" : self.alter_word(self.words),
            "year" : [f"{i}" for i in range(self.yearMin, self.yearMax)],
            "char" : [i for i in string.ascii_lowercase],
            "special char" : [i for i in string.punctuation],
            "(00-99)" : [f"0{i}" for i in range(10)] + [f"{i}" for i in range(101)],
            "keywalk" : ["123", "321", "1234", "4321", "1234", "123456", "123456789", "qwe", "qwerty", "asd",
                        "qaz", "wsx", "edc", "rfv", "zxc", "zxcvbnm", "!@#", "!@#$",
                        ],
        }


    def leetize(self, word):
        newWord = ""
        for char in word:
            if len(leetMapping[char]) >= 2:
                newWord += leetMapping[char][1]
            else:
                newWord += char

        # Full leet, not recommended:
        # choices = [leetMapping.get(char, [char]) for char in word]
        # variations = ["".join(chars) for chars in itertools.product(*choices)]
        # return variations
        return newWord


    def alter_word(self, wordlist):
        alteredWordList = []
        alteredWordList.extend(wordlist)
        for word in wordlist:
            alteredWordList.append(word.capitalize())
        for word in wordlist:
            i = max(word.rfind(v) for v in "aeiou")
            alteredWordList.append(word[:i] + word[i + 1:])
            alteredWordList.append((word[:i] + word[i + 1:]).capitalize())
        if self.leetMode:
            for word in wordlist:
                alteredWordList.append(self.leetize(word))
        return set(alteredWordList)


    def generate(self, pattern):
        combinations = ["".join(i) for i in itertools.product(*[self.replacements[i] for i in pattern]) if len("".join(i)) >= self.passSizeMin]
        self.count += len(combinations)
        return "\n".join(combinations) + "\n"


    def generate2(self, pattern, fileName):
        with open(fileName, "a", buffering=WRITE_BUFFER_LEN) as f:
            it = itertools.product(*[self.replacements[i] for i in pattern])
            while True:
                batch = [
                    s for i in itertools.islice(it, BATCH_LEN)
                    if len(s := "".join(i)) >= self.passSizeMin
                ]
                self.count += len(batch)
                if not batch:
                    break
                f.write("\n".join(batch) + "\n")
                del batch


    def guess(self):
        if self.stdout:
            stderr = open("/tmp/log", "w")
            fileName = "/proc/self/fd/1"
        else:
            stderr = sys.stderr
            fileName = "custom-wordlist.lst"
        for pattern in patterns:
            print(f"Generating pattern: {pattern}...", file=stderr)
            self.generate2(pattern, fileName)
        print(f"Generated {self.count:,} guesses.", file=stderr)
        print("Successfully generated wordlist: custom-wordlist.txt", file=stderr)


def main():
    def words_or_wordlist(value):
        if path.isfile(value):
            with open(value, "r") as f:
                return f.read().split("\n")
        return [item.strip().lower() for item in value.split(",")]
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--words", type=words_or_wordlist, required=True, help="Comma separated words like: password,test,acme,foobar")
    parser.add_argument("-x", "--leet", action=argparse.BooleanOptionalAction, help="1337 mode")
    parser.add_argument("-l", "--length", type=int, required=False, help="Minimum password length, default: 8")
    parser.add_argument("-ys", "--year-start", type=int, required=False, help="Year start")
    parser.add_argument("-ye", "--year-end", type=int, required=False, help="Year end")
    parser.add_argument("-s", "--stdout", action=argparse.BooleanOptionalAction, help="Stdout mode")
    args = parser.parse_args()
    if path.exists("custom-wordlist.lst"):
            remove("custom-wordlist.lst")
    a = PasswordGuesser(args.words, args.leet, args.length, args.year_start, args.year_end, args.stdout)
    a.guess()


if __name__ == "__main__":
    main()


import random

def get_words():
    with open("words.txt") as f:
        return f.read().split()

words = sorted(list(map(lambda x: x.upper(), get_words())))

def num_to_indicator(n):
    D = {0: "incorrect", 1: "correct", 2: "misplaced"}
    return D.get(n, "WEIRD")

def guess(guesses):
    cites = []
    for j, guess in enumerate(guesses):
        word = guess["word"]
        score = guess["score"]
        print("word: {}".format(word, score))
        for i in range(0, 5):
            print(" {} : {}".format(word[i], num_to_indicator(score[i])))
            if score[i] == 2 and word[i] in "AEIOU":
                cites.append((j, i))
        print("")

    if len(cites) > 0:
        return {
            "title":"Something's not right",
            "message": "There appear to be yellow vowels.  Remove yellow vowels.  Then hit next",
            "cites":cites
        }

    return {"next": random.choice(words)}

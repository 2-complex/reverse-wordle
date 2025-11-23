import random

def get_words():
    with open("words.txt") as f:
        return f.read().split()

words = sorted(list(map(lambda x: x.upper(), get_words())))

def num_to_indicator(n):
    D = {0: "incorrect", 1: "correct", 2: "misplaced"}
    return D.get(n, "WEIRD")

def guess(guesses):
    for guess in guesses:
        word = guess["word"]
        score = guess["score"]
        print("word: {}".format(word, score))
        for i in range(0, 5):
            print(" {} : {}".format(word[i], num_to_indicator(score[i])))
        print("")

    if len(guesses) == 3:
        return {"title":"Something's not right", "message": "There appear to be three guesses.  That's an awful lot.  Are you sure you want to continue?", "options":["continue"]}

    return {"next": random.choice(words)}

import random

def get_words():
    with open("common_words.txt") as f:
        return f.read().split()

lexicon = sorted(list(map(lambda x: x.upper(), get_words())))

def can_eliminate_letter(letter, guess_word, score):
    for i in range(0, 5):
        if guess_word[i] == letter and score[i] != 0:
            return False
    return True

def reveal(guesses_so_far, word):
    return {
        "title":"I still give up!",
        "message": word,
        "gameover":True,
    }

def guess(guesses_so_far):
    s = set(lexicon)

    for guess in guesses_so_far:
        def is_viable(candidate_word):
            for i in range(0, 5):
                if guess['score'][i] == 0 and can_eliminate_letter(guess['word'][i], guess['word'], guess['score']) and guess['word'][i] in candidate_word:
                    return False

                if guess['score'][i] == 1 and guess['word'][i] != candidate_word[i]:
                    return False

                if guess['score'][i] == 2 and guess['word'][i] not in candidate_word:
                    return False

                if guess['score'][i] == 2 and guess['word'][i] == candidate_word[i]:
                    return False
            return True

        s = set(filter(is_viable, s))

    if len(s) == 0:
        return {
            "title":"I give up!",
            "message": "What was your word?",
            "gameover":True,
            "entry":True,
        }

    cites = []
    if len(cites) > 0:
        return {
            "title":"Something's not right",
            "message": "There appear to be yellow vowels.  Remove yellow vowels.  Then hit next",
            "cites":cites
        }

    if len(guesses_so_far) > 0 and guesses_so_far[-1]["score"] == 5*[1]:
        return {
            "title":"Thank you",
            "message": "Word guessed",
            "cites":[],
            "gameover":True
        }

    return {"next_guess": random.choice(list(s))}

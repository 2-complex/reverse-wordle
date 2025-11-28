import random

def get_words(path):
    def words_from_file(p):
        with open(p) as f:
            return f.read().split()
    return sorted(list(map(lambda x: x.upper(), words_from_file(path))))

common_lexicon = get_words("common_words.txt")
less_common_lexicon = get_words("less_common_words.txt")


def counts(word):
    D = {}
    for char in word:
        D[char] = D.get(char, 0) + 1
    return D

class Conclusion:
    def __init__(self):
        self.cites = []

    def at_cites(self, cites):
        self.cites = cites
        return self

class Exactly(Conclusion):
    def __init__(self, letter, count):
        self.letter = letter
        self.count = count

    def __repr__(self):
        if self.count == 0:
            return "'{}' not present".format(self.letter)
        elif self.count == 1:
            return "'{}' occurs exactly once".format(self.letter)
        else:
            return "'{}' occurs exactly {} times".format(self.letter, self.count)

    def __eq__(self, other):
        return type(other) is type(self) and self.count == other.count and self.letter == other.letter

    def __hash__(self):
        return hash(("Exactly", self.count, self.letter))

class AtLeast(Conclusion):
    def __init__(self, letter, count):
        self.letter = letter
        self.count = count

    def __repr__(self):
        if self.count == 0:
            return "'{}' occurs at least 0 times, which is vacuous, that's weird".format(self.letter)
        if self.count == 1:
            return "'{}' occurs at least once".format(self.letter)
        if self.count == 1:
            return "'{}' occurs at {} times".format(self.letter, self.count)

    def __eq__(self, other):
        return type(other) is type(self) and self.count == other.count and self.letter == other.letter

    def __hash__(self):
        return hash(("AtLeast", self.count, self.letter))

class MustBe(Conclusion):
    def __init__(self, index, letter):
        self.index = index
        self.letter = letter

    def __repr__(self):
        return "'{}' in position {}".format(self.letter, self.index)

    def __eq__(self, other):
        return type(other) is type(self) and self.index == other.index and self.letter == other.letter

    def __hash__(self):
        return hash(("MustBe", self.index, self.letter))

class CannotBe(Conclusion):
    def __init__(self, index, letter):
        self.index = index
        self.letter = letter

    def __repr__(self):
        return "letter in position {} cannot be '{}'".format(self.index, self.letter)

    def __eq__(self, other):
        return type(other) is type(self) and self.index == other.index and self.letter == other.letter

    def __hash__(self):
        return hash(("CannotBe", self.index, self.letter))


class Contradiction(Exception):
    def sentence(self, guesses):
        return "The above letters seem to contradict"

    def get_cites(self):
        pass


class LetterExactCountsContradict(Contradiction):
    def __init__(self, first_exactly, second_exactly):
        self.first_exactly = first_exactly
        self.second_exactly = second_exactly

    def get_cites(self):
        return self.first_exactly.cites + self.second_exactly.cites

class LetterExactCountContradictsMinimum(Contradiction):
    def __init__(self, exactly, at_least):
        self.exactly = exactly
        self.at_least = at_least

    def get_cites(self):
        return self.exactly.cites + self.at_least.cites

class LetterAtIndexMustBeTwoDifferentThings(Contradiction):
    def __init__(self, first_must_be, second_must_be):
        self.first_must_be = first_must_be
        self.second_must_be = second_must_be

    def get_cites(self):
        return self.first_must_be.cites + self.second_must_be.cites

class LetterAtIndexMustBeAndAlsoCannotBe(Contradiction):
    def __init__(self, must_be, cannot_be):
        self.must_be = must_be
        self.cannot_be = cannot_be

    def get_cites(self):
        return self.must_be.cites + self.cannot_be.cites

class Batch:
    def __init__(self, exactly = [], at_least = [], must_be = [], cannot_be = []):
        self.exactly = exactly
        self.at_least = at_least
        self.must_be = must_be
        self.cannot_be = cannot_be

    def all(self):
        return set(self.exactly + self.at_least + self.must_be + self.cannot_be)


    def check_word(self, word):
        contradictions = []
        for ex in self.exactly:
            if word.count(ex.letter) != ex.count:
                contradictions.append(ex)

        for atl in self.at_least:
            if word.count(atl.letter) < atl.count:
                contradictions.append(atl)

        for mb in self.must_be:
            if word[mb.index] != mb.letter:
                contradictions.append(mb)

        for cb in self.cannot_be:
            if word[cb.index] == cb.letter:
                contradictions.append(cb)

        return contradictions


    def congeal(self):
        letter_to_exactly = {}
        for ex in self.exactly:
            if ex.letter in letter_to_exactly:
                if letter_to_exactly[ex.letter].count != ex.count:
                    raise LetterExactCountsContradict(letter_to_exactly[ex.letter], ex)
            else:
                letter_to_exactly[ex.letter] = ex

        letter_to_at_least = {}
        for atl in self.at_least:
            if atl.letter in letter_to_at_least:
                if atl.count > letter_to_at_least[atl.letter].count:
                    letter_to_at_least[atl.letter] = atl
            else:
                if atl.letter in letter_to_exactly:
                    ex = letter_to_exactly[atl.letter]
                    if ex.count < atl.count:
                        raise LetterExactCountContradictsMinimum(ex, atl)
                else:
                    letter_to_at_least[atl.letter] = atl

        index_to_must_be = {}
        for mb in self.must_be:
            if mb.index in index_to_must_be:
                current = index_to_must_be[mb.index]
                if current.letter != mb.letter:
                    raise LetterAtIndexMustBeTwoDifferentThings(current, mb)
            else:
                index_to_must_be[mb.index] = mb

        index_to_cannot_be_letters = {}
        for cb in self.cannot_be:
            if cb.index in index_to_must_be:
                if index_to_must_be[cb.index].letter == cb.letter:
                    raise LetterAtIndexMustBeAndAlsoCannotBe(index_to_must_be[cb.index], cb)

            if cb.index in index_to_cannot_be_letters:
                index_to_cannot_be_letters[cb.index].append(cb.letter)
            else:
                index_to_cannot_be_letters[cb.index] = [cb.letter]

        def criterion(word):
            for letter, exactly in letter_to_exactly.items():
                if word.count(letter) != exactly.count:
                    return False

            for letter, at_least in letter_to_at_least.items():
                if word.count(letter) < at_least.count:
                    return False

            for index, must_be in index_to_must_be.items():
                if word[index] != must_be.letter:
                    return False

            for index, cannot_be_letters in index_to_cannot_be_letters.items():
                if word[index] in cannot_be_letters:
                    return False

            return True

        return criterion

def draw_conclusions(guesses, row = 0):
    exactly = []
    at_least = []
    must_be = []
    cannot_be = []

    for j, guess in enumerate(guesses):
        word = guess['word']
        score = guess['score']

        for i in range(0, 5):
            if score[i] == 1:
                must_be.append(MustBe(i, word[i]).at_cites([(row+j,i)]))
            if score[i] == 2:
                cannot_be.append(CannotBe(i, word[i]).at_cites([(row+j,i)]))

        for letter in set(word):
            cites = []
            indices = [i for i, char in enumerate(word) if char == letter]
            some_are_gray = False
            count = 0
            for i in indices:
                cites.append((row+j,i))
                if score[i] == 0:
                    some_are_gray = True
                else:
                    count += 1

            if some_are_gray:
                exactly.append(Exactly(letter, count).at_cites(cites))
            else:
                at_least.append(AtLeast(letter, count).at_cites(cites))
    return Batch(exactly, at_least, must_be, cannot_be)


def can_eliminate_letter(letter, guess_word, score):
    for i in range(0, 5):
        if guess_word[i] == letter and score[i] != 0:
            return False
    return True

import string
def is_valid_word(target_word):
    if len(target_word) != 5:
        return False

    for c in target_word:
        if c not in string.ascii_uppercase:
            return False

    return True


def reveal(guesses_so_far, target_word):
    target_word = target_word.upper()
    if not is_valid_word(target_word):
        return {
            "title":"Invalid Input",
            "message": "Words must be five-letters, A-Z.  What was your word?",
            "entry": True,
            "gameover":False,
        }

    cites = []
    for row, guess in enumerate(guesses_so_far):
        batch = draw_conclusions([guess], row)
        for c in batch.check_word(target_word):
            cites += c.cites

    if len(cites) > 0:
        return {
            "title":"Something's not right",
            "message": "Check the letters above?  They seem to contradict {}.  We can keep playing, if you adjust and hit Next".format(target_word),
            "gameover":False,
            "cites":cites
        }
    else:
        return {
            "title": "You're right!",
            "message": "{} meets all those criteria".format(target_word),
            "gameover":True,
        }

def guess(guesses_so_far):
    batch = draw_conclusions(guesses_so_far)
    criterion = None
    try:
        criterion = batch.congeal()
    except Contradiction as cont:
        print(type(cont))
        return {
            "title":"Something's not right",
            "message": cont.sentence(guesses_so_far),
            "cites": cont.get_cites()
        }

    arcane = False
    remaining_choices = list(filter(criterion, common_lexicon))

    if len(remaining_choices) == 0:
        arcane = True
        remaining_choices = list(filter(criterion, less_common_lexicon))

    if len(remaining_choices) == 0:
        return {
            "title":"I give up!",
            "message":"What was your word?",
            "entry":True,
        }

    if len(guesses_so_far) > 0 and guesses_so_far[-1]["score"] == 5*[1]:
        return {
            "title":"Word guessed",
            "message": "Thanks for playing",
            "cites":[],
            "gameover":True
        }

    return {
        "title":"Excellent",
        "message":"Next, score the guess.  Click the letters to change their color.",
        "next_guess": random.choice(list(remaining_choices))}


def test_sets_of_conclusions():
    assert({AtLeast(1, 'A')} == {AtLeast(1, 'A')})
    assert({AtLeast(1, 'A').at_cites([(1,2)])} == {AtLeast(1, 'A').at_cites([(3,4)])})

def test_congeal_function():
    batch = draw_conclusions([
        {'word': 'THREE', 'score': [2, 0, 2, 0, 1]},
    ])

    assert(batch.all() == {
        AtLeast('T', 1),
        Exactly('E', 1),
        Exactly('H', 0),
        AtLeast('R', 1),
        CannotBe(0, 'T'),
        CannotBe(2, 'R'),
        MustBe(4, 'E'),
    })

def test_congeal_function_2():
    batch = draw_conclusions([
        {'word': 'THREE', 'score': [0, 0, 1, 1, 1]},
    ])

    assert(batch.all() == {
        Exactly('T', 0),
        Exactly('H', 0),
        AtLeast('E', 2),
        AtLeast('R', 1),
        MustBe(2, 'R'),
        MustBe(3, 'E'),
        MustBe(4, 'E'),
    })

test_words = ["APPLE", "CRATE", "THERE", "IRATE", "GREAT", "MATTE"]

def test_criterion():
    batch = draw_conclusions([
        {'word': 'THREE', 'score': [2, 0, 2, 0, 1]},
    ])
    assert(set(filter(batch.congeal(), test_words)) == {"CRATE", "IRATE"})


def test_criterion2():
    batch = draw_conclusions([
        {'word': 'LATHE', 'score': [0, 1, 1, 0, 1]},
    ])
    assert(set(filter(batch.congeal(), test_words)) == {"MATTE"})


def test_criterion_two_guesses():
    batch = draw_conclusions([
        {'word': 'COALS', 'score': [0, 0, 2, 1, 0]},
        {'word': 'ADULT', 'score': [1, 0, 0, 1, 0]},
    ])
    assert(set(filter(batch.congeal(), test_words)) == {"APPLE"})


def test_exact_count_contradiction():
    batch = Batch(
        exactly=[Exactly('A', 1), Exactly('A', 2)],
    )

    try:
        batch.congeal()
        assert(False)
    except LetterExactCountsContradict as cont:
        assert(cont.first_exactly.letter == 'A')
        assert(cont.second_exactly.letter == 'A')


def test_at_least_count_contradiction():
    batch = Batch(
        exactly=[Exactly('A', 0)],
        at_least=[AtLeast('A', 1)],
    )

    try:
        batch.congeal()
        assert(False)
    except LetterExactCountContradictsMinimum as cont:
        assert(cont.exactly.letter == 'A')
        assert(cont.exactly.count == 0)
        assert(cont.at_least.letter == 'A')
        assert(cont.at_least.count == 1)


def test_letter_at_index_two_different_things_contradiction():
    batch = Batch(
        must_be = [MustBe(2, 'B'), MustBe(2, 'Q')]
    )

    try:
        batch.congeal()
        assert(False)
    except LetterAtIndexMustBeTwoDifferentThings as cont:
        assert(cont.first_must_be.index == 2)
        assert(cont.first_must_be.letter == 'B')
        assert(cont.second_must_be.index == 2)
        assert(cont.second_must_be.letter == 'Q')


def test_letter_must_be_and_also_cannot_be():
    batch = Batch(
        must_be = [MustBe(3, 'B')],
        cannot_be = [CannotBe(3, 'B')]
    )

    try:
        batch.congeal()
        assert(False)
    except LetterAtIndexMustBeAndAlsoCannotBe as cont:
        assert(cont.must_be.index == 3)
        assert(cont.must_be.letter == 'B')
        assert(cont.cannot_be.index == 3)
        assert(cont.cannot_be.letter == 'B')

test_sets_of_conclusions()
test_congeal_function()
test_congeal_function_2()
test_criterion()
test_criterion2()
test_exact_count_contradiction()
test_at_least_count_contradiction()
test_letter_at_index_two_different_things_contradiction()
test_criterion_two_guesses()

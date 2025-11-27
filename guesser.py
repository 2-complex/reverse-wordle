import random

def get_words():
    with open("words.txt") as f:
        return f.read().split()

lexicon = sorted(list(map(lambda x: x.upper(), get_words())))


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
            return "'{}' not in answer".format(self.letter)
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
        return "'{}' occurs at least {}".format(self.letter, self.count)

    def __eq__(self, other):
        return type(other) is type(self) and self.count == other.count and self.letter == other.letter

    def __hash__(self):
        return hash(("AtLeast", self.count, self.letter))

class MustBe(Conclusion):
    def __init__(self, index, letter):
        self.index = index
        self.letter = letter

    def __repr__(self):
        return "letter in position {} is '{}'".format(self.index, self.letter)

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

class LetterExactCountsContradict(Exception):
    def __init__(self, first_exactly, second_exactly):
        self.first_exactly = first_exactly
        self.second_exactly = second_exactly

class LetterExactCountContradictsMinimum(Exception):
    def __init__(self, exactly, at_least):
        self.exactly = exactly
        self.at_least = at_least

class LetterAtIndexMustBeTwoDifferentThings(Exception):
    def __init__(self, first_must_be, second_must_be):
        self.first_must_be = first_must_be
        self.second_must_be = second_must_be

class LetterAtIndexMustBeAndAlsoCannotBe(Exception):
    def __init__(self, must_be, cannot_be):
        self.must_be = must_be
        self.cannot_be = cannot_be

class Batch:
    def __init__(self, exactly = [], at_least = [], must_be = [], cannot_be = []):
        self.exactly = exactly
        self.at_least = at_least
        self.must_be = must_be
        self.cannot_be = cannot_be

    def all(self):
        return set(self.exactly + self.at_least + self.must_be + self.cannot_be)

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
            if cb.index in index_to_cannot_be_letters:
                index_to_cannot_be_letters[cb.index].append(cb.letter)
            else:
                if cb.index in index_to_must_be:
                    raise LetterAtIndexMustBeAndAlsoCannotBe(index, index_to_must_be[cb.index], cb)
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

def draw_conclusions(guesses_so_far):
    exactly = []
    at_least = []
    must_be = []
    cannot_be = []

    for j, guess in enumerate(guesses_so_far):
        word = guess['word']
        score = guess['score']

        for i in range(0, 5):
            if score[i] == 1:
                must_be.append(MustBe(i, word[i]).at_cites([(j,i)]))
            if score[i] == 2:
                cannot_be.append(CannotBe(i, word[i]).at_cites([(j,i)]))

        for letter in set(word):
            cites = []
            indices = [i for i, char in enumerate(word) if char == letter]
            some_are_gray = False
            count = 0
            for i in indices:
                cites.append((j,i))
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
            "title":"Something's not right",
            "message": "I can eliminate all words based on these scores, please reexamine scores and resubmit"
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

    return {"next": random.choice(list(s))}


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

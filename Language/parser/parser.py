import nltk
import sys

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

# ENP = Enhanced noun phrase, this is used as a buffer to stop
# multiple Det's being applied
NONTERMINALS = """
S -> ENP VP | S Conj S | PP S | S Conj VP | NP VP
ENP -> ENP Conj ENP | Det NP | ENP PP | PP ENP | ENP Conj NP | NP Conj ENP
PP -> P NP | P ENP
NP -> N | Adj NP
VP -> V | VP NP | Adv VP | VP Adv | VP PP | VP Conj NP
VP -> VP ENP | VP Conj VP
"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """
    tokens = nltk.word_tokenize(sentence)
    valid_tokens = [
        token.lower()
        for token in tokens
        # Checks to make sure there is at least one letter
        if any(character.isalpha() for character in token)
    ]
    return valid_tokens


def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    noun_phrases = list()
    # This finds every single noun phrase on all levels
    for np in tree.subtrees(lambda t: t.label() == 'NP'):
        has_sub_np = False
        # This loop checks if this subtree has any noun phrases in it
        for st in np.subtrees(lambda t: t.label() == 'NP'):
            if st == np:
                continue
            has_sub_np = True
            break

        # If it doesn't have sub noun phrases, it's a chunk
        if not has_sub_np:
            noun_phrases.append(np)

    return noun_phrases


if __name__ == "__main__":
    main()

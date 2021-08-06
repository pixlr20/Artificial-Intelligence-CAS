import nltk

t = nltk.Tree.fromstring("(S (NP (D the) (N dog)) (VP (V chased) (NP (D the) (N cat))))")
t.pretty_print()

for subtree in t.subtrees(lambda t: t.label() == 'NP'):
    subtree.pretty_print()
    print(subtree.subtrees(lambda t: t.label() == 'NP'))
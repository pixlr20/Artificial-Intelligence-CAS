from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Puzzle 0
# A says "I am both a knight and a knave."
A_Statement = And(AKnight, AKnave)
knowledge0 = And(
    # The first two lines replicate XOR
    Or(AKnight, AKnave),
    Not(And(AKnight, AKnave)),
    # Statements are biconditional because if we know a
    # statement is true, we know who a person is
    Biconditional(AKnight, A_Statement),
    Biconditional(AKnave, Not(A_Statement))
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
A_Statement = And(AKnave, BKnave)
knowledge1 = And(
    # For each person, there is another xor statement
    Or(AKnight, AKnave),
    Not(And(AKnight, AKnave)),
    Or(BKnight, BKnave),
    Not(And(BKnight, BKnave)),
    Biconditional(AKnight, A_Statement),
    Biconditional(AKnave, Not(A_Statement))
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
A_Statement = Or(And(AKnave, BKnave), And(AKnight, BKnight))
B_Statement = Or(And(BKnight, AKnave), And(BKnave, AKnight))
knowledge2 = And(
    Or(AKnight, AKnave),
    Not(And(AKnight, AKnave)),
    Or(BKnight, BKnave),
    Not(And(BKnight, BKnave)),
    Biconditional(AKnight, A_Statement),
    Biconditional(AKnave, Not(A_Statement)),
    Biconditional(BKnight, Or(B_Statement)),
    Biconditional(BKnave, Not(B_Statement))
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
A_Statement = Or(AKnight, AKnave)
B_Statement = CKnave
C_Statement = AKnight
knowledge3 = And(
    Or(AKnight, AKnave),
    Not(And(AKnight, AKnave)),
    Or(BKnight, BKnave),
    Not(And(BKnight, BKnave)),
    Or(CKnight, CKnave),
    Not(And(CKnight, CKnave)),
    Biconditional(AKnight, A_Statement),
    Biconditional(AKnave, Not(A_Statement)),
    Biconditional(BKnight, B_Statement),
    Biconditional(BKnave, Not(B_Statement)),
    Biconditional(CKnight, C_Statement),
    Biconditional(CKnave, Not(C_Statement))
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()

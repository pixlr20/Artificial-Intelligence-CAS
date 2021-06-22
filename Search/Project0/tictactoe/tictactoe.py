"""
Tic Tac Toe Player
"""

import math

X = "X"
O = "O"
EMPTY = None 


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Counting lines based on https://stackoverflow.com/questions/43082149/simple-way-to-count-number-of-specific-elements-in-2d-array-python
    I thought there would be a simpler way of counting the number of Xs & Os 
    then a nested loop so I looked for a way to count specific elements in a 2D
    array online.
    """
    x_count = sum(row.count(X) for row in board)
    o_count = sum(row.count(O) for row in board)
    if x_count == o_count:
        return X
    else:
        return O
    
            

def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    moves = set()
    for row in range(len(board)):
        for col in range(len(row)):
            if board[row][col] == EMPTY:
                moves.add((row, col))
    return moves


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    new_board = board.copy()
    if board[action[0]][action[1]] != EMPTY:
        raise Exception("FOR DEBUGGING: You can't make a move on a non-empty tile")
    else:
        new_board[action[0]][action[1]] = player(board)
    return new_board

def find_winner(line):
    """
    Checks if line has winner or not
    """
    if line.count(X) == 3:
        return X
    elif line.count(O) == 3:
        return O
    else:
        return None

def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    for num in range(3):
        result = find_winner(board[num])
        if result != None:
            return result
        result = find_winner([board[0][num], board[1][num], board[2][num]])
        if result != None:
            return result

    result = find_winner([board[0][0], board[1][1], board[2][2]])
    if result != None:
        return result
    result = find_winner([board[0][2], board[1][1], board[2][0]])
    if result != None:
        return result
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    return (sum(row.count(EMPTY) for row in board) == 0 or winner(board) != None)


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    champ = winner(board)
    if champ == X:
        return 1
    if champ == O:
        return -1
    return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    raise NotImplementedError

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
        for col in range(len(board)):
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
    empty_spaces = sum(row.count(EMPTY) for row in board)
    win = winner(board)
    return (empty_spaces == 0 or win != None)


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

def max_value(board):
    if terminal(board):
        return utility(board)
    v = float('-inf')
    for action in actions(board):
        v = max(v, min_value(result(board, action)))
    return v

def min_value(board):
    if terminal(board):
        return utility(board)
    v = float('+inf')
    for action in actions(board):
        v = min(v, max_value(result(board, action)))
    return v

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    turn = player(board)
    moves = actions(board)
    best_move = None
    if turn == X:
        best_score = float('-inf')
        for action in moves:
            score = max_value(result(board, action))
            if score > best_score:
                best_score = score
                best_move = action
    if turn == O:
        best_score = float('+inf')
        for action in moves:
            score = min_value(result(board, action))
            if score < best_score:
                best_score = score
                best_move = action

    return best_move

test = [['X', 'O', 'X'], ['O', 'X', 'X'], ['O', 'O', 'X']]
print(terminal(test))
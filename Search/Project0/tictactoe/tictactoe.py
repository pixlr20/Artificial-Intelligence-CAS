"""
Tic Tac Toe Player
"""

import math

X = "X"
O = "O"
EMPTY = None

# For readability, I added these constanst
POS_INF = float('+inf')
NEG_INF = float('-inf')


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns which player's turn it is.

    Counting lines based on www.tinyurl.com/xw4ha3pn (shortened long url)
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
    # The choice of list over set was because when moves is a set
    # the AI chooses the upper middle box instead of the upper left
    # corner as its first move as X (mostly an arbitrary decision)
    moves = list()
    for row in range(len(board)):
        for col in range(len(board)):
            if board[row][col] == EMPTY:
                moves.append((row, col))
    return moves


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.

    I must copy each row individually so changing the board on one level
    of recursion does not change it on every layer (this took me quite some
    time to figure out).
    """
    new_board = [row.copy() for row in board]
    new_board[action[0]][action[1]] = player(board)
    return new_board


def find_winner(line):
    """
    Helper function that checks if line has winner or not
    """
    if line.count(X) == 3:
        return X
    elif line.count(O) == 3:
        return O
    else:
        return None


def update_result(result, line_winner):
    """
    Helper function that consisely changes the variable, result,
    if a winner has been found.
    """
    return line_winner if line_winner is not None else result


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    result = None
    for n in range(3):
        # Checks row n
        row = board[n]
        result = update_result(result, find_winner(row))
        # Checks column n
        column = [board[0][n], board[1][n], board[2][n]]
        result = update_result(result, find_winner(column))

    # Check diagonals
    diagonal_a = [board[0][0], board[1][1], board[2][2]]
    diagonal_b = [board[0][2], board[1][1], board[2][0]]
    result = update_result(result, find_winner(diagonal_a))
    result = update_result(result, find_winner(diagonal_b))
    return result


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    empty_spaces = sum(row.count(EMPTY) for row in board)
    champ = winner(board)
    return (empty_spaces == 0 or champ is not None)


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


def max_value(board, alpha, beta):
    """
    Returns the highest possible score this state, board, can achieve

    I implemented alpha-beta pruning after learning about it from wikipedia:
    https://en.wikipedia.org/wiki/Alpha%E2%80%93beta_pruning.
    It was helpful for understanding what it meant.

    Alpha is the minimum score the maximizing player knows they can get.
    Beta is the maximum score the minimizing player knows they can get.
    """
    if terminal(board):
        return utility(board)
    v = NEG_INF
    for action in actions(board):
        v = max(v, min_value(result(board, action), alpha, beta))
        # If the lowest possible score the minimizing player can
        # get in this state, v, is greater than the the maximum score
        # they're assured of, beta, there is no reason delve further
        # into this node because the maximizing player will choose
        # a state with a higher score than beta.
        if v >= beta:
            break
        alpha = max(alpha, v)
    return v


def min_value(board, alpha, beta):
    """
    Returns the lowest possible score this state, board, can achieve.
    This also implements alpha-beta pruning.
    """
    if terminal(board):
        return utility(board)
    v = POS_INF
    for action in actions(board):
        v = min(v, max_value(result(board, action), alpha, beta))
        # If the highest possible score the maximizing player can
        # get in this state, v, is less than the the minimum score
        # they're assured of, alpha, there is no reason delve further
        # into this node because the minimizing player will choose
        # a state with a lower score than alpha.
        if v <= alpha:
            break
        beta = min(beta, v)
    return v


def get_best_move(board, moves, best_score, score_func, comp_factor):
    """
    Finds the best move for the max or min player
    using the minimax algorithm by comparing
    each possible action and calculating their score
    """
    best_move = None
    for action in moves:
        score = score_func(result(board, action), NEG_INF, POS_INF)
        # If this is for O, comp_factor = -1 so it'll actually
        # check if score < best_score since we don't flip the sign
        # after multiplying by -1
        if score * comp_factor > best_score * comp_factor:
            best_score = score
            best_move = action
    return best_move


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    turn = player(board)
    moves = actions(board)
    best_move = None
    if turn == X:
        best_move = get_best_move(board, moves, NEG_INF, min_value, 1)

    if turn == O:
        best_move = get_best_move(board, moves, POS_INF, max_value, -1)

    return best_move

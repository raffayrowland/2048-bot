from board import get_zeros_location, do_move_if_legal, left, right, up, down
from board_score import evaluate_board

_ = [
#   0  1  2  3
    2, 2, 2, 0, # 0
    2, 2, 2, 2, # 4
    2, 2, 2, 0, # 8
    8, 4, 4, 2, # 12
]

MOVES = [(0, left), (1, right), (2, up), (3, down)]

def generate_all_possible_spawns(board):
    zeros = get_zeros_location(board)
    configurations = []
    zero_count = len(zeros)

    for zero in zeros:
        p2 = 0.9 / zero_count
        p4 = 0.1 / zero_count

        b2 = board.copy()
        b2[zero] = 2
        configurations.append([b2, p2])

        b4 = board.copy()
        b4[zero] = 4
        configurations.append([b4, p4])

    return configurations

def expected_value_after_spawn(board):
    zeros = get_zeros_location(board)
    zero_count = len(zeros)

    if zero_count == 0:
        return evaluate_board(board)

    expected_value = 0
    for zero in zeros:
        board[zero] = 2
        expected_value += (0.9 / zero_count) * evaluate_board(board)

        board[zero] = 4
        expected_value += (0.1 / zero_count) * evaluate_board(board)

        board[zero] = 0

    return expected_value

def one_play(states):
    next = []
    for board, probability, rm in states:
        for move_idx, move in MOVES:
            changed, result, _ = do_move_if_legal(board.copy(), move, spawn=False)
            if not changed:
                continue
            root_move = move_idx if rm is None else rm
            for child, prob in generate_all_possible_spawns(result):
                next.append((child, probability * prob, root_move))

    return next


def get_best_move(state, depth=1):
    # State is tuple like (board, probability, root_move)
    plays = [state]

    for _ in range(depth):
        plays = one_play(plays)

    totals = [0, 0, 0, 0]
    for board, prob, root_move in plays:
        if root_move is not None:
            totals[root_move] += prob * evaluate_board(board)

    best = max(range(4), key=lambda m: totals[m])
    return best, totals

example = get_best_move((_, 1, None), depth=3)
print(example)
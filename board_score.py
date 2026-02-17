_ = [
#   0  1  2  3
    4, 8, 0, 0, # 0
    0, 0, 2, 0, # 4
    0, 0, 0, 0, # 8
    16, 8, 4, 2, # 12
]

def highest_in_corner(board):
    highest = max(board)

    if board[12] == highest:
        return True

    return False

def snake_pattern(board, weights=None):
    if weights is None:
        weights = [
            0, 0, 0, 0,
            2, 1, 0, 0,
            9, 10, 12, 15,
            50, 35, 25, 20,
        ]

    return sum(w * v for w, v in zip(weights, board))


def count_empty_spaces(board):
    space_count = 0
    for item in board:
        if item == 0:
            space_count += 1

    return space_count

def bottom_row_full(board):
    if 0 in board[12:]:
        return False

    return True

def evaluate_board(board):
    score = 0
    weights = [
        0, 0, 0, 0,
        0, 0, 0, 2,
        4, 8, 16, 32,
        512, 256, 128, 64,
    ]

    spaces = count_empty_spaces(board)
    snake = snake_pattern(board, weights)
    highest_corner = highest_in_corner(board)
    # full_bottom_row = bottom_row_full(board)

    score += snake * 0.1
    score += spaces * 20
    score += 300 if highest_corner else 0
    # score += 2000 if full_bottom_row else 0

    return score

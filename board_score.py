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

def snake_pattern(board, weights):
    return sum(w * v for w, v in zip(weights, board))

def get_max_possible_snake(board):
    sorted_weights = [512, 256, 128, 64, 32, 16, 8, 4, 2, 0, 0, 0, 0, 0, 0, 0]
    sorted_board = (sorted(board, reverse=True))

    return sum(w * v for w, v in zip(sorted_weights, sorted_board))

def count_empty_spaces(board):
    space_count = 0
    for item in board:
        if item == 0:
            space_count += 1

    return space_count

def evaluate_board(board, prints=False):
    score = 0
    weights = [
        0, 0, 0, 0,
        0, 0, 0, 2,
        4, 8, 16, 32,
        512, 256, 128, 64,
    ]

    spaces = count_empty_spaces(board)

    # max_possible_snake_score = get_max_possible_snake(board)
    # snake = snake_pattern(board, weights) / max_possible_snake_score
    snake = snake_pattern(board, weights)

    highest_corner = highest_in_corner(board)

    # score += snake * 1000  # Max 1000
    # score += spaces * 1  # Max 15
    # score += 30 if highest_corner else 0
    score += snake
    score += spaces * 0.01 * snake
    score += snake * 0.1 if highest_corner else 0

    if prints:
        print(score)
        print(f"Snake: {snake}    + {snake}\nSpaces: {spaces}     + {spaces * 0.01 * snake}\nHighest Corner: {snake * 0.1 if highest_corner else 0}")

    return score

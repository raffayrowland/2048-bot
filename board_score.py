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

    def tile_rank(v):
        # Returns log2 for powers of 2. Basically gets k in 2^k
        return 0 if v == 0 else v.bit_length() - 1

    return sum(w * tile_rank(v) for w, v in zip(weights, board))


def count_empty_spaces(board):
    space_count = 0
    for item in board:
        if item == 0:
            space_count += 1

    return space_count

def second_highest_next_to_highest(board):
    highest = [0, None]
    second_highest = [0, None]
    for i in range(16):
        if board[i] > highest[0]:
            second_highest = highest
            highest = [board[i], i]

        elif board[i] > second_highest[0]:
            second_highest = [board[i], i]

    index = highest[1]
    possible_surroundings = []

    if index not in [0, 4, 8, 12]:
        possible_surroundings.append(index - 1)

    if index not in [3, 7, 11, 15]:
        possible_surroundings.append(index + 1)

    if index >= 4:
        possible_surroundings.append(index - 4)

    if index <= 11:
        possible_surroundings.append(index + 4)

    for i in possible_surroundings:
        if board[i] == second_highest[0]:
            return True

    return False

def bottom_row_full(board):
    if 0 in board[12:]:
        return False

    return True

def evaluate_board(board):
    score = 0
    weights = [
        0, 0, 0, 0,
        0, 0, 0, 1,
        3, 4, 5, 8,
        25, 19, 18, 17,
    ]

    spaces = count_empty_spaces(board)
    snake = snake_pattern(board, weights)
    highest_corner = highest_in_corner(board)
    # full_bottom_row = bottom_row_full(board)

    score += snake * 0.5
    score += spaces * 20
    score += 300 if highest_corner else 0
    # score += 2000 if full_bottom_row else 0

    return score

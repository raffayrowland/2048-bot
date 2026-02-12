from itertools import count

_ = [
#   0  1  2  3
    4, 8, 0, 0, # 0
    0, 0, 2, 0, # 4
    0, 0, 0, 0, # 8
    16, 8, 4, 2, # 12
]

def highest_in_corner(board):
    highest = max(board)

    corners = [0, 3, 12, 15]

    for corner in corners:
        if board[corner] == highest:
            return True

    return False

def highest_is_unique(board):
    highest = max(board)

    if board.count(highest) == 1:
        return True

    return False

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

    print(highest)
    print(second_highest)
    print(possible_surroundings)

    for i in possible_surroundings:
        if board[i] == second_highest[0]:
            return True

    return False

def bottom_row_full(board):
    if 0 in board[12:]:
        return False

    return True

def evaluate_board(board):
    b = board.copy()
    score = 0

    max_in_corner = highest_in_corner(b)
    full_bottom_row = bottom_row_full(b)
    spaces = count_empty_spaces(b)

    score += 10 if max_in_corner else 0
    score += 1.5 if full_bottom_row else 0
    score += spaces

    return score

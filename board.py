import random

test_board = [
    2, 0, 2, 2,
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 2, 0, 2,
]

def get_zeros_location(board):
    zeros = []
    for i in range(16):
        if board[i] == 0:
            zeros.append(i)

    return zeros

def spawn_random_tile(board, zeros):
    index = random.randint(0, len(zeros) - 1)  # choose random zero
    tile_value = random.randint(1, 10) # 90% chance value is a 2
    board[zeros[index]] = 4 if tile_value == 1 else 2
    return board


def draw_board(board):
    for i in range(len(board)):
        print(board[i], end=' ')
        if (i + 1) % 4 == 0:  # newline every 4 numbers
            print()

    print()

def move_row_left(board, row): # for top row, row=0. Second row=1 etc
    # leftmost and rightmost side of the row
    row_idx = row * 4
    row_end = row_idx + 4

    non_zero_values = [x for x in board[row_idx:row_end] if x != 0]  # Gather nonzero values
    board[row_idx:row_end] = non_zero_values + [0] * (4 - len(non_zero_values))  # put nonzero values to the left, and make up the difference with 0s

    # combine numbers that are the same
    for i in range(row_idx, row_end - 1):
        if board[i] == board[i + 1]:
            board[i] = board[i] * 2
            board[i + 1:row_end] = board[i + 2: row_end] + [0]  # shift the right side of the row left

    return board

def move_row_right(board, row):
    # leftmost and rightmost side of the row
    row_idx = row * 4
    row_end = row_idx + 4

    non_zero_values = [x for x in board[row_idx:row_end] if x != 0]  # Gather nonzero values
    board[row_idx:row_end] = [0] * (4 - len(non_zero_values)) + non_zero_values  # pad with 0s and put nonzeros to the right

    # combine numbers that are the same
    for i in range(row_end - 1, row_idx, -1):
        if board[i] == board[i - 1]:
            board[i] = board[i] * 2
            board[row_idx:i] = [0] + board[row_idx:i - 1]  # shift left side of the row right

    return board

draw_board(test_board)
draw_board(move_row_right(test_board, 0))
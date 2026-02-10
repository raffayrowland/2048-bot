import random

board = [
    0, 2, 0, 2,
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
    index = random.randint(0, len(zeros) - 1)
    tile_value = random.randint(1, 10)
    board[zeros[index]] = 4 if tile_value == 1 else 2
    return board


def draw_board(board):
    for i in range(16):
        print(board[i], end=' ')
        if (i + 1) % 4 == 0:
            print()

    print()

def move_row_left(board, row): # for top row, row=0. Second row=1 etc
    row_idx = row * 4
    row_end = row_idx + 4

    for i in range(row_end - 1, row_idx - 1, -1):
        if board[i] == 0:
            board[i:row_end] = board[i + 1:row_end] + [0]

    for i in range(row_idx, row_end - 1):
        if board[i] == board[i + 1]:
            board[i] = board[i] * 2
            board[i + 1:row_end] = board[i + 2: row_end] + [0]

    return board

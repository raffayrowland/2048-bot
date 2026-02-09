import random

board = [
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0,
]

def spawn_random_tile(board):
    zeros = []

    for i in range(16):
        if board[i] == 0:
            zeros.append(i)

    index = random.randint(0, len(zeros) - 1)
    return zeros[index]

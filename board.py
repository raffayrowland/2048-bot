import random

left_or_up_cache = {}
right_or_down_cache = {}

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

def draw_board(board, score=0):
    print(f"Score: {score}")
    for i in range(len(board)):
        print(board[i], " " * (5 - len(str(board[i]))), end=' ')
        if (i + 1) % 4 == 0:  # newline every 4 numbers
            print()

    print()

def move_row_left_or_up(row):
    row_key = tuple(row)
    if row_key in left_or_up_cache:
        return left_or_up_cache[row_key]

    non_zeros = [x for x in row if x != 0]
    new_row = []
    score = 0

    while len(non_zeros) > 0:
        if len(non_zeros) > 1 and non_zeros[0] == non_zeros[1]:
            new_row = new_row + [non_zeros[0] * 2]
            score += non_zeros[0]
            non_zeros = non_zeros[2:]

        else:
            new_row = new_row + [non_zeros[0]]
            non_zeros = non_zeros[1:]

    new_row = new_row + [0] * (4 - len(new_row))

    left_or_up_cache[row_key] = (new_row, score)
    return new_row, score

def move_row_right_or_down(row):
    row_key = tuple(row)
    if row_key in right_or_down_cache:
        return right_or_down_cache[row_key]

    non_zeros = [x for x in row if x != 0]
    new_row = []
    score = 0

    i = len(non_zeros) - 1
    while len(non_zeros) > 0:
        if i != 0 and non_zeros[i] == non_zeros[i - 1]:
            new_row = [non_zeros[i] * 2] + new_row
            score += non_zeros[i]
            non_zeros = non_zeros[:-2]
            i -= 2

        else:
            new_row = [non_zeros[i]] + new_row
            non_zeros = non_zeros[:-1]
            i -= 1

    new_row = [0] * (4 - len(new_row)) + new_row

    right_or_down_cache[row_key] = (new_row, score)
    return new_row, score

def up(board):
    total_score = 0
    new_board = [0] * 16

    for i in range(4):
        row = [board[x] for x in range(i, i + 16, 4)]
        new_row, score = move_row_left_or_up(row)
        total_score += score
        for j in range(i, i + 16, 4):
            new_board[j] = new_row[j // 4]

    changed = (board != new_board)
    return changed, new_board, total_score

def down(board):
    total_score = 0
    new_board = [0] * 16

    for i in range(4):
        row = [board[x] for x in range(i, i + 16, 4)]
        new_row, score = move_row_right_or_down(row)
        total_score += score
        for j in range(i, i + 16, 4):
            new_board[j] = new_row[j // 4]

    changed = (board != new_board)
    return changed, new_board, total_score

def left(board):
    total_score = 0
    new_board = []
    for i in range(4):
        row = board[i * 4:i * 4 + 4]
        new_row, score = move_row_left_or_up(row)
        new_board += new_row
        total_score += score

    changed = (board != new_board)
    return changed, new_board, total_score

def right(board):
    total_score = 0
    new_board = []
    for i in range(4):
        row = board[i * 4:i * 4 + 4]
        new_row, score = move_row_right_or_down(row)
        new_board += new_row
        total_score += score

    changed = (board != new_board)
    return changed, new_board, total_score

def do_move_if_legal(board, move, spawn=False):
    changed, b, gained = move(board)

    if changed:
        if spawn:
            spawn_random_tile(b, get_zeros_location(b))
        return True, b, gained

    return False, board, 0

def is_game_over(board):
    if 0 in board:
        return False
    for move in (up, down, left, right):
        changed, _, _ = do_move_if_legal(board, move)
        if changed:
            return False

    return True


def start_game():
    board = [
        0, 0, 0, 0,
        0, 0, 0, 0,
        0, 0, 0, 0,
        0, 0, 0, 0,
    ]

    for _ in range(2):
        spawn_random_tile(board, get_zeros_location(board))

    return board

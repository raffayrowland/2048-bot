import random

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

def move_row_left(board, row): # for top row, row=0. Second row=1 etc
    # leftmost and rightmost side of the row
    row_idx = row * 4
    row_end = row_idx + 4
    score = 0

    non_zero_values = [x for x in board[row_idx:row_end] if x != 0]  # Gather nonzero values
    board[row_idx:row_end] = non_zero_values + [0] * (4 - len(non_zero_values))  # put nonzero values to the left, and make up the difference with 0s

    # combine numbers that are the same
    for i in range(row_idx, row_end - 1):
        if board[i] == board[i + 1] and board[i] != 0:
            board[i] = board[i] * 2
            score += board[i]
            board[i + 1:row_end] = board[i + 2: row_end] + [0]  # shift the right side of the row left

    return board, score

def move_row_right(board, row):
    # leftmost and rightmost side of the row
    row_idx = row * 4
    row_end = row_idx + 4
    score = 0

    non_zero_values = [x for x in board[row_idx:row_end] if x != 0]  # Gather nonzero values
    board[row_idx:row_end] = [0] * (4 - len(non_zero_values)) + non_zero_values  # pad with 0s and put nonzeros to the right

    # combine numbers that are the same
    for i in range(row_end - 1, row_idx, -1):
        if board[i] == board[i - 1] and board[i] != 0:
            board[i] = board[i] * 2
            score += board[i]
            board[row_idx:i] = [0] + board[row_idx:i - 1]  # shift left side of the row right

    return board, score

def move_column_up(board, column):  # Left column=0, middle left = 1 etc.
    score = 0
    non_zero_values = [board[x] for x in range(column, column + 13, 4) if board[x] != 0]  # Gather nonzero values

    # Shift the nonzero values to the top.
    for i in range(column, column + 13, 4):
        if non_zero_values:
            board[i] = non_zero_values[0]
            non_zero_values = non_zero_values[1:]

        else:
            board[i] = 0  # When we run out of non zeros, populate the rest with 0s

    # Merge tiles that are the same and adjacent
    for i in range(column, column + 9, 4):
        if board[i] == board[i + 4] and board[i] != 0:
            board[i] = board[i] * 2  # Double the tile that has been merged
            score += board[i]
            for j in range(i + 4, column + 9, 4):  # Shift the rest up
                board[j] = board[j + 4]
            board[column + 12] = 0

    return board, score

def move_column_down(board, column):
    score = 0
    non_zero_values = [board[x] for x in range(column + 12, column - 1, -4) if board[x] != 0]  # Gather nonzero values

    # Shift the nonzero values to the bottom
    for i in range(column + 12, column - 1, -4):
        if non_zero_values:
            board[i] = non_zero_values[0]  # Pop the next nonzero
            non_zero_values = non_zero_values[1:]

        else:
            board[i] = 0

    # Merge tiles that are the same and adjacent
    for i in range(column + 12, column, -4):
        if board[i] == board[i - 4] and board[i] != 0:  # If the tiles are the same, merge them
            board[i] = board[i] * 2
            score += board[i]
            for j in range(i - 4, column, -4):  # Shift the rest of them down
                board[j] = board[j - 4]
            board[column] = 0

    return board, score

def up(board):
    total_score = 0
    for i in range(4):
        board, score = move_column_up(board, i)
        total_score += score

    return board, total_score

def down(board):
    total_score = 0
    for i in range(4):
        board, score = move_column_down(board, i)
        total_score += score

    return board, total_score

def left(board):
    total_score = 0
    for i in range(4):
        board, score = move_row_left(board, i)
        total_score += score

    return board, total_score

def right(board):
    total_score = 0
    for i in range(4):
        board, score = move_row_right(board, i)
        total_score += score

    return board, total_score

def do_move_if_legal(board, move, spawn=False):
    b = board.copy()

    b, gained = move(b)
    changed = b != board

    if changed:
        if spawn:
            spawn_random_tile(b, get_zeros_location(b))
        return True, b, gained

    return False, board, 0

def is_game_over(board):
    if 0 in board:
        return False
    for move in (up, down, left, right):
        starting_board = board.copy()
        move(starting_board)
        if starting_board != board:
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

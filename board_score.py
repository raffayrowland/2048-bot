WEIGHTS = [
    0, 0, 0, 0,
    0, 0, 0, 2,
    4, 8, 16, 32,
    512, 256, 128, 64,
]

def evaluate_board(board, prints=False):
    total_score = 0
    snake_score = 0
    space_count = 0
    max_tile = 0

    for i in range(16):
        snake_score += WEIGHTS[i] * board[i]

        if max_tile < board[i]:
            max_tile = board[i]

        if board[i] == 0:
            space_count += 1

    max_corner = True if board[12] == max_tile else False

    total_score += snake_score
    total_score += space_count * 0.01 * snake_score
    total_score += snake_score * 0.1 if max_corner else 0


    if prints:
        print(total_score)
        print(f"Snake: {snake_score}    + {snake_score}\nSpaces: {space_count}     + {space_count * 0.01 * snake_score}\nHighest Corner: {snake_score * 0.1 if max_corner else 0}")

    return total_score

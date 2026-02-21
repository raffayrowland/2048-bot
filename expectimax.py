from board import *
from board_score import evaluate_board
from visuals import start_game_record, record_game_step, finish_game_record, replay_recording
from collections import OrderedDict

test_board = [
    0, 0, 2, 0,
    0, 0, 2, 0,
    0, 0, 0, 0,
    0, 4, 0, 0,
]

MOVES = [(0, left), (1, right), (2, down), (3, up)]

MAX_CACHE_SIZE = 1_000_000
move_cache = OrderedDict()
spawn_cache = OrderedDict()

def clear_cache():
    global move_cache
    global spawn_cache

    caches = [move_cache, spawn_cache, left_cache, right_cache, up_cache, down_cache]

    print(
        f"""Best cache size: {len(move_cache)}, 
Worst cache size: {len(spawn_cache)}
Left cache size: {len(left_cache)}
Right cache size: {len(right_cache)}
Up cache size: {len(up_cache)}
Down cache size: {len(down_cache)}"""
          )

    for cache in caches:
        overflow = len(cache) - MAX_CACHE_SIZE
        for _ in range(max(0, overflow)):
            cache.popitem(last=False)


def generate_all_spawns(board):
    possible_spawns = []
    zeros = get_zeros_location(board)

    p2 = (1 / len(zeros)) * 0.9
    p4 = (1 / len(zeros)) * 0.1

    for zero in zeros:
        b2 = board.copy()
        b4 = board.copy()
        b2[zero] = 2
        b4[zero] = 4
        possible_spawns.append((b2, p2))
        possible_spawns.append((b4, p4))

    return possible_spawns

def generate_boards_after_possible_moves(board):
    new_boards = []

    for move in MOVES:
        changed, new_board, _ = do_move_if_legal(board, move[1], spawn=False)
        if changed:
            new_boards.append((move[0], new_board))

    return new_boards

def get_weighted_spawns(board, depth):
    board_key = (tuple(board), depth)
    if board_key in spawn_cache:
        return spawn_cache[board_key]

    possible_spawns = generate_all_spawns(board)

    if not possible_spawns:
        eval = evaluate_board(board)
        spawn_cache[board_key] = eval
        return eval

    if depth == 0:
        cumulative_score = 0

        for position, p in possible_spawns:
            cumulative_score += p * evaluate_board(position)

        spawn_cache[board_key] = cumulative_score
        return cumulative_score

    cumulative_score = 0
    for position, p in possible_spawns:
        _, next_value = get_best_move(position, depth - 1)
        cumulative_score += p * next_value

    spawn_cache[board_key] = cumulative_score
    return cumulative_score

def get_best_move(board, depth):
    board_key = (tuple(board), depth)
    if board_key in move_cache:
        return move_cache[board_key]

    boards_after_moves = generate_boards_after_possible_moves(board)  # (move_idx, new_board)

    if not boards_after_moves:
        best = (None, -1000)
        move_cache[board_key] = best
        return best

    if depth == 0:
        best = None

        for move_idx, position in boards_after_moves:
            current_eval = evaluate_board(position)
            if best is None or current_eval > best[1]:
                best = (move_idx, current_eval)

        move_cache[board_key] = best
        return best

    best = None

    for move_idx, position in boards_after_moves:
        eval = get_weighted_spawns(position, depth)
        if best is None or eval > best[1]:
            best = (move_idx, eval)

    move_cache[board_key] = best
    return best


if __name__ == '__main__':
    play_board = start_game()
    draw_board(play_board)
    total_score = 0
    rec = start_game_record("replays/latest_game.json", play_board, total_score)

    while not is_game_over(play_board):
        best_move = get_best_move(play_board, 4)[0]
        if best_move is None:
            break

        _, play_board, score = do_move_if_legal(play_board, MOVES[best_move][1], spawn=True)
        total_score += score

        record_game_step(rec, best_move, play_board, total_score)

        draw_board(play_board, total_score)
        evaluate_board(play_board, prints=True)
        print("-----------------------------")
        clear_cache()

    finish_game_record(rec)
    replay_recording("replays/latest_game.json")

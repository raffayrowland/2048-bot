from board import *
from board_score import evaluate_board, default_params
from visuals import start_game_record, record_game_step, finish_game_record, replay_recording
from functools import lru_cache

MOVES = [(0, left), (1, right), (2, down), (3, up)]

MAX_CACHE_SIZE = 100_000
EVALUATION_CACHE_SIZE = 8_192

def clear_cache(prints=False):
    if prints:
        print(
            f"Move cache size: {get_best_move.cache_info().currsize}\n"
            f"Spawn cache size: {get_weighted_spawns.cache_info().currsize}\n"
            f"Evaluation cache size: {evaluate_position.cache_info().currsize}\n"
            f"Left cache size: {len(left_or_up_cache)}\n"
            f"Right cache size: {len(right_or_down_cache)}"
        )

    # Search caches evict on insertion; row caches are ordinary insertion-ordered dicts.
    for cache in (left_or_up_cache, right_or_down_cache):
        overflow = len(cache) - MAX_CACHE_SIZE
        if overflow > 0:
            for key in list(cache)[:overflow]:
                del cache[key]

@lru_cache(maxsize=EVALUATION_CACHE_SIZE)
def evaluate_position(board, params):
    return evaluate_board(board, params)


def generate_all_spawns(board):
    possible_spawns = []
    zeros = get_zeros_location(board)
    if not zeros:
        return possible_spawns

    p2 = (1 / len(zeros)) * 0.9
    p4 = (1 / len(zeros)) * 0.1

    for zero in zeros:
        b2 = board.copy()
        b4 = board.copy()
        b2[zero] = 1
        b4[zero] = 2
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


@lru_cache(maxsize=MAX_CACHE_SIZE)
def get_weighted_spawns(board, depth, params):
    possible_spawns = generate_all_spawns(list(board))

    if not possible_spawns:
        return evaluate_position(board, params)

    if depth == 0:
        cumulative_score = 0

        for position, p in possible_spawns:
            cumulative_score += p * evaluate_position(tuple(position), params)

        return cumulative_score

    cumulative_score = 0
    for position, p in possible_spawns:
        _, next_value = get_best_move(tuple(position), depth - 1, params)
        cumulative_score += p * next_value

    return cumulative_score


@lru_cache(maxsize=MAX_CACHE_SIZE)
def get_best_move(board, depth, params):
    boards_after_moves = generate_boards_after_possible_moves(list(board))

    if not boards_after_moves:
        return None, -1e18

    if depth == 0:
        best = None

        for move_idx, position in boards_after_moves:
            current_eval = evaluate_position(tuple(position), params)
            if best is None or current_eval > best[1]:
                best = (move_idx, current_eval)

        return best

    best = None

    for move_idx, position in boards_after_moves:
        eval = get_weighted_spawns(tuple(position), depth, params)
        if best is None or eval > best[1]:
            best = (move_idx, eval)

    return best

def start_one_player(params, depth=2, replay_path=None):
    play_board = start_game()
    total_score = 0
    rec = None

    if replay_path is not None:
        rec = start_game_record(replay_path, play_board, total_score)

    while not is_game_over(play_board):
        best_move = get_best_move(tuple(play_board), depth, params)[0]
        if best_move is None:
            break

        _, play_board, score = do_move_if_legal(play_board, MOVES[best_move][1], spawn=True)
        total_score += score
        if rec is not None:
            record_game_step(rec, best_move, play_board, total_score)

        clear_cache()

    if rec is not None:
        finish_game_record(rec)

    return total_score


if __name__ == '__main__':
    play_board = start_game()
    draw_board(play_board)
    total_score = 0
    rec = start_game_record("replays/latest_game.json", play_board, total_score)

    while not is_game_over(play_board):
        best_move = get_best_move(tuple(play_board), 2, default_params)[0]
        if best_move is None:
            break

        _, play_board, score = do_move_if_legal(play_board, MOVES[best_move][1], spawn=True)
        total_score += score

        record_game_step(rec, best_move, play_board, total_score)

        draw_board(play_board, total_score)
        evaluate_board(play_board, prints=True)
        print("\n-----------------------------\n")
        clear_cache(prints=True)

    finish_game_record(rec)
    replay_recording("replays/latest_game.json")

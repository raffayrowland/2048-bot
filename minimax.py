from board import draw_board, start_game, is_game_over, get_zeros_location, do_move_if_legal, left, right, up, down
from board_score import evaluate_board
from visuals import start_game_record, record_game_step, finish_game_record, replay_recording
from collections import OrderedDict

MOVES = [(0, left), (1, right), (2, down), (3, up)]

MAX_CACHE_SIZE = 1_000_000
best_cache = OrderedDict()
worst_cache = OrderedDict()

def clear_cache():
    global best_cache
    global worst_cache
    print(f"Best cache size: {len(best_cache)}, Worst cache size: {len(worst_cache)}")

    overflow = len(best_cache) - MAX_CACHE_SIZE
    for _ in range(max(0, overflow)):
        best_cache.popitem(last=False)

    overflow = len(worst_cache) - MAX_CACHE_SIZE
    for _ in range(max(0, overflow)):
        worst_cache.popitem(last=False)

def generate_all_spawns(state):
    # State is (move_idx, board)
    possible_spawns = []
    zeros = get_zeros_location(state[1])

    for zero in zeros:
        b2 = state[1].copy()
        b4 = state[1].copy()
        b2[zero] = 2
        b4[zero] = 4
        possible_spawns.append((state[0], b2))
        possible_spawns.append((state[0], b4))

    return possible_spawns

def get_boards_after_possible_moves(board):
    new_boards = []  # [(move_idx, board), ...]

    for move in MOVES:
        changed, new_board, _ = do_move_if_legal(board.copy(), move[1], spawn=False)
        if changed:
            new_boards.append((move[0], new_board))

    return new_boards

def get_best_player_move(state, depth):
    # State is tuple like (root_move_idx, board)
    board_key = (tuple(state[1]), depth)
    if board_key in best_cache:
        return best_cache[board_key]

    if depth == 0:
        out = (None, evaluate_board(state[1]))
        best_cache[board_key] = out
        return out

    post_move_boards = get_boards_after_possible_moves(state[1])

    if not post_move_boards:
        best_cache[board_key] = (None, -1000)
        return None, -1000

    worst_case_spawn_scores = {
        0: None,
        1: None,
        2: None,
        3: None
    }

    for move_idx, board in post_move_boards:
        worst_case = get_worst_spawn((move_idx, board), depth)
        worst_case_spawn_scores[move_idx] = worst_case[2]

    possible_moves = [(k, v) for k, v in worst_case_spawn_scores.items() if v is not None]
    out = max(possible_moves, key=lambda x: x[1]) if possible_moves else None
    best_cache[board_key] = out
    return out


def get_worst_spawn(state, depth):
    # State is tuple like (root_move_idx, board)
    board_key = (tuple(state[1]), depth)
    if board_key in worst_cache:
        cached = worst_cache[board_key]
        return state[0], cached[1], cached[2]

    post_spawn_boards = generate_all_spawns(state)

    if not post_spawn_boards:
        if depth == 0:
            out = state[0], state[1], evaluate_board(state[1])
            worst_cache[board_key] = out
            return out
        best_move = get_best_player_move(state, depth - 1)
        out = state[0], state[1], best_move[1]
        worst_cache[board_key] = out
        return out

    if depth == 0:
        worst_case = None  # Tuple like (move_idx, board, board_score)

        for move_idx, board in post_spawn_boards:
            board_score = evaluate_board(board)
            if worst_case is None:
                worst_case = (move_idx, board, board_score)

            elif board_score < worst_case[2]:
                worst_case = (move_idx, board, board_score)

        out = worst_case
        worst_cache[board_key] = out
        return out

    worst_spawn = None
    for move_idx, board in post_spawn_boards:
        best_move_for_this_spawn = get_best_player_move((move_idx, board), depth - 1)
        score = best_move_for_this_spawn[1]
        if worst_spawn is None:
            worst_spawn = (move_idx, board, score)

        elif score < worst_spawn[2]:
            worst_spawn = (move_idx, board, score)

    out = worst_spawn
    worst_cache[board_key] = out
    return out


if __name__ == "__main__":
    play_board = start_game()
    draw_board(play_board)
    total_score = 0
    rec = start_game_record("replays/latest_game.json", play_board, total_score)

    while not is_game_over(play_board):
        best_move = get_best_player_move((None, play_board), 4)
        if best_move[0] is None:
            break
        print(best_move)
        _, play_board, score = do_move_if_legal(play_board, MOVES[best_move[0]][1], spawn=True)
        total_score += score

        record_game_step(rec, best_move[0], play_board, total_score)

        draw_board(play_board, total_score)
        evaluate_board(play_board, prints=True)
        print()
        clear_cache()

    finish_game_record(rec)
    replay_recording("replays/latest_game.json")
from pathlib import Path
from expectimax import start_one_player
from board_score import default_params
from concurrent.futures import ProcessPoolExecutor
from visuals import replay_recording

RUNS = 1000
MAX_WORKERS = 16
DEPTH = 3
REPLAY_DIR = Path("replays")


def run_one_with_replay(run_idx: int):
    replay_path = REPLAY_DIR / f"run_{run_idx}.json"
    score = start_one_player(default_params, DEPTH, replay_path=str(replay_path))
    print(score)
    return score, str(replay_path)


if __name__ == "__main__":
    REPLAY_DIR.mkdir(parents=True, exist_ok=True)

    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(run_one_with_replay, i) for i in range(RUNS)]
        results = [future.result() for future in futures]

    best_score, best_replay_path = max(results, key=lambda item: item[0])
    print(f"Best score: {best_score}, Path: {best_replay_path}")
    replay_recording(best_replay_path)

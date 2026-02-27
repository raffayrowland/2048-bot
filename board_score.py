from dataclasses import dataclass
from typing import Tuple

DEFAULT_WEIGHTS = [
    923.3489108762112,
    369.9723326920124,
    509.63565361370956,
    187.41351997836804,
    774.3004822322991,
    409.74197276751255,
    249.7571272050992,
    448.3835916795614,
    711.358567227876,
    212.05068823645746,
    680.160777814878,
    432.0734322906679,
    670.6365582728158,
    452.0054352438986,
    128.87927579615751,
    423.80351527914377
  ]

@dataclass(frozen=True)
class EvalParams:
    max_corner_reward: float = 0.2680921366073329
    space_count_reward: float = 0.8681930859481921
    weights: Tuple[float, ...] = tuple(DEFAULT_WEIGHTS)

    def __post_init__(self):
        object.__setattr__(self, "weights", tuple(self.weights))

default_params = EvalParams()


def evaluate_board(board, params=default_params, prints=False):
    total_score = 0
    snake_score = 0
    space_count = 0
    max_tile = 0

    for i in range(16):
        snake_score += params.weights[i] * (board[i])

        if max_tile < board[i]:
            max_tile = board[i]

        if board[i] == 0:
            space_count += 1

    max_corner = True if board[12] == max_tile else False

    total_score += snake_score
    total_score += space_count * params.space_count_reward * snake_score
    total_score += snake_score * params.max_corner_reward if max_corner else 0


    if prints:
        print(total_score)
        print(
            f"Snake: {snake_score}    + {snake_score}\n"
            f"Spaces: {space_count}     + {space_count * params.space_count_reward * snake_score}\n"
            f"Highest Corner: {snake_score * params.max_corner_reward if max_corner else 0}"
        )

    return total_score

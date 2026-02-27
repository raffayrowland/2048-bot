from dataclasses import dataclass
from typing import Tuple

DEFAULT_WEIGHTS = [
    874, 486, 883, 66,
    305, 269, 401, 221,
    190, 286, 631, 337,
    470, 215, 173, 468,
]

@dataclass(frozen=True)
class EvalParams:
    max_corner_reward: float = 0.45
    space_count_reward: float = 0.59
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

import math
from dataclasses import dataclass
from typing import Tuple
import json

MY_WEIGHTS = [
    0, 0, 0, 0,
    0, 0, 0, 2,
    4, 8, 16, 32,
    512, 256, 128, 64,
]

trained_params = json.load(open("params/best_ga_params.json"))
TRAINED_DISTANCE_PENALTY = trained_params["distance_penalty"]
TRAINED_SPACE_COUNT = trained_params["space_count_reward"]
TRAINED_WEIGHTS = trained_params["weights"]

@dataclass(frozen=True)
class EvalParams:
    distance_penalty: float = TRAINED_DISTANCE_PENALTY
    space_count_reward: float = TRAINED_SPACE_COUNT
    weights: Tuple[float, ...] = tuple(TRAINED_WEIGHTS)

    def __post_init__(self):
        object.__setattr__(self, "weights", tuple(self.weights))

default_params = EvalParams()

# Precompute Euclidean distances between all board indices once.
_INDEX_COORDS = [(i % 4, i // 4) for i in range(16)]
_DIST_BY_INDEX = tuple(
    tuple(
        math.sqrt(
            (_INDEX_COORDS[i][0] - _INDEX_COORDS[j][0]) ** 2
            + (_INDEX_COORDS[i][1] - _INDEX_COORDS[j][1]) ** 2
        )
        for j in range(16)
    )
    for i in range(16)
)


def evaluate_board(board, params=default_params, prints=False):
    snake_score = 0.0
    distance_penalty = 0.0
    space_count = 0

    prev_index_by_value = {}
    weights = params.weights

    for i, value in enumerate(board):
        snake_score += weights[i] * value
        if value == 0:
            space_count += 1
            continue

        previous_index = prev_index_by_value.get(value)
        if previous_index is not None:
            distance_penalty += value * _DIST_BY_INDEX[previous_index][i]
        prev_index_by_value[value] = i

    total_score = snake_score
    total_score += space_count * params.space_count_reward * snake_score
    total_score -= distance_penalty * params.distance_penalty

    if prints:
        print(total_score)
        print(
            f"Snake: {snake_score}    + {snake_score}\n"
            f"Spaces: {space_count}     + {space_count * params.space_count_reward * snake_score}\n"
            f"Distance Penalty: {distance_penalty * params.distance_penalty}\n"
        )

    return total_score

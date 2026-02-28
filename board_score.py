import math
from dataclasses import dataclass
from typing import Tuple

DEFAULT_WEIGHTS = [
    0, 0, 0, 0,
    0, 0, 0, 2,
    4, 8, 16, 32,
    512, 256, 128, 64,
]

@dataclass(frozen=True)
class EvalParams:
    distance_penalty: float = 5
    space_count_reward: float = 0.01
    weights: Tuple[float, ...] = tuple(DEFAULT_WEIGHTS)

    def __post_init__(self):
        object.__setattr__(self, "weights", tuple(self.weights))

default_params = EvalParams()


def evaluate_board(board, params=default_params, prints=False):
    total_score = 0
    snake_score = 0
    distance_penalty = 0
    space_count = 0

    value_coords = {}

    for i in range(16):
        if board[i] not in value_coords:
            value_coords[board[i]] = []

        value_coords[board[i]].append(i)

        snake_score += params.weights[i] * (board[i])

        if board[i] == 0:
            space_count += 1

    for k, v in value_coords.items():
        pairs = []
        for coordinate in v:
            x = coordinate % 4
            y = coordinate // 4
            pairs.append((x, y))

        for pair in range(len(pairs) - 1):
            distance = math.sqrt(abs(pairs[0][0] - pairs[1][0]) ** 2 + abs(pairs[0][1] - pairs[1][1]) ** 2)
            distance_penalty += k * distance


    total_score += snake_score
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

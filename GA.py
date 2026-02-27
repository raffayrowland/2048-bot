from board_score import EvalParams
from expectimax import start_one_player, clear_cache

def chromosome_to_params(chromosome):
    params = EvalParams(
        max_corner_reward=chromosome[0],
        space_count_reward=chromosome[1],
        weights=tuple(chromosome[2:18]),
    )

    return params

def fitness(chromosome, episodes=3, depth=2):
    params = chromosome_to_params(chromosome)
    total = 0
    for _ in range(episodes):
        clear_cache()
        total += start_one_player(params, depth=depth)

    return total / episodes
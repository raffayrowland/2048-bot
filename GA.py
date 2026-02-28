from board_score import EvalParams
from expectimax import start_one_player
import json
import random
import os
from concurrent.futures import ProcessPoolExecutor
from typing import Tuple, List

# [max_corner_reward, space_count_reward, w0 ... w15]
GENE_BOUNDS: List[Tuple[float, float]] = [
    (0.0, 0.5),  # Max corner reward bound
    (0.0, 2.0),  # Max space reward bound
] + [(-32.0, 1024.0)] * 16  # Weight bounds

POPULATION_SIZE = 25
GENERATIONS = 10
EPISODES_PER_FITNESS = 10
SEARCH_DEPTH = 2
ELITE_COUNT = 4
TOURNAMENT_K = 3
MUTATION_RATE = 0.15
MUTATION_STD_FRAC = 0.08
MAX_PARALLEL_PLAYERS = 20

def clamp(x, lo, hi):
    return max(lo, min(x, hi))

def random_chromosome():
    return [random.uniform(lo, hi) for lo, hi in GENE_BOUNDS]

def chromosome_to_params(chromosome):
    params = EvalParams(
        max_corner_reward=chromosome[0],
        space_count_reward=chromosome[1],
        weights=tuple(chromosome[2:18]),
    )

    return params

def run_seeded_episode(seed, params, depth):
    random.seed(seed)
    return start_one_player(params, depth=depth)

def fitness(chromosome, seeds, episodes=3, depth=2):
    params = chromosome_to_params(chromosome)
    episode_seeds = seeds[:episodes]
    if not episode_seeds:
        return 0.0

    scores = [run_seeded_episode(seed, params, depth) for seed in episode_seeds]
    return sum(scores) / len(episode_seeds)

def tournament_select(scored_pop, k=TOURNAMENT_K):
    contenders = random.sample(scored_pop, k)
    contenders.sort(key = lambda x: x[1], reverse = True)
    return contenders[0][0]

def crossover(a, b):
    child = []

    for i, (ga, gb) in enumerate(zip(a, b)):
        alpha = random.random()
        lo, hi = GENE_BOUNDS[i]
        child.append(clamp(alpha * ga + (1 - alpha) * gb, lo, hi))

    return child

def mutate(chromosome):
    out = chromosome[:]
    for i, (lo, hi) in enumerate(GENE_BOUNDS):
        if random.random() < MUTATION_RATE:
            sigma = (hi - lo) * MUTATION_STD_FRAC
            out[i] = clamp(out[i] + random.gauss(0, sigma), lo, hi)

    return out

def evolve():
    population = [random_chromosome() for _ in range(POPULATION_SIZE)]
    goat = None
    goat_score = float("-inf")

    with ProcessPoolExecutor(max_workers=MAX_PARALLEL_PLAYERS) as executor:
        for gen in range(GENERATIONS):
            seeds = [10000 * gen + i for i in range(max(EPISODES_PER_FITNESS, 8))]
            futures = [
                executor.submit(fitness, chromosome, seeds, EPISODES_PER_FITNESS, SEARCH_DEPTH)
                for chromosome in population
            ]
            scores = [future.result() for future in futures]
            scored = list(zip(population, scores))
            scored.sort(key = lambda x: x[1], reverse = True)

            gen_best, gen_best_score = scored[0]
            if gen_best_score > goat_score:
                goat_score = gen_best_score
                goat = gen_best[:]

            print(f"Gen {gen:03d} | best={gen_best_score:.2f} | global_best={goat_score:.2f}")

            # Elitism
            next_population = [chrom[:] for chrom, _ in scored[:ELITE_COUNT]]

            # Fill rest
            while len(next_population) < POPULATION_SIZE:
                p1 = tournament_select(scored)
                p2 = tournament_select(scored)
                child = crossover(p1, p2)
                child = mutate(child)
                next_population.append(child)

            population = next_population

    best_params = chromosome_to_params(goat)
    print("\nBest chromosome:", goat)
    print("Best params:", best_params)
    print("Best fitness:", goat_score)

    os.makedirs("params", exist_ok=True)
    with open("params/best_ga_params.json", "w") as f:
        json.dump(
            {
                "fitness": goat_score,
                "max_corner_reward": best_params.max_corner_reward,
                "space_count_reward": best_params.space_count_reward,
                "weights": list(best_params.weights),
            },
            f,
            indent=2,
        )


if __name__ == "__main__":
    random.seed(42)
    evolve()

import time
from board_score import EvalParams
from expectimax import start_one_player
import json
import random
import os
from concurrent.futures import ProcessPoolExecutor
from typing import Tuple, List

os.makedirs("params", exist_ok=True)
PARAMS_FILE_NAME = f"params/params{int(time.time())}.json"
RESUME_PREVIOUS_TRAINING = True

# [distance_penalty, space_count_reward, w0 ... w15]
GENE_BOUNDS: List[Tuple[float, float]] = [
    (0.0, 100.0),  # Distance penalty bound
    (0.0, 1.0),  # Max space reward bound
] + [(-256.0, 1024.0)] * 16  # Weight bounds

if RESUME_PREVIOUS_TRAINING:
    with open("params/best_ga_params.json", "r") as f:
        params = json.load(f)
        POPULATION_SIZE = params["training_params"]["population_size"]
        GENERATIONS = params["training_params"]["generations"]
        EPISODES_PER_FITNESS = params["training_params"]["episodes_per_fitness"]
        SEARCH_DEPTH = params["training_params"]["search_depth"]
        ELITE_COUNT = params["training_params"]["elite_count"]
        TOURNAMENT_K = params["training_params"]["tournament_k"]
        MUTATION_RATE = params["training_params"]["mutation_rate"]
        MUTATION_STD_FRAC = params["training_params"]["mutation_std_frac"]
        MAX_PARALLEL_PLAYERS = params["training_params"]["max_parallel_players"]

        prev_population = params["evaluation_params"]["population"]
        prev_eval = params["evaluation_params"]
        prev_goat = params["evaluation_params"]["goat"]
        prev_goat_score = params["evaluation_params"]["fitness"]

elif not RESUME_PREVIOUS_TRAINING:
    POPULATION_SIZE = 150
    GENERATIONS = 15
    EPISODES_PER_FITNESS = 15
    SEARCH_DEPTH = 1
    ELITE_COUNT = 4
    TOURNAMENT_K = 9
    MUTATION_RATE = 0.25
    MUTATION_STD_FRAC = 0.08
    MAX_PARALLEL_PLAYERS = 20

gen_log = {
    "params": {
        "population_size": POPULATION_SIZE,
        "generations": GENERATIONS,
        "episodes_per_fitness": EPISODES_PER_FITNESS,
        "search_depth": SEARCH_DEPTH,
        "elite_count": ELITE_COUNT,
        "tournament_k": TOURNAMENT_K,
        "mutation_rate": MUTATION_RATE,
        "mutation_std_frac": MUTATION_STD_FRAC,
        "max_parallel_players": MAX_PARALLEL_PLAYERS
    },

    "generations": [

    ]
}

def clamp(x, lo, hi):
    return max(lo, min(x, hi))

def random_chromosome():
    return [random.uniform(lo, hi) for lo, hi in GENE_BOUNDS]

def chromosome_to_params(chromosome):
    params = EvalParams(
        distance_penalty=chromosome[0],
        space_count_reward=chromosome[1],
        weights=tuple(chromosome[2:18]),
    )

    return params

def run_seeded_episode(seed, params, depth):
    random.seed(seed)
    return start_one_player(params, depth=depth)

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
    if RESUME_PREVIOUS_TRAINING:
        population = prev_population
        goat = prev_goat
        goat_score = prev_goat_score

    else:
        population = [random_chromosome() for _ in range(POPULATION_SIZE)]
        goat = None
        goat_score = float("-inf")

    with ProcessPoolExecutor(max_workers=MAX_PARALLEL_PLAYERS) as executor:
        for gen in range(GENERATIONS):
            seeds = [10000 * gen + i for i in range(max(EPISODES_PER_FITNESS, 8))]

            t0 = time.perf_counter()

            futures = []
            params = [chromosome_to_params(chromosome) for chromosome in population]

            for seed in seeds[:EPISODES_PER_FITNESS]:
                for i in range(len(population)):
                    futures.append((executor.submit(run_seeded_episode, seed, params[i], SEARCH_DEPTH), i ))

            scores = [(future.result(), player_idx) for future, player_idx in futures]

            grouped_scores = [0] * len(population)

            for score, player_idx in scores:
                grouped_scores[player_idx] += score

            for i in range(len(grouped_scores)):
                grouped_scores[i] /= EPISODES_PER_FITNESS

            dt = time.perf_counter() - t0

            scored = list(zip(population, grouped_scores))
            scored.sort(key = lambda x: x[1], reverse = True)

            gen_best, gen_best_score = scored[0]
            if gen_best_score > goat_score:
                goat_score = gen_best_score
                goat = gen_best[:]

            print(f"Gen {gen:03d} | eval_time={dt:.3f} | best={gen_best_score:.1f} | global_best={goat_score:.2f}")

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

            log_params = chromosome_to_params(gen_best)
            gen_log["generations"].append(
                {
                    "generation": gen,
                    "fitness": gen_best_score,
                    "distance_penalty": log_params.distance_penalty,
                    "space_count_reward": log_params.space_count_reward,
                    "weights": list(log_params.weights),
                    "population": population
                }
            )

            with open(PARAMS_FILE_NAME, "w") as f:
                json.dump(gen_log, f, indent=2)

    best_params = chromosome_to_params(goat)
    print("\nBest chromosome:", goat)
    print(f"Best distance penalty: {best_params.distance_penalty}")
    print(f"Best space count reward: {best_params.space_count_reward}")
    for i in range(16):
        print(f"{best_params.weights[i]:.0f}", end="  ")
        if (i + 1) % 4 == 0:
            print()
    print("Best fitness:", goat_score)

    try:
        with open("params/best_ga_params.json", "r") as f:
            prev_best = json.load(f)
            score = prev_best["evaluation_params"]["fitness"]

    except Exception as e:
        print(e)
        score = 0

    if score > goat_score:
        best_params = chromosome_to_params(goat)
        with open("params/best_ga_params.json", "w") as f:
            json.dump(
                {
                    "training_params": {
                        "population_size": POPULATION_SIZE,
                        "generations": GENERATIONS,
                        "episodes_per_fitness": EPISODES_PER_FITNESS,
                        "search_depth": SEARCH_DEPTH,
                        "elite_count": ELITE_COUNT,
                        "tournament_k": TOURNAMENT_K,
                        "mutation_rate": MUTATION_RATE,
                        "mutation_std_frac": MUTATION_STD_FRAC,
                        "max_parallel_players": MAX_PARALLEL_PLAYERS
                    },
                    "evaluation_params": {
                        "fitness": goat_score,
                        "distance_penalty": best_params.distance_penalty,
                        "space_count_reward": best_params.space_count_reward,
                        "weights": list(best_params.weights),
                        "goat": goat,
                        "population": population
                    }
                },
                f,
                indent=2,
            )


if __name__ == "__main__":
    random.seed(42)
    evolve()

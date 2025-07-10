# Imports
import os
import json
import copy
import random
import numpy as np
from collections import OrderedDict
import argparse
import multiprocessing

# Helper Functions and Classes
def secure_float(rng):
    return rng.random()

def sample(population, k, random_generator):
    n = len(population)
    if not 0 <= k <= n:
        raise ValueError("Die Anzahl k muss zwischen 0 und der Größe der Population liegen.")

    selected = []
    selected_set = set()

    for i in range(k):
        random_index = int(random_generator() * n)
        while random_index in selected_set:
            random_index = int(random_generator() * n)
        selected.append(population[random_index])
        selected_set.add(random_index)

    return selected

class ValueOrderedDict(OrderedDict):
    def sort_by_value(self):
        sorted_items = sorted(super().items(), key=lambda item: item[1])
        self.clear()
        for key, value in sorted_items:
            self[key] = value

    def peekitem(self):
        return next(iter(self.items()))

    def peekitem_excluding(self, exclude_list=[]):
        for key, value in self.items():
            if key not in exclude_list:
                return key, value
        return None

def read_data(filename):
    with open(filename, 'r') as file:
        return json.load(file)

def save_data(filename, d):
    directory = os.path.dirname(filename)

    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(filename, 'w') as file:
        json.dump(d, file)

# Approaches
class fox_rr():
    def __init__(self, rng_seed):
        self.rng = np.random.default_rng(rng_seed)

    def randomized_respond(self, bit, q, r):
        if secure_float(self.rng) <= q:
            return bit
        else:
            if secure_float(self.rng) <= r:
                return 1
            else:
                return 0

    def perturb(self, encoded_responses, q, r, tau):
        return [{key: self.randomized_respond(value, q, r) for key, value in response.items()} for response in encoded_responses]

    def simulate(self, seed, q, r, tau):
        frequencies = ValueOrderedDict({str(c): 0 for c in range(len(seed[0]))})
        sets = self.perturb(seed, q, r, tau)

        for s in sets:
            for k,v in s.items():
                frequencies[k] += v

        return sets, frequencies

    def simulate_and_save(self, params):
        seed, q, r, tau, run = params
        sets, frequencies = self.simulate(seed, q, r, tau)

        save_data("results/fox/frequencies/run-{}_q-{}_r-{}_tau-{}.json".format(run, q, r, tau), frequencies)

class mangat_rr():
    def __init__(self, rng_seed):
        self.rng = np.random.default_rng(rng_seed)

    def randomized_respond(self, bit, r):
        if bit == 1:
            return 1
        else:
            if secure_float(self.rng) <= r:
                return 1
            else:
                return 0

    def perturb(self, encoded_responses, r):
        return [{key: self.randomized_respond(value, r) for key, value in response.items()} for response in encoded_responses]

    def simulate(self, seed, q, r, tau):
        frequencies = ValueOrderedDict({str(c): 0 for c in range(len(seed[0]))})
        sets = self.perturb(seed, r)

        for s in sets:
            for k,v in s.items():
                frequencies[k] += v

        return sets, frequencies

    def simulate_and_save(self, params):
        seed, q, r, tau, run = params
        sets, frequencies = self.simulate(seed, q, r, tau)

        save_data("results/mangat/frequencies/run-{}_q-{}_r-{}_tau-{}.json".format(run, q, r, tau), frequencies)

class fixed_rr():
    def __init__(self, rng_seed):
        self.rng = np.random.default_rng(rng_seed)

    def randomized_respond(self, bit, r):
        if bit == 1:
            print("ERROR")
            return 1
        else:
            if secure_float(self.rng) <= r:
                return 1
            else:
                return 0

    def simulate(self, seed, q, r, tau):
        frequencies = ValueOrderedDict({str(c): 0 for c in range(len(seed[0]))})
        sets = []

        for s in seed:
            res = copy.copy(s)
            zero_index = []
            for key, value in s.items():
                if value == 0:
                    zero_index.append(key)

            if len(zero_index) > 0:
                l = min(tau, len(zero_index))
                zero_index = sample(zero_index, l, self.rng.random)

            for i in zero_index:
                res[i] = self.randomized_respond(value, r)

            sets.append(res)

        for s in sets:
            for k,v in s.items():
                frequencies[k] += v

        return sets, frequencies

    def simulate_and_save(self, params):
        seed, q, r, tau, run = params
        sets, frequencies = self.simulate(seed, q, r, tau)

        save_data("results/fixed/frequencies/run-{}_q-{}_r-{}_tau-{}.json".format(run, q, r, tau), frequencies)

# Simulation
# Usage: simulation.py --seed 'path/to/zipf_distribution.json' --q q_value_as_float --r r_value_as_float --tau q_value_as_int --run counter_for_simulation_run_as_int
if __name__ == "__main__":
    parser=argparse.ArgumentParser(description="Test run for each approach")
    parser.add_argument("--seed", type=str)
    parser.add_argument("--q", type=float)
    parser.add_argument("--r", type=float)
    parser.add_argument("--tau", type=int)
    parser.add_argument("--run", type=int)
    args=parser.parse_args()

    params = (read_data(args.seed), args.q, args.r, args.tau, args.run)

    pool = multiprocessing.Pool(processes=3)

    r_seed = 22527 + args.run

    fox = fox_rr(r_seed)
    mangat = mangat_rr(r_seed)
    fixed = fixed_rr(r_seed)

    pool.map(fox.simulate_and_save, (params,))
    pool.map(mangat.simulate_and_save, (params,))
    pool.map(fixed.simulate_and_save, (params,))

    pool.close()
    pool.join()
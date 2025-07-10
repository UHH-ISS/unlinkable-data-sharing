import copy
import json
from collections import OrderedDict
from collections import Counter
import numpy as np

rng = np.random.default_rng(seed=22527)

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
    with open(filename, 'w') as file:
        json.dump(d, file)

def gen_zipf_dist(num_topics, user_count):
    size = num_topics
    while True:
        a = 2
        set = rng.zipf(a, size)

        c = Counter(set)

        max = c.most_common(1)[0][1]

        factor = int(user_count / max)

        rtn = {str(i): int(value * factor) for i,value in enumerate(c.values())}
        if len(rtn) == num_topics:
            return rtn
        else:
            size += 1

def create_seed(nbOfProviders, categories):
    frequencies = ValueOrderedDict({c: v for c,v in categories.items()})
    org_freq = copy.copy(frequencies)
    seed = [{} for _ in range(nbOfProviders)]

    for i,s in enumerate(seed):
        for c,v in frequencies.items():
            if v > 0:
                seed[i][c] = 1
                frequencies[c] -= 1
            else:
                seed[i][c] = 0

    return seed


# constants
nbOfProviders  = 100_000
categories = gen_zipf_dist(50, 50_000)

# generating seed
seed = create_seed(nbOfProviders, categories)

save_data("zipf_50k_seed.json", seed)
seed = None
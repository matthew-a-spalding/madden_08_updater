r"""
    This file allows for the testing of potential inputs to the function for generating weighted random values.
"""
import logging, itertools
from numpy import array, random

logging.basicConfig(filename="test.log", level=logging.INFO, format="%(message)s")

def get_weighted_random(values_list, weights_list):
    """ Gets a random value from a list of possible values where each value is assigned a weighted probability. """
    weights_array = array(weights_list)
    normalized_weights = weights_array / weights_array.sum()
    return random.choice(values_list, p=normalized_weights)

elements = list(range(0, 100))
weights = [0.03] + [.003] * 20 + [.0015] * 20 + [.003] * 10 + [.02] * 10 + [.0125] * 20 + [.025] * 10 + [.016667] * 9

print("elements = ", elements)
print("weights = ", weights)
print("len(elements) = ", len(elements))
print("len(weights) = ", len(weights))

for _ in itertools.repeat(None, 2000):
    logging.info(get_weighted_random(elements, weights))

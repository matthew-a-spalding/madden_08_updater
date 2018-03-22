r""" randomizer_functions.py
    
    This module contains the functions used by the methods of roster_manager.RosterManager (which each live in 
    separate files) to generate pseudo-random values (given certain options and porbability weightings).
"""

from numpy import array, random

def get_weighted_random(values_list, weights_list):
    """ Gets a random value from a list of possible values where each value is assigned a weighted probability. """
    weights_array = array(weights_list)
    normalized_weights = weights_array / weights_array.sum()
    return random.choice(values_list, p=normalized_weights)

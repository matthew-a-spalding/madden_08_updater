r"""test_curve_fit.py
    
    A script to calculate the paramters needed by the function:
        y = a * np.exp(b * x) + c    # (where np is the numpy library)
    for each position's set of data points (xdata, ydata) where the xdata is each player's overall_rating, and the 
    ydata is that player's total_salary.
    
    See https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html
    
    The 21 sets of parameters returned by the calls to curve_fit() will be printed out to the file 
    "pay_curve_parameters.csv".
    
    To populate the data points used to determine the best-fit curve and get the parameters, this script will read in 
    the file "My 20[XX] Player Attributes - In Progress 20[XX]_MM_DD.csv". This file MUST BE SORTED by position and 
    then by total_salary (ascending). The player data is used to create 21 sets of two lists, pairing the (derived) 
    overall ratings with the corresponding yearly(!) salaries. These two lists are feed into scipy's curve_fit() to 
    generate two arrays (which we convert to lists) of the a, b, and c parameters we will need when defining the two 
    functions. These functions are the ones that will take as input one overall rating at a time and generate a value 
    (which we can then modify within 2 standard deviations, to randomize it a bit more) that will serve as the total 
    yearly salaryfor a player. Length of the contract will then be reandomly chosen, within a reasonable range, based 
    on the player's years pro. Then, signing bonus will finally be determined as a multiple of the number of years we 
    set the contract to.)
    
    Later, in step 5,each player without contract info will get a slightly randomized value for their per-year-salary, 
    a reasonable number of years on the contract (taking into account their no. of years pro), the number of years 
    left on the contract (again, taking into account their no. of years pro), and their signing bonus figure. 
"""

# ----------------------------------------------------- SECTION 1 -----------------------------------------------------
# ----------------------------------------- IMPORTS, SETTINGS, AND CONSTANTS ------------------------------------------

# 1.1 - Standard library imports

import csv, math, os
#from ctypes import byref, cast, c_bool, c_char, c_char_p, c_int, POINTER, Structure, WinDLL
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

# 1.2 - Third-party imports


# 1.3 - Application-specific imports


# 1.4 - Global settings


# 1.5 - Global constants

# Set the base path we will use to keep other paths relative, and shorter :^)
# This will be the directory above the directory above the directory this file is in.
BASE_MADDEN_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ----------------------------------------------------- SECTION 2 -----------------------------------------------------
# ------------------------------------------------ Class Declarations -------------------------------------------------


# ----------------------------------------------------- SECTION 3 -----------------------------------------------------
# ------------------------------------------------- Helper Functions --------------------------------------------------

def func(x, a, b, c):
    """
    This is the function for which we will be finding the paramters that allow us to create a best-fit curve for each 
    set of inputs (overall_ratings and yearly_salaries).
    """
    return a + (b * x) + (c * x * x)

def calculate_overall_rating(player_dict):
    """
    This function calculates the overall_rating of a player based on his position.
    """
    if player_dict["position"].upper() == "QB":
        throw_power = int(max(min(int(player_dict["throw_power"]), 99), 70))
        throw_accuracy = int(max(min(math.ceil(
            ((2 * (
                int(player_dict["throw_accuracy_short"]) + 
                int(player_dict["throw_accuracy_mid"]) + 
                int(player_dict["throw_accuracy_deep"]) + 
                int(player_dict["throw_on_the_run"]) + 
                int(player_dict["playaction"])
            )) - (2 * min(
                int(player_dict["throw_accuracy_short"]), 
                int(player_dict["throw_accuracy_mid"]), 
                int(player_dict["throw_accuracy_deep"]), 
                int(player_dict["throw_on_the_run"]), 
                int(player_dict["playaction"])
            ))
            ) / 8
        ), 99), 60))
        break_tackles = int(max(min(
            math.ceil(((int(player_dict["elusiveness"]) + int(player_dict["trucking"])) / 2) + 7), 
            90), 20))
        agility = int(max(min(int(player_dict["agility"]), 98), 45))
        awareness = int(max(min(int(player_dict["awareness"]), 99), 40))
        speed = int(max(min(int(player_dict["speed"]), 95), 55))
        
        overall_rating = 0.0
        overall_rating += ((throw_power - 50.0) / 10.0) * 4.9
        overall_rating += ((throw_accuracy - 50.0) / 10.0) * 5.8
        overall_rating += ((break_tackles - 50.0) / 10.0) * 0.8
        overall_rating += ((agility - 50.0) / 10.0) * 0.8
        overall_rating += ((awareness - 50.0) / 10.0) * 4.0
        overall_rating += ((speed - 50.0) / 10.0) * 2.0
        overall_rating = int(max(min((round(overall_rating) + 28), 99), 40))
        return overall_rating
    
    if player_dict["position"].upper() == "HB":
        pass_block = int(max(min(math.ceil(
            (
                int(player_dict["pass_block"]) + 
                int(player_dict["pass_block_power"]) + 
                int(player_dict["pass_block_finesse"])
            ) / 3
        ), 70), 25))
        break_tackles = int(max(min(
            (math.ceil((int(player_dict["elusiveness"]) + int(player_dict["trucking"])) / 2) + 5), 
            99), 50))
        carrying = int(max(min(int(player_dict["carrying"]), 99), 60))
        acceleration = int(max(min(int(player_dict["acceleration"]), 99), 80))
        agility = int(max(min(int(player_dict["agility"]), 99), 70))
        awareness = int(max(min(int(player_dict["awareness"]), 99), 45))
        strength = int(max(min(int(player_dict["strength"]), 90), 45))
        speed = int(max(min(int(player_dict["speed"]), 99), 80))
        catching = int(max(min(int(player_dict["catching"]), 95), 50))
        
        overall_rating = 0.0
        overall_rating += ((pass_block - 50.0) / 10.0) * 0.33
        overall_rating += ((break_tackles - 50.0) / 10.0) * 0.8
        overall_rating += ((carrying - 50.0) / 10.0) * 2.0
        overall_rating += ((acceleration - 50.0) / 10.0) * 1.8
        overall_rating += ((agility - 50.0) / 10.0) * 2.8
        overall_rating += ((awareness - 50.0) / 10.0) * 2.0
        overall_rating += ((strength - 50.0) / 10.0) * 0.6
        overall_rating += ((speed - 50.0) / 10.0) * 3.3
        overall_rating += ((catching - 50.0) / 10.0) * 1.4
        overall_rating = int(max(min((round(overall_rating) + 27), 99), 40))
        return overall_rating
    
    if player_dict["position"].upper() == "FB":
        pass_block = int(max(min(math.ceil(
            (
                int(player_dict["pass_block"]) + 
                int(player_dict["pass_block_power"]) + 
                int(player_dict["pass_block_finesse"])
            ) / 3
        ), 75), 40))
        run_block = int(max(min(math.ceil(
            (
                int(player_dict["run_block"]) + 
                int(player_dict["run_block_power"]) + 
                int(player_dict["run_block_finesse"])
            ) / 3
        ), 85), 45))
        break_tackles = int(max(min(
            (math.ceil((int(player_dict["elusiveness"]) + int(player_dict["trucking"])) / 2) + 5), 
            99), 55))
        carrying = int(max(min(int(player_dict["carrying"]), 99), 60))
        acceleration = int(max(min(int(player_dict["acceleration"]), 95), 65))
        agility = int(max(min(int(player_dict["agility"]), 95), 55))
        awareness = int(max(min(int(player_dict["awareness"]), 99), 45))
        strength = int(max(min(int(player_dict["strength"]), 95), 60))
        speed = int(max(min(int(player_dict["speed"]), 95), 60))
        catching = int(max(min(int(player_dict["catching"]), 95), 45))
        
        overall_rating = 0.0
        overall_rating += ((pass_block - 50.0) / 10.0) * 1.0
        overall_rating += ((run_block - 50.0) / 10.0) * 7.2
        overall_rating += ((break_tackles - 50.0) / 10.0) * 1.8
        overall_rating += ((carrying - 50.0) / 10.0) * 1.8
        overall_rating += ((acceleration - 50.0) / 10.0) * 1.8
        overall_rating += ((agility - 50.0) / 10.0) * 1.0
        overall_rating += ((awareness - 50.0) / 10.0) * 2.8
        overall_rating += ((strength - 50.0) / 10.0) * 1.8
        overall_rating += ((speed - 50.0) / 10.0) * 1.8
        overall_rating += ((catching - 50.0) / 10.0) * 5.2
        overall_rating = int(max(min((round(overall_rating) + 39), 99), 40))
        return overall_rating
    
    if player_dict["position"].upper() == "WR":
        break_tackles = int(max(min(
            math.ceil((int(player_dict["elusiveness"]) + int(player_dict["trucking"])) / 2), 
            80), 35))
        acceleration = int(max(min(int(player_dict["acceleration"]), 99), 75))
        agility = int(max(min(int(player_dict["agility"]), 99), 75))
        awareness = int(max(min(int(player_dict["awareness"]), 99), 35))
        strength = int(max(min(int(player_dict["strength"]), 85), 35))
        speed = int(max(min(int(player_dict["speed"]), 99), 80))
        catching = int(max(min(int(player_dict["catching"]), 99), 65))
        jumping = int(max(min(int(player_dict["jumping"]), 99), 65))
        
        overall_rating = 0.0
        overall_rating += ((break_tackles - 50.0) / 10.0) * 0.8
        overall_rating += ((acceleration - 50.0) / 10.0) * 2.3
        overall_rating += ((agility - 50.0) / 10.0) * 2.3
        overall_rating += ((awareness - 50.0) / 10.0) * 2.3
        overall_rating += ((strength - 50.0) / 10.0) * 0.8
        overall_rating += ((speed - 50.0) / 10.0) * 2.3
        overall_rating += ((catching - 50.0) / 10.0) * 4.75
        overall_rating += ((jumping - 50.0) / 10.0) * 1.4
        overall_rating = int(max(min((round(overall_rating) + 26), 99), 40))
        return overall_rating
    
    if player_dict["position"].upper() == "TE":
        speed = int(max(min(int(player_dict["speed"]), 95), 55))
        strength = int(max(min(int(player_dict["strength"]), 90), 55))
        awareness = int(max(min(int(player_dict["awareness"]), 99), 35))
        agility = int(max(min(int(player_dict["agility"]), 95), 55))
        acceleration = int(max(min(int(player_dict["acceleration"]), 95), 60))
        catching = int(max(min(int(player_dict["catching"]), 99), 45))
        break_tackles = int(max(min(
            (math.ceil((int(player_dict["elusiveness"]) + int(player_dict["trucking"])) / 2) + 5), 
            95), 20))
        pass_block = int(max(min(math.ceil(
            (
                int(player_dict["pass_block"]) + 
                int(player_dict["pass_block_power"]) + 
                int(player_dict["pass_block_finesse"])
            ) / 3
        ), 80), 35))
        run_block = int(max(min(math.ceil(
            (
                int(player_dict["run_block"]) + 
                int(player_dict["run_block_power"]) + 
                int(player_dict["run_block_finesse"])
            ) / 3
        ), 85), 35))
        
        overall_rating = 0.0
        overall_rating += ((speed - 50.0) / 10.0) * 2.65
        overall_rating += ((strength - 50.0) / 10.0) * 2.65
        overall_rating += ((awareness - 50.0) / 10.0) * 2.65
        overall_rating += ((agility - 50.0) / 10.0) * 1.25
        overall_rating += ((acceleration - 50.0) / 10.0) * 1.25
        overall_rating += ((catching - 50.0) / 10.0) * 5.4
        overall_rating += ((break_tackles - 50.0) / 10.0) * 1.2
        overall_rating += ((pass_block - 50.0) / 10.0) * 1.2
        overall_rating += ((run_block - 50.0) / 10.0) * 5.4
        overall_rating = int(max(min((round(overall_rating) + 35), 99), 40))
        return overall_rating
    
    if player_dict["position"].upper() == "LT" or player_dict["position"].upper() == "RT":
        speed = int(max(min(int(player_dict["speed"]), 85), 45))
        strength = int(max(min(int(player_dict["strength"]), 99), 70))
        awareness = int(max(min(int(player_dict["awareness"]), 99), 40))
        agility = int(max(min(int(player_dict["agility"]), 85), 40))
        acceleration = int(max(min(int(player_dict["acceleration"]), 90), 60))
        pass_block = int(max(min(math.ceil(
            (
                int(player_dict["pass_block"]) + 
                int(player_dict["pass_block_power"]) + 
                int(player_dict["pass_block_finesse"])
            ) / 3
        ), 99), 60))
        run_block = int(max(min(math.ceil(
            (
                int(player_dict["run_block"]) + 
                int(player_dict["run_block_power"]) + 
                int(player_dict["run_block_finesse"])
            ) / 3
        ), 99), 60))
        
        overall_rating = 0.0
        overall_rating += ((speed - 50.0) / 10.0) * 0.8
        overall_rating += ((strength - 50.0) / 10.0) * 3.3
        overall_rating += ((awareness - 50.0) / 10.0) * 3.3
        overall_rating += ((agility - 50.0) / 10.0) * 0.8
        overall_rating += ((acceleration - 50.0) / 10.0) * 0.8
        overall_rating += ((pass_block - 50.0) / 10.0) * 4.75
        overall_rating += ((run_block - 50.0) / 10.0) * 3.75
        overall_rating = int(max(min((round(overall_rating) + 26), 99), 40))
        return overall_rating
    
    if (player_dict["position"].upper() == "LG" or player_dict["position"].upper() == "RG" or 
            player_dict["position"].upper() == "C"):
        speed = int(max(min(int(player_dict["speed"]), 85), 45))
        strength = int(max(min(int(player_dict["strength"]), 99), 70))
        awareness = int(max(min(int(player_dict["awareness"]), 99), 40))
        agility = int(max(min(int(player_dict["agility"]), 85), 40))
        acceleration = int(max(min(int(player_dict["acceleration"]), 90), 60))
        pass_block = int(max(min(math.ceil(
            (
                int(player_dict["pass_block"]) + 
                int(player_dict["pass_block_power"]) + 
                int(player_dict["pass_block_finesse"])
            ) / 3
        ), 99), 65))
        run_block = int(max(min(math.ceil(
            (
                int(player_dict["run_block"]) + 
                int(player_dict["run_block_power"]) + 
                int(player_dict["run_block_finesse"])
            ) / 3
        ), 99), 65))
        
        overall_rating = 0.0
        overall_rating += ((speed - 50.0) / 10.0) * 1.7
        overall_rating += ((strength - 50.0) / 10.0) * 3.25
        overall_rating += ((awareness - 50.0) / 10.0) * 3.25
        overall_rating += ((agility - 50.0) / 10.0) * 0.8
        overall_rating += ((acceleration - 50.0) / 10.0) * 1.7
        overall_rating += ((pass_block - 50.0) / 10.0) * 3.25
        overall_rating += ((run_block - 50.0) / 10.0) * 4.8
        overall_rating = int(max(min((round(overall_rating) + 28), 99), 40))
        return overall_rating
    
    if player_dict["position"].upper() == "LE" or player_dict["position"].upper() == "RE":
        speed = int(max(min(int(player_dict["speed"]), 90), 55))
        strength = int(max(min(int(player_dict["strength"]), 99), 60))
        awareness = int(max(min(int(player_dict["awareness"]), 99), 40))
        agility = int(max(min(int(player_dict["agility"]), 90), 45))
        acceleration = int(max(min(int(player_dict["acceleration"]), 95), 65))
        tackle = int(max(min(int(player_dict["tackle"]), 99), 60))
        
        overall_rating = 0.0
        overall_rating += ((speed - 50.0) / 10.0) * 3.75
        overall_rating += ((strength - 50.0) / 10.0) * 3.75
        overall_rating += ((awareness - 50.0) / 10.0) * 1.75
        overall_rating += ((agility - 50.0) / 10.0) * 1.75
        overall_rating += ((acceleration - 50.0) / 10.0) * 3.8
        overall_rating += ((tackle - 50.0) / 10.0) * 5.5
        overall_rating = int(max(min((round(overall_rating) + 30), 99), 40))
        return overall_rating
    
    if player_dict["position"].upper() == "DT":
        speed = int(max(min(int(player_dict["speed"]), 90), 45))
        strength = int(max(min(int(player_dict["strength"]), 99), 70))
        awareness = int(max(min(int(player_dict["awareness"]), 99), 40))
        agility = int(max(min(int(player_dict["agility"]), 90), 40))
        acceleration = int(max(min(int(player_dict["acceleration"]), 95), 65))
        tackle = int(max(min(int(player_dict["tackle"]), 99), 65))
        
        overall_rating = 0.0
        overall_rating += ((speed - 50.0) / 10.0) * 1.8
        overall_rating += ((strength - 50.0) / 10.0) * 5.5
        overall_rating += ((awareness - 50.0) / 10.0) * 3.8
        overall_rating += ((agility - 50.0) / 10.0) * 1
        overall_rating += ((acceleration - 50.0) / 10.0) * 2.8
        overall_rating += ((tackle - 50.0) / 10.0) * 4.55
        overall_rating = int(max(min((round(overall_rating) + 29), 99), 40))
        return overall_rating
    
    if player_dict["position"].upper() == "LOLB" or player_dict["position"].upper() == "ROLB":
        speed = int(max(min(int(player_dict["speed"]), 95), 70))
        strength = int(max(min(int(player_dict["strength"]), 99), 60))
        awareness = int(max(min(int(player_dict["awareness"]), 99), 40))
        agility = int(max(min(int(player_dict["agility"]), 95), 65))
        acceleration = int(max(min(int(player_dict["acceleration"]), 95), 75))
        catching = int(max(min(int(player_dict["catching"]), 90), 20))
        tackle = int(max(min(int(player_dict["tackle"]), 99), 60))
        
        overall_rating = 0.0
        overall_rating += ((speed - 50.0) / 10.0) * 3.75
        overall_rating += ((strength - 50.0) / 10.0) * 2.4
        overall_rating += ((awareness - 50.0) / 10.0) * 3.6
        overall_rating += ((agility - 50.0) / 10.0) * 2.4
        overall_rating += ((acceleration - 50.0) / 10.0) * 1.3
        overall_rating += ((catching - 50.0) / 10.0) * 1.3
        overall_rating += ((tackle - 50.0) / 10.0) * 4.8
        overall_rating = int(max(min((round(overall_rating) + 29), 99), 40))
        return overall_rating
    
    if player_dict["position"].upper() == "MLB":
        speed = int(max(min(int(player_dict["speed"]), 95), 65))
        strength = int(max(min(int(player_dict["strength"]), 99), 60))
        awareness = int(max(min(int(player_dict["awareness"]), 99), 35))
        agility = int(max(min(int(player_dict["agility"]), 95), 65))
        acceleration = int(max(min(int(player_dict["acceleration"]), 95), 75))
        tackle = int(max(min(int(player_dict["tackle"]), 99), 65))
        
        overall_rating = 0.0
        overall_rating += ((speed - 50.0) / 10.0) * 0.75
        overall_rating += ((strength - 50.0) / 10.0) * 3.4
        overall_rating += ((awareness - 50.0) / 10.0) * 5.2
        overall_rating += ((agility - 50.0) / 10.0) * 1.65
        overall_rating += ((acceleration - 50.0) / 10.0) * 1.75
        overall_rating += ((tackle - 50.0) / 10.0) * 5.2
        overall_rating = int(max(min((round(overall_rating) + 27), 99), 40))
        return overall_rating
    
    if player_dict["position"].upper() == "CB":
        speed = int(max(min(int(player_dict["speed"]), 99), 80))
        strength = int(max(min(int(player_dict["strength"]), 85), 40))
        awareness = int(max(min(int(player_dict["awareness"]), 99), 35))
        agility = int(max(min(int(player_dict["agility"]), 99), 75))
        acceleration = int(max(min(int(player_dict["acceleration"]), 99), 80))
        catching = int(max(min(int(player_dict["catching"]), 95), 40))
        jumping = int(max(min(int(player_dict["jumping"]), 99), 65))
        tackle = int(max(min(int(player_dict["tackle"]), 85), 30))
        
        overall_rating = 0.0
        overall_rating += ((speed - 50.0) / 10.0) * 3.85
        overall_rating += ((strength - 50.0) / 10.0) * 0.9
        overall_rating += ((awareness - 50.0) / 10.0) * 3.85
        overall_rating += ((agility - 50.0) / 10.0) * 1.55
        overall_rating += ((acceleration - 50.0) / 10.0) * 2.35
        overall_rating += ((catching - 50.0) / 10.0) * 3
        overall_rating += ((jumping - 50.0) / 10.0) * 1.55
        overall_rating += ((tackle - 50.0) / 10.0) * 1.55
        overall_rating = int(max(min((round(overall_rating) + 28), 99), 40))
        return overall_rating
    
    if player_dict["position"].upper() == "FS":
        speed = int(max(min(int(player_dict["speed"]), 99), 75))
        strength = int(max(min(int(player_dict["strength"]), 85), 45))
        awareness = int(max(min(int(player_dict["awareness"]), 99), 40))
        agility = int(max(min(int(player_dict["agility"]), 99), 70))
        acceleration = int(max(min(int(player_dict["acceleration"]), 99), 80))
        catching = int(max(min(int(player_dict["catching"]), 95), 35))
        jumping = int(max(min(int(player_dict["jumping"]), 99), 65))
        tackle = int(max(min(int(player_dict["tackle"]), 90), 45))
        
        overall_rating = 0.0
        overall_rating += ((speed - 50.0) / 10.0) * 3.0
        overall_rating += ((strength - 50.0) / 10.0) * 0.9
        overall_rating += ((awareness - 50.0) / 10.0) * 4.85
        overall_rating += ((agility - 50.0) / 10.0) * 1.5
        overall_rating += ((acceleration - 50.0) / 10.0) * 2.5
        overall_rating += ((catching - 50.0) / 10.0) * 3.0
        overall_rating += ((jumping - 50.0) / 10.0) * 1.5
        overall_rating += ((tackle - 50.0) / 10.0) * 2.5
        overall_rating = int(max(min((round(overall_rating) + 30), 99), 40))
        return overall_rating
    
    if player_dict["position"].upper() == "SS":
        speed = int(max(min(int(player_dict["speed"]), 99), 75))
        strength = int(max(min(int(player_dict["strength"]), 90), 45))
        awareness = int(max(min(int(player_dict["awareness"]), 99), 40))
        agility = int(max(min(int(player_dict["agility"]), 99), 70))
        acceleration = int(max(min(int(player_dict["acceleration"]), 99), 80))
        catching = int(max(min(int(player_dict["catching"]), 95), 35))
        jumping = int(max(min(int(player_dict["jumping"]), 99), 65))
        tackle = int(max(min(int(player_dict["tackle"]), 90), 45))
        
        overall_rating = 0.0
        overall_rating += ((speed - 50.0) / 10.0) * 3.2
        overall_rating += ((strength - 50.0) / 10.0) * 1.7
        overall_rating += ((awareness - 50.0) / 10.0) * 4.75
        overall_rating += ((agility - 50.0) / 10.0) * 1.7
        overall_rating += ((acceleration - 50.0) / 10.0) * 1.7
        overall_rating += ((catching - 50.0) / 10.0) * 3.2
        overall_rating += ((jumping - 50.0) / 10.0) * 0.9
        overall_rating += ((tackle - 50.0) / 10.0) * 3.2
        overall_rating = int(max(min((round(overall_rating) + 30), 99), 40))
        return overall_rating
    
    if player_dict["position"].upper() == "K":
        awareness = int(max(min(int(player_dict["awareness"]), 85), 35))
        kick_power = int(max(min(int(player_dict["kick_power"]), 99), 80))
        kick_accuracy = int(max(min(int(player_dict["kick_accuracy"]), 99), 70))
        
        overall_rating = (-177 + (0.218 * awareness) + (1.28 * kick_power) + (1.47 * kick_accuracy))
        overall_rating = int(max(min(round(overall_rating), 99), 40))
        return overall_rating
    
    if player_dict["position"].upper() == "P":
        awareness = int(max(min(int(player_dict["awareness"]), 85), 40))
        kick_power = int(max(min(int(player_dict["kick_power"]), 99), 80))
        kick_accuracy = int(max(min(int(player_dict["kick_accuracy"]), 99), 70))
        
        overall_rating = (-183 + (0.218 * awareness) + (1.5 * kick_power) + (1.33 * kick_accuracy))
        overall_rating = int(max(min(round(overall_rating), 99), 40))
        return overall_rating
    

# ----------------------------------------------------- SECTION 4 -----------------------------------------------------
# -------------------------------------------------- Main Function ----------------------------------------------------

# We need to figure out what the file's name will be, using today's date.
time_now = datetime.now()

input_path = BASE_MADDEN_PATH + r"\docs\My Ratings\{0}".format(time_now.year)

input_name = ("My " + str(time_now.year) + r" Player Attributes" + 
              r" - In Progress " + time_now.strftime("%Y_%m_%d") + ".csv")

output_path = BASE_MADDEN_PATH + r"\docs\Pay Calculations\{0}".format(time_now.year)

output_name = ("pay_curve_parameters.csv")

# Open the file to read from.
input_file = open(os.path.join(input_path, input_name), "r", newline="")

# Open the file to write to.
output_file = open(os.path.join(output_path, output_name), "w", newline="")

# Create our DictReader.
player_attribute_dict_reader = csv.DictReader(input_file)

# Create our DictWriter w/ header row info.
output_fields = ["position", "a_param", "b_param", "c_param"]
pay_curve_parameters_writer = csv.DictWriter(output_file, output_fields)

# Write the header first.
pay_curve_parameters_writer.writeheader()

# Initialize the variables we will need in the main logic loop.
working_position = "" # Current position we are dealing with.
dicts_by_position = {} # Our dict of dicts: {position : {rating:salary, rating:salary, ...}, ... }

# Start looping over the records and performing our logic on each.
for player_dict in player_attribute_dict_reader:
    
    # See if this player's team is different from the previous player's team.
    if player_dict["position"] != working_position:
        # Update the current working_team
        working_position = player_dict["position"]
        # Create the new sub-dict keyed to this position in our dict of dicts.
        dicts_by_position[working_position] = {}
    
    # See if this player is missing contract info or attributes.
    if player_dict["total_salary"] == "" or player_dict["awareness"] == "":
        # Nothing to do with this player for now.
        continue
    
    # Calculate the player's overall rating.
    overall_rating = float(calculate_overall_rating(player_dict))
    # Get the length of this player's contract.
    contract_length = int(player_dict["contract_length"])
    # Calculate the player's yearly salary.
    yearly_salary = round(int(player_dict["total_salary"]) / contract_length)
    
    # Since we might have issues if we add multiple yearly_salary values with the same exact overall_rating, let's 
    # check for players with the same ratings and incrementally inflate the player's rating by a small amount to 
    # keep the xdata unique.
    while overall_rating in [*dicts_by_position[working_position]]:
        # Increment our adjustment factor and add it to this player's overall_rating.
        overall_rating = round(overall_rating + 0.025, 3)
    
    # Add this player's rating and yearly salary to the appropriate lists.
    dicts_by_position[working_position][overall_rating] = yearly_salary
    
# Close the input file.
input_file.close()

# Now that we have all of the dicts, let's feed them to the curve_fit() function and get the resulting params.
index = 0
for working_position, ratings_and_salaries_dict in dicts_by_position.items():
    
    # Sort the dictionary, putting the keys (ratings) into overall_ratings_list and the values (salaries) into 
    # yearly_salaries_list.
    overall_ratings_list = []
    yearly_salaries_list = []
    for (rating, salary) in sorted(ratings_and_salaries_dict.items()):
        overall_ratings_list.append(float(rating))
        yearly_salaries_list.append(salary)
    
    # Now feed these lists into curve_fit() and write the results to our output file.
    popt, pcov = curve_fit(func, overall_ratings_list, yearly_salaries_list)
    
    # TESTING
    # For the first set of data, plot and show both the data and fit curve.
    if index == 1:
        plt.plot(overall_ratings_list, yearly_salaries_list, "b-", label=f"{working_position} data")
        np.savetxt('center_ratings.txt', overall_ratings_list, fmt='%s')
        np.savetxt('center_salaries.txt', yearly_salaries_list, fmt='%s')
        plt.plot(overall_ratings_list, func(np.array(overall_ratings_list), *popt), 'r-', 
                 label='fit: a=%5.3f, b=%5.3f, c=%5.3f' % tuple(popt))
    
    # Take the output array of parameters and append it to the output list of lists.
    position_params_dict = {"position" : working_position, 
                            "a_param" : str(popt[0]), 
                            "b_param" : str(popt[1]), 
                            "c_param" : str(popt[2])}
    
    # Write this set of parameters to the output file.
    pay_curve_parameters_writer.writerow(position_params_dict)
    
    index += 1
    

# Close the output file.
output_file.close()

plt.xlabel("overall_rating")
plt.ylabel("yearly_salary")
plt.legend()
plt.show()

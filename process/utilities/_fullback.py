r""" _fullback.py
    
    This is one of the 21 method-definition modules used by the main RosterManager class. This module contains the 
    method used to populate the fields for a fullback record in the roster DB.
"""

# --------------------------------------------------- SECTION 1 -------------------------------------------------------
# ---------------------------------------- IMPORTS, SETTINGS, AND CONSTANTS -------------------------------------------
# 1 - Standard library imports
import math

# 2 - Third-party imports

# 3 - Application-specific imports
from .randomizer_functions import get_weighted_random
from . import player_roles

# 4 - Global settings

# 5 - Global constants


# ----------------------------------------------------- SECTION 2 -----------------------------------------------------
# ------------------------------------------------ Class Declarations -------------------------------------------------


# ----------------------------------------------------- SECTION 3 -----------------------------------------------------
# ------------------------------------------------- Helper Functions --------------------------------------------------


# ----------------------------------------------------- SECTION 4 -----------------------------------------------------
# ------------------------------------------------ Main Functionality -------------------------------------------------

def create_fullback(self, player_dict, index):
    """
    Given a dictionary of a new player and the index of the related record to modify in the DB, performs all of 
    the calculations and updates necessary to create the player as a FB in the DB.
    """
    
    position = 2 # FB
    
    # For all of the following fields, we simply use 0.
    # PCPH, PFHO, PJTY, PMUS, PSTM, PSTY, PSXP, PTSL, PUCL, TLEL, TLHA, TLWR, TREL, TRHA, TRWR 
    self.set_player_integer_field('PCPH', index, 0)
    self.set_player_integer_field('PFHO', index, 0)
    self.set_player_integer_field('PJTY', index, 0)
    self.set_player_integer_field('PMUS', index, 0)
    self.set_player_integer_field('PSTM', index, 0)
    self.set_player_integer_field('PSTY', index, 0)
    self.set_player_integer_field('PSXP', index, 0)
    self.set_player_integer_field('PTSL', index, 0)
    self.set_player_integer_field('PUCL', index, 0)
    self.set_player_integer_field('TLEL', index, 0)
    self.set_player_integer_field('TLHA', index, 0)
    self.set_player_integer_field('TLWR', index, 0)
    self.set_player_integer_field('TREL', index, 0)
    self.set_player_integer_field('TRHA', index, 0)
    self.set_player_integer_field('TRWR', index, 0)
    
    # PCMT gets 999, PJER gets a 1, PLHY gets -31, PLPL gets 100, and PPTI will always get 1009.
    self.set_player_integer_field('PCMT', index, 999)
    self.set_player_integer_field('PJER', index, 1)
    self.set_player_integer_field('PLHY', index, -31)
    self.set_player_integer_field('PLPL', index, 100)
    self.set_player_integer_field('POPS', index, position)
    self.set_player_integer_field('PPOS', index, position)
    self.set_player_integer_field('PPTI', index, 1009)
    
    # For many attributes in 'Latest Player Attributes.csv', we simply use the exact value from the file.
    self.set_player_integer_field('PAGE', index, int(player_dict["age"]))
    contract_length = int(player_dict["contract_length"])
    self.set_player_integer_field('PCON', index, contract_length)
    self.set_player_integer_field('PCYL', index, int(player_dict["contract_years_left"]))
    draft_pick = int(player_dict["draft_pick"])
    self.set_player_integer_field('PDPI', index, draft_pick)
    draft_round = int(player_dict["draft_round"])
    self.set_player_integer_field('PDRO', index, draft_round)
    self.set_player_integer_field('PFPB', index, int(player_dict["pro_bowl"]))
    self.set_player_integer_field('PHED', index, int(player_dict["hair_style"]))
    self.set_player_integer_field('PHCL', index, int(player_dict["hair_color"]))
    self.set_player_integer_field('PHGT', index, int(player_dict["height"]))
    self.set_player_integer_field('PICN', index, int(player_dict["nfl_icon"]))
    self.set_player_integer_field('PJEN', index, int(player_dict["jersey_number"]))
    self.set_player_integer_field('PSKI', index, int(player_dict["skin_color"]))
    self.set_player_integer_field('PTAL', index, int(player_dict["tattoo_left"]))
    self.set_player_integer_field('PTAR', index, int(player_dict["tattoo_right"]))
    self.set_player_integer_field('PVCO', index, contract_length)
    years_pro = int(player_dict["years_pro"])
    self.set_player_integer_field('PYRP', index, years_pro)
    # This is correct - we are intentionally setting the years with team to the number of years pro.
    self.set_player_integer_field('PYWT', index, years_pro)
    
    
    # For these next attributes, the calculations involve the value from a column in the player dict.
    
    # PBRE: If the value in the CSV is -1, give 70% a 0 (none), 20% a 1 (white), and 10% a 2 (black).
    if int(player_dict["breathing_strip"]) == -1:
        elements = [0, 1, 2]
        weights = [70, 20, 10]
        breathing_strip = get_weighted_random(elements, weights)
    else:
        breathing_strip = int(player_dict["breathing_strip"])
    self.set_player_integer_field('PBRE', index, breathing_strip)
    
    # The college ID is simply picked from a list.
    self.set_player_integer_field('PCOL', index, self.get_college_id(player_dict["college"]))
    
    # For eye_black, if the CSV says -1, give 70% a 0 (none) and 30% a 1 (black).
    if int(player_dict["eye_black"]) == -1:
        elements = [0, 1]
        weights = [70, 30]
        eye_black = get_weighted_random(elements, weights)
    else:
        eye_black = int(player_dict["eye_black"])
    self.set_player_integer_field('PEYE', index, eye_black)
    
    # For face_id, if the CSV says -1, pick a random value between 2 and 518.
    if int(player_dict["face_id"]) == -1:
        elements = list(range(2, 519))
        weights = [100/517]*517
        face_id = get_weighted_random(elements, weights)
    else:
        face_id = int(player_dict["face_id"])
    self.set_player_integer_field('PFEx', index, face_id)
    
    # If the value in the CSV is -1, set 10% to 1 (3-bar), 5% to 3 (full-cage), 10% to 7 (2-Bar RB), 40% to 8 (3-Bar 
    # RB), 15% to 9 (RB Robots),  10% to 10 (RB Bull), and 10% to 11. NOTE: If choosing 11, must also set PHLM to 4 !!
    if int(player_dict["face_mask"]) == -1:
        elements = [1, 3, 7, 8, 9, 10, 11]
        weights = [10, 5, 10, 40, 15, 10, 10]
        face_mask = get_weighted_random(elements, weights)
    else:
        face_mask = int(player_dict["face_mask"])
    self.set_player_integer_field('PFMK', index, face_mask)
    
    # Get the first 11 characters of the first name.
    if len(player_dict["first_name"]) < 12:
        self.set_player_string_field('PFNA', index, player_dict["first_name"])
    else:
        self.set_player_string_field('PFNA', index, player_dict["first_name"][:11])
    
    # The handedness is 0 for right, 1 for left.
    if "RIGHT" in player_dict["handedness"].upper():
        handedness = 0
    else:
        handedness = 1
    self.set_player_integer_field('PHAN', index, handedness)
    
    # For left_elbow, if the value in the CSV is -1, set 40% to 0 (none), 20% to 1 (turf tape), 5% to 2 (rubber pad), 
    # 15% to 7 (black wrist), and 15% to 8 (white wrist), and 5% to 9 (team-color wrist).
    if int(player_dict["left_elbow"]) == -1:
        elements = [0, 1, 2, 7, 8, 9]
        weights = [40, 20, 5, 15, 15, 5]
        left_elbow = get_weighted_random(elements, weights)
    else:
        left_elbow = int(player_dict["left_elbow"])
    self.set_player_integer_field('PLEL', index, left_elbow)
    
    # For left_hand, if the value in the CSV is -1, set 20% to 0 (none), 20% to 2 (black gloves), 10% to 3 (white 
    # gloves), 10% to 4 (team-color gloves), 10% to 5 (white RB gloves), 15% to 6 (black RB gloves), and 15% to 7 
    # (team-color RB gloves).
    if int(player_dict["left_hand"]) == -1:
        elements = [0, 2, 3, 4, 5, 6, 7]
        weights = [20, 20, 10, 10, 10, 15, 15]
        left_hand = get_weighted_random(elements, weights)
    else:
        left_hand = int(player_dict["left_hand"])
    self.set_player_integer_field('PLHA', index, left_hand)
    
    # Get the first 13 characters of the last name.
    if len(player_dict["last_name"]) < 14:
        self.set_player_string_field('PLNA', index, player_dict["last_name"])
    else:
        self.set_player_string_field('PLNA', index, player_dict["last_name"][:13])
    
    # For left_shoe, if the value in the CSV is -1, set 80% to 0 (none) and 20% to 1 (white tape).
    if int(player_dict["left_shoe"]) == -1:
        elements = [0, 1]
        weights = [80, 20]
        left_shoe = get_weighted_random(elements, weights)
    else:
        left_shoe = int(player_dict["left_shoe"])
    self.set_player_integer_field('PLSH', index, left_shoe)
    
    # For left_knee, if the value in the CSV is -1, just use 0 (none). Otherwise, go with the value in the file.
    if int(player_dict["left_knee"]) == -1:
        left_knee = 0
    else:
        left_knee = int(player_dict["left_knee"])
    self.set_player_integer_field('PLTH', index, left_knee)
    
    # For left_wrist, set 60% to 0 (Normal), 15% to 2 (White wrist), 15% to 3 (Black wrist), and 10% to 4 (Team-color 
    # wrist).
    if int(player_dict["left_wrist"]) == -1:
        elements = [0, 2, 3, 4]
        weights = [60, 15, 15, 10]
        left_wrist = get_weighted_random(elements, weights)
    else:
        left_wrist = int(player_dict["left_wrist"])
    self.set_player_integer_field('PLWR', index, left_wrist)
    
    # For mouthpiece, give 60% of players 0 (none), 20% 1 (white), 10% 2 (black), and 10% 3 (team-color).
    if int(player_dict["mouthpiece"]) == -1:
        elements = [0, 1, 2, 3]
        weights = [60, 20, 10, 10]
        mouthpiece = get_weighted_random(elements, weights)
    else:
        mouthpiece = int(player_dict["mouthpiece"])
    self.set_player_integer_field('PMPC', index, mouthpiece)
    
    # For neck_pad, if the value in the CSV is -1, set 80% to 0 (none) and 20% to 1 (neck roll).
    if int(player_dict["neck_pad"]) == -1:
        elements = [0, 1]
        weights = [80, 20]
        neck_pad = get_weighted_random(elements, weights)
    else:
        neck_pad = int(player_dict["neck_pad"])
    self.set_player_integer_field('PNEK', index, neck_pad)
    
    # For right_elbow, if the value in the CSV is -1: If PLEL was 0, set 60% to 0, and 10% to each of 2, 7, 8, and 9. 
    # If PLEL was 1, set 100% to 1. If it was an other non-zero, value set 80% to the same value, and 20% to 0.
    if int(player_dict["right_elbow"]) == -1:
        if left_elbow == 0:
            elements = [0, 2, 7, 8, 9]
            weights = [60, 10, 10, 10, 10]
            right_elbow = get_weighted_random(elements, weights)
        elif left_elbow == 1:
            right_elbow = 1
        else:
            elements = [left_elbow, 0]
            weights = [80, 20]
            right_elbow = get_weighted_random(elements, weights)
    else:
        right_elbow = int(player_dict["right_elbow"])
    self.set_player_integer_field('PREL', index, right_elbow)
    
    # For right_hand, just use the same value as PLHA.
    right_hand = left_hand
    self.set_player_integer_field('PRHA', index, right_hand)
    
    # For right_shoe, if the CSV says -1, just match it to the left_shoe.
    if int(player_dict["right_shoe"]) == -1:
        right_shoe = left_shoe
    else:
        right_shoe = int(player_dict["right_shoe"])
    self.set_player_integer_field('PRSH', index, right_shoe)
    
    # For right_knee, if the CSV says -1, always use 0. Otherwise, just use what is in the file.
    if int(player_dict["right_knee"]) == -1:
        right_knee = 0
    else:
        right_knee = int(player_dict["right_knee"])
    self.set_player_integer_field('PRTH', index, right_knee)
    
    # For right_wrist, just use the same value as PLWR.
    right_wrist = left_wrist
    self.set_player_integer_field('PRWR', index, right_wrist)
    
     # For visor, if the value in the CSV is -1, set 60% to 0 (none), 25% to 1 (clear), 10% to 2 (dark), and 5% to 3 
     # (amber).
    if int(player_dict["visor"]) == -1:
        elements = [0, 1, 2, 3]
        weights = [60, 25, 10, 5]
        visor = get_weighted_random(elements, weights)
    else:
        visor = int(player_dict["visor"])
    self.set_player_integer_field('PVIS', index, visor)
    
    # Subtract 160 from the players weight, unless he is already under 160.
    if int(player_dict["weight"]) > 159:
        self.set_player_integer_field('PWGT', index, (int(player_dict["weight"]) - 160))
    else:
        self.set_player_integer_field('PWGT', index, 0)
    
    # The team ID is simply picked from a list.
    self.set_player_integer_field('TGID', index, self.get_team_id(player_dict["team"]))
    
    
    # Here is where we set the main attributes used by this position. See the file 'Methods for Setting Field 
    # Values.xlsx' for details on the calculations used.
    
    if player_dict["speed"]:
        speed = int(max(min(int(player_dict["speed"]), 95), 60))
    else:
        # A random distribution from 70 to 83, where the most likely values are 72 - 76.
        elements = list(range(70, 84))
        weights = [3, 5, 11, 12, 12, 12, 10, \
                   9, 8, 7, 5, 3, 2, 1]
        speed = get_weighted_random(elements, weights)
    self.set_player_integer_field('PSPD', index, speed)
    
    if player_dict["strength"]:
        strength = int(max(min(int(player_dict["strength"]), 95), 60))
    else:
        # A random distribution from 65 to 85, where the most likely values are 69 - 72.
        elements = list(range(65, 86))
        weights = [1, 2, 6, 9, 11, 11, 11, \
                   11, 9, 7, 6, 4, 3, 2, \
                   1, 1, 1, 1, 1, 1, 1]
        strength = get_weighted_random(elements, weights)
    self.set_player_integer_field('PSTR', index, strength)
    
    if player_dict["awareness"]:
        awareness = int(max(min(int(player_dict["awareness"]), 99), 45))
    else:
        # A random distribution from 45 to 65, where the most likely values are 45 - 48.
        elements = list(range(45, 66))
        weights = [10, 10, 10, 9, 9, 8, 7, \
                   7, 6, 5, 4, 3, 3, 2, \
                   1, 1, 1, 1, 1, 1, 1]
        awareness = get_weighted_random(elements, weights)
    self.set_player_integer_field('PAWR', index, awareness)
    
    if player_dict["agility"]:
        agility = int(max(min(int(player_dict["agility"]), 95), 55))
    else:
        # A random distribution from 65 to 85, where the most likely values are 69 - 73.
        elements = list(range(65, 86))
        weights = [1, 2, 4, 7, 9, 10, 10, \
                   10, 9, 8, 7, 6, 5, 4, \
                   2, 1, 1, 1, 1, 1, 1]
        agility = get_weighted_random(elements, weights)
    self.set_player_integer_field('PAGI', index, agility)
    
    if player_dict["acceleration"]:
        acceleration = int(max(min(int(player_dict["acceleration"]), 95), 65))
    else:
        # A random distribution from 70 to 88, where the most likely values are 76 - 79.
        elements = list(range(70, 89))
        weights = [1, 1, 2, 4, 6, 8, 10, 10, 10, 10, \
                   9, 8, 7, 5, 4, 2, 1, 1, 1]
        acceleration = get_weighted_random(elements, weights)
    self.set_player_integer_field('PACC', index, acceleration)
    
    if player_dict["carrying"]:
        carrying = int(max(min(int(player_dict["carrying"]), 99), 60))
    else:
        # A random distribution from 66 to 85, where the most likely values are 65 - 69.
        elements = list(range(66, 86))
        weights = [6, 8, 10, 12, 13, 12, \
                   10, 8, 6, 4, 2, 1, 1, \
                   1, 1, 1, 1, 1, 1, 1]
        carrying = get_weighted_random(elements, weights)
    self.set_player_integer_field('PCAR', index, carrying)
    
    if player_dict["catching"]:
        catching = int(max(min(int(player_dict["catching"]), 95), 45))
    else:
        # A random distribution from 48 to 70, where the most likely values are 50 - 52.
        elements = list(range(48, 71))
        weights = [5, 8, 11, 11, 11, 11, 9, \
                   8, 6, 4, 3, 2, 1, 1, 1, \
                   1, 1, 1, 1, 1, 1, 1, 1]
        catching = get_weighted_random(elements, weights)
    self.set_player_integer_field('PCTH', index, catching)
    
    if player_dict["jumping"]:
        jumping = int(max(min(int(player_dict["jumping"]), 95), 55))
    else:
        # A random distribution from 60 to 90, where the most likely values are 65 - 78.
        elements = list(range(60, 91))
        weights = [1, 1, 2, 3, 4, 5, 5, 5, 5, 5, 5, \
                   5, 5, 5, 5, 5, 5, 5, 5, 4, 3, \
                   2, 2, 1, 1, 1, 1, 1, 1, 1, 1]
        jumping = get_weighted_random(elements, weights)
    self.set_player_integer_field('PJMP', index, jumping)
    
    if player_dict["elusiveness"] and player_dict["trucking"]:
        break_tackles = int(max(min(
            (math.ceil((int(player_dict["elusiveness"]) + int(player_dict["trucking"])) / 2) + 5), 
            99), 55))
    else:
        # A random distribution from 57 to 78, where the most likely values are 62 - 66.
        elements = list(range(57, 79))
        weights = [1, 2, 4, 6, 8, 10, 10, 11, \
                   10, 10, 8, 6, 4, 2, 1, \
                   1, 1, 1, 1, 1, 1, 1]
        break_tackles = get_weighted_random(elements, weights)
    self.set_player_integer_field('PBTK', index, break_tackles)
    
    if player_dict["tackle"]:
        tackle = int(max(min(int(player_dict["tackle"]), 85), 30))
    else:
        # A random distribution from 35 to 75, where the most likely values are 38 - 47.
        elements = list(range(35, 76))
        weights = [3, 3, 4, 5, 5, 5, 5, 5, 5, 5, 5, \
                   5, 5, 4, 4, 3, 3, 2, 2, 1, 1, \
                   1, 1, 1, 1, 1, 1, 1, 1, 1, 1, \
                   1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        tackle = get_weighted_random(elements, weights)
    self.set_player_integer_field('PTAK', index, tackle)
    
    if player_dict["throw_power"]:
        throw_power = int(max(min(int(player_dict["throw_power"]) + 5, 80), 20))
    else:
        # A random distribution from 20 to 60, where the most likely values are 24 - 35.
        elements = list(range(20, 61))
        weights = [1, 2, 3, 4, 5, 5, 5, 5, 5, 5, 5, \
                   5, 5, 5, 5, 5, 4, 3, 1, 1, 1, \
                   1, 1, 1, 1, 1, 1, 1, 1, 1, 1, \
                   1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        throw_power = get_weighted_random(elements, weights)
    self.set_player_integer_field('PTHP', index, throw_power)
    
    if (player_dict["throw_accuracy_short"] and player_dict["throw_accuracy_mid"] 
            and player_dict["throw_accuracy_deep"] and player_dict["throw_on_the_run"] and player_dict["playaction"]):
        throw_accuracy = int(max(min(math.ceil(
            ((2 * (
                int(player_dict["throw_accuracy_short"]) + 
                int(player_dict["throw_accuracy_mid"]) + 
                int(player_dict["throw_accuracy_deep"]) + 
                int(player_dict["throw_on_the_run"]) + 
                int(player_dict["playaction"])
            )
             ) - min(
                 int(player_dict["throw_accuracy_short"]), 
                 int(player_dict["throw_accuracy_mid"]), 
                 int(player_dict["throw_accuracy_deep"]), 
                 int(player_dict["throw_on_the_run"]), 
                 int(player_dict["playaction"])
             )
            ) / 9
        ) + 10, 80), 15))
    else:
        # A random distribution from 20 to 65, where the most likely values are 20 - 29.
        elements = list(range(20, 66))
        weights = [5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 4, 4, 3, 3, 2, 2, \
                   2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, \
                   1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        throw_accuracy = get_weighted_random(elements, weights)
    self.set_player_integer_field('PTHA', index, throw_accuracy)
    
    if player_dict["pass_block"] and player_dict["pass_block_power"] and player_dict["pass_block_finesse"]:
        pass_block = int(max(min(math.ceil(
            (
                int(player_dict["pass_block"]) + 
                int(player_dict["pass_block_power"]) + 
                int(player_dict["pass_block_finesse"])
            ) / 3
        ), 75), 40))
    else:
        # A random distribution from 40 to 60, where the most likely values are 40 - 48.
        elements = list(range(40, 61))
        weights = [6, 7, 8, 8, 9, 9, 9, \
                   8, 8, 6, 5, 4, 3, 2, \
                   2, 1, 1, 1, 1, 1, 1]
        pass_block = get_weighted_random(elements, weights)
    self.set_player_integer_field('PPBK', index, pass_block)
    
    if player_dict["run_block"] and player_dict["run_block_power"] and player_dict["run_block_finesse"]:
        run_block = int(max(min(math.ceil(
            (
                int(player_dict["run_block"]) + 
                int(player_dict["run_block_power"]) + 
                int(player_dict["run_block_finesse"])
            ) / 3
        ), 85), 45))
    else:
        # A random distribution from 45 to 65, where the most likely values are 45 - 53.
        elements = list(range(45, 66))
        weights = [8, 9, 10, 11, 10, 9, 8, \
                   7, 6, 5, 4, 3, 2, 1, \
                   1, 1, 1, 1, 1, 1, 1]
        run_block = get_weighted_random(elements, weights)
    self.set_player_integer_field('PRBK', index, run_block)
    
    if player_dict["kick_power"]:
        kick_power = int(max(min(int(player_dict["kick_power"]), 45), 10))
    else:
        # A random distribution from 10 to 40, where the most likely values are 15 - 20.
        elements = list(range(10, 41))
        weights = [2, 3, 4, 5, 6, 7, 7, 7, 7, 7, 7, \
                   6, 5, 4, 3, 3, 2, 2, 1, 1, 1, \
                   1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        kick_power = get_weighted_random(elements, weights)
    self.set_player_integer_field('PKPR', index, kick_power)
    
    if player_dict["kick_accuracy"]:
        kick_accuracy = int(max(min(int(player_dict["kick_accuracy"]), 40), 5))
    else:
        # A random distribution from 5 to 35, where the most likely values are 10 - 15.
        elements = list(range(5, 36))
        weights = [2, 3, 4, 5, 6, 7, 7, 7, 7, 7, 7, \
                   6, 5, 4, 3, 3, 2, 2, 1, 1, 1, \
                   1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        kick_accuracy = get_weighted_random(elements, weights)
    self.set_player_integer_field('PKAC', index, kick_accuracy)
    
    if player_dict["kick_return"]:
        kick_return = int(max(min(int(player_dict["kick_return"]), 85), 15))
    else:
        # A random distribution from 15 to 65, where the most likely values are 15 - 25.
        elements = list(range(15, 66))
        weights = [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, \
                   3, 3, 3, 3, 3, 2, 2, 2, 2, 2, \
                   2, 1, 1, 1, 1, 1, 1, 1, 1, 1, \
                   1, 1, 1, 1, 1, 1, 1, 1, 1, 1, \
                   1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        kick_return = get_weighted_random(elements, weights)
    self.set_player_integer_field('PKRT', index, kick_return)
    
    if player_dict["stamina"]:
        stamina = int(max(min(int(player_dict["stamina"]), 99), 70))
    else:
        # A random distribution from 80 to 90, where the most likely values are 81 - 85.
        elements = list(range(80, 91))
        weights = [5, 14, 14, 14, 14, 14, 10, 7, 5, 2, 1]
        stamina = get_weighted_random(elements, weights)
    self.set_player_integer_field('PSTA', index, stamina)
    
    if player_dict["injury"]:
        injury = int(max(min(int(player_dict["injury"]), 99), 65))
    else:
        # A random distribution from 75 to 95, where the most likely values are 83 - 90.
        elements = list(range(75, 96))
        weights = [2, 2, 3, 3, 4, 4, 5, \
                   5, 7, 7, 7, 7, 7, 7, \
                   7, 7, 5, 4, 3, 2, 2]
        injury = get_weighted_random(elements, weights)
    self.set_player_integer_field('PINJ', index, injury)
    
    if player_dict["toughness"]:
        toughness = int(max(min(int(player_dict["toughness"]), 99), 60))
    else:
        # A random distribution from 65 to 95, where the most likely values are 75 - 84.
        elements = list(range(65, 96))
        weights = [1, 1, 1, 1, 1, 1, 2, 3, 4, 5, 6, \
                   6, 6, 6, 6, 6, 6, 6, 6, 6, 5, \
                   4, 3, 1, 1, 1, 1, 1, 1, 1, 1]
        toughness = get_weighted_random(elements, weights)
    self.set_player_integer_field('PTGH', index, toughness)
    
    
    # For the following attributes, we will use weighted random distributions or other non-dependant means without 
    # checking the CSV file at all.
    
    # PCHS: A random distribution from 0 to 50, where the most likely value is 15 and the least likely is 50.
    elements = list(range(0, 51))
    weights = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, \
               2, 2, 3, 5, 8, 11, 8, 5, 3, 2, \
               2, 2, 2, 2, 2, 2, 2, 2, 2, 2, \
               1, 1, 1, 1, 1, 1, 1, 1, 1, 1, \
               1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    chest_shelf = get_weighted_random(elements, weights)
    self.set_player_integer_field('PCHS', index, chest_shelf)
    
    # PEGO: Set 5% to 0, 10% to something btwn 1 - 20, 5% to btwn 21 - 40, 5% to btwn 41 - 50, 20% to btwn 51 - 60, 
    # 25% to btwn 61 - 80, 20% to btwn 81 - 90, and 10% to btwn 91 - 99.
    elements = list(range(0, 100))
    weights = [5.0] + [0.5]*20 + [.25]*20 + [.5]*10 + [2.0]*10 + [1.25]*20 + [2.0]*10 + [1.1111]*9
    ego = get_weighted_random(elements, weights)
    self.set_player_integer_field('PEGO', index, ego)
    
    # PFAS: A random distribution from 0 to 20, where the most likely value is 5 and the least likely is 20.
    elements = list(range(0, 21))
    weights = [3, 5, 6, 8, 11, 16, 11, 8, 6, 5, 4, 3, 3, 2, 2, 2, 1, 1, 1, 1, 1]
    arm_fat = get_weighted_random(elements, weights)
    self.set_player_integer_field('PFAS', index, arm_fat)
    
    # PFCS: A random distribution from 0 to 25, where the most likely value is 5 and the least likely is 25.
    elements = list(range(0, 26))
    weights = [1, 2, 4, 6, 8, 10, 9, 8, 7, 6, 6, 5, 4, \
               3, 3, 3, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1]
    calf_fat = get_weighted_random(elements, weights)
    self.set_player_integer_field('PFCS', index, calf_fat)
    
    # PFGS: A random distribution from 0 to 40, where the most likely value is 15 and the least likely is 40.
    elements = list(range(0, 41))
    weights = [1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 3, \
               3, 4, 6, 7, 9, 7, 6, 4, 3, 3, \
               3, 2, 2, 2, 2, 2, 2, 2, 2, 2, \
               1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    glute_fat = get_weighted_random(elements, weights)
    self.set_player_integer_field('PFGS', index, glute_fat)
    
    # PFHS: A random distribution from 0 to 40, where the most likely value is 15 and the least likely is 40.
    elements = list(range(0, 41))
    weights = [1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 3, \
               3, 4, 6, 7, 9, 7, 6, 4, 3, 3, \
               3, 2, 2, 2, 2, 2, 2, 2, 2, 2, \
               1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    thigh_fat = get_weighted_random(elements, weights)
    self.set_player_integer_field('PFHS', index, thigh_fat)
    
    # PFTS: A random distribution from 0 to 35, where the most likely value is 8 and the least likely is 35.
    elements = list(range(0, 36))
    weights = [1, 1, 1, 1, 1, 2, 3, 8, 13, 10, 7, 5, 4, 4, 4, 3, 3, 3, \
               3, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    torso_fat = get_weighted_random(elements, weights)
    self.set_player_integer_field('PFTS', index, torso_fat)
    
    # PGID: Try starting with 0 and simply incrementing the count with each player. If altering these causes any 
    # problems, try just leaving the value as it was in the default roster.
    self.set_player_integer_field('PGID', index, index)
    
    # PLSS: A random distribution from 5 to 45, where the most likely value is 20 and the least likely is 45.
    elements = list(range(5, 46))
    weights = [1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 3, \
               3, 4, 6, 7, 9, 7, 6, 4, 3, 3, \
               3, 2, 2, 2, 2, 2, 2, 2, 2, 2, \
               1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    shoe_length = get_weighted_random(elements, weights)
    self.set_player_integer_field('PLSS', index, shoe_length)
    
    # PMAS: A random distribution from 0 to 45, where the most likely value is 15 and the least likely are 0 and 45.
    elements = list(range(0, 46))
    weights = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 3, 5, 7, 11, \
               8, 6, 4, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2, 2, \
               1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    arm_muscle = get_weighted_random(elements, weights)
    self.set_player_integer_field('PMAS', index, arm_muscle)
    
    # PMCS: A random distribution from 0 to 55, where the most likely value is 20 and the least likely are 0 and 55.
    elements = list(range(0, 56))
    weights = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, \
               2, 2, 2, 2, 3, 6, 10, 7, 5, 3, 3, 2, 2, 2, \
               2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, \
               1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    calf_muscle = get_weighted_random(elements, weights)
    self.set_player_integer_field('PMCS', index, calf_muscle)
    
    # PMHS: A random distribution from 0 to 65, where the most likely value is 20 and the least likely are 0 and 65.
    elements = list(range(0, 66))
    weights = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, \
               1, 2, 3, 5, 10, 6, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2, \
               1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, \
               1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    thigh_muscle = get_weighted_random(elements, weights)
    self.set_player_integer_field('PMHS', index, thigh_muscle)
    
    # PMOR: Set 20% to between 50 - 79, 20% to 80 - 89, and 60% to 90 - 99.
    elements = list(range(50, 80)) + list(range(80, 90)) + list(range(90, 100))
    weights = [2/3]*30 + [2]*10 + [6]*10
    morale = get_weighted_random(elements, weights)
    self.set_player_integer_field('PMOR', index, morale)
    
    # PMTS: A random distribution from 0 to 30, where the most likely value is 10 and the least likely is 30.
    elements = list(range(0, 31))
    weights = [1, 1, 1, 2, 2, 3, 3, 5, 7, 10, 13, 10, 7, 5, 3, 3, \
               3, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1]
    mid_torso = get_weighted_random(elements, weights)
    self.set_player_integer_field('PMTS', index, mid_torso)
    
    # POID: Just set this to the same number as PGID.
    self.set_player_integer_field('POID', index, index)
    
    # PSBS: A random distribution from 29 to 94, where the most likely value is 69 (to result in a Body Overall Size 
    # of 30), and the least likely is 29 (Overall = 70).
    elements = list(range(29, 95))
    weights = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, \
               1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, \
               1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, \
               2, 2, 2, 3, 3, 4, 6, 10, 4, 2, 2, \
               2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, \
               1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    subtract_for_body_size = get_weighted_random(elements, weights)
    self.set_player_integer_field('PSBS', index, subtract_for_body_size)
    
    # PUTS: A random distribution from 10 to 50, where the most likely value is 20 and the least likely is 50.
    elements = list(range(10, 51))
    weights = [1, 1, 1, 1, 2, 2, 3, 4, 6, 9, 13, \
               9, 7, 5, 3, 3, 2, 2, 2, 2, 2, \
               1, 1, 1, 1, 1, 1, 1, 1, 1, 1, \
               1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    upper_torso = get_weighted_random(elements, weights)
    self.set_player_integer_field('PUTS', index, upper_torso)
    
    
    # These calculations use the results of previous calculations.
    
    # PTEN: If the CSV is -1, use the FB's pass_block, run_block, and catching attributes to determine his tendency.
    if int(player_dict["tendency"]) == -1:
        # If the FB has enough catching ability, call him a receiving back.
        if catching > 67:
            tendency = 1 # receiving
        # Otherwise, if the FB has enough overall blocking ability, call him a blocking back.
        elif (pass_block > 67 and run_block > 57) or (pass_block > 57 and run_block > 67) or catching < 57:
            tendency = 0 # blocking
        else:
            tendency = 2 # balanced
    else:
        tendency = int(player_dict["tendency"])
    self.set_player_integer_field('PTEN', index, tendency)
    
    # PHLM: Check the value from PFMK. If it was set to 13, we must use 4. Otherwise, see what is in the CSV. If it is 
    # -1, give 75% a 0 (Style 1) and 25% a 2 (Style 3).
    if face_mask == 13:
        helmet = 4
    elif int(player_dict["helmet"]) == -1:
        elements = [0, 2]
        weights = [75, 25]
        helmet = get_weighted_random(elements, weights)
    else:
        helmet = int(player_dict["helmet"])
    self.set_player_integer_field('PHLM', index, helmet)
    
    # PGSL: If the CSV has -1 and we didn't set PLEL, PREL, PTAL, or PTAR to anything but 0, set 80% to 0 (none), 3% 
    # to 1 (black), 5% to 2 (white), 3% to 3 (team-color), 3% to 4 (white half), 3% to 5 (black half), and 3% to 6 
    # (team-color half).
    if int(player_dict["sleeves"]) == -1:
        if (left_elbow == 0 and 
                right_elbow == 0 and 
                int(player_dict["tattoo_left"]) == 0 and 
                int(player_dict["tattoo_right"]) == 0):
            elements = [0, 1, 2, 3, 4, 5, 6]
            weights = [80, 3, 5, 3, 3, 3, 3]
            sleeves = get_weighted_random(elements, weights)
        else:
            sleeves = 0
    else:
        sleeves = int(player_dict["sleeves"])
    self.set_player_integer_field('PGSL', index, sleeves)
    
    # Use the formula found in 04 - FORMULA for Calculating Overall Rating.txt
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
    self.set_player_integer_field('POVR', index, overall_rating)
    
    # PIMP: We're relating the importance of a player to his overall rating and his position. FBs should be fairly 
    # unimportant, so use the following:  int(max(min(ceil((([POVR]/100)^2) * 70) + ([POVR] - 75), 99), 15))
    importance = int(max(min(math.ceil((math.pow((overall_rating / 100), 2) * 70) + (overall_rating - 75)), 99), 15))
    self.set_player_integer_field('PIMP', index, importance)
    
    # PROL: Check for these roles IN THIS ORDER: 1) injury_prone, 2) team_distraction, 3) underachiever, 4) 
    # fumble_prone, 5) road_blocker, 6) run_blocker, 7) pass_blocker 8) project_player, 9) fan_favorite 10) 
    # team_mentor 11) team_leader 12) first_round_pick.
    role_one = int(player_dict["role_one"])
    if role_one == 45:
        if player_roles.is_injury_prone(role_one, injury, toughness):
            role_one = 14
        elif player_roles.is_team_distraction(role_one, morale, importance):
            role_one = 8
        elif player_roles.is_underachiever(role_one, draft_round, draft_pick, years_pro, overall_rating):
            role_one = 4
        elif player_roles.is_fumble_prone(role_one, carrying):
            role_one = 15
        elif player_roles.is_road_blocker(role_one, position, run_block, pass_block):
            role_one = 26
        elif player_roles.is_run_blocker(role_one, position, run_block):
            role_one = 24
        elif player_roles.is_pass_blocker(role_one, position, pass_block):
            role_one = 25
        elif player_roles.is_project_player(role_one, overall_rating, years_pro, awareness, position, throw_power, 
                                            throw_accuracy, speed, acceleration, break_tackles, agility, strength, 
                                            kick_power):
            role_one = 7
        elif player_roles.is_fan_favorite(role_one, years_pro, morale, overall_rating):
            role_one = 13
        elif player_roles.is_team_mentor(role_one, position, awareness, morale, years_pro, overall_rating):
            role_one = 5
        elif player_roles.is_team_leader(role_one, position, awareness, morale, years_pro, overall_rating):
            role_one = 6
        elif player_roles.is_first_round_pick(role_one, draft_round):
            role_one = 12
    self.set_player_integer_field('PROL', index, role_one)
    
    # PRL2: Check for these roles IN THIS ORDER: 1) injury_prone 2) team_distraction 3) franchise_qb 
    # 4) qb_of_the_future 5) project_player 6) underachiever 7) precision_passer 8) cannon_arm 9) scrambler 
    # 10) game_manager 11) fan_favorite 12) team_mentor 13) team_leader 14) first_round_pick .
    role_two = int(player_dict["role_two"])
    if role_two == 45 and role_one != 45:
        if player_roles.is_injury_prone(role_one, injury, toughness):
            role_two = 14
        elif player_roles.is_team_distraction(role_one, morale, overall_rating):
            role_two = 8
        elif player_roles.is_underachiever(role_one, draft_round, draft_pick, years_pro, overall_rating):
            role_two = 4
        elif player_roles.is_fumble_prone(role_one, carrying):
            role_two = 15
        elif player_roles.is_road_blocker(role_one, position, run_block, pass_block):
            role_two = 26
        elif player_roles.is_run_blocker(role_one, position, run_block):
            role_two = 24
        elif player_roles.is_pass_blocker(role_one, position, pass_block):
            role_two = 25
        elif player_roles.is_project_player(role_one, overall_rating, years_pro, awareness, position, throw_power, 
                                            throw_accuracy, speed, acceleration, break_tackles, agility, strength, 
                                            kick_power):
            role_two = 7
        elif player_roles.is_fan_favorite(role_one, years_pro, morale, overall_rating):
            role_two = 13
        elif player_roles.is_team_mentor(role_one, position, awareness, morale, years_pro, overall_rating):
            role_two = 5
        elif player_roles.is_team_leader(role_one, position, awareness, morale, years_pro, overall_rating):
            role_two = 6
        elif player_roles.is_first_round_pick(role_one, draft_round):
            role_two = 12
    self.set_player_integer_field('PRL2', index, role_two)
    
    # PTSA & PVTS: Use the formula for this year to reduce actual salary and bonus numbers by certain ratios to 
    # account for inflation.
    total_salary = int(player_dict["total_salary"])
    if total_salary > 10000000:
        total_salary = round((total_salary / 10000) * self.get_salary_adjustment("first"))
    elif total_salary > 1000000:
        total_salary = round((total_salary / 10000) * self.get_salary_adjustment("second"))
    else:
        total_salary = round((total_salary / 10000) * self.get_salary_adjustment("third"))
    
    self.set_player_integer_field('PTSA', index, total_salary)
    self.set_player_integer_field('PVTS', index, total_salary)
    
    # PSBO & PVSB: Use the formula for this year to reduce actual salary and bonus numbers by certain ratios to 
    # account for inflation.
    signing_bonus = int(player_dict["signing_bonus"])
    if signing_bonus > 10000000:
        signing_bonus = round((signing_bonus / 10000) * self.get_bonus_adjustment("first"))
    elif signing_bonus > 1000000:
        signing_bonus = round((signing_bonus / 10000) * self.get_bonus_adjustment("second"))
    elif signing_bonus > 100000:
        signing_bonus = round((signing_bonus / 10000) * self.get_bonus_adjustment("third"))
    else:
        signing_bonus = round((signing_bonus / 10000) * self.get_bonus_adjustment("fourth"))
    # PSBO must always be in multiples of PCON (contract_length).
    if signing_bonus % contract_length > 0:
        signing_bonus += (contract_length - (signing_bonus % contract_length))
    
    self.set_player_integer_field('PSBO', index, signing_bonus)
    self.set_player_integer_field('PVSB', index, signing_bonus)

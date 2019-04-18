r""" _right_end.py
    
    This is one of the 21 method-definition modules used by the main RosterManager class. This module contains the 
    method used to populate the fields for a right_end record in the roster DB.
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

def create_right_end(self, player_dict, index):
    """
    Given a dictionary of a new player and the index of the related record to modify in the DB, performs all of 
    the calculations and updates necessary to create the player as a RE in the DB.
    """
    
    position = 11 # RE
    
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
    
    # PBRE: If the value in the CSV is -1, give 80% a 0 (none), 15% a 1 (white), and 5% a 2 (black).
    if int(player_dict["breathing_strip"]) == -1:
        elements = [0, 1, 2]
        weights = [80, 15, 5]
        breathing_strip = get_weighted_random(elements, weights)
    else:
        breathing_strip = int(player_dict["breathing_strip"])
    self.set_player_integer_field('PBRE', index, breathing_strip)
    
    # The college ID is simply picked from a list.
    self.set_player_integer_field('PCOL', index, self.get_college_id(player_dict["college"]))
    
    # For eye_black, if the CSV says -1, give 85% a 0 (none) and 15% a 1 (black).
    if int(player_dict["eye_black"]) == -1:
        elements = [0, 1]
        weights = [85, 15]
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
    
    # For facemask, if the value in the CSV is -1, set 15% to 2 (half-cage), 50% to 3 (full-cage), 10% to 8 (3-Bar 
    # RB), 5% to 9 (RB Robots), 10% to 10 (RB Bull), and 10% to 12. NOTE!! If choosing 12, must also set PHLM to 4 !!
    if int(player_dict["face_mask"]) == -1:
        elements = [2, 3, 8, 9, 10, 12]
        weights = [15, 50, 10, 5, 10, 10]
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
    
    # For left_elbow, if the value in the CSV is -1, set 50% to 0 (none), 15% to 2 (rubber pad), 10% to 7 (black 
    # wrist), 10% to 8 (white wrist), and 15% to 9 (team-color wrist).
    if int(player_dict["left_elbow"]) == -1:
        elements = [0, 2, 7, 8, 9]
        weights = [50, 15, 10, 10, 15]
        left_elbow = get_weighted_random(elements, weights)
    else:
        left_elbow = int(player_dict["left_elbow"])
    self.set_player_integer_field('PLEL', index, left_elbow)
    
    # For left_hand, if the value in the CSV is -1, set 35% to 0 (none), 20% to 1 (taped), 15% to 2 (black gloves), 
    # 15% to 3 (white gloves), and 15% to 4 (team-color gloves).
    if int(player_dict["left_hand"]) == -1:
        elements = [0, 1, 2, 3, 4]
        weights = [35, 20, 15, 15, 15]
        left_hand = get_weighted_random(elements, weights)
    else:
        left_hand = int(player_dict["left_hand"])
    self.set_player_integer_field('PLHA', index, left_hand)
    
    # Get the first 13 characters of the last name.
    if len(player_dict["last_name"]) < 14:
        self.set_player_string_field('PLNA', index, player_dict["last_name"])
    else:
        self.set_player_string_field('PLNA', index, player_dict["last_name"][:13])
    
    # For left_shoe, if the value in the CSV is -1, give 65% of players a 0 (none), 20% a 1 (white), 10% a 2 (black), 
    # and 5% a 3 (team-color).
    if int(player_dict["left_shoe"]) == -1:
        elements = [0, 1, 2, 3]
        weights = [65, 20, 10, 5]
        left_shoe = get_weighted_random(elements, weights)
    else:
        left_shoe = int(player_dict["left_shoe"])
    self.set_player_integer_field('PLSH', index, left_shoe)
    
    # For left_wrist, if the value in the CSV is -1, set 40% to 0 (Normal), 15% to 2 (White wrist), 10% to 3 (Black 
    # wrist), 10% to 4 (Team-color wrist), 15% to 5 (white double), 5% to 6 (black double), and 5% to 7 (team-color 
    # double).
    if int(player_dict["left_wrist"]) == -1:
        elements = [0, 2, 3, 4, 5, 6, 7]
        weights = [40, 15, 10, 10, 15, 5, 5]
        left_wrist = get_weighted_random(elements, weights)
    else:
        left_wrist = int(player_dict["left_wrist"])
    self.set_player_integer_field('PLWR', index, left_wrist)
    
    # For mouthpiece, if the value in the CSV is -1, give 70% of players 0 (none), 10% 1 (white), 10% 2 (black), and 
    # 10% 3 (team-color).
    if int(player_dict["mouthpiece"]) == -1:
        elements = [0, 1, 2, 3]
        weights = [70, 10, 10, 10]
        mouthpiece = get_weighted_random(elements, weights)
    else:
        mouthpiece = int(player_dict["mouthpiece"])
    self.set_player_integer_field('PMPC', index, mouthpiece)
    
    # For neck_pad, if the value in the CSV is -1, set 95% to 0 (none), and 5% to 1 (neckroll).
    if int(player_dict["neck_pad"]) == -1:
        elements = [0, 1]
        weights = [95, 5]
        neck_pad = get_weighted_random(elements, weights)
    else:
        neck_pad = int(player_dict["neck_pad"])
    self.set_player_integer_field('PNEK', index, neck_pad)
    
    # For right_elbow, if the value in the CSV is -1: If PLEL was 0, set 80% to 0, and 5% to each of 2, 7, 8, and 9. 
    # If PLEL was non-zero, set 80% to the same value, and 20% to 0.
    if int(player_dict["right_elbow"]) == -1:
        if left_elbow == 0:
            elements = [0, 2, 7, 8, 9]
            weights = [80, 5, 5, 5, 5]
            right_elbow = get_weighted_random(elements, weights)
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
    
    # For right_shoe, if the value in the CSV is -1: If PLSH was 0, set 85% to 0, 5% to 1, 5% to 2, and 5% to 3. If 
    # PLSH was non-zero, set 70% to the same value, and 30% to 0.
    if int(player_dict["right_shoe"]) == -1:
        if left_shoe == 0:
            elements = [0, 1, 2, 3]
            weights = [85, 5, 5, 5]
            right_shoe = get_weighted_random(elements, weights)
        else:
            elements = [left_shoe, 0]
            weights = [70, 30]
            right_shoe = get_weighted_random(elements, weights)
    else:
        right_shoe = int(player_dict["right_shoe"])
    self.set_player_integer_field('PRSH', index, right_shoe)
    
    # For right_wrist, if the value in the CSV is -1: If PLWR was 0, set 76% to 0, and 24% to one of 2, 3, 4, 5, 6, 
    # or 7. If PLWR was non-zero, set 80% to the same value, and 20% to 0.
    if int(player_dict["right_wrist"]) == -1:
        if left_wrist == 0:
            elements = [0, 2, 3, 4, 5, 6, 7]
            weights = [76, 4, 4, 4, 4, 4, 4]
            right_wrist = get_weighted_random(elements, weights)
        else:
            elements = [left_wrist, 0]
            weights = [80, 20]
            right_wrist = get_weighted_random(elements, weights)
    else:
        right_wrist = int(player_dict["right_wrist"])
    self.set_player_integer_field('PRWR', index, right_wrist)
    
     # For visor, if the value in the CSV is -1, set 85% to 0 (none) and 15% to 1 (clear).
    if int(player_dict["visor"]) == -1:
        elements = [0, 1]
        weights = [85, 15]
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
    
    de_type = -1
    
    if player_dict["speed"]:
        speed = int(max(min(int(player_dict["speed"]), 90), 55))
    else:
        # A random distribution from 59 to 86, where the most likely values are 66 - 75.
        elements = list(range(59, 87))
        weights = [1, 1, 1, 2, 3, 4, 5, 6, 6, 6, \
                   6, 6, 6, 6, 6, 6, 6, 5, 4, \
                   3, 3, 2, 1, 1, 1, 1, 1, 1]
        speed = get_weighted_random(elements, weights)
    self.set_player_integer_field('PSPD', index, speed)
    
    if player_dict["strength"]:
        strength = int(max(min(int(player_dict["strength"]), 99), 60))
    else:
        if speed > 75:
            # Pass-rushing end. Allow strength to range from 62 to 81, where the most likely values are 64 - 67.
            de_type = 0
            elements = list(range(62, 82))
            weights = [3, 7, 10, 10, 10, 10, 9, 8, 7, 6, \
                       5, 4, 3, 2, 1, 1, 1, 1, 1, 1]
        else:
            # Run-stopping end. Allow strength to range from 66 to 85, where the most likely values are 68 - 71.
            de_type = 1
            elements = list(range(66, 86))
            weights = [3, 7, 10, 10, 10, 10, 9, 8, 7, 6, \
                       5, 4, 3, 2, 1, 1, 1, 1, 1, 1]
        strength = get_weighted_random(elements, weights)
    self.set_player_integer_field('PSTR', index, strength)
    
    if player_dict["awareness"]:
        awareness = int(max(min(int(player_dict["awareness"]), 99), 40))
    else:
        # A random distribution from 40 to 56, where the most likely values are 43 - 47.
        elements = list(range(40, 57))
        weights = [4, 6, 8, 9, 9, 9, 9, 9, 8, \
                   7, 6, 5, 4, 3, 2, 1, 1]
        awareness = get_weighted_random(elements, weights)
    self.set_player_integer_field('PAWR', index, awareness)
    
    if player_dict["agility"]:
        agility = int(max(min(int(player_dict["agility"]), 90), 45))
    else:
        if de_type == 0:
            # Pass-rushing end. Allow agility to range from 63 to 82, where the most likely values are 68 - 74.
            elements = list(range(63, 83))
            weights = [1, 1, 3, 5, 7, 9, 9, 9, 9, 9, \
                       9, 9, 7, 5, 3, 1, 1, 1, 1, 1]
        else:
            # Run-stopping end. Allow agility to range from 53 to 72, where the most likely values are 58 - 64.
            elements = list(range(53, 73))
            weights = [1, 1, 3, 5, 7, 9, 9, 9, 9, 9, \
                       9, 9, 7, 5, 3, 1, 1, 1, 1, 1]
        agility = get_weighted_random(elements, weights)
    self.set_player_integer_field('PAGI', index, agility)
    
    if player_dict["acceleration"]:
        acceleration = int(max(min(int(player_dict["acceleration"]), 95), 65))
    else:
        if de_type == 0:
            # Pass-rushing end. Allow acceleration to range from 76 to 85, where the most likely values are 79 - 82.
            elements = list(range(76, 86))
            weights = [5, 8, 11, 13, 13, 13, 13, 10, 8, 6]
        else:
            # Run-stopping end. Allow acceleration to range from 72 to 81, where the most likely values are 75 - 78.
            elements = list(range(72, 82))
            weights = [5, 8, 11, 13, 13, 13, 13, 10, 8, 6]
        acceleration = get_weighted_random(elements, weights)
    self.set_player_integer_field('PACC', index, acceleration)
    
    if player_dict["carrying"]:
        carrying = int(max(min(int(player_dict["carrying"]), 75), 15))
    else:
        # A random distribution from 20 to 65, where the most likely values are 25 - 40.
        elements = list(range(20, 66))
        weights = [2, 2, 2, 2, 3, 4, 4, 4, 4, 4, \
                   4, 4, 4, 4, 4, 4, 4, 4, 4, \
                   4, 4, 1, 1, 1, 1, 1, 1, 1, \
                   1, 1, 1, 1, 1, 1, 1, 1, 1, \
                   1, 1, 1, 1, 1, 1, 1, 1, 1]
        carrying = get_weighted_random(elements, weights)
    self.set_player_integer_field('PCAR', index, carrying)
    
    if player_dict["catching"]:
        catching = int(max(min(int(player_dict["catching"]), 80), 15))
    else:
        # A random distribution from 22 to 62, where the most likely values are 27 - 36.
        elements = list(range(22, 63))
        weights = [1, 1, 2, 2, 4, 6, 6, 6, 6, 6, 6, \
                   6, 6, 6, 6, 4, 2, 1, 1, 1, 1, \
                   1, 1, 1, 1, 1, 1, 1, 1, 1, 1, \
                   1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        catching = get_weighted_random(elements, weights)
    self.set_player_integer_field('PCTH', index, catching)
    
    if player_dict["jumping"]:
        jumping = int(max(min(int(player_dict["jumping"]), 90), 50))
    else:
        # A random distribution from 58 to 93, where the most likely values are 65 - 74.
        elements = list(range(58, 94))
        weights = [1, 1, 1, 1, 1, 1, 2, 6, 6, \
                   6, 6, 6, 6, 6, 6, 6, 6, 5, \
                   4, 3, 3, 2, 1, 1, 1, 1, 1, \
                   1, 1, 1, 1, 1, 1, 1, 1, 1]
        jumping = get_weighted_random(elements, weights)
    self.set_player_integer_field('PJMP', index, jumping)
    
    if player_dict["elusiveness"] and player_dict["trucking"]:
        break_tackles = int(max(min(
            math.ceil((int(player_dict["elusiveness"]) + int(player_dict["trucking"])) / 2), 
            65), 10))
    else:
        # A random distribution from 15 to 50, where the most likely values are 18 - 27.
        elements = list(range(15, 51))
        weights = [2, 3, 4, 5, 5, 5, 5, 5, 5, \
                   5, 5, 5, 5, 4, 4, 4, 3, 3, \
                   3, 2, 2, 2, 1, 1, 1, 1, 1, \
                   1, 1, 1, 1, 1, 1, 1, 1, 1]
        break_tackles = get_weighted_random(elements, weights)
    self.set_player_integer_field('PBTK', index, break_tackles)
    
    if player_dict["tackle"]:
        tackle = int(max(min(int(player_dict["tackle"]), 99), 60))
    else:
        if de_type == 0:
            # Pass-rushing end. Allow tackle to range from 62 to 75, where the most likely values are 64 - 67.
            elements = list(range(62, 76))
            weights = [7, 10, 13, 13, 13, 13, 11, 7, 5, 3, 2, 1, 1, 1]
        else:
            # Run-stopping end. Allow tackle to range from 69 to 82, where the most likely values are 71 - 74.
            elements = list(range(69, 83))
            weights = [7, 10, 13, 13, 13, 13, 11, 7, 5, 3, 2, 1, 1, 1]
        tackle = get_weighted_random(elements, weights)
    self.set_player_integer_field('PTAK', index, tackle)
    
    if player_dict["throw_power"]:
        throw_power = int(max(min(int(player_dict["throw_power"]), 75), 10))
    else:
        # A random distribution from 10 to 50, where the most likely values are 10 - 24.
        elements = list(range(10, 51))
        weights = [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, \
                   4, 4, 4, 4, 3, 3, 3, 3, 3, 2, \
                   2, 2, 2, 1, 1, 1, 1, 1, 1, 1, \
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
        ), 70), 10))
    else:
        # A random distribution from 10 to 60, where the most likely values are 15 - 24.
        elements = list(range(10, 61))
        weights = [2, 2, 2, 2, 2, 4, 4, 4, 4, 4, 4, \
                   4, 4, 4, 4, 2, 2, 2, 2, 2, 2, \
                   2, 2, 2, 2, 2, 2, 2, 2, 1, 1, \
                   1, 1, 1, 1, 1, 1, 1, 1, 1, 1, \
                   1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        throw_accuracy = get_weighted_random(elements, weights)
    self.set_player_integer_field('PTHA', index, throw_accuracy)
    
    if player_dict["pass_block"] and player_dict["pass_block_power"] and player_dict["pass_block_finesse"]:
        pass_block = int(max(min(math.ceil(
            (
                int(player_dict["pass_block"]) + 
                int(player_dict["pass_block_power"]) + 
                int(player_dict["pass_block_finesse"])
            ) / 3
        ), 65), 30))
    else:
        # A random distribution from 40 to 60, where the most likely values are 45 - 50.
        elements = list(range(40, 61))
        weights = [3, 3, 4, 5, 6, 8, 8, \
                   8, 8, 8, 8, 6, 5, 4, \
                   4, 3, 3, 2, 2, 1, 1]
        pass_block = get_weighted_random(elements, weights)
    self.set_player_integer_field('PPBK', index, pass_block)
    
    if player_dict["run_block"] and player_dict["run_block_power"] and player_dict["run_block_finesse"]:
        run_block = int(max(min(math.ceil(
            (
                int(player_dict["run_block"]) + 
                int(player_dict["run_block_power"]) + 
                int(player_dict["run_block_finesse"])
            ) / 3
        ), 75), 40))
    else:
        # A random distribution from 45 to 65, where the most likely values are 50 - 55.
        elements = list(range(45, 66))
        weights = [3, 3, 4, 5, 6, 8, 8, \
                   8, 8, 8, 8, 6, 5, 4, \
                   4, 3, 3, 2, 2, 1, 1]
        run_block = get_weighted_random(elements, weights)
    self.set_player_integer_field('PRBK', index, run_block)
    
    if player_dict["kick_power"]:
        kick_power = int(max(min(int(player_dict["kick_power"]), 60), 10))
    else:
        # A random distribution from 15 to 40, where the most likely values are 20 - 29.
        elements = list(range(15, 41))
        weights = [1, 2, 3, 4, 5, 6, 6, 6, 6, \
                   6, 6, 6, 6, 6, 6, 5, 4, 3, \
                   2, 2, 2, 2, 2, 1, 1, 1]
        kick_power = get_weighted_random(elements, weights)
    self.set_player_integer_field('PKPR', index, kick_power)
    
    if player_dict["kick_accuracy"]:
        kick_accuracy = int(max(min(int(player_dict["kick_accuracy"]), 50), 5))
    else:
        # A random distribution from 10 to 35, where the most likely values are 15 - 24.
        elements = list(range(10, 36))
        weights = [1, 2, 3, 4, 5, 6, 6, 6, 6, \
                   6, 6, 6, 6, 6, 6, 5, 4, 3, \
                   2, 2, 2, 2, 2, 1, 1, 1]
        kick_accuracy = get_weighted_random(elements, weights)
    self.set_player_integer_field('PKAC', index, kick_accuracy)
    
    if player_dict["kick_return"]:
        kick_return = int(max(min(int(player_dict["kick_return"]), 35), 10))
    else:
        # A random distribution from 10 to 30, where the most likely values are 15 - 24.
        elements = list(range(10, 31))
        weights = [3, 3, 4, 4, 5, 6, 6, \
                   6, 6, 6, 6, 6, 6, 6, \
                   6, 5, 4, 4, 3, 3, 2]
        kick_return = get_weighted_random(elements, weights)
    self.set_player_integer_field('PKRT', index, kick_return)
    
    if player_dict["stamina"]:
        stamina = int(max(min(int(player_dict["stamina"]), 99), 65))
    else:
        # A random distribution from 70 to 95, where the most likely values are 75 - 84.
        elements = list(range(70, 96))
        weights = [2, 2, 3, 4, 5, 6, 6, 6, 6, \
                   6, 6, 6, 6, 6, 6, 5, 4, 3, \
                   3, 2, 2, 1, 1, 1, 1, 1]
        stamina = get_weighted_random(elements, weights)
    self.set_player_integer_field('PSTA', index, stamina)
    
    if player_dict["injury"]:
        injury = int(max(min(int(player_dict["injury"]), 99), 65))
    else:
        # A random distribution from 75 to 98, where the most likely values are 83 - 91.
        elements = list(range(75, 99))
        weights = [2, 3, 3, 3, 4, 4, 5, 5, \
                   6, 6, 6, 6, 6, 6, 6, 6, \
                   6, 5, 4, 3, 2, 1, 1, 1]
        injury = get_weighted_random(elements, weights)
    self.set_player_integer_field('PINJ', index, injury)
    
    if player_dict["toughness"]:
        toughness = int(max(min(int(player_dict["toughness"]), 99), 60))
    else:
        # A random distribution from 65 to 98, where the most likely values are 80 - 86.
        elements = list(range(65, 99))
        weights = [1, 1, 1, 2, 2, 2, 2, 2, 2, 3, 3, 3, \
                   3, 4, 5, 6, 6, 6, 6, 6, 6, 6, 5, \
                   4, 3, 2, 1, 1, 1, 1, 1, 1, 1, 1]
        toughness = get_weighted_random(elements, weights)
    self.set_player_integer_field('PTGH', index, toughness)
    
    
    # For the following attributes, we will use weighted random distributions or other non-dependant means without 
    # checking the CSV file at all.
    
    # PCHS: A random distribution from 0 to 40, where the most likely value is 15 and the least likely is 40.
    elements = list(range(0, 41))
    weights = [1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 3, \
               3, 4, 6, 7, 9, 7, 6, 4, 3, 3, \
               3, 2, 2, 2, 2, 2, 2, 2, 2, 2, \
               1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    chest_shelf = get_weighted_random(elements, weights)
    self.set_player_integer_field('PCHS', index, chest_shelf)
    
    # PEGO: Set 5% to 0, 10% to something btwn 1 - 20, 5% to btwn 21 - 40, 5% to btwn 41 - 50, 20% to btwn 51 - 60, 
    # 25% to btwn 61 - 80, 20% to btwn 81 - 90, and 10% to btwn 91 - 99.
    elements = list(range(0, 100))
    weights = [5.0] + [0.5]*20 + [.25]*20 + [.5]*10 + [2.0]*10 + [1.25]*20 + [2]*10 + [1.1111]*9
    ego = get_weighted_random(elements, weights)
    self.set_player_integer_field('PEGO', index, ego)
    
    # PFAS: A random distribution from 5 to 25, where the most likely value is 10 and the least likely is 25.
    elements = list(range(5, 26))
    weights = [5, 6, 9, 11, 13, 15, 10, 6, 4, 3, 3, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1]
    arm_fat = get_weighted_random(elements, weights)
    self.set_player_integer_field('PFAS', index, arm_fat)
    
    # PFCS: A random distribution from 5 to 30, where the most likely value is 10 and the least likely is 30.
    elements = list(range(5, 31))
    weights = [4, 5, 7, 9, 11, 13, 10, 7, 5, 4, 3, 3, 3, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    calf_fat = get_weighted_random(elements, weights)
    self.set_player_integer_field('PFCS', index, calf_fat)
    
    # PFGS: A random distribution from 5 to 45, where the most likely value is 20 and the least likely is 45.
    elements = list(range(5, 46))
    weights = [1, 1, 1, 1, 2, 2, 2, 2, 3, 3, \
               3, 3, 4, 6, 8, 10, 8, 6, 4, 3, \
               3, 2, 2, 2, 2, 1, 1, 1, 1, 1, \
               1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    glute_fat = get_weighted_random(elements, weights)
    self.set_player_integer_field('PFGS', index, glute_fat)
    
    # PFHS: A random distribution from 5 to 45, where the most likely value is 20 and the least likely is 45.
    elements = list(range(5, 46))
    weights = [1, 1, 1, 1, 2, 2, 2, 2, 3, 3, \
               3, 3, 4, 6, 8, 10, 8, 6, 4, 3, \
               3, 2, 2, 2, 2, 1, 1, 1, 1, 1, \
               1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    thigh_fat = get_weighted_random(elements, weights)
    self.set_player_integer_field('PFHS', index, thigh_fat)
    
    # PFTS: A random distribution from 5 to 40, where the most likely value is 15 and the least likely is 40.
    elements = list(range(5, 41))
    weights = [1, 2, 2, 2, 3, 3, 3, 4, 6, \
               9, 10, 8, 6, 4, 3, 3, 3, 3, \
               2, 2, 2, 2, 2, 2, 2, 1, 1, \
               1, 1, 1, 1, 1, 1, 1, 1, 1]
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
    
    # PMAS: A random distribution from 10 to 40, where the most likely value is 15 and the least likely is 40.
    elements = list(range(10, 41))
    weights = [3, 4, 6, 9, 11, 13, 9, 6, 4, 3, \
               3, 3, 3, 2, 2, 2, 2, 2, 1, 1, \
               1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    arm_muscle = get_weighted_random(elements, weights)
    self.set_player_integer_field('PMAS', index, arm_muscle)
    
    # PMCS: A random distribution from 10 to 70, where the most likely value is 25 and the least likely is 70.
    elements = list(range(10, 71))
    weights = [1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 4, 6, 9, \
               6, 4, 3, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, \
               1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, \
               1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    calf_muscle = get_weighted_random(elements, weights)
    self.set_player_integer_field('PMCS', index, calf_muscle)
    
    # PMHS: A random distribution from 10 to 70, where the most likely value is 25 and the least likely is 70.
    elements = list(range(10, 71))
    weights = [1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 4, 6, 9, \
               6, 4, 3, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, \
               1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, \
               1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    thigh_muscle = get_weighted_random(elements, weights)
    self.set_player_integer_field('PMHS', index, thigh_muscle)
    
    # PMOR: Set 20% to between 50 - 79, 20% to 80 - 89, and 60% to 90 - 99.
    elements = list(range(50, 80)) + list(range(80, 90)) + list(range(90, 100))
    weights = [2/3]*30 + [2]*10 + [6]*10
    morale = get_weighted_random(elements, weights)
    self.set_player_integer_field('PMOR', index, morale)
    
    # PMTS: A random distribution from 5 to 45, where the most likely value is 15 and the least likely is 45.
    elements = list(range(5, 46))
    weights = [1, 1, 1, 2, 2, 3, 3, 5, 6, 8, 12, \
               8, 6, 5, 4, 3, 3, 2, 2, 2, 1, \
               1, 1, 1, 1, 1, 1, 1, 1, 1, 1, \
               1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    mid_torso = get_weighted_random(elements, weights)
    self.set_player_integer_field('PMTS', index, mid_torso)
    
    # POID: Just set this to the same number as PGID.
    self.set_player_integer_field('POID', index, index)
    
    # PSBS: A random distribution from 24 to 89, where the most likely value is 59 (to result in a Body Overall Size 
    # of 40), and the least likely are 24 (Overall = 75) and 89 (Overall = 10).
    elements = list(range(24, 90))
    weights = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, \
               1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 3, 3, 4, \
               6, 7, 6, 4, 3, 3, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, \
               1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
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
    
    # For left_knee, when the value in the CSV is -1: If PSPD < 70 and PAGI < 65, give a 30% chance of getting a 1.
    if int(player_dict["left_knee"]) == -1:
        if speed < 70 and agility < 65:
            elements = [0, 1]
            weights = [70, 30]
            left_knee = get_weighted_random(elements, weights)
        else:
            left_knee = 0
    else:
        left_knee = int(player_dict["left_knee"])
    self.set_player_integer_field('PLTH', index, left_knee)
    
    # For right_knee, when the CSV says -1: If PSPD < 70 and PAGI < 60, then give a 40% chance of getting a 1 
    # regardless of PLTH. Otherwise, if PLTH == 0 and PSPD < 70 and PAGI < 65, then give a 35% chance of getting a 1.
    if int(player_dict["right_knee"]) == -1:
        if speed < 70 and agility < 60:
            elements = [0, 1]
            weights = [60, 40]
            right_knee = get_weighted_random(elements, weights)
        elif left_knee == 0 and speed < 70 and agility < 65:
            elements = [0, 1]
            weights = [65, 35]
            right_knee = get_weighted_random(elements, weights)
        else:
            right_knee = 0
    else:
        right_knee = int(player_dict["right_knee"])
    self.set_player_integer_field('PRTH', index, right_knee)
    
    # PTEN: If the CSV is -1, use the RE's speed, acceleration, and agility attributes to determine the tendency.
    if int(player_dict["tendency"]) == -1:
        if speed > 76 and acceleration > 84 and agility > 73:
            tendency = 0 # pass_rushing
        elif speed < 76 and acceleration < 84 and agility < 73 and tackle > 80:
            tendency = 1 # run_stopping
        else:
            tendency = 2 # balanced
    else:
        tendency = int(player_dict["tendency"])
    self.set_player_integer_field('PTEN', index, tendency)
    
    # PHLM: Check PFMK. If it was set to 12, we must use 4. Otherwise, give 80% 0 (Style 1) and 20% 2 (Style 3).
    if face_mask == 12:
        helmet = 4
    elif int(player_dict["helmet"]) == -1:
        elements = [0, 2]
        weights = [80, 20]
        helmet = get_weighted_random(elements, weights)
    else:
        helmet = int(player_dict["helmet"])
    self.set_player_integer_field('PHLM', index, helmet)
    
    # PGSL: If the CSV has -1 and we didn't set PLEL, PREL, PTAL, or PTAR to anything but 0, set 60% to 0 (none), 5% 
    # to 1 (black), 15% to 2 (white), 5% to 3 (team-color), 5% to 4 (white half), 5% to 5 (black half), and 5% to 6 
    # (team-color half).
    if int(player_dict["sleeves"]) == -1:
        if (left_elbow == 0 and 
                right_elbow == 0 and 
                int(player_dict["tattoo_left"]) == 0 and 
                int(player_dict["tattoo_right"]) == 0):
            elements = [0, 1, 2, 3, 4, 5, 6]
            weights = [60, 5, 15, 5, 5, 5, 5]
            sleeves = get_weighted_random(elements, weights)
        else:
            sleeves = 0
    else:
        sleeves = int(player_dict["sleeves"])
    self.set_player_integer_field('PGSL', index, sleeves)
    
    # Use the formula found in 04 - FORMULA for Calculating Overall Rating.txt
    overall_rating = 0.0
    overall_rating += ((speed - 50.0) / 10.0) * 3.75
    overall_rating += ((strength - 50.0) / 10.0) * 3.75
    overall_rating += ((awareness - 50.0) / 10.0) * 1.75
    overall_rating += ((agility - 50.0) / 10.0) * 1.75
    overall_rating += ((acceleration - 50.0) / 10.0) * 3.8
    overall_rating += ((tackle - 50.0) / 10.0) * 5.5
    overall_rating = int(max(min((round(overall_rating) + 30), 99), 40))
    self.set_player_integer_field('POVR', index, overall_rating)
    
    # PIMP: We're relating the importance of a player to his overall rating and his position. REs should be of average 
    # importance, so use the following here: int(max(min(ceil((([POVR]/100)^2) * 70) + ([POVR] - 70), 99), 15))
    importance = int(max(min(math.ceil((math.pow((overall_rating / 100), 2) * 70) + (overall_rating - 70)), 99), 15))
    self.set_player_integer_field('PIMP', index, importance)
    
    # PROL: Check for these roles IN THIS ORDER: 1) injury_prone, 2) team_distraction, 3) underachiever, 4) 
    # force_of_nature, 5) pass_rusher, 6) run_stopper, 7) heavy_hitter, 8) project_player, 9) fan_favorite, 10) 
    # team_mentor, 11) team_leader, 12) first_round_pick.
    role_one = int(player_dict["role_one"])
    if role_one == 45:
        if player_roles.is_injury_prone(role_one, injury, toughness):
            role_one = 14
        elif player_roles.is_team_distraction(role_one, morale, importance):
            role_one = 8
        elif player_roles.is_underachiever(role_one, draft_round, draft_pick, years_pro, overall_rating):
            role_one = 4
        elif player_roles.is_force_of_nature(role_one, position, acceleration, strength):
            role_one = 27
        elif player_roles.is_pass_rusher(role_one, position, speed, acceleration):
            role_one = 39
        elif player_roles.is_run_stopper(role_one, position, strength, tackle):
            role_one = 40
        elif player_roles.is_heavy_hitter(role_one, position, tackle):
            role_one = 28
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
    
    # PRL2: Check for these roles IN THIS ORDER: 1) injury_prone, 2) team_distraction, 3) underachiever, 4) 
    # force_of_nature, 5) pass_rusher, 6) run_stopper, 7) heavy_hitter, 8) project_player, 9) fan_favorite, 10) 
    # team_mentor, 11) team_leader, 12) first_round_pick.
    role_two = int(player_dict["role_two"])
    if role_two == 45 and role_one != 45:
        if player_roles.is_injury_prone(role_one, injury, toughness):
            role_two = 14
        elif player_roles.is_team_distraction(role_one, morale, importance):
            role_two = 8
        elif player_roles.is_underachiever(role_one, draft_round, draft_pick, years_pro, overall_rating):
            role_two = 4
        elif player_roles.is_force_of_nature(role_one, position, acceleration, strength):
            role_two = 27
        elif player_roles.is_pass_rusher(role_one, position, speed, acceleration):
            role_two = 39
        elif player_roles.is_run_stopper(role_one, position, strength, tackle):
            role_two = 40
        elif player_roles.is_heavy_hitter(role_one, position, tackle):
            role_two = 28
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
        total_salary = round((total_salary / 10000) * 0.725)
    elif total_salary > 1000000:
        total_salary = round((total_salary / 10000) * 0.58)
    else:
        total_salary = round((total_salary / 10000) * 0.43)
    
    self.set_player_integer_field('PTSA', index, total_salary)
    self.set_player_integer_field('PVTS', index, total_salary)
    
    # PSBO & PVSB: Use the formula for this year to reduce actual salary and bonus numbers by certain ratios to 
    # account for inflation.
    signing_bonus = int(player_dict["signing_bonus"])
    if signing_bonus > 10000000:
        signing_bonus = round((signing_bonus / 10000) * 0.4)
    elif signing_bonus > 1000000:
        signing_bonus = round((signing_bonus / 10000) * 0.5)
    elif signing_bonus > 100000:
        signing_bonus = round((signing_bonus / 10000) * 0.65)
    else:
        signing_bonus = round((signing_bonus / 10000) * 0.8)
    # PSBO must always be in multiples of PCON (contract_length).
    if signing_bonus % contract_length > 0:
        signing_bonus += (contract_length - (signing_bonus % contract_length))
    
    self.set_player_integer_field('PSBO', index, signing_bonus)
    self.set_player_integer_field('PVSB', index, signing_bonus)

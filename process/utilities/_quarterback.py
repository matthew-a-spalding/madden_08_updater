r""" _quarterback.py
    
    This is one of the 21 method definition modules used by the main RosterManager class. This module contains the 
    method used to populate the fields for a quarterback record in the roster DB.
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

def create_quarterback(self, player_dict, index):
    """
    Given a dictionary of a new player and the index of the related record to modify in the DB, performs all of 
    the calculations and updates necessary to create the player as a QB in the DB.
    """
    
    position = 0 # QB
    
    # For all of the following fields, we simply use 0.
    # PCPH, PFHO, PJTY, PMPC, PMUS, POPS, PPOS, PSTM, PSTY, PSXP, PTSL, PUCL, TLEL, TLHA, TLWR, TREL, TRHA, TRWR 
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
    # QBs will never have a mouthpiece, so PMPC = 0 is a constant as well.
    # Position (PPOS) and 'other' position (POPS) are both set to the value for this position.
    self.set_player_integer_field('PCMT', index, 999)
    self.set_player_integer_field('PJER', index, 1)
    self.set_player_integer_field('PLHY', index, -31)
    self.set_player_integer_field('PLPL', index, 100)
    self.set_player_integer_field('PMPC', index, 0)
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
    
    # The college ID is simply picked from a list.
    self.set_player_integer_field('PCOL', index, self.get_college_id(player_dict["college"]))
    
    # For eye_black, if the CSV says -1, give 80% a 0 (none) and 20% a 1 (black).
    if int(player_dict["eye_black"]) == -1:
        elements = [0, 1]
        weights = [80, 20]
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
    
    # For face_mask, if the CSV says -1, set 10% to 0 (2-bar), 20% to 1 (3-bar), 30% to 6 (3-Bar QB), 10% to 8 
    # (3-Bar RB), and 30% to 11 (REVOG2EG). NOTE!! If choosing 11, must also set PHLM to 4 !!
    if int(player_dict["face_mask"]) == -1:
        elements = [0, 1, 6, 8, 11]
        weights = [10, 20, 30, 10, 30]
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
    
    # For left_elbow, if the CSV says -1, give 85% a 0 (none), 5% a 7 (black wrist), 5% a 8 (white wrist), and 
    # 5% a 9 (team-color wrist).
    if int(player_dict["left_elbow"]) == -1:
        elements = [0, 7, 8, 9]
        weights = [85, 5, 5, 5]
        left_elbow = get_weighted_random(elements, weights)
    else:
        left_elbow = int(player_dict["left_elbow"])
    self.set_player_integer_field('PLEL', index, left_elbow)
    
    # For left_hand, if the CSV says -1 and the player's handedness is right, set 70% to 0 (none), 5% to 2 
    # (black glove), 5% to 3 (white glove), 5% to 4 (team-color glove), 5% to 5 (white RB glove), 5% to 6 (black 
    # RB glove), and 5% to 7 (team-color RB glove).
    if int(player_dict["left_hand"]) == -1:
        if handedness == 0:
            elements = [0, 2, 3, 4, 5, 6, 7]
            weights = [70, 5, 5, 5, 5, 5, 5]
            left_hand = get_weighted_random(elements, weights)
        else:
            left_hand = 0
    else:
        left_hand = int(player_dict["left_hand"])
    self.set_player_integer_field('PLHA', index, left_hand)
    
    # Get the first 13 characters of the last name.
    if len(player_dict["last_name"]) < 14:
        self.set_player_string_field('PLNA', index, player_dict["last_name"])
    else:
        self.set_player_string_field('PLNA', index, player_dict["last_name"][:13])
    
    # For left_shoe, if the CSV says -1, give 90% a 0 (none) and 10% a 1 (white tape).
    if int(player_dict["left_shoe"]) == -1:
        elements = [0, 1]
        weights = [90, 10]
        left_shoe = get_weighted_random(elements, weights)
    else:
        left_shoe = int(player_dict["left_shoe"])
    self.set_player_integer_field('PLSH', index, left_shoe)
    
    # For left_knee, if the CSV says -1, always use 0. Otherwise, just use what is in the file.
    if int(player_dict["left_knee"]) == -1:
        left_knee = 0
    else:
        left_knee = int(player_dict["left_knee"])
    self.set_player_integer_field('PLTH', index, left_knee)
    
    # For left_wrist, if the CSV says -1: When the player's handedness is right, use 1 (QB wrist). Otherwise, set 
    # 30% to 0 (normal), 40% to 2 (white wrist), 10% to 3 (black wrist), 10% to 4 (team-color wrist), and 10% to 5 
    # (white double).
    if int(player_dict["left_wrist"]) == -1:
        if handedness == 0:
            left_wrist = 1
        else:
            elements = [0, 2, 3, 4, 5]
            weights = [30, 40, 10, 10, 10]
            left_wrist = get_weighted_random(elements, weights)
    else:
        left_wrist = int(player_dict["left_wrist"])
    self.set_player_integer_field('PLWR', index, left_wrist)
    
    # For neck_pad, if the CSV says -1, always use 0. Otherwise, just use what is in the file.
    if int(player_dict["neck_pad"]) == -1:
        neck_pad = 0
    else:
        neck_pad = int(player_dict["neck_pad"])
    self.set_player_integer_field('PNEK', index, neck_pad)
    
    # For right_elbow, if the CSV says -1: If the left_elbow was 0, set 85% to 0 (none), 5% to 7 (black wrist), 5% 
    # to 8 (white wrist), and 5% to 9 (team-color wrist). If left_elbow was non-zero, set 80% to the same value, 
    # and 20% to 0. If the CSV value is not -1, just use what is in there.
    if int(player_dict["right_elbow"]) == -1:
        if left_elbow == 0:
            elements = [0, 7, 8, 9]
            weights = [85, 5, 5, 5]
            right_elbow = get_weighted_random(elements, weights)
        else:
            elements = [left_elbow, 0]
            weights = [80, 20]
            right_elbow = get_weighted_random(elements, weights)
    else:
        right_elbow = int(player_dict["right_elbow"])
    self.set_player_integer_field('PREL', index, right_elbow)
    
    # For right_hand, if the CSV says -1 and the player's handedness is left, set 70% to 0 (none), 5% to 2 
    # (black glove), 5% to 3 (white glove), 5% to 4 (team-color glove), 5% to 5 (white RB glove), 5% to 6 (black 
    # RB glove), and 5% to 7 (team-color RB glove).
    if int(player_dict["right_hand"]) == -1:
        if handedness == 1:
            elements = [0, 2, 3, 4, 5, 6, 7]
            weights = [70, 5, 5, 5, 5, 5, 5]
            right_hand = get_weighted_random(elements, weights)
        else:
            right_hand = 0
    else:
        right_hand = int(player_dict["right_hand"])
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
    
    # For right_wrist, if the CSV says -1: When the player's handedness is left, use 1 (QB wrist). Otherwise, set 
    # 30% to 0 (normal), 40% to 2 (white wrist), 10% to 3 (black wrist), 10% to 4 (team-color wrist), and 10% to 5 
    # (team-color double).
    if int(player_dict["right_wrist"]) == -1:
        if handedness == 1:
            right_wrist = 1
        else:
            elements = [0, 2, 3, 4, 5]
            weights = [30, 40, 10, 10, 10]
            right_wrist = get_weighted_random(elements, weights)
    else:
        right_wrist = int(player_dict["right_wrist"])
    self.set_player_integer_field('PRWR', index, right_wrist)
    
     # For visor, if the CSV says -1, always use 0. Otherwise, just use what is in the file.
    if int(player_dict["visor"]) == -1:
        visor = 0
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
    
    # The QB's type starts out as unknown.
    qb_type = -1
    
    if player_dict["speed"]:
        speed = int(max(min(int(player_dict["speed"]), 95), 55))
    else:
        # A random distribution from 60 to 89, where the most likely values are 71 - 73, 83 - 84.
        elements = list(range(60, 90))
        weights = [1, 1, 1, 2, 2, 3, 3, 4, 4, 5, \
                   5, 6, 7, 6, 5, 5, 4, 3, 2, 1, \
                   2, 2, 4, 6, 6, 4, 2, 2, 1, 1]
        speed = get_weighted_random(elements, weights)
    self.set_player_integer_field('PSPD', index, speed)
    
    if player_dict["strength"]:
        strength = int(max(min(int(player_dict["strength"]), 80), 45))
    else:
        # A random distribution from 50 to 80, where the most likely values are 52 - 61.
        elements = list(range(50, 81))
        weights = [1, 3, 6, 6, 6, 6, 6, 6, 6, 6, 6, \
                   6, 5, 5, 4, 3, 3, 2, 2, 1, 1, \
                   1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        strength = get_weighted_random(elements, weights)
    self.set_player_integer_field('PSTR', index, strength)
    
    if player_dict["awareness"]:
        awareness = int(max(min(int(player_dict["awareness"]), 99), 40))
    else:
        if speed > 81:
            # Scrambler. Limit awareness range to 41 - 55, where the most likely values are 45 - 48.
            qb_type = 1 # scrambling
            elements = list(range(41, 56))
            weights = [3, 6, 8, 9, 10, 10, 10, 10, 9, 7, 6, 5, 4, 2, 1]
        elif speed < 70:
            # Pocket passer. Allow for awareness from 47 up to 61, where the most likely values are 51 - 54.
            qb_type = 0 # pocket passer
            elements = list(range(47, 62))
            weights = [3, 6, 8, 9, 10, 10, 10, 10, 9, 7, 6, 5, 4, 2, 1]
        else:
            # Allow awareness to range from 44 up to 58, where the most likely values are 48 - 51.
            qb_type = 2 # balanced
            elements = list(range(44, 59))
            weights = [3, 6, 8, 9, 10, 10, 10, 10, 9, 7, 6, 5, 4, 2, 1]
        awareness = get_weighted_random(elements, weights)
    self.set_player_integer_field('PAWR', index, awareness)
    
    if player_dict["agility"]:
        agility = int(max(min(int(player_dict["agility"]), 98), 45))
    else:
        if qb_type == 1:
            # Scrambler. Agility needs to be in the range 80 - 92, where the most likely values are 82 - 85.
            elements = list(range(80, 93))
            weights = [4, 8, 13, 15, 15, 13, 10, 8, 6, 4, 2, 1, 1]
        elif qb_type == 0:
            # Pocket passer. Agility needs to be in the range 55 - 75, where the most likely values are 62 - 65.
            elements = list(range(55, 76))
            weights = [1, 1, 2, 3, 4, 6, 8, \
                       10, 10, 10, 10, 8, 6, 5, \
                       4, 3, 3, 2, 2, 1, 1]
        else:
            # Allow agility to range from 68 to 82, with the most likely values being 70 - 74.
            elements = list(range(68, 83))
            weights = [5, 8, 11, 12, 12, 12, 11, 9, \
                       7, 5, 3, 2, 1, 1, 1]
        agility = get_weighted_random(elements, weights)
    self.set_player_integer_field('PAGI', index, agility)
    
    if player_dict["acceleration"]:
        acceleration = int(max(min(int(player_dict["acceleration"]), 95), 55))
    else:
        if qb_type == 1:
            # Scrambler. Acceleration needs to be in the range 81 - 90, where the most likely values are 81 - 85.
            elements = list(range(81, 91))
            weights = [13, 13, 13, 13, 13, 11, 9, 7, 5, 3]
        elif qb_type == 0:
            # Pocket passer. Acceleration needs to be in the range 62 - 84, where the most likely values are 69 - 77.
            elements = list(range(62, 85))
            weights = [1, 1, 1, 2, 3, 4, 6, 7, \
                       7, 7, 7, 7, 7, 7, 7, 7, \
                       6, 4, 3, 2, 2, 1, 1]
        else:
            # Allow acceleration to range from 75 to 87, with the most likely values being 77 - 82.
            elements = list(range(75, 88))
            weights = [5, 8, 11, 11, 11, 11, 11, 11, 8, 6, 4, 2, 1]
        acceleration = get_weighted_random(elements, weights)
    self.set_player_integer_field('PACC', index, acceleration)
    
    if player_dict["carrying"]:
        carrying = int(max(min(int(player_dict["carrying"]), 80), 40))
    else:
        if qb_type == 1:
            # Scrambler. Carrying needs to be in the range 45 - 75, where the most likely values are 57 - 64.
            elements = list(range(45, 76))
            weights = [1, 1, 1, 1, 1, 2, 2, 2, 3, 3, 4, \
                       5, 6, 6, 6, 6, 6, 6, 6, 6, 5, \
                       4, 3, 3, 3, 2, 2, 1, 1, 1, 1]
        elif qb_type == 0:
            # Pocket passer. Carrying needs to be in the range 45 - 70, where the most likely values are 52 - 60.
            elements = list(range(45, 71))
            weights = [1, 1, 1, 1, 2, 4, 6, 7, 7, \
                       7, 7, 7, 7, 7, 7, 7, 6, 4, \
                       3, 2, 1, 1, 1, 1, 1, 1]
        else:
            # Allow carrying to range from 45 to 72, with the most likely values being 56 - 61.
            elements = list(range(45, 73))
            weights = [1, 1, 1, 1, 1, 2, 3, 4, 4, 5, \
                       6, 7, 7, 7, 7, 7, 7, 6, 5, \
                       4, 4, 3, 2, 1, 1, 1, 1, 1]
        carrying = get_weighted_random(elements, weights)
    self.set_player_integer_field('PCAR', index, carrying)
    
    if player_dict["catching"]:
        catching = int(max(min(int(player_dict["catching"]), 85), 15))
    else:
        # A random distribution from 20 to 70, where the most likely values are 30 - 39.
        elements = list(range(20, 71))
        weights = [1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 4, 4, 4, \
                   4, 4, 4, 4, 4, 4, 4, 3, 3, 3, 2, 2, 2, \
                   1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, \
                   1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        catching = get_weighted_random(elements, weights)
    self.set_player_integer_field('PCTH', index, catching)
    
    if player_dict["jumping"]:
        jumping = int(max(min(int(player_dict["jumping"]), 95), 40))
    else:
        if qb_type == 1:
            # Scrambler. Jumping needs to be in the range 70 - 90, where the most likely values are 75 - 84.
            elements = list(range(70, 91))
            weights = [1, 1, 2, 4, 6, 7, 7, 7, 7, 7, 7, \
                       7, 7, 7, 7, 6, 4, 2, 2, 1, 1]
        elif qb_type == 0:
            # Pocket passer. Jumping needs to be in the range 43 - 78, where the most likely values are 55 - 64.
            elements = list(range(43, 79))
            weights = [1, 1, 1, 1, 1, 2, 2, 2, 3, \
                       3, 3, 4, 5, 5, 5, 5, 5, 5, \
                       5, 5, 5, 5, 4, 3, 3, 3, 2, \
                       2, 2, 1, 1, 1, 1, 1, 1, 1]
        else:
            # Allow jumping to range from 50 to 85, with the most likely values being 64 - 71.
            elements = list(range(50, 86))
            weights = [1, 1, 1, 1, 1, 1, 1, 1, 2, \
                       2, 2, 3, 4, 5, 6, 6, 6, 6, \
                       6, 6, 6, 6, 5, 4, 3, 2, 2, \
                       2, 1, 1, 1, 1, 1, 1, 1, 1]
        jumping = get_weighted_random(elements, weights)
    self.set_player_integer_field('PJMP', index, jumping)
    
    if player_dict["elusiveness"] and player_dict["trucking"]:
        break_tackles = int(max(min(
            math.ceil(((int(player_dict["elusiveness"]) + int(player_dict["trucking"])) / 2) + 7), 
            90), 20))
    else:
        if qb_type == 1:
            # Scrambler. Break_tackles needs to be in the range 50 - 85, where the most likely values are 55 - 62.
            elements = list(range(50, 86))
            weights = [1, 1, 1, 2, 4, 6, 6, 6, 6, \
                       6, 6, 6, 6, 5, 5, 4, 4, 3, \
                       3, 2, 2, 1, 1, 1, 1, 1, 1, \
                       1, 1, 1, 1, 1, 1, 1, 1, 1]
        elif qb_type == 0:
            # Pocket passer. Break_tackles needs to be in the range 25 - 54, where the most likely values are 30 - 35.
            elements = list(range(25, 55))
            weights = [2, 3, 4, 5, 6, 7, 7, 7, 7, 7, 7, 6, 5, 4, 3, \
                       2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        else:
            # Allow break_tackles to range from 32 to 80, with the most likely values being 40 - 49.
            elements = list(range(32, 81))
            weights = [1, 1, 1, 2, 2, 3, 3, 3, 4, 4, 4, 4, 4,\
                       4, 4, 4, 4, 4, 3, 3, 3, 3, 2, 2, 2, \
                       2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, \
                       1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        break_tackles = get_weighted_random(elements, weights)
    self.set_player_integer_field('PBTK', index, break_tackles)
    
    if player_dict["tackle"]:
        tackle = int(max(min(int(player_dict["tackle"]), 65), 10))
    else:
        # A random distribution from 15 to 40, where the most likely values are 20 - 29.
        elements = list(range(15, 41))
        weights = [1, 2, 3, 4, 5, 6, 6, 6, 6, 6, 6, 6, 6, \
                   6, 6, 5, 5, 4, 3, 2, 1, 1, 1, 1, 1, 1]
        tackle = get_weighted_random(elements, weights)
    self.set_player_integer_field('PTAK', index, tackle)
    
    if player_dict["throw_power"]:
        throw_power = int(max(min(int(player_dict["throw_power"]), 99), 70))
    else:
        # Throw_power needs to be in the range 73 - 90, where the most likely values are 78 - 84.
        elements = list(range(73, 91))
        weights = [1, 2, 3, 6, 8, 9, 9, 9, 9, 9, 9, 8, 7, 5, 3, 1, 1, 1]
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
            )) - (2 * min(
                int(player_dict["throw_accuracy_short"]), 
                int(player_dict["throw_accuracy_mid"]), 
                int(player_dict["throw_accuracy_deep"]), 
                int(player_dict["throw_on_the_run"]), 
                int(player_dict["playaction"])
            ))
            ) / 8
        ), 99), 60))
    else:
        if qb_type == 1:
            # Scrambler. Accuracy needs to be in the range 62 to 83, where the most likely values are 68 - 74.
            elements = list(range(62, 84))
            weights = [2, 3, 4, 4, 5, 6, 7, 7, 7, 7, 7, \
                       7, 7, 6, 5, 4, 3, 3, 2, 2, 1, 1]
        elif qb_type == 0:
            # Pocket passer. Accuracy needs to be in the range 68 to 89, where the most likely values are 74 - 80.
            elements = list(range(68, 90))
            weights = [2, 3, 4, 4, 5, 6, 7, 7, 7, 7, 7, \
                       7, 7, 6, 5, 4, 3, 3, 2, 2, 1, 1]
        else:
            # Allow accuracy to range from 65 to 86, where the most likely values are 71 - 77.
            elements = list(range(65, 87))
            weights = [2, 3, 4, 4, 5, 6, 7, 7, 7, 7, 7, \
                       7, 7, 6, 5, 4, 3, 3, 2, 2, 1, 1]
        throw_accuracy = get_weighted_random(elements, weights)
    self.set_player_integer_field('PTHA', index, throw_accuracy)
    
    if player_dict["pass_block"] and player_dict["pass_block_power"] and player_dict["pass_block_finesse"]:
        pass_block = int(max(min(math.ceil(
            (
                int(player_dict["pass_block"]) + 
                int(player_dict["pass_block_power"]) + 
                int(player_dict["pass_block_finesse"])
            ) / 3
        ), 45), 5))
    else:
        # A random distribution from 10 to 30, where the most likely values are 13 - 16.
        elements = list(range(10, 31))
        weights = [7, 7, 7, 8, 8, 8, 8, 7, 7, 7, 6, 5, 4, 3, 2, 1, 1, 1, 1, 1, 1]
        pass_block = get_weighted_random(elements, weights)
    self.set_player_integer_field('PPBK', index, pass_block)
    
    if player_dict["run_block"] and player_dict["run_block_power"] and player_dict["run_block_finesse"]:
        run_block = int(max(min(math.ceil(
            (
                int(player_dict["run_block"]) + 
                int(player_dict["run_block_power"]) + 
                int(player_dict["run_block_finesse"])
            ) / 3
        ), 50), 10))
    else:
        # A random distribution from 10 to 35, where the most likely values are 13 - 20.
        elements = list(range(10, 36))
        weights = [1, 3, 5, 8, 8, 8, 8, 8, 8, 8, 8, 6, 4, \
                   3, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        run_block = get_weighted_random(elements, weights)
    self.set_player_integer_field('PRBK', index, run_block)
    
    if player_dict["kick_power"]:
        kick_power = int(max(min(int(player_dict["kick_power"]), 75), 5))
    else:
        # A random distribution from 10 to 50, where the most likely values are 15 - 20.
        elements = list(range(10, 51))
        weights = [1, 3, 4, 5, 6, 6, 6, 6, 6, 6, 6, \
                   6, 5, 4, 3, 2, 1, 1, 1, 1, 1, \
                   1, 1, 1, 1, 1, 1, 1, 1, 1, 1, \
                   1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        kick_power = get_weighted_random(elements, weights)
    self.set_player_integer_field('PKPR', index, kick_power)
    
    if player_dict["kick_accuracy"]:
        kick_accuracy = int(max(min(int(player_dict["kick_accuracy"]), 75), 5))
    else:
        # A random distribution from 10 to 50, where the most likely values are 15 - 20.
        elements = list(range(10, 51))
        weights = [1, 3, 4, 5, 6, 6, 6, 6, 6, 6, 6, \
                   6, 5, 4, 3, 2, 1, 1, 1, 1, 1, \
                   1, 1, 1, 1, 1, 1, 1, 1, 1, 1, \
                   1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        kick_accuracy = get_weighted_random(elements, weights)
    self.set_player_integer_field('PKAC', index, kick_accuracy)
    
    if player_dict["kick_return"]:
        kick_return = int(max(min(int(player_dict["kick_return"]), 85), 5))
    else:
        # A random distribution from 5 to 25, where the most likely values are 10 - 15.
        elements = list(range(5, 26))
        weights = [3, 3, 4, 5, 6, 8, 8, 8, 8, 8, 8, \
                   7, 6, 5, 4, 3, 2, 1, 1, 1, 1]
        kick_return = get_weighted_random(elements, weights)
    self.set_player_integer_field('PKRT', index, kick_return)
    
    if player_dict["stamina"]:
        stamina = int(max(min(int(player_dict["stamina"]), 99), 75))
    else:
        # A random distribution from 75 to 95, where the most likely values are 87 - 93.
        elements = list(range(75, 96))
        weights = [1, 1, 1, 1, 1, 2, 2, 3, 4, 5, 6, \
                   7, 8, 8, 8, 8, 8, 8, 8, 6, 4]
        stamina = get_weighted_random(elements, weights)
    self.set_player_integer_field('PSTA', index, stamina)
    
    if player_dict["injury"]:
        injury = int(max(min(int(player_dict["injury"]), 99), 60))
    else:
        # A random distribution from 75 to 97, where the most likely values are 83 - 90.
        elements = list(range(75, 98))
        weights = [1, 1, 1, 1, 1, 3, 4, 6, 8, 8, 8, 8, \
                   8, 8, 8, 8, 6, 4, 3, 2, 1, 1, 1]
        injury = get_weighted_random(elements, weights)
    self.set_player_integer_field('PINJ', index, injury)
    
    if player_dict["toughness"]:
        toughness = int(max(min(int(player_dict["toughness"]), 99), 55))
    else:
        # A random distribution from 68 to 99, where the most likely values are 84 - 89.
        elements = list(range(68, 100))
        weights = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, \
                   2, 3, 4, 5, 6, 7, 7, 7, 7, 7, 7, \
                   6, 5, 4, 3, 3, 2, 1, 1, 1, 1]
        toughness = get_weighted_random(elements, weights)
    self.set_player_integer_field('PTGH', index, toughness)
    
    
    # For the following attributes, we will use weighted random distributions or other non-dependant means without 
    # checking the CSV file at all.
    
    # PCHS: A random distribution from 0 to 30, where the most likely value is 10 and the least likely is 30.
    elements = list(range(0, 31))
    weights = [1, 1, 1, 2, 2, 3, 3, 4, 5, 6, 7, 6, 6, 5, 5, \
               4, 4, 4, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2, 2]
    chest_shelf = get_weighted_random(elements, weights)
    self.set_player_integer_field('PCHS', index, chest_shelf)
    
    # PEGO: A random distribution from 0 to 99, where the most likely value is 85 and the least likely is 21-40.
    elements = list(range(0, 100))
    weights = [3.0] + [0.3]*20 + [.15]*20 + [.3]*10 + [2.0]*10 + [1.25]*20 + [2.5]*10 + [1.6667]*9
    ego = get_weighted_random(elements, weights)
    self.set_player_integer_field('PEGO', index, ego)
    
    # PFAS: A random distribution from 0 to 10, where the most likely value is 0 and the least likely is 10.
    elements = list(range(0, 11))
    weights = [24, 19, 15, 11, 8, 7, 6, 5, 3, 1, 1]
    arm_fat = get_weighted_random(elements, weights)
    self.set_player_integer_field('PFAS', index, arm_fat)
    
    # PFCS: A random distribution from 0 to 15, where the most likely value is 0 and the least likely is 15.
    elements = list(range(0, 16))
    weights = [17, 15, 13, 10, 8, 7, 6, 5, 4, 4, 3, 2, 2, 2, 1, 1]
    calf_fat = get_weighted_random(elements, weights)
    self.set_player_integer_field('PFCS', index, calf_fat)
    
    # PFGS: A random distribution from 0 to 20, where the most likely value is 5 and the least likely is 20.
    elements = list(range(0, 21))
    weights = [4, 4, 6, 8, 12, 15, 12, 8, 6, 4, \
               3, 3, 2, 2, 2, 2, 2, 2, 1, 1, 1]
    glute_fat = get_weighted_random(elements, weights)
    self.set_player_integer_field('PFGS', index, glute_fat)
    
    # PFHS: A random distribution from 0 to 20, where the most likely value is 5 and the least likely is 20.
    elements = list(range(0, 21))
    weights = [4, 4, 6, 8, 12, 15, 12, 8, 6, 4, \
               3, 3, 2, 2, 2, 2, 2, 2, 1, 1, 1]
    thigh_fat = get_weighted_random(elements, weights)
    self.set_player_integer_field('PFHS', index, thigh_fat)
    
    # PFTS: A random distribution from 0 to 25, where the most likely value is 0 and the least likely is 25.
    elements = list(range(0, 26))
    weights = [8, 8, 8, 8, 8, 8, 7, 6, 5, 4, 3, 3, 3, \
               2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1]
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
    
    # PMAS: A random distribution from 0 to 25, where the most likely value is 10 and the least likely is 25.
    elements = list(range(0, 26))
    weights = [1, 1, 2, 2, 3, 4, 5, 6, 7, 9, 12, 9, 7, \
               6, 5, 4, 3, 3, 2, 2, 2, 1, 1, 1, 1, 1]
    arm_muscle = get_weighted_random(elements, weights)
    self.set_player_integer_field('PMAS', index, arm_muscle)
    
    # PMCS: A random distribution from 0 to 30, where the most likely value is 10 and the least likely is 30.
    elements = list(range(0, 31))
    weights = [1, 1, 1, 2, 2, 3, 3, 5, 7, 10, 13, 10, 7, 5, 3, 3, \
               3, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1]
    calf_muscle = get_weighted_random(elements, weights)
    self.set_player_integer_field('PMCS', index, calf_muscle)
    
    # PMHS: Random distribution from 0 to 25, where the most likely value is 10 and the least likely are 0 and 25.
    elements = list(range(0, 26))
    weights = [1, 1, 2, 2, 3, 4, 5, 6, 7, 9, 12, 9, 7, \
               6, 5, 4, 3, 3, 2, 2, 2, 1, 1, 1, 1, 1]
    thigh_muscle = get_weighted_random(elements, weights)
    self.set_player_integer_field('PMHS', index, thigh_muscle)
    
    # PMOR: Set 20% to between 50 - 79, 20% to 80 - 89, and 60% to 90 - 99.
    elements = list(range(50, 80)) + list(range(80, 90)) + list(range(90, 100))
    weights = [2/3]*30 + [2]*10 + [6]*10
    morale = get_weighted_random(elements, weights)
    self.set_player_integer_field('PMOR', index, morale)
    
    # PMTS: A random distribution from 0 to 25, where the most likely value is 5 and the least likely is 25.
    elements = list(range(0, 26))
    weights = [2, 4, 6, 8, 11, 14, 11, 8, 6, 4, 3, 3, 2, \
               2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1]
    mid_torso = get_weighted_random(elements, weights)
    self.set_player_integer_field('PMTS', index, mid_torso)
    
    # POID: Just set this to the same number as PGID.
    self.set_player_integer_field('POID', index, index)
    
    # PSBS: Random distribution from 34 to 99, where the most likely value is 79 and the least likely is 34.
    elements = list(range(34, 100))
    weights = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, \
               1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, \
               1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, \
               2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, \
               5, 10, 5, 3, 2, 2, 1, 1, 1, 1, 1, \
               1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    subtract_for_body_size = get_weighted_random(elements, weights)
    self.set_player_integer_field('PSBS', index, subtract_for_body_size)
    
    # PUTS: A random distribution from 5 to 40, where the most likely value is 10 and the least likely is 40.
    elements = list(range(5, 41))
    weights = [1, 1, 2, 4, 8, 15, 8, 4, 3, \
               3, 3, 3, 3, 3, 3, 3, 3, 3, \
               2, 2, 2, 2, 2, 2, 2, 2, 2, \
               1, 1, 1, 1, 1, 1, 1, 1, 1]
    upper_torso = get_weighted_random(elements, weights)
    self.set_player_integer_field('PUTS', index, upper_torso)
    
    
    # These calculations use the results of previous calculations.
    
    # PTEN: If the CSV is -1, use the QB's awareness, speed, acceleration, and agility attributes to determine his 
    # tendency.
    if int(player_dict["tendency"]) == -1:
        # If any one of the QB's speed, acceleration, or agility ratings is too low, he is a pocket passer. 
        if speed < 70 or acceleration < 75 or agility < 70:
            tendency = 0 # pocket passer
        # If the QB has good speed, acceleration, and agility but not enough awareness, he is a scrambler.
        elif speed > 80 and acceleration > 80 and agility > 80 and awareness < 85:
            tendency = 1 # scrambling
        else:
            tendency = 2 # balanced
    else:
        tendency = int(player_dict["tendency"])
    self.set_player_integer_field('PTEN', index, tendency)
    
    # PBRE: If the QB has a PTEN of 1 (Scrambling), give him a 40% chance of getting a 0 (none), a 30% chance of 
    # getting a 1 (white strip), and a 30% chance of getting a 2 (black strip).
    if int(player_dict["breathing_strip"]) == -1:
        if tendency == 1:
            elements = [0, 1, 2]
            weights = [40, 30, 30]
            breathing_strip = get_weighted_random(elements, weights)
        else:
            breathing_strip = 0
    else:
        breathing_strip = int(player_dict["breathing_strip"])
    self.set_player_integer_field('PBRE', index, breathing_strip)
    
    # PHLM: Check the value from PFMK. If it was set to 11, we must use 4. Otherwise, see what is in the CSV. If 
    # it is -1, give 80% a 0 (Style 1) and 20% a 2 (Style 3).
    if face_mask == 11:
        helmet = 4
    elif int(player_dict["helmet"]) == -1:
        elements = [0, 2]
        weights = [80, 20]
        helmet = get_weighted_random(elements, weights)
    else:
        helmet = int(player_dict["helmet"])
    self.set_player_integer_field('PHLM', index, helmet)
    
    # PGSL: If the CSV has -1 and we didn't set PLEL, PREL, PTAL, or PTAR to anything but 0, set 86% to 0 (none), 
    # 2% to 1 (black), 10% to 2 (white), and 2% to 3 (team-color). (For others, just use 0.)
    if int(player_dict["sleeves"]) == -1:
        if (left_elbow == 0 and 
                right_elbow == 0 and 
                int(player_dict["tattoo_left"]) == 0 and 
                int(player_dict["tattoo_right"]) == 0):
            elements = [0, 1, 2, 3]
            weights = [86, 2, 10, 2]
            sleeves = get_weighted_random(elements, weights)
        else:
            sleeves = 0
    else:
        sleeves = int(player_dict["sleeves"])
    self.set_player_integer_field('PGSL', index, sleeves)
    
    # POVR: Use the formula found in 04 - FORMULA for Calculating Overall Rating.txt
    overall_rating = 0.0
    overall_rating += ((throw_power - 50.0) / 10.0) * 4.9
    overall_rating += ((throw_accuracy - 50.0) / 10.0) * 5.8
    overall_rating += ((break_tackles - 50.0) / 10.0) * 0.8
    overall_rating += ((agility - 50.0) / 10.0) * 0.8
    overall_rating += ((awareness - 50.0) / 10.0) * 4.0
    overall_rating += ((speed - 50.0) / 10.0) * 2.0
    overall_rating = int(max(min((round(overall_rating) + 28), 99), 40))
    self.set_player_integer_field('POVR', index, overall_rating)
    
    # PIMP: We're relating the importance of a player to his overall rating and his position. QB is the most 
    # important position, so we will give the highest importance ratings to good ones. 
    importance = int(max(min(math.ceil((math.pow((overall_rating / 100), 2) * 85) + (overall_rating - 68)), 99), 15))
    self.set_player_integer_field('PIMP', index, importance)
    
    # PROL: Check for these roles IN THIS ORDER: 1) injury_prone 2) team_distraction 3) franchise_qb 
    # 4) qb_of_the_future 5) project_player 6) underachiever 7) precision_passer 8) cannon_arm 9) scrambler 
    # 10) game_manager 11) fan_favorite 12) team_mentor 13) team_leader 14) first_round_pick .
    role_one = int(player_dict["role_one"])
    if role_one == 45:
        if player_roles.is_injury_prone(role_one, injury, toughness):
            role_one = 14
        elif player_roles.is_team_distraction(role_one, morale, importance):
            role_one = 8
        elif player_roles.is_franchise_qb(role_one, awareness, overall_rating):
            role_one = 20
        elif player_roles.is_qb_of_the_future(role_one, draft_round, years_pro, throw_power, throw_accuracy, 
                                              overall_rating):
            role_one = 0
        elif player_roles.is_project_player(role_one, overall_rating, years_pro, awareness, position, throw_power, 
                                            throw_accuracy, speed, acceleration, break_tackles, agility, strength, 
                                            kick_power):
            role_one = 7
        elif player_roles.is_underachiever(role_one, draft_round, draft_pick, years_pro, overall_rating):
            role_one = 4
        elif player_roles.is_precision_passer(role_one, throw_accuracy):
            role_one = 17
        elif player_roles.is_cannon_arm(role_one, throw_accuracy):
            role_one = 18
        elif player_roles.is_scrambler(role_one, speed, acceleration, agility):
            role_one = 19
        elif player_roles.is_game_manager(role_one, years_pro, awareness, throw_power, throw_accuracy, 
                                          overall_rating):
            role_one = 10
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
        elif player_roles.is_team_distraction(role_one, morale, importance):
            role_two = 8
        elif player_roles.is_franchise_qb(role_one, awareness, overall_rating):
            role_two = 20
        elif player_roles.is_qb_of_the_future(role_one, draft_round, years_pro, throw_power, throw_accuracy, 
                                              overall_rating):
            role_two = 0
        elif player_roles.is_project_player(role_one, overall_rating, years_pro, awareness, position, throw_power, 
                                            throw_accuracy, speed, acceleration, break_tackles, agility, strength, 
                                            kick_power):
            role_two = 7
        elif player_roles.is_underachiever(role_one, draft_round, draft_pick, years_pro, overall_rating):
            role_two = 4
        elif player_roles.is_precision_passer(role_one, throw_accuracy):
            role_two = 17
        elif player_roles.is_cannon_arm(role_one, throw_accuracy):
            role_two = 18
        elif player_roles.is_scrambler(role_one, speed, acceleration, agility):
            role_two = 19
        elif player_roles.is_game_manager(role_one, years_pro, awareness, throw_power, throw_accuracy, 
                                          overall_rating):
            role_two = 10
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

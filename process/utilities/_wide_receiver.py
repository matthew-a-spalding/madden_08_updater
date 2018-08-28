r""" _wide_receiver.py
    
    This is one of the 21 method-definition modules used by the main RosterManager class. This module contains the 
    method used to populate the fields for a wide_receiver record in the roster DB.
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

def create_wide_receiver(self, player_dict, index):
    """
    Given a dictionary of a new player and the index of the related record to modify in the DB, performs all of 
    the calculations and updates necessary to create the player as a WR in the DB.
    """
    
    position = 3 # WR
    
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
    
    # PBRE: If the value in the CSV is -1, give 65% a 0 (none), 20% a 1 (white), and 15% a 2 (black).
    if int(player_dict["breathing_strip"]) == -1:
        elements = [0, 1, 2]
        weights = [65, 20, 15]
        breathing_strip = get_weighted_random(elements, weights)
    else:
        breathing_strip = int(player_dict["breathing_strip"])
    self.set_player_integer_field('PBRE', index, breathing_strip)
    
    # The college ID is simply picked from a list.
    self.set_player_integer_field('PCOL', index, self.get_college_id(player_dict["college"]))
    
    # For eye_black, if the CSV says -1, give 75% a 0 (none) and 25% a 1 (black).
    if int(player_dict["eye_black"]) == -1:
        elements = [0, 1]
        weights = [75, 25]
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
    
    # If the value in the CSV is -1, set 40% to 0 (2-bar), 25% to 1 (3-bar), 15% to 7 (2-Bar RB), 15% to 8 (3-Bar RB), 
    # and 5% to 11. NOTE!! If choosing 11, must also set PHLM to 4 !!
    if int(player_dict["face_mask"]) == -1:
        elements = [0, 1, 7, 8, 11]
        weights = [40, 25, 15, 15, 5]
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
    
    # For left_elbow, if the value in the CSV is -1, set 50% to 0 (none), 10% to 1 (turf tape), 15% to 7 (black 
    # wrist), 15% to 8 (white wrist), and 10% to 9 (team-color wrist).
    if int(player_dict["left_elbow"]) == -1:
        elements = [0, 1, 7, 8, 9]
        weights = [50, 10, 15, 15, 10]
        left_elbow = get_weighted_random(elements, weights)
    else:
        left_elbow = int(player_dict["left_elbow"])
    self.set_player_integer_field('PLEL', index, left_elbow)
    
    # For left_hand, if the value in the CSV is -1, set 6% to 0 (none), 30% to 2 (black gloves), 15% to 3 (white 
    # gloves), 40% to 4 (team-color gloves), 3% to 5 (white RB gloves), 3% to 6 (black RB gloves), and 3% to 7 
    # (team-color RB gloves).
    if int(player_dict["left_hand"]) == -1:
        elements = [0, 2, 3, 4, 5, 6, 7]
        weights = [6, 30, 15, 40, 3, 3, 3]
        left_hand = get_weighted_random(elements, weights)
    else:
        left_hand = int(player_dict["left_hand"])
    self.set_player_integer_field('PLHA', index, left_hand)
    
    # Get the first 13 characters of the last name.
    if len(player_dict["last_name"]) < 14:
        self.set_player_string_field('PLNA', index, player_dict["last_name"])
    else:
        self.set_player_string_field('PLNA', index, player_dict["last_name"][:13])
    
    # For left_shoe, if the value in the CSV is -1, just use 0 (none).
    if int(player_dict["left_shoe"]) == -1:
        left_shoe = 0
    else:
        left_shoe = int(player_dict["left_shoe"])
    self.set_player_integer_field('PLSH', index, left_shoe)
    
    # For left_knee, if the value in the CSV is -1, just use 0 (none). 
    if int(player_dict["left_knee"]) == -1:
        left_knee = 0
    else:
        left_knee = int(player_dict["left_knee"])
    self.set_player_integer_field('PLTH', index, left_knee)
    
    # For left_wrist, set 70% to 0 (Normal), 10% to 2 (White wrist), 10% to 3 (Black wrist), and 10% to 4 (team-color 
    # wrist).
    if int(player_dict["left_wrist"]) == -1:
        elements = [0, 2, 3, 4]
        weights = [70, 10, 10, 10]
        left_wrist = get_weighted_random(elements, weights)
    else:
        left_wrist = int(player_dict["left_wrist"])
    self.set_player_integer_field('PLWR', index, left_wrist)
    
    # For mouthpiece, give 70% of players 0 (none), 10% 1 (white), 10% 2 (black), and 10% 3 (team-color).
    if int(player_dict["mouthpiece"]) == -1:
        elements = [0, 1, 2, 3]
        weights = [70, 10, 10, 10]
        mouthpiece = get_weighted_random(elements, weights)
    else:
        mouthpiece = int(player_dict["mouthpiece"])
    self.set_player_integer_field('PMPC', index, mouthpiece)
    
    # For neck_pad, if the value in the CSV is -1, just use 0 (none).
    if int(player_dict["neck_pad"]) == -1:
        neck_pad = 0
    else:
        neck_pad = int(player_dict["neck_pad"])
    self.set_player_integer_field('PNEK', index, neck_pad)
    
    # For right_elbow, if the value in the CSV is -1: If PLEL was 0, set 70% to 0, and 10% to each of 7, 8, and 9. If 
    # PLEL was 1, set 100% to 1. If it was an other non-zero, value set 80% to the same value, and 20% to 0.
    if int(player_dict["right_elbow"]) == -1:
        if left_elbow == 0:
            elements = [0, 7, 8, 9]
            weights = [70, 10, 10, 10]
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
    
    # For right_shoe, if the CSV says -1, just use 0. Otherwise, just use what is in the file.
    if int(player_dict["right_shoe"]) == -1:
        right_shoe = 0
    else:
        right_shoe = int(player_dict["right_shoe"])
    self.set_player_integer_field('PRSH', index, right_shoe)
    
    # For right_knee, if the CSV says -1, always use 0.
    if int(player_dict["right_knee"]) == -1:
        right_knee = 0
    else:
        right_knee = int(player_dict["right_knee"])
    self.set_player_integer_field('PRTH', index, right_knee)
    
    # For right_wrist, if the value in the CSV is -1: If PLWR was 0, set 70% to 0, and 10% to each of 2, 3, and 4. If 
    # PLWR was non-zero, set 80% to the same value, and 20% to 0.
    if int(player_dict["right_wrist"]) == -1:
        if left_wrist == 0:
            elements = [0, 2, 3, 4]
            weights = [70, 10, 10, 10]
            right_wrist = get_weighted_random(elements, weights)
        else:
            elements = [left_wrist, 0]
            weights = [80, 20]
            right_wrist = get_weighted_random(elements, weights)
    else:
        right_wrist = int(player_dict["right_wrist"])
    self.set_player_integer_field('PRWR', index, right_wrist)
    
     # For visor, if the value in the CSV is -1, set 75% to 0 (none), 20% to 1 (clear), and 5% to 2 (dark).
    if int(player_dict["visor"]) == -1:
        elements = [0, 1, 2]
        weights = [75, 20, 5]
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
    
    speed = int(max(min(int(player_dict["speed"]), 99), 80))
    self.set_player_integer_field('PSPD', index, speed)
    
    strength = int(max(min(int(player_dict["strength"]), 85), 35))
    self.set_player_integer_field('PSTR', index, strength)
    
    awareness = int(max(min(int(player_dict["awareness"]), 99), 35))
    self.set_player_integer_field('PAWR', index, awareness)
    
    agility = int(max(min(int(player_dict["agility"]), 99), 75))
    self.set_player_integer_field('PAGI', index, agility)
    
    acceleration = int(max(min(int(player_dict["acceleration"]), 99), 75))
    self.set_player_integer_field('PACC', index, acceleration)
    
    carrying = int(max(min(int(player_dict["carrying"]), 95), 45))
    self.set_player_integer_field('PCAR', index, carrying)
    
    catching = int(max(min(int(player_dict["catching"]), 99), 65))
    self.set_player_integer_field('PCTH', index, catching)
    
    jumping = int(max(min(int(player_dict["jumping"]), 99), 65))
    self.set_player_integer_field('PJMP', index, jumping)
    
    break_tackles = int(max(min(
        math.ceil((int(player_dict["elusiveness"]) + int(player_dict["trucking"]) - 10) / 2), 
        80), 35))
    self.set_player_integer_field('PBTK', index, break_tackles)
    
    tackle = int(max(min(int(player_dict["tackle"]), 70), 15))
    self.set_player_integer_field('PTAK', index, tackle)
    
    throw_power = int(max(min(int(player_dict["throw_power"]), 90), 20))
    self.set_player_integer_field('PTHP', index, throw_power)
    
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
    ), 80), 20))
    self.set_player_integer_field('PTHA', index, throw_accuracy)
    
    pass_block = int(max(min(math.ceil(
        (
            int(player_dict["pass_block"]) + 
            int(player_dict["pass_block_power"]) + 
            int(player_dict["pass_block_finesse"])
        ) / 3
    ), 65), 20))
    self.set_player_integer_field('PPBK', index, pass_block)
    
    run_block = int(max(min(math.ceil(
        (
            int(player_dict["run_block"]) + 
            int(player_dict["run_block_power"]) + 
            int(player_dict["run_block_finesse"])
        ) / 3
    ), 75), 20))
    self.set_player_integer_field('PRBK', index, run_block)
    
    kick_power = int(max(min(int(player_dict["kick_power"]), 50), 10))
    self.set_player_integer_field('PKPR', index, kick_power)
    
    kick_accuracy = int(max(min(int(player_dict["kick_accuracy"]), 50), 5))
    self.set_player_integer_field('PKAC', index, kick_accuracy)
    
    kick_return = int(max(min(int(player_dict["kick_return"]), 99), 20))
    self.set_player_integer_field('PKRT', index, kick_return)
    
    stamina = int(max(min(int(player_dict["stamina"]), 99), 65))
    self.set_player_integer_field('PSTA', index, stamina)
    
    injury = int(max(min(int(player_dict["injury"]), 99), 60))
    self.set_player_integer_field('PINJ', index, injury)
    
    toughness = int(max(min(int(player_dict["toughness"]), 99), 45))
    self.set_player_integer_field('PTGH', index, toughness)
    
    
    # For the following attributes, we will use weighted random distributions or other non-dependant means without 
    # checking the CSV file at all.
    
    # PCHS: A random distribution from 0 to 30, where the most likely value is 5 and the least likely is 30.
    elements = list(range(0, 31))
    weights = [1, 2, 4, 6, 10, 15, 10, 7, 5, 4, 3, 3, 3, 3, 2, 2, \
               2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    chest_shelf = get_weighted_random(elements, weights)
    self.set_player_integer_field('PCHS', index, chest_shelf)
    
    # PEGO: Set 3% to 0, 6% to something btwn 1 - 20, 3% to btwn 21 - 40, 3% to btwn 41 - 50, 20% to btwn 51 - 60, 25% 
    # to btwn 61 - 80, 25% to btwn 81 - 90, and 15% to btwn 91 - 99.
    elements = list(range(0, 100))
    weights = [3.0] + [0.3]*20 + [.15]*20 + [.3]*10 + [2.0]*10 + [1.25]*20 + [2.5]*10 + [1.6666]*9
    ego = get_weighted_random(elements, weights)
    self.set_player_integer_field('PEGO', index, ego)
    
    # PFAS: A random distribution from 0 to 10, where the most likely value is 0 and the least likely is 10.
    elements = list(range(0, 11))
    weights = [24, 21, 17, 12, 8, 6, 4, 3, 2, 2, 1]
    arm_fat = get_weighted_random(elements, weights)
    self.set_player_integer_field('PFAS', index, arm_fat)
    
    # PFCS: A random distribution from 0 to 15, where the most likely value is 0 and the least likely is 15.
    elements = list(range(0, 16))
    weights = [17, 16, 15, 12, 9, 6, 5, 4, 3, 3, 3, 2, 2, 1, 1, 1]
    calf_fat = get_weighted_random(elements, weights)
    self.set_player_integer_field('PFCS', index, calf_fat)
    
    # PFGS: A random distribution from 0 to 20, where the most likely value is 5 and the least likely is 20.
    elements = list(range(0, 21))
    weights = [3, 5, 6, 8, 11, 16, 11, 8, 6, 5, 4, 3, 3, 2, 2, 2, 1, 1, 1, 1, 1]
    glute_fat = get_weighted_random(elements, weights)
    self.set_player_integer_field('PFGS', index, glute_fat)
    
    # PFHS: A random distribution from 0 to 20, where the most likely value is 5 and the least likely is 20.
    elements = list(range(0, 21))
    weights = [3, 5, 6, 8, 11, 16, 11, 8, 6, 5, 4, 3, 3, 2, 2, 2, 1, 1, 1, 1, 1]
    thigh_fat = get_weighted_random(elements, weights)
    self.set_player_integer_field('PFHS', index, thigh_fat)
    
    # PFTS: A random distribution from 0 to 20, where the most likely value is 0 and the least likely is 20.
    elements = list(range(0, 21))
    weights = [18, 16, 14, 8, 6, 5, 4, 4, 3, 3, \
               3, 3, 2, 2, 2, 2, 1, 1, 1, 1, 1]
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
    
    # PMAS: A random distribution from 0 to 35, where the most likely value is 10 and the least likely is 35.
    elements = list(range(0, 36))
    weights = [1, 1, 1, 2, 2, 3, 3, 4, 6, 9, 13, 9, 6, 4, 3, 3, 3, 3, \
               2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    arm_muscle = get_weighted_random(elements, weights)
    self.set_player_integer_field('PMAS', index, arm_muscle)
    
    # PMCS: A random distribution from 0 to 45, where the most likely value is 15 and the least likely is 45.
    elements = list(range(0, 46))
    weights = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 3, 5, 7, 11, \
               8, 6, 4, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2, 2, \
               1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    calf_muscle = get_weighted_random(elements, weights)
    self.set_player_integer_field('PMCS', index, calf_muscle)
    
    # PMHS: A random distribution from 0 to 60, where the most likely value is 20 and the least likely are 0 and 60.
    elements = list(range(0, 61))
    weights = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 3, 3, 5, 6, 8, \
               6, 5, 3, 3, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, \
               1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    thigh_muscle = get_weighted_random(elements, weights)
    self.set_player_integer_field('PMHS', index, thigh_muscle)
    
    # PMOR: Set 20% to between 50 - 79, 20% to 80 - 89, and 60% to 90 - 99.
    elements = list(range(50, 80)) + list(range(80, 90)) + list(range(90, 100))
    weights = [2/3]*30 + [2]*10 + [6]*10
    morale = get_weighted_random(elements, weights)
    self.set_player_integer_field('PMOR', index, morale)
    
    # PMTS: A random distribution from 0 to 25, where the most likely value is 5 and the least likely is 25.
    elements = list(range(0, 26))
    weights = [1, 2, 4, 6, 8, 10, 9, 8, 7, 6, 6, 5, 4, \
               3, 3, 3, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1]
    mid_torso = get_weighted_random(elements, weights)
    self.set_player_integer_field('PMTS', index, mid_torso)
    
    # POID: Just set this to the same number as PGID.
    self.set_player_integer_field('POID', index, index)
    
    # PSBS: A random distribution from 39 to 99, where the most likely value is 79 (to result in a Body Overall Size 
    # of 20), and the least likely is 39 (Overall = 60).
    elements = list(range(39, 100))
    weights = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, \
               1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 3, 6, 9, \
               6, 4, 3, 3, 3, 3, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    subtract_for_body_size = get_weighted_random(elements, weights)
    self.set_player_integer_field('PSBS', index, subtract_for_body_size)
    
    # PUTS: A random distribution from 5 to 40, where the most likely value is 10 and the least likely is 40.
    elements = list(range(5, 41))
    weights = [1, 2, 3, 5, 8, 11, 9, 7, 5, 4, 3, 3, 3, 3, 3, 3, 2, 2, \
               2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    upper_torso = get_weighted_random(elements, weights)
    self.set_player_integer_field('PUTS', index, upper_torso)
    
    
    # These calculations use the results of previous calculations.
    
    # PTEN: If the CSV is -1, use the WR's speed, acceleration, and catching attributes to determine the tendency.
    if int(player_dict["tendency"]) == -1:
        # If the WR has enough catching ability (or simply no speed), call him a possession receiver.
        if speed < 85 or (catching > 84 and speed < 90 and acceleration < 95):
            tendency = 0 # possession
        # Otherwise, if the WR has enough overall running ability, call him a speed receiver.
        elif catching < 91 and speed > 90 and acceleration > 88:
            tendency = 1 # speed
        else:
            tendency = 2 # balanced
    else:
        tendency = int(player_dict["tendency"])
    self.set_player_integer_field('PTEN', index, tendency)
    
    # PHLM: Check PFMK. If it was 11, we must use 4. Otherwise, give 80% 0 (Style 1) and 20% 2 (Style 3).
    if face_mask == 11:
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
    overall_rating += ((break_tackles - 50.0) / 10.0) * 0.8
    overall_rating += ((acceleration - 50.0) / 10.0) * 2.3
    overall_rating += ((agility - 50.0) / 10.0) * 2.3
    overall_rating += ((awareness - 50.0) / 10.0) * 2.3
    overall_rating += ((strength - 50.0) / 10.0) * 0.8
    overall_rating += ((speed - 50.0) / 10.0) * 2.3
    overall_rating += ((catching - 50.0) / 10.0) * 4.75
    overall_rating += ((jumping - 50.0) / 10.0) * 1.4
    overall_rating = int(max(min((round(overall_rating) + 26), 99), 40))
    self.set_player_integer_field('POVR', index, overall_rating)
    
    # PIMP: We're relating the importance of a player to his overall rating and his position. WRs should be of average 
    # importance, so use the following:  int(max(min(ceil((([POVR]/100)^2) * 70) + ([POVR] - 70), 99), 15))
    importance = int(max(min(math.ceil((math.pow((overall_rating / 100), 2) * 70) + (overall_rating - 70)), 99), 15))
    self.set_player_integer_field('PIMP', index, importance)
    
    # PROL: Check for these roles IN THIS ORDER: 1) injury_prone, 2) team_distraction, 3) underachiever, 4) 
    # fumble_prone, 5) go_to_guy, 6) deep_threat, 7) possession_receiver, 8) project_player, 9) fan_favorite, 10) 
    # team_mentor, 11) team_leader, 12) first_round_pick.
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
        elif player_roles.is_go_to_guy(role_one, position, speed, catching, overall_rating):
            role_one = 35
        elif player_roles.is_deep_threat(role_one, position, speed, acceleration):
            role_one = 36
        elif player_roles.is_possession_receiver(role_one, position, catching, awareness):
            role_one = 37
        elif player_roles.is_return_specialist(role_one, speed, acceleration, agility, kick_return, overall_rating):
            role_one = 11
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
    # fumble_prone, 5) go_to_guy, 6) deep_threat, 7) possession_receiver, 8) project_player, 9) fan_favorite, 10) 
    # team_mentor, 11) team_leader, 12) first_round_pick.
    role_two = int(player_dict["role_two"])
    if role_two == 45 and role_one != 45:
        if player_roles.is_injury_prone(role_one, injury, toughness):
            role_two = 14
        elif player_roles.is_team_distraction(role_one, morale, importance):
            role_two = 8
        elif player_roles.is_underachiever(role_one, draft_round, draft_pick, years_pro, overall_rating):
            role_two = 4
        elif player_roles.is_fumble_prone(role_one, carrying):
            role_two = 15
        elif player_roles.is_go_to_guy(role_one, position, speed, catching, overall_rating):
            role_two = 35
        elif player_roles.is_deep_threat(role_one, position, speed, acceleration):
            role_two = 36
        elif player_roles.is_possession_receiver(role_one, position, catching, awareness):
            role_two = 37
        elif player_roles.is_return_specialist(role_one, speed, acceleration, agility, kick_return, overall_rating):
            role_two = 11
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

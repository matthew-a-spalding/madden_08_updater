r""" player_roles.py
    
    This module contains only the helper functions that determine if a player is a match for a certain role.
"""

import math

def is_cannon_arm(role_one, throw_power):
    """ Determines whether the given values qualify a player to be labeled as a 'cannon arm'. """
    if role_one in [18]:
        return False
    if throw_power > 92:
        return True
    return False

def is_deep_threat(role_one, position, speed, acceleration):
    """ Determines whether the given values qualify a player to be labeled as a 'deep threat'. """
    if role_one in [35, 36, 37]:
        return False
    # WRs
    if position == 3:
        if (speed > 89 and acceleration > 93) or (speed > 92 and acceleration > 89):
            return True
    # TEs
    elif position == 4:
        if (speed > 86 and acceleration > 89) or (speed > 89 and acceleration > 86):
            return True
    return False

def is_defensive_enforcer(role_one, speed, strength):
    """ Determines whether the given values qualify a player to be labeled as a 'defensive enforcer'. """
    if role_one in [41, 42, 27, 39, 40, 28]:
        return False
    if speed > 85 and strength > 79:
        return True
    return False

def is_elusive_back(role_one, acceleration, agility):
    """ Determines whether the given values qualify a player to be labeled as an 'elusive back'. """
    if role_one in [21, 22, 23]:
        return False
    if acceleration > 90 and agility > 90:
        return True
    return False

def is_fan_favorite(role_one, years_pro, morale, overall_rating):
    """ Determines whether the given values qualify a player to be labeled as a 'fan favorite'. """
    if role_one in [8, 13]:
        return False
    if years_pro > 5 and morale > 80 and overall_rating > 90:
        return True
    return False

def is_feature_back(role_one, awareness, speed, acceleration, agility, break_tackles, carrying, overall_rating):
    """ Determines whether the given values qualify a player to be labeled as a 'feature back'. """
    if role_one in [34, 14, 15]:
        return False
    if (awareness > 75 and speed > 88 and acceleration > 90 and agility > 88 and break_tackles > 70 and carrying > 74 
            and overall_rating > 88):
        return True
    return False

def is_first_round_pick(role_one, draft_round):
    """ Determines whether the given values qualify a player to be labeled as a 'first round pick'. """
    if role_one in [12]:
        return False
    if draft_round == 1:
        return True
    return False

def is_force_of_nature(role_one, position, acceleration, strength):
    """ Determines whether the given values qualify a player to be labeled as a 'force of nature'. """
    if role_one in [27, 28, 39, 40]:
        return False
    if position in [10, 11]: #L/REs
        if acceleration > 85 and strength > 85:
            return True
    if position == 12: #DTs
        if acceleration > 83 and strength > 88:
            return True
    if position in [13, 14, 15]: #LBs
        if acceleration > 87 and strength > 82:
            return True
    return False

def is_franchise_qb(role_one, awareness, overall_rating):
    """ Determines whether the given values qualify a player to be labeled as a 'franchise QB'. """
    if role_one in [8, 14, 20]:
        return False
    if awareness > 79 and overall_rating > 87:
        return True
    return False

def is_fumble_prone(role_one, carrying):
    """ Determines whether the given values qualify a player to be labeled as 'fumble prone'. """
    if role_one in [15]:
        return False
    if carrying < 70:
        return True
    return False

def is_game_manager(role_one, years_pro, awareness, throw_power, throw_accuracy, overall_rating):
    """ Determines whether the given values qualify a player to be labeled as a 'game manager'. """
    if role_one in [10]:
        return False
    if years_pro > 4 and awareness > 74 and throw_power < 92 and throw_accuracy > 80 and overall_rating < 88:
        return True
    return False

def is_go_to_guy(role_one, position, speed, catching, overall_rating):
    """ Determines whether the given values qualify a player to be labeled as a 'go-to guy'. """
    if role_one in [35, 36, 37]:
        return False
    # WRs
    if position == 3:
        if speed > 88 and catching > 90 and overall_rating > 79:
            return True
    # TEs
    elif position == 4:
        if speed > 84 and catching > 85 and overall_rating > 79:
            return True
    return False

def is_heavy_hitter(role_one, position, tackle):
    """ Determines whether the given values qualify a player to be labeled as a 'heavy hitter'. """
    if role_one in [28, 27, 39, 40]:
        return False
    # L/REs
    if position in [10, 11]:
        if tackle > 83:
            return True
    # DTs
    if position == 12:
        if tackle > 89:
            return True
    # LBs
    if position in [13, 14, 15]:
        if tackle > 84:
            return True
    return False

def is_injury_prone(role_one, injury, toughness):
    """ Determines whether the given values qualify a player to be labeled as 'injury prone'. """
    if role_one in [14]:
        return False
    if injury < 71 and toughness < 81:
        return True
    return False

def is_pass_blocker(role_one, position, pass_block):
    """ Determines whether the given values qualify a player to be labeled as a 'pass blocker'. """
    if role_one in [25, 24, 26]:
        return False
    # FBs
    if position == 2:
        if pass_block > 65:
            return True
    # TEs
    elif position == 4:
        if pass_block > 65:
            return True
    # L/RTs
    elif position in [5, 9]:
        if pass_block > 87:
            return True
    # L/RGs
    elif position in [6, 8]:
        if pass_block > 84:
            return True
    # Cs
    elif position == 7:
        if pass_block > 84:
            return True
    return False

def is_pass_rusher(role_one, position, speed, acceleration):
    """ Determines whether the given values qualify a player to be labeled as a 'pass rusher'. """
    if role_one in [39, 27, 28, 40, 41, 42]:
        return False
    # L/REs
    if position in [10, 11]:
        if speed > 79 and acceleration > 86:
            return True
    # DTs
    if position == 12:
        if speed > 72 and acceleration > 83:
            return True
    # LBs
    if position in [13, 14, 15]:
        if speed > 84 and acceleration > 88:
            return True
    return False

def is_playmaker(role_one, speed, awareness):
    """ Determines whether the given values qualify a player to be labeled as a 'playmaker'. """
    if role_one in [42, 41, 27, 39, 40, 28]:
        return False
    if speed > 83 and awareness > 81:
        return True
    return False

def is_possession_receiver(role_one, position, catching, awareness):
    """ Determines whether the given values qualify a player to be labeled as a 'possession receiver'. """
    if role_one in [35, 36, 37]:
        return False
    # WRs
    if position == 3:
        if catching > 88 and awareness > 85:
            return True
    # TEs
    elif position == 4:
        if catching > 85 and awareness > 85:
            return True
    return False

def is_power_back(role_one, strength, break_tackles):
    """ Determines whether the given values qualify a player to be labeled as a 'power back'. """
    if role_one in [21, 22, 23]:
        return False
    if strength > 69 and break_tackles > 89:
        return True
    return False

def is_precision_passer(role_one, throw_accuracy):
    """ Determines whether the given values qualify a player to be labeled as a 'precision passer'. """
    if role_one in [17]:
        return False
    if throw_accuracy > 89:
        return True
    return False

def is_project_player(role_one, overall_rating, years_pro, awareness, position, throw_power, throw_accuracy, speed, 
                      acceleration, break_tackles, agility, strength, kick_power):
    """ Determines whether the given values qualify a player to be labeled as a 'project player'. """
    if role_one in [7]:
        return False
    if overall_rating > 87 or years_pro > 4 or awareness > 79:
        return False
    # QBs
    if position == 0:
        if (throw_power > 90 and throw_accuracy < 80) or (speed > 80 and acceleration > 82 and break_tackles > 57):
            return True
    # HBs
    elif position == 1:
        if (speed > 90 and acceleration > 90 and agility > 90) or (strength > 80 and break_tackles > 82):
            return True
    # FBs
    elif position == 2:
        if (speed > 82 and acceleration > 85 and strength > 70) or (strength > 80):
            return True
    # WRs
    elif position == 3:
        if speed > 89 and acceleration > 89 and agility > 89:
            return True
    # TEs
    elif position == 4:
        if (speed > 84 and acceleration > 86 and agility > 80) or strength > 80:
            return True
    # L/RTs
    elif position in [5, 9]:
        if (speed > 70 and acceleration > 80 and agility > 70 and strength > 86) or strength > 90:
            return True
    # L/RGs
    elif position in [6, 8]:
        if (speed > 66 and acceleration > 79 and agility > 65 and strength > 84) or strength > 90:
            return True
    # Cs
    elif position == 7:
        if (speed > 66 and acceleration > 79 and agility > 65 and strength > 84) or strength > 90:
            return True
    # L/REs
    elif position in [10, 11]:
        if (speed > 77 and acceleration > 84 and agility > 79 and strength > 75) or strength > 87:
            return True
    # DTs
    elif position == 12:
        if (speed > 69 and acceleration > 81 and agility > 67 and strength > 84) or strength > 88:
            return True
    # L/ROLBs
    elif position in [13, 15]:
        if (speed > 82 and acceleration > 86 and agility > 79 and strength > 75) or strength > 83:
            return True
    return False

def is_qb_of_the_future(role_one, draft_round, years_pro, throw_power, throw_accuracy, overall_rating):
    """ Determines whether the given values qualify a player to be labeled as a 'QB of the future'. """
    if role_one in [0]:
        return False
    if draft_round < 6 and years_pro < 5 and throw_power > 86 and throw_accuracy > 76 and overall_rating > 74:
        return True
    return False

def is_return_specialist(role_one, speed, acceleration, agility, kick_return, overall_rating):
    """ Determines whether the given values qualify a player to be labeled as a 'return specialist'. """
    if role_one in [11, 34, 35, 37]:
        return False
    if (overall_rating < 86 and speed > 89 and acceleration > 89 and agility > 89 and kick_return > 79 
            and math.ceil((speed + acceleration + agility) / 3) > 91):
        return True
    return False

def is_road_blocker(role_one, position, run_block, pass_block):
    """ Determines whether the given values qualify a player to be labeled as a 'road blocker'. """
    if role_one in [26, 24, 25]:
        return False
    # FBs
    if position == 2:
        if run_block > 69 and pass_block > 65:
            return True
    # TEs
    elif position == 4:
        if run_block > 69 and pass_block > 65:
            return True
    # L/RTs
    elif position in [5, 9]:
        if run_block > 84 and pass_block > 87:
            return True
    # L/RGs
    elif position in [6, 8]:
        if run_block > 87 and pass_block > 84:
            return True
    # Cs
    elif position == 7:
        if run_block > 84 and pass_block > 84:
            return True
    return False

def is_run_blocker(role_one, position, run_block):
    """ Determines whether the given values qualify a player to be labeled as a 'run blocker'. """
    if role_one in [24, 25, 26]:
        return False
    # FBs
    if position == 2:
        if run_block > 69:
            return True
    # TEs
    elif position == 4:
        if run_block > 69:
            return True
    #L/RTs
    elif position in [5, 9]:
        if run_block > 84:
            return True
    #L/RGs
    elif position in [6, 8]:
        if run_block > 87:
            return True
    #Cs
    elif position == 7:
        if run_block > 84:
            return True
    return False

def is_run_stopper(role_one, position, strength, tackle):
    """ Determines whether the given values qualify a player to be labeled as a 'run stopper'. """
    if role_one in [40, 27, 28, 39]:
        return False
    # L/REs
    if position in [10, 11]:
        if strength > 84 and tackle > 84:
            return True
    # DTs
    if position == 12:
        if strength > 89 and tackle > 86:
            return True
    # DTs
    if position in [13, 14, 15]:
        if strength > 79 and tackle > 80:
            return True
    return False

def is_scrambler(role_one, speed, acceleration, agility):
    """ Determines whether the given values qualify a player to be labeled as a 'scrambler'. """
    if role_one in [19]:
        return False
    if speed > 80 and acceleration > 80 and agility > 80:
        return True
    return False

def is_speed_back(role_one, speed, acceleration):
    """ Determines whether the given values qualify a player to be labeled as a 'speed back'. """
    if role_one in [21, 22, 23]:
        return False
    if speed > 94 or (speed > 92 and acceleration > 88) or (speed > 91 and acceleration > 90):
        return True
    return False

def is_team_distraction(role_one, morale, importance):
    """ Determines whether the given values qualify a player to be labeled as a 'team distraction'. """
    if role_one in [8, 5, 6]:
        return False
    if morale < 55 and importance > 60:
        return True
    return False

def is_team_leader(role_one, position, awareness, morale, years_pro, overall_rating):
    """ Determines whether the given values qualify a player to be labeled as a 'team leader'. """
    if role_one in [6, 5, 8] or position in [19, 20]:
        return False
    if awareness > 90 and morale > 74 and years_pro > 6 and overall_rating > 90:
        return True
    return False

def is_team_mentor(role_one, position, awareness, morale, years_pro, overall_rating):
    """ Determines whether the given values qualify a player to be labeled as a 'team mentor'. """
    if role_one in [5, 6, 8] or position in [19, 20]:
        return False
    if awareness > 87 and morale > 80 and years_pro > 8 and overall_rating > 85:
        return True
    return False

def is_underachiever(role_one, draft_round, draft_pick, years_pro, overall_rating):
    """ Determines whether the given values qualify a player to be labeled as an 'underachiever'. """
    if role_one in [4]:
        return False
    if draft_round == 1 and draft_pick < 16 and years_pro > 3 and years_pro < 10 and overall_rating < 83:
        return True
    return False

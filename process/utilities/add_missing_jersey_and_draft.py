r"""add_missing_jersey_and_draft.py
    
    This file opens (to read) the file "My 20[XX] Player Attributes - In Progress 20[XX]_MM_DD.csv", found in 
    "[BASE_MADDEN_PATH]docs\My Ratings\20[XX]" (where 20[XX] is the current year and MM_DD is the current date); it 
    also opens another file to write to, called "UPDATED My 20[XX] Player Attributes - In Progress 20[XX]_MM_DD.csv". 
    
    The main loop reads each record from the original file, performing a few tasks per row. First, if this player is 
    missing draft info, it sets those fields to the defaults (round 15, pick 63). Then, it checks to see if the 
    'jersey_number' field is blank. If so, it chooses the next number from the list associated with the player's 
    position in the dict POSSIBLE_POSITION_NUMBERS which is not also in assigned_jersey_numbers[team]. It subsequently 
    updates the list of assigned_jersey_numbers[team] and writes the record to the updated output file.
"""

# ----------------------------------------------------- SECTION 1 -----------------------------------------------------
# ----------------------------------------- IMPORTS, SETTINGS, AND CONSTANTS ------------------------------------------

# 1.1 - Standard library imports

import csv, os, random
#from ctypes import byref, cast, c_bool, c_char, c_char_p, c_int, POINTER, Structure, WinDLL
from datetime import datetime

# 1.2 - Third-party imports


# 1.3 - Application-specific imports


# 1.4 - Global settings


# 1.5 - Global constants

# Set the base path we will use to keep other paths relative, and shorter :^)
# This will be the directory above the directory above the directory this file is in.
BASE_MADDEN_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# This is the dict of all positions and which jersey numbers can be used for them.
    # "C":[50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79],
    # "CB":[20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49],
POSSIBLE_POSITION_NUMBERS = {
    "C":list(range(50, 80)),
    "CB":list(range(20, 50)),
    "DT":[50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, \
            70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99],
    "FB":list(range(20, 50)),
    "FS":list(range(20, 50)),
    "HB":list(range(20, 50)),
    "K":list(range(1, 20)),
    "LE":[50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, \
            70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99],
    "LG":list(range(60, 80)),
    "LOLB":[40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, \
            90, 91, 92, 93, 94, 95, 96, 97, 98, 99],
    "LT":list(range(60, 80)),
    "MLB":[40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, \
            90, 91, 92, 93, 94, 95, 96, 97, 98, 99],
    "P":list(range(1, 20)),
    "QB":list(range(1, 20)),
    "RE":[50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, \
            70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99],
    "RG":list(range(60, 80)),
    "ROLB":[40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, \
            90, 91, 92, 93, 94, 95, 96, 97, 98, 99],
    "RT":list(range(60, 80)),
    "SS":list(range(20, 50)),
    "TE":[40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89],
    "WR":[10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89],
}

# ----------------------------------------------------- SECTION 2 -----------------------------------------------------
# ------------------------------------------------ Class Declarations -------------------------------------------------


# ----------------------------------------------------- SECTION 3 -----------------------------------------------------
# ------------------------------------------------- Helper Functions --------------------------------------------------


# ----------------------------------------------------- SECTION 4 -----------------------------------------------------
# -------------------------------------------------- Main Function ----------------------------------------------------

# We need to figure out what the file's name will be, using today's date.
time_now = datetime.now()

full_path = BASE_MADDEN_PATH + r"\docs\My Ratings\{0}".format(time_now.year)

input_name = ("My " + str(time_now.year) + r" Player Attributes" + 
              r" - In Progress " + time_now.strftime("%Y_%m_%d") + ".csv")
output_name = ("Added Jersey and Draft - My " + str(time_now.year) + r" Player Attributes" + 
               r" - In Progress " + time_now.strftime("%Y_%m_%d") + ".csv")

# Open the file to read from/write to.
input_file = open(os.path.join(full_path, input_name), "r", newline='')

# Open the file to read from/write to.
output_file = open(os.path.join(full_path, output_name), "w", newline='')

# Create our DictReader.
player_attribute_dict_reader = csv.DictReader(input_file)

# Create our DictWriter.
player_attribute_dict_writer = csv.DictWriter(output_file, player_attribute_dict_reader.fieldnames)

# Write the header first.
player_attribute_dict_writer.writeheader()

# Initialize the variables we will need in the main logic loop.
working_team = "" # Team name string
assigned_jersey_numbers = {} # Dict of lists which will use team names as keys.

# Start looping over the records and performing our logic on each.
for player_dict in player_attribute_dict_reader:
    
    # See if this player's team is different from the previous player's team.
    if player_dict["team"] != working_team:
        # Update the current working_team
        working_team = player_dict["team"]
        # Create the new list for this team in our dict of assigned numbers.
        assigned_jersey_numbers[working_team] = []
    
    # Check this player's draft info.
    if player_dict["draft_round"] == "":
        player_dict["draft_round"] = str(15)
        player_dict["draft_pick"] = str(63)
    
    # See if this player is missing a jersey_number.
    if player_dict["jersey_number"] == "":
        # Find the next available jersey number for this team at this player's position.
        for jersey_number in POSSIBLE_POSITION_NUMBERS[player_dict["position"]]:
            if jersey_number not in assigned_jersey_numbers[working_team]:
                # Put this number into the player's record.
                player_dict["jersey_number"] = str(jersey_number)
                break
    
    # Just need ONE FINAL CHECK to make sure that the player now has a jersey number, in case all numbers were taken.
    if player_dict["jersey_number"] == "":
        player_dict["jersey_number"] = str(random.choice(POSSIBLE_POSITION_NUMBERS[player_dict["position"]]))
    
    # Now put this player's jersey_number into this team's list of assigned numbers.
    assigned_jersey_numbers[working_team].append(int(player_dict["jersey_number"]))
    
    # Write this player record out to the output file.
    player_attribute_dict_writer.writerow(player_dict)

# Close the output file.
output_file.close()

# Close the input file.
input_file.close()

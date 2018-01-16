r""" step_5_update_roster_file.py
    This is one of the two main Python scripts called when updating the base Madden NFL '08 roster file, to be called 
    using the syntax: 
        > python step_5_update_roster_file.py
    
    This script is only one part of the process for generating an updated Madden NFL '08 Roster file. Prior to running 
    this script, the first four steps of the process need to be performed. Please refer to the document 
    "step_1 README for Madden_08_Updater.docx" for more information. 
    
    This script requires the following files to be placed in the "utilities" folder alongside it, meaning in 
    os.path.join(os.path.dirname(os.path.abspath(__file__)), r"utilities\") : 
        1) The helper file, "helper_functions.py" 
        2) The folder and file "tdbaccess\old\tdbaccess.dll" 
    Additionally, the below files must be in the "inputs" folder, meaning in 
    os.path.join(os.path.dirname(os.path.abspath(__file__)), r"inputs\") : 
        1) The base Madden '08 Roster file to update, named "base.ros" 
        2) The latest NFL roster-based CSV file, named "Latest Player Attributes.csv" 
    
    This script will generate the file "latest.ros" in the folder "outputs".
"""

    
    # TODO: Figure out what to do in the two situations, where either 1) we have fewer players in the file 
    # 'Latest Player Attributes.csv' than in 'base.ros', or 2) we have more players. I'd imagine it will require 
    # getting the RecordCount from the TDBTablePropertiesStruct for the PLAY table, comparing it to the number of rows 
    # in the 'Latest Player Attributes.csv' file, and maybe updating NextDeletedRecord and/or DeletedCount on the 
    # table before compacting and saving the DB? At least for the first scenario. In the second scenario, I will 
    # probably need to call TDBTableRecordAdd before calling the attribute editors.
    
    
# ----------------------------------------------------- SECTION 1 -----------------------------------------------------
# ----------------------------------------- IMPORTS, SETTINGS, AND CONSTANTS ------------------------------------------
# 1 - Standard library imports

import csv, logging, os
#from importlib import reload

# 2 - Third-party imports

# 3 - Application-specific imports

from utilities import helper_functions as helper

# 4 - Global settings

# Set our logging level to Info.
#logging.shutdown()
#reload(logging)
logging.basicConfig(level=logging.INFO)

# 5 - Global constants

# Set the base path we will use to keep other paths relative, and shorter :^)
# This will be the directory above the directory this file is in.
BASE_MADDEN_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ----------------------------------------------------- SECTION 2 -----------------------------------------------------
# ------------------------------------------------ Class Declarations -------------------------------------------------


# ----------------------------------------------------- SECTION 3 -----------------------------------------------------
# ------------------------------------------------- Helper Functions --------------------------------------------------


# ----------------------------------------------------- SECTION 4 -----------------------------------------------------
# ------------------------------------------------ Main Functionality -------------------------------------------------

# Open the CSV file with all the players and their latest attributes.
with open(os.path.join(BASE_MADDEN_PATH, r"process\inputs\Latest Player Attributes.csv")) as PLAYER_ATTRIBUTES_FILE: 
    
    # Get a DictReader to read the rows into dicts using the header row as keys.
    ATTRIBUTES_DICT_READER = csv.DictReader(PLAYER_ATTRIBUTES_FILE)
    
    # Pull our records into a list so we can count them and iterate over them as often as needed.
    NEW_PLAYER_LIST = list(ATTRIBUTES_DICT_READER)

#logging.info("NEW_PLAYER_LIST[0] = %s", NEW_PLAYER_LIST[0])

# Get the number of new players (in the list).
NEW_PLAYER_COUNT = len(NEW_PLAYER_LIST)
logging.info("NEW_PLAYER_COUNT = %d", NEW_PLAYER_COUNT)

# Get the number of existing players (in the roster file).
EXISTING_PLAYER_COUNT = helper.get_existing_player_count()
logging.info("EXISTING_PLAYER_COUNT = %d", EXISTING_PLAYER_COUNT)

# If we have fewer new players than existing players, delete the excess. If we have more, create records for them.
if NEW_PLAYER_COUNT < EXISTING_PLAYER_COUNT:
    helper.delete_players(EXISTING_PLAYER_COUNT - NEW_PLAYER_COUNT)
elif NEW_PLAYER_COUNT > EXISTING_PLAYER_COUNT:
    helper.add_players(NEW_PLAYER_COUNT - EXISTING_PLAYER_COUNT)

# Loop over each element in the list and process the player's attributes for inserting into our roster file.
for i, player_dict in enumerate(NEW_PLAYER_LIST):
    
    # Determine which function to call based on the 'position' field value.
    if player_dict["position"].upper() == "QB":
        helper.create_quarterback(player_dict, i)
    elif player_dict["position"].upper() == "HB":
        helper.create_halfback(player_dict, i)
    elif player_dict["position"].upper() == "FB":
        helper.create_fullback(player_dict, i)
    elif player_dict["position"].upper() == "WR":
        helper.create_wide_receiver(player_dict, i)
    elif player_dict["position"].upper() == "TE":
        helper.create_tight_end(player_dict, i)
    elif player_dict["position"].upper() == "LT":
        helper.create_left_tackle(player_dict, i)
    elif player_dict["position"].upper() == "LG":
        helper.create_left_guard(player_dict, i)
    elif player_dict["position"].upper() == "C":
        helper.create_center(player_dict, i)
    elif player_dict["position"].upper() == "RG":
        helper.create_right_guard(player_dict, i)
    elif player_dict["position"].upper() == "RT":
        helper.create_right_tackle(player_dict, i)
    elif player_dict["position"].upper() == "LE":
        helper.create_left_end(player_dict, i)
    elif player_dict["position"].upper() == "RE":
        helper.create_right_end(player_dict, i)
    elif player_dict["position"].upper() == "DT":
        helper.create_defensive_tackle(player_dict, i)
    elif player_dict["position"].upper() == "LOLB":
        helper.create_left_outside_linebacker(player_dict, i)
    elif player_dict["position"].upper() == "MLB":
        helper.create_middle_linebacker(player_dict, i)
    elif player_dict["position"].upper() == "ROLB":
        helper.create_right_outside_linebacker(player_dict, i)
    elif player_dict["position"].upper() == "CB":
        helper.create_cornerback(player_dict, i)
    elif player_dict["position"].upper() == "FS":
        helper.create_free_safety(player_dict, i)
    elif player_dict["position"].upper() == "SS":
        helper.create_strong_safety(player_dict, i)
    elif player_dict["position"].upper() == "K":
        helper.create_kicker(player_dict, i)
    elif player_dict["position"].upper() == "P":
        helper.create_punter(player_dict, i)
    else:
        logging.error("Player %d's position was not recognized: %s", i, player_dict["position"].upper())

# Compact, save, and close the DB.
helper.compact_save_close_db()

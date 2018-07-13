r"""step_5_update_roster_file.py
    
    This is one of the two main Python scripts called when updating the base Madden NFL '08 roster file, to be called 
    using the syntax: 
        > python step_5_update_roster_file.py
    
    This script is only one part of the process for generating an updated Madden NFL '08 Roster file. Prior to running 
    this script, the first four steps of the process need to be performed. Please refer to the document 
    "step_1 README for madden_08_updater.txt" for more information. 
    
    This script requires the following files to be placed in the "utilities" folder alongside it, meaning in 
    os.path.join(os.path.dirname(os.path.abspath(__file__)), r"utilities\") : 
        1) The main helper file, "roster_manager.py"
        2) The individual position helper files, like "_center.py", etc.
        3) The file 'player_roles.py', used to decide which roles to assign to players
        4) The file 'randomizer_functions.py', which is used when generating psuedo-random numbers
        5) The folder and file "tdbaccess\new\tdbaccess.dll"
        6) colleges_and_ids.csv
        7) teams_and_ids.csv
    Additionally, the base Madden roster file to update, named "base.ros", must be in the "process\inputs\step5" 
    folder, and the final version of the latest player attributes file must be in "process\inputs\both" as a CSV file 
    named "Latest Player Attributes.csv."
    
    This script (or, more accurately, its helper, "roster_manager.py") will generate the file "latest.ros" in the 
    folder "outputs\step5\".
"""

# ----------------------------------------------------- SECTION 1 -----------------------------------------------------
# ----------------------------------------- IMPORTS, SETTINGS, AND CONSTANTS ------------------------------------------
# 1 - Standard library imports

import csv, logging, os
#from importlib import reload

# 2 - Third-party imports

# 3 - Application-specific imports

from utilities.roster_manager import RosterManager

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
with open(os.path.join(
    BASE_MADDEN_PATH, 
    r"process\inputs\both\Latest Player Attributes.csv")
         ) as PLAYER_ATTRIBUTES_FILE: 
    # Get a DictReader to read the rows into dicts using the header row as keys.
    ATTRIBUTES_DICT_READER = csv.DictReader(PLAYER_ATTRIBUTES_FILE)
    # Pull our records into a list so we can count them and iterate over them as often as needed.
    NEW_PLAYER_LIST = list(ATTRIBUTES_DICT_READER)

# Get the number of new players, ie. the count of dicts in the list.
NEW_PLAYER_COUNT = len(NEW_PLAYER_LIST)
logging.info("NEW_PLAYER_COUNT = %d", NEW_PLAYER_COUNT)

try:
    
    # Instantiate our RosterManager object.
    ROSTERMANAGER = RosterManager()
    
    # Size our player table.
    ROSTERMANAGER.size_player_table(NEW_PLAYER_COUNT)
    
    # Loop over each element in the list and process the player's attributes for inserting into our roster file.
    for i, player_dict in enumerate(NEW_PLAYER_LIST):
        
        # Determine which function to call based on the 'position' field value.
        if player_dict["position"].upper() == "QB":
            ROSTERMANAGER.create_quarterback(player_dict, i)
        elif player_dict["position"].upper() == "HB":
            ROSTERMANAGER.create_halfback(player_dict, i)
        elif player_dict["position"].upper() == "FB":
            ROSTERMANAGER.create_fullback(player_dict, i)
        elif player_dict["position"].upper() == "WR":
            ROSTERMANAGER.create_wide_receiver(player_dict, i)
        elif player_dict["position"].upper() == "TE":
            ROSTERMANAGER.create_tight_end(player_dict, i)
        elif player_dict["position"].upper() == "LT":
            ROSTERMANAGER.create_left_tackle(player_dict, i)
        elif player_dict["position"].upper() == "LG":
            ROSTERMANAGER.create_left_guard(player_dict, i)
        elif player_dict["position"].upper() == "C":
            ROSTERMANAGER.create_center(player_dict, i)
        elif player_dict["position"].upper() == "RG":
            ROSTERMANAGER.create_right_guard(player_dict, i)
        elif player_dict["position"].upper() == "RT":
            ROSTERMANAGER.create_right_tackle(player_dict, i)
        elif player_dict["position"].upper() == "LE":
            ROSTERMANAGER.create_left_end(player_dict, i)
        elif player_dict["position"].upper() == "RE":
            ROSTERMANAGER.create_right_end(player_dict, i)
        elif player_dict["position"].upper() == "DT":
            ROSTERMANAGER.create_defensive_tackle(player_dict, i)
        elif player_dict["position"].upper() == "LOLB":
            ROSTERMANAGER.create_left_outside_linebacker(player_dict, i)
        elif player_dict["position"].upper() == "MLB":
            ROSTERMANAGER.create_middle_linebacker(player_dict, i)
        elif player_dict["position"].upper() == "ROLB":
            ROSTERMANAGER.create_right_outside_linebacker(player_dict, i)
        elif player_dict["position"].upper() == "CB":
            ROSTERMANAGER.create_cornerback(player_dict, i)
        elif player_dict["position"].upper() == "FS":
            ROSTERMANAGER.create_free_safety(player_dict, i)
        elif player_dict["position"].upper() == "SS":
            ROSTERMANAGER.create_strong_safety(player_dict, i)
        elif player_dict["position"].upper() == "K":
            ROSTERMANAGER.create_kicker(player_dict, i)
        elif player_dict["position"].upper() == "P":
            ROSTERMANAGER.create_punter(player_dict, i)
        else:
            logging.error("Player %d's position was not recognized: %s", i, player_dict["position"].upper())
    
    # Compact, save, and close the DB.
    ROSTERMANAGER.compact_save_close_db()
    
except SystemExit:
    logging.critical("Unable to open file 'latest.ros'. TDBOpen returned -1. Exiting.")

except RuntimeError:
    # This makes sure that, in case of an error, we correctly close the DB file.
    ROSTERMANAGER.__del__()

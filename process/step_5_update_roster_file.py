r""" step_5_update_roster_file.py
    This is one of the two main Python scripts called when updating the base Madden NFL '08 roster file, to be called 
    using the syntax: 
        > python step_5_update_roster_file.py
    
    This script is only one part of the process for generating an updated Madden NFL '08 Roster file. Prior to running 
    this script, the first four steps of the process need to be performed. Please refer to the document 
    "step_1 README for Madden_08_Updater.docx" for more information. 
    
    This script requires the following files to be placed in the "utilities" folder alongside it, meaning in 
    os.path.join(os.path.dirname(os.path.abspath(__file__)), r"utilities\") : 
        1) The helper file, 'helper_functions.py' 
        2) The folder and file 'tdbaccess\old\tdbaccess.dll' 
    Additionally, the below files must be in the 'inputs' folder, meaning in 
    os.path.join(os.path.dirname(os.path.abspath(__file__)), r"inputs\") : 
        1) The base Madden '08 Roster file to update, named 'base.ros' 
        2) The latest NFL roster-based CSV file, named 'Latest Player Attributes.csv' 
    
    This script will generate the file "latest.ros" in the folder 'outputs'.
"""

# ----------------------------------------------------- SECTION 1 -----------------------------------------------------
# ----------------------------------------- IMPORTS, SETTINGS, AND CONSTANTS ------------------------------------------
# 1 - Standard library imports

import csv, logging, math, os
from ctypes import byref, cast, c_bool, c_char, c_char_p, c_float, c_int, POINTER, Structure, WinDLL
#from enum import Enum


# 2 - Third-party imports


# 3 - Application-specific imports

#from utilities.helper_functions import *


# 4 - Global settings


# 5 - Global constants

PLAYERS_TABLE = b'PLAY'

# Set the base path we will use to keep other paths relative, and shorter :^)
# This will be the directory above the directory this file is in.
BASE_MADDEN_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Get a handle for our DLL.
TDBACCESS_DLL = WinDLL(os.path.join(BASE_MADDEN_PATH, r"process\utilities\tdbaccess\old\tdbaccess.dll"))

# Open the roster file through the DLL and get its index.
DB_INDEX = TDBACCESS_DLL.TDBOpen(os.path.join(BASE_MADDEN_PATH, r"process\inputs\base.ros").encode('utf-8'))

# Open the CSV file with all the players and their latest attributes.
LATEST_PLAYER_ATTRIBUTES_FILE = open(os.path.join(BASE_MADDEN_PATH, r"process\inputs\Latest Player Attributes.csv"))

# Get a DictReader to read the rows into dicts using the header row as keys.
ATTRIBUTES_DICT_READER = csv.DictReader(LATEST_PLAYER_ATTRIBUTES_FILE)


# ----------------------------------------------------- SECTION 2 -----------------------------------------------------
# ------------------------------------------------ Class Declarations -------------------------------------------------

class TDBTablePropertiesStruct(Structure):
    """Structure whose fields hold all the properties of a table in the roster file."""
    _fields_ = [
        ('Name', c_char_p),
        ('FieldCount', c_int),
        ('Capacity', c_int),
        ('RecordCount', c_int),
        ('DeletedCount', c_int),
        ('NextDeletedRecord', c_int),
        ('Flag0', c_bool),
        ('Flag1', c_bool),
        ('Flag2', c_bool),
        ('Flag3', c_bool),
        ('NonAllocated', c_bool),
        ('HasVarchar', c_bool),
        ('HasCompressedVarchar', c_bool),
    ]
    
    def __init__(self, *args):
        self.Name = cast((c_char * 8)(), c_char_p)
        Structure.__init__(self, *args)

class TDBFieldPropertiesStruct(Structure):
    """Structure whose fields hold all the properties of a field from a table in the roster file."""
    _fields_ = [
        ('Name', c_char_p),
        ('Size', c_int),
        ('FieldType', c_int),
    ]
    
    def __init__(self, *args):
        self.Name = cast((c_char * 8)(), c_char_p)
        Structure.__init__(self, *args)

# Add the argtype and restype definitions here for the DLL functions we'll use.

TDBACCESS_DLL.TDBClose.argtypes = [c_int]
TDBACCESS_DLL.TDBClose.restype = c_bool

TDBACCESS_DLL.TDBDatabaseCompact.argtypes = [c_int]
TDBACCESS_DLL.TDBDatabaseCompact.restype = c_bool

TDBACCESS_DLL.TDBFieldGetValueAsInteger.argtypes = [c_int, c_char_p, c_char_p, c_int]
TDBACCESS_DLL.TDBFieldGetValueAsInteger.restype = c_int

TDBACCESS_DLL.TDBFieldGetValueAsString.argtypes = [c_int, c_char_p, c_char_p, c_int, POINTER(c_char_p)]
TDBACCESS_DLL.TDBFieldGetValueAsString.restype = c_bool

TDBACCESS_DLL.TDBFieldSetValueAsInteger.argtypes = [c_int, c_char_p, c_char_p, c_int, c_int]
TDBACCESS_DLL.TDBFieldSetValueAsInteger.restype = c_bool

TDBACCESS_DLL.TDBFieldSetValueAsString.argtypes = [c_int, c_char_p, c_char_p, c_int, c_char_p]
TDBACCESS_DLL.TDBFieldSetValueAsString.restype = c_bool

TDBACCESS_DLL.TDBOpen.argtypes = [c_char_p]
TDBACCESS_DLL.TDBOpen.restype = c_int

TDBACCESS_DLL.TDBSave.argtypes = [c_int]
TDBACCESS_DLL.TDBSave.restype = c_bool

TDBACCESS_DLL.TDBTableGetProperties.argtypes = [c_int, c_int, POINTER(TDBTablePropertiesStruct)]
TDBACCESS_DLL.TDBTableGetProperties.restype = c_bool


# ----------------------------------------------------- SECTION 3 -----------------------------------------------------
# ------------------------------------------------- Helper Functions --------------------------------------------------

def set_player_integer_field(field_name, player_index, field_int_value):
    """ Sets a given field on a given player's record to a given integer value. """
    value_was_set_as_int = TDBACCESS_DLL.TDBFieldSetValueAsInteger(
        DB_INDEX, PLAYERS_TABLE, field_name, player_index, field_int_value)
#    if value_was_set_as_int:
#        int_value_set = TDBACCESS_DLL.TDBFieldGetValueAsInteger(DB_INDEX, PLAYERS_TABLE, field_name, player_index)
#        logging.info("\nSet Player %d's %s field to %d", player_index, field_name.decode(), int_value_set)
#    else:
    if not value_was_set_as_int:
        logging.error("Error in setting Player %d's %s field as integer.", player_index, field_name.decode())

def set_player_string_field(field_name, player_index, field_str_value):
    """ Sets a given field on a given player's record to a given string value. """
    value_was_set_as_string = TDBACCESS_DLL.TDBFieldSetValueAsString(
        DB_INDEX, PLAYERS_TABLE, field_name, player_index, field_str_value)
#    if value_was_set_as_string:
#        value_as_string = cast((c_char * 14)(), c_char_p)
#        got_str_value = TDBACCESS_DLL.TDBFieldGetValueAsString(
#            DB_INDEX, PLAYERS_TABLE, field_name, player_index, byref(value_as_string))
#        if got_str_value:
#            logging.info("\nSet Player %d's %s field to %s", 
#                         player_index, 
#                         field_name.decode(), 
#                         value_as_string.value.decode())
#        else:
#            logging.error("\nError in getting Player %d's %s field.", player_index, field_name.decode())
#    else:
    if not value_was_set_as_string:
        logging.error("Error in setting Player %d's %s field as string.", player_index, field_name.decode())


# ----------------------------------------------------- SECTION 4 -----------------------------------------------------
# ------------------------------------------------ Main Functionality -------------------------------------------------

if __name__ == "__main__":
    
    # Loop over each row in the dict reader and process the player's attributes for inserting into our roster file.
    for i, player_dict in enumerate(ATTRIBUTES_DICT_READER, start=1):
        #logging.info("player_dict %d = %r", i, player_dict)
        
        # Determine which function to call based on the 'position' field value.
        if player_dict["position"].upper() == "QB":
            create_quarterback(player_dict, i)
        elif player_dict["position"].upper() == "HB":
            create_halfback(player_dict, i)
        elif player_dict["position"].upper() == "FB":
            create_fullback(player_dict, i)
        elif player_dict["position"].upper() == "WR":
            create_wide_receiver(player_dict, i)
        elif player_dict["position"].upper() == "TE":
            create_tight_end(player_dict, i)
        elif player_dict["position"].upper() == "LT":
            create_left_tackle(player_dict, i)
        elif player_dict["position"].upper() == "LG":
            create_left_guard(player_dict, i)
        elif player_dict["position"].upper() == "C":
            create_center(player_dict, i)
        elif player_dict["position"].upper() == "RG":
            create_right_guard(player_dict, i)
        elif player_dict["position"].upper() == "RT":
            create_right_tackle(player_dict, i)
        elif player_dict["position"].upper() == "LE":
            create_left_end(player_dict, i)
        elif player_dict["position"].upper() == "RE":
            create_right_end(player_dict, i)
        elif player_dict["position"].upper() == "DT":
            create_defensive_tackle(player_dict, i)
        elif player_dict["position"].upper() == "LOLB":
            create_left_outside_linebacker(player_dict, i)
        elif player_dict["position"].upper() == "MLB":
            create_middle_linebacker(player_dict, i)
        elif player_dict["position"].upper() == "ROLB":
            create_right_outside_linebacker(player_dict, i)
        elif player_dict["position"].upper() == "CB":
            create_cornerback(player_dict, i)
        elif player_dict["position"].upper() == "FS":
            create_free_safety(player_dict, i)
        elif player_dict["position"].upper() == "SS":
            create_strong_safety(player_dict, i)
        elif player_dict["position"].upper() == "K":
            create_kicker(player_dict, i)
        elif player_dict["position"].upper() == "P":
            create_punter(player_dict, i)
        else:
            logging.error("Player %d's position was not recognized: %s", i, player_dict["position"].upper())

    # -----------  FINAL ACTIONS: Compact, save, and close the DB, and close the Latest Player Attributes file. -----------

    # Compact the DB.
    compacted_database = TDBACCESS_DLL.TDBDatabaseCompact(DB_INDEX)
    if compacted_database:
        logging.info("\nCompacted the TDBDatabase.")
    else:
        logging.error("\nError: Failed to compact the TDBDatabase.")

    # Save the DB.
    saved_database = TDBACCESS_DLL.TDBSave(DB_INDEX)
    if saved_database:
        logging.info("\nSaved the TDBDatabase.")
    else:
        logging.error("\nError: Failed to save the TDBDatabase.")

    # Close the DB.
    closed_database = TDBACCESS_DLL.TDBClose(DB_INDEX)
    if closed_database:
        logging.info("\nClosed the TDBDatabase.")
    else:
        logging.error("\nError: Failed to close the TDBDatabase.")

    # Close the Latest Player Attributes.csv file.
    LATEST_PLAYER_ATTRIBUTES_FILE.close()

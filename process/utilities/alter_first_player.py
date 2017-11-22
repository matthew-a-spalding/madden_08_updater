r""" alter_first_player.py
    
    This file reads the first dict of player attributes from "process\inputs\Latest Madden Ratings.csv" and then uses 
    some of those values to alter the first player record in "process\inputs\base.ros" while changing the player's 
    position into a WR.
"""

# ----------------------------------------------------- SECTION 1 -----------------------------------------------------
# ----------------------------------------- IMPORTS, SETTINGS, AND CONSTANTS ------------------------------------------

# 1.1 - Standard library imports

import csv, logging, math, os
from ctypes import cast, c_bool, c_char, c_char_p, c_int, Structure, WinDLL #POINTER, 


# 1.2 - Third-party imports


# 1.3 - Application-specific imports


# 1.4 - Global settings


# 1.5 - Global constants

PLAYERS_TABLE = b'PLAY'

# Set the base path we will use to keep other paths relative, and shorter :^)
# This will be the directory above the directory this file is in.
BASE_MADDEN_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Get a handle for our DLL.
TDBACCESS_DLL = WinDLL(os.path.join(BASE_MADDEN_PATH, r"process\utilities\tdbaccess\old\tdbaccess.dll"))

# Open the roster file through the DLL and get its index.
DB_INDEX = TDBACCESS_DLL.TDBOpen(os.path.join(BASE_MADDEN_PATH, r"process\inputs\base.ros").encode('utf-8'))


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

#TDBACCESS_DLL.TDBFieldGetValueAsInteger.argtypes = [c_int, c_char_p, c_char_p, c_int]
#TDBACCESS_DLL.TDBFieldGetValueAsInteger.restype = c_int

#TDBACCESS_DLL.TDBFieldGetValueAsString.argtypes = [c_int, c_char_p, c_char_p, c_int, POINTER(c_char_p)]
#TDBACCESS_DLL.TDBFieldGetValueAsString.restype = c_bool

TDBACCESS_DLL.TDBFieldSetValueAsInteger.argtypes = [c_int, c_char_p, c_char_p, c_int, c_int]
TDBACCESS_DLL.TDBFieldSetValueAsInteger.restype = c_bool

TDBACCESS_DLL.TDBFieldSetValueAsString.argtypes = [c_int, c_char_p, c_char_p, c_int, c_char_p]
TDBACCESS_DLL.TDBFieldSetValueAsString.restype = c_bool

TDBACCESS_DLL.TDBOpen.argtypes = [c_char_p]
TDBACCESS_DLL.TDBOpen.restype = c_int

TDBACCESS_DLL.TDBSave.argtypes = [c_int]
TDBACCESS_DLL.TDBSave.restype = c_bool


# ----------------------------------------------------- SECTION 3 -----------------------------------------------------
# ------------------------------------------------- Helper Functions --------------------------------------------------

def set_player_integer_field(field_name, player_index, field_int_value):
    """ Sets a given attribute on a given player to a given integer value. """
    value_was_set_as_int = TDBACCESS_DLL.TDBFieldSetValueAsInteger(
        DB_INDEX, PLAYERS_TABLE, field_name, player_index, field_int_value)
#    if value_was_set_as_int:
#        int_value_set = TDBACCESS_DLL.TDBFieldGetValueAsInteger(DB_INDEX, PLAYERS_TABLE, field_name, player_index)
#        logging.info("\nSet Player %d's %s field to %d", player_index, field_name.decode(), int_value_set)
#    else:
    if not value_was_set_as_int:
        logging.error("\nError in setting Player %d's %s field.", player_index, field_name.decode())

def set_player_string_field(field_name, player_index, field_str_value):
    """ Sets a given attribute on a given player to a given string value. """
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
#            logging.warning("\nError in getting Player %d's %s field.", player_index, field_name.decode())
#    else:
    if not value_was_set_as_string:
        logging.warning("\nError in setting Player %d's %s field.", player_index, field_name.decode())


# ----------------------------------------------------- SECTION 4 -----------------------------------------------------
# ------------------------------------------------ Main Functionality -------------------------------------------------

# ------------ READ FROM THE MADDEN RATINGS .csv FILE ------------

# Open the CSV file with all the players and their Madden ratings.
madden_ratings_file = open(os.path.join(BASE_MADDEN_PATH, r"process\inputs\Latest Madden Ratings.csv"))

# Get a DictReader to read the rows into dicts using the header row as keys.
madden_ratings_dict_reader = csv.DictReader(madden_ratings_file)

# Get the dict representing the first row.
first_player_dict = next(madden_ratings_dict_reader)

# Show what we got.
logging.info("\nfirst_player_dict = %r", first_player_dict)

# Close the Madden Ratings .csv file.
madden_ratings_file.close()


# ------------------ WRITE NEW VALUES FOR IMPORTANT ATTRIBUTES OF THE FIRST PLAYER ------------------

# Start by setting Player 0's PRL2 (Player Role 2) to 37, Possession Receiver.
set_player_integer_field(b'PRL2', 0, 37)

# Set his gloves (PLHA and PRHA) to White RB gloves (5).
set_player_integer_field(b'PLHA', 0, 5)

set_player_integer_field(b'PRHA', 0, 5)

# Set Player 0's throwing accuracy (PTHA) to:
#   max(65, min(99, ceil((2 * (m_tas + m_tam + m_tad) - min(m_tas, m_tam, m_tad))/5))).
# Start by getting a list of the values we want out of the player dict, 
# using the keys 'Throw Accuracy Short', 'Throw Accuracy Mid', and 'Throw Accuracy Deep'.
throwing_acc_keys_list = ['Throw Accuracy Short', 'Throw Accuracy Mid', 'Throw Accuracy Deep']
throwing_acc_values_list = [int(first_player_dict[x]) for x in throwing_acc_keys_list]
# Now to calculate the PTHA value we want.
PTHA_value = int(
    max([65, 
         min([99, 
              math.ceil(
                  (2 * (
                      int(first_player_dict['Throw Accuracy Short']) 
                      + int(first_player_dict['Throw Accuracy Mid']) 
                      + int(first_player_dict['Throw Accuracy Deep'])
                      ) 
                   - min(throwing_acc_values_list)
                  ) / 5
                  )
             ])
        ])
    )
# Now set the PTHA value.
set_player_integer_field(b'PTHA', 0, PTHA_value)

# Set Player 0's first name (PFNA).
set_player_string_field(b'PFNA', 0, first_player_dict['First'].encode('utf-8'))

# Set Player 0's last name (PLNA).
set_player_string_field(b'PLNA', 0, first_player_dict['Last'].encode('utf-8'))

# Set Player 0's stamina (PSTA).
set_player_integer_field(b'PSTA', 0, int(first_player_dict['Stamina']))

# Set Player 0's kicking accuracy (PKAC).
set_player_integer_field(b'PKAC', 0, int(first_player_dict['Kick Accuracy']))

# Set Player 0's acceleration (PACC).
set_player_integer_field(b'PACC', 0, int(first_player_dict['Acceleration']))

# Set Player 0's speed (PSPD).
set_player_integer_field(b'PSPD', 0, int(first_player_dict['Speed']))

# Set Player 0's toughness (PTGH).
set_player_integer_field(b'PTGH', 0, int(first_player_dict['Toughness']))

# Set Player 0's catching (PCTH).
set_player_integer_field(b'PCTH', 0, int(first_player_dict['Catching']))

# Set Player 0's agility (PAGI).
set_player_integer_field(b'PAGI', 0, int(first_player_dict['Agility']))

# Set Player 0's injury (PINJ).
set_player_integer_field(b'PINJ', 0, int(first_player_dict['Injury']))

# Set Player 0's tackling (PTAK).
set_player_integer_field(b'PTAK', 0, int(first_player_dict['Tackle']))

# Set Player 0's pass blocking (PPBK).
set_player_integer_field(b'PPBK', 0, int(first_player_dict['Pass Block']))

# Set Player 0's run blocking (PRBK).
set_player_integer_field(b'PRBK', 0, int(first_player_dict['Run Block']))

# Set Player 0's break tackle (PBTK).
set_player_integer_field(b'PBTK', 0, int(first_player_dict['Trucking']))

# Set Player 0's Player Role 1 (PROL) to 35 (Go-To Guy).
set_player_integer_field(b'PROL', 0, 35)

# Set Player 0's jersey number (PJEN).
set_player_integer_field(b'PJEN', 0, int(first_player_dict['Jersey']))

# Set Player 0's throwing power (PTHP).
set_player_integer_field(b'PTHP', 0, int(first_player_dict['Throw Power']))

# Set Player 0's jumping (PJMP).
set_player_integer_field(b'PJMP', 0, int(first_player_dict['Jumping']))

# Set Player 0's portrait ID (PSXP).
set_player_integer_field(b'PSXP', 0, 0)

# Set Player 0's carrying (PCAR).
set_player_integer_field(b'PCAR', 0, int(first_player_dict['Carrying']))

# Set Player 0's kicking power (PKPR).
set_player_integer_field(b'PKPR', 0, int(first_player_dict['Kick Power']))

# Set Player 0's strength (PSTR).
set_player_integer_field(b'PSTR', 0, int(first_player_dict['Strength']))

# Set Player 0's overall rating (POVR).
set_player_integer_field(b'POVR', 0, 25)

# Set Player 0's awareness (PAWR).
set_player_integer_field(b'PAWR', 0, int(first_player_dict['Awareness']))

# Set Player 0's Position ID (PPOS) to 3 (WR).
set_player_integer_field(b'PPOS', 0, 3)

# Set Player 0's Other Position ID (POPS) to 3 (WR).
set_player_integer_field(b'POPS', 0, 3)

# Set Player 0's kick returns (PKRT).
set_player_integer_field(b'PKRT', 0, int(first_player_dict['Kick Return']))


# ------------  FINAL ACTIONS: Compact, save, and close the DB. ------------

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

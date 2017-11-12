r""" DLLtest3.py
    
    This file reads the first dict of player attributes from "process\inputs\Latest Madden Ratings.csv" and then uses 
    those values to alter the first player record in "process\inputs\base.ros". This completely changes the player 
    into a WR as well. 
"""

# ----------------------------------------------------- SECTION 1 -----------------------------------------------------
# ----------------------------------------- IMPORTS, SETTINGS, AND CONSTANTS ------------------------------------------

# 1.1 - Standard library imports

import csv, math, os
from ctypes import byref, cast, c_bool, c_char, c_char_p, c_float, c_int, POINTER, Structure, WinDLL


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
#        ('Name', c_wchar_p),
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
#        self.Name = cast((c_wchar * 8)(), c_wchar_p)
        Structure.__init__(self, *args)
#        super(TDBTablePropertiesStruct, self).__init__(*args)

class TDBFieldPropertiesStruct(Structure):
    """Structure whose fields hold all the properties of a field from a table in the roster file."""
    _fields_ = [
        ('Name', c_char_p),
#        ('Name', c_wchar_p),
        ('Size', c_int),
        ('FieldType', c_int),
    ]
    
    def __init__(self, *args):
        self.Name = cast((c_char * 8)(), c_char_p)
#        self.Name = cast((c_wchar * 8)(), c_wchar_p)
        Structure.__init__(self, *args)
#        super(TDBFieldPropertiesStruct, self).__init__(*args)

# Add the argtype and restype definitions here for the DLL functions we'll use.

TDBACCESS_DLL.TDBClose.argtypes = [c_int]
TDBACCESS_DLL.TDBClose.restype = c_bool

TDBACCESS_DLL.TDBDatabaseCompact.argtypes = [c_int]
TDBACCESS_DLL.TDBDatabaseCompact.restype = c_bool

TDBACCESS_DLL.TDBDatabaseGetTableCount.argtypes = [c_int]
TDBACCESS_DLL.TDBDatabaseGetTableCount.restype = c_int

TDBACCESS_DLL.TDBFieldGetProperties.argtypes = [c_int, c_char_p, c_int, POINTER(TDBFieldPropertiesStruct)]
#TDBACCESS_DLL.TDBFieldGetProperties.argtypes = [c_int, c_wchar_p, c_int, POINTER(TDBFieldPropertiesStruct)]
TDBACCESS_DLL.TDBFieldGetProperties.restype = c_int

#TDBACCESS_DLL.TDBFieldGetValueAsBinary.argtypes = [c_int, c_char_p, c_char_p, c_int, POINTER(c_char_p)]

#TDBACCESS_DLL.TDBFieldGetValueAsFloat.argtypes = [c_int, c_char_p, c_char_p, c_int]

TDBACCESS_DLL.TDBFieldGetValueAsInteger.argtypes = [c_int, c_char_p, c_char_p, c_int]
TDBACCESS_DLL.TDBFieldGetValueAsInteger.restype = c_int

TDBACCESS_DLL.TDBFieldGetValueAsString.argtypes = [c_int, c_char_p, c_char_p, c_int, POINTER(c_char_p)]
TDBACCESS_DLL.TDBFieldGetValueAsString.restype = c_bool

#TDBACCESS_DLL.TDBFieldSetValueAsFloat.argtypes = [c_int, c_char_p, c_char_p, c_int, c_float]

TDBACCESS_DLL.TDBFieldSetValueAsInteger.argtypes = [c_int, c_char_p, c_char_p, c_int, c_int]
TDBACCESS_DLL.TDBFieldSetValueAsInteger.restype = c_bool

TDBACCESS_DLL.TDBFieldSetValueAsString.argtypes = [c_int, c_char_p, c_char_p, c_int, c_char_p]
TDBACCESS_DLL.TDBFieldSetValueAsString.restype = c_bool

TDBACCESS_DLL.TDBOpen.argtypes = [c_char_p]
#TDBACCESS_DLL.TDBOpen.argtypes = [c_wchar_p]
TDBACCESS_DLL.TDBOpen.restype = c_int

TDBACCESS_DLL.TDBSave.argtypes = [c_int]
TDBACCESS_DLL.TDBSave.restype = c_bool

TDBACCESS_DLL.TDBTableGetProperties.argtypes = [c_int, c_int, POINTER(TDBTablePropertiesStruct)]
TDBACCESS_DLL.TDBTableGetProperties.restype = c_bool


# ----------------------------------------------------- SECTION 3 -----------------------------------------------------
# ------------------------------------------------- Helper Functions --------------------------------------------------

def set_player_integer_attribute(attr_name, player_index, attr_int_value):
    value_was_set_as_int = TDBACCESS_DLL.TDBFieldSetValueAsInteger(
        DB_INDEX, PLAYERS_TABLE, attr_name, player_index, attr_int_value)
    if value_was_set_as_int:
        int_value_set = TDBACCESS_DLL.TDBFieldGetValueAsInteger(DB_INDEX, PLAYERS_TABLE, attr_name, player_index)
        print("\nSet Player %d's %s field to %d" % (player_index, attr_name.decode(), int_value_set))
    else:
        print("\nError in setting Player %d's %s field." % (player_index, attr_name.decode()))

def set_player_string_attribute(attr_name, player_index, attr_str_value):
    value_was_set_as_string = TDBACCESS_DLL.TDBFieldSetValueAsString(
        DB_INDEX, PLAYERS_TABLE, attr_name, player_index, attr_str_value)
    if value_was_set_as_string:
        str_value_set = cast((c_char * 14)(), c_char_p)
        got_str_value = TDBACCESS_DLL.TDBFieldGetValueAsString(
            DB_INDEX, PLAYERS_TABLE, attr_name, player_index, byref(str_value_set))
        if got_str_value:
            print("\nSet Player %d's %s field to %s" % (player_index, attr_name.decode(), str_value_set.value.decode()))
        else:
            print("\nError in getting Player %d's %s field." % (player_index, attr_name.decode()))
    else:
        print("\nError in setting Player %d's %s field." % (player_index, attr_name.decode()))


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
print("\nfirst_player_dict = %r" % first_player_dict)

# Close the Madden Ratings .csv file.
madden_ratings_file.close()


# ------------------ WRITE NEW VALUES FOR IMPORTANT ATTRIBUTES OF THE FIRST PLAYER ------------------

# NOTE: I think this section immediately following, commented out in the docstring format, 
# was the code I used to prove that it was possible to edit a player in the .ros file so completely that he was an 
# entirely new character. See if that is the case by uncommenting that section and trying to do it again.

# Start by setting Player 0's PRL2 (Player Role 2) to 37, Possession Receiver.
set_player_integer_attribute(b'PRL2', 0, 37)
#value_was_set_as_int = TDBACCESS_DLL.TDBFieldSetValueAsInteger(DB_INDEX, PLAYERS_TABLE, "PRL2", 0, 37)
#if value_was_set_as_int:
#    int_value_set = TDBACCESS_DLL.TDBFieldGetValueAsInteger(DB_INDEX, PLAYERS_TABLE, "PRL2", 0)
#    print("\nSet Player 0's PRL2 field to %d" % int_value_set)
#else:
#    print("\nError in setting Player 0's PRL2 field.")

# Set his gloves (PLHA and PRHA) to White RB gloves (5).
set_player_integer_attribute(b'PLHA', 0, 5)
#value_was_set_as_int = TDBACCESS_DLL.TDBFieldSetValueAsInteger(DB_INDEX, PLAYERS_TABLE, "PLHA", 0, 5)
#if value_was_set_as_int:
#    int_value_set = TDBACCESS_DLL.TDBFieldGetValueAsInteger(DB_INDEX, PLAYERS_TABLE, "PLHA", 0)
#    print("Set Player 0's PLHA field to %d" % int_value_set)
#else:
#    print("\nError in setting Player 0's PLHA field.")

set_player_integer_attribute(b'PRHA', 0, 5)
#value_was_set_as_int = TDBACCESS_DLL.TDBFieldSetValueAsInteger(DB_INDEX, PLAYERS_TABLE, "PRHA", 0, 5)
#if value_was_set_as_int:
#    int_value_set = TDBACCESS_DLL.TDBFieldGetValueAsInteger(DB_INDEX, PLAYERS_TABLE, "PRHA", 0)
#    print("Set Player 0's PRHA field to %d" % int_value_set)
#else:
#    print("\nError in setting Player 0's PRHA field.")

# Set Player 0's throwing accuracy (PTHA) to:
#   max(65, min(99, ceil((2 * (m_tas + m_tam + m_tad) - min(m_tas, m_tam, m_tad))/5))).
# Start by getting a list of the values we want out of the player dict, 
# using the keys 'Throw Accuracy SHORT', 'Throw Accuracy MED', and 'Throw Accuracy DEEP'.
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
                    ) - min(throwing_acc_values_list)
                ) / 5
            )
        ])
    ])
)
# Set the value.
set_player_integer_attribute(b'PTHA', 0, PTHA_value)
#value_was_set_as_int = TDBACCESS_DLL.TDBFieldSetValueAsInteger(DB_INDEX, PLAYERS_TABLE, b'PTHA', 0, PTHA_value)
#if value_was_set_as_int:
#    int_value_set = TDBACCESS_DLL.TDBFieldGetValueAsInteger(DB_INDEX, PLAYERS_TABLE, "PTHA", 0)
#    print("Set Player 0's PTHA field to %d" % int_value_set)
#else:
#    print("\nError in setting Player 0's PTHA field.")

# Set Player 0's first name (PFNA).
set_player_string_attribute(b'PFNA', 0, first_player_dict['First'].encode('utf-8'))
#value_was_set_as_string = TDBACCESS_DLL.TDBFieldSetValueAsString(
#    DB_INDEX, PLAYERS_TABLE, "PFNA", 0, first_player_dict['FIRST'])
#if value_was_set_as_string:
#    str_value_set = cast((c_char * 12)(), c_char_p)
#    got_str_value = TDBACCESS_DLL.TDBFieldGetValueAsString(DB_INDEX, PLAYERS_TABLE, "PFNA", 0, byref(str_value_set))
#    if got_str_value:
#        print("Set Player 0's PFNA field to %s" % str_value_set.value)
#    else:
#        print("\nError in setting Player 0's PFNA field.")
#else:
#    print("\nError in setting Player 0's PFNA field.")

# Set Player 0's last name (PLNA).
set_player_string_attribute(b'PLNA', 0, first_player_dict['Last'].encode('utf-8'))
#value_was_set_as_string = TDBACCESS_DLL.TDBFieldSetValueAsString(
#    DB_INDEX, PLAYERS_TABLE, "PLNA", 0, first_player_dict['LAST'])
#if value_was_set_as_string:
#    str_value_set = cast((c_char * 14)(), c_char_p)
#    got_str_value = TDBACCESS_DLL.TDBFieldGetValueAsString(DB_INDEX, PLAYERS_TABLE, "PLNA", 0, byref(str_value_set))
#    if got_str_value:
#        print("Set Player 0's PLNA field to %s" % str_value_set.value)
#    else:
#        print("\nError in setting Player 0's PLNA field.")
#else:
#    print("\nError in setting Player 0's PLNA field.")

# Set Player 0's stamina (PSTA).
set_player_integer_attribute(b'PSTA', 0, int(first_player_dict['Stamina']))
#value_was_set_as_int = TDBACCESS_DLL.TDBFieldSetValueAsInteger(
#    DB_INDEX, PLAYERS_TABLE, "PSTA", 0, int(first_player_dict['STAMINA']))
#if value_was_set_as_int:
#    int_value_set = TDBACCESS_DLL.TDBFieldGetValueAsInteger(DB_INDEX, PLAYERS_TABLE, "PSTA", 0)
#    print("Set Player 0's PSTA field to %d" % int_value_set)
#else:
#    print("\nError in setting Player 0's PSTA field.")

# Set Player 0's kicking accuracy (PKAC).
set_player_integer_attribute(b'PKAC', 0, int(first_player_dict['Kick Accuracy']))
#value_was_set_as_int = TDBACCESS_DLL.TDBFieldSetValueAsInteger(
#    DB_INDEX, PLAYERS_TABLE, "PKAC", 0, int(first_player_dict['KICK ACCURACY']))
#if value_was_set_as_int:
#    int_value_set = TDBACCESS_DLL.TDBFieldGetValueAsInteger(DB_INDEX, PLAYERS_TABLE, "PKAC", 0)
#    print("Set Player 0's PKAC field to %d" % int_value_set)
#else:
#    print("\nError in setting Player 0's PKAC field.")

# Set Player 0's acceleration (PACC).
set_player_integer_attribute(b'PACC', 0, int(first_player_dict['Acceleration']))
#value_was_set_as_int = TDBACCESS_DLL.TDBFieldSetValueAsInteger(
#    DB_INDEX, PLAYERS_TABLE, "PACC", 0, int(first_player_dict['ACCELERATION']))
#if value_was_set_as_int:
#    int_value_set = TDBACCESS_DLL.TDBFieldGetValueAsInteger(DB_INDEX, PLAYERS_TABLE, "PACC", 0)
#    print("Set Player 0's PACC field to %d" % int_value_set)
#else:
#    print("\nError in setting Player 0's PACC field.")

# Set Player 0's speed (PSPD).
set_player_integer_attribute(b'PSPD', 0, int(first_player_dict['Speed']))
#value_was_set_as_int = TDBACCESS_DLL.TDBFieldSetValueAsInteger(
#    DB_INDEX, PLAYERS_TABLE, "PSPD", 0, int(first_player_dict['SPEED']))
#if value_was_set_as_int:
#    int_value_set = TDBACCESS_DLL.TDBFieldGetValueAsInteger(DB_INDEX, PLAYERS_TABLE, "PSPD", 0)
#    print("Set Player 0's PSPD field to %d" % int_value_set)
#else:
#    print("\nError in setting Player 0's PSPD field.")

# Set Player 0's toughness (PTGH).
set_player_integer_attribute(b'PTGH', 0, int(first_player_dict['Toughness']))
#value_was_set_as_int = TDBACCESS_DLL.TDBFieldSetValueAsInteger(
#    DB_INDEX, PLAYERS_TABLE, "PTGH", 0, int(first_player_dict['TOUGHNESS']))
#if value_was_set_as_int:
#    int_value_set = TDBACCESS_DLL.TDBFieldGetValueAsInteger(DB_INDEX, PLAYERS_TABLE, "PTGH", 0)
#    print("Set Player 0's PTGH field to %d" % int_value_set)
#else:
#    print("\nError in setting Player 0's PTGH field.")

# Set Player 0's catching (PCTH).
set_player_integer_attribute(b'PCTH', 0, int(first_player_dict['Catching']))
#value_was_set_as_int = TDBACCESS_DLL.TDBFieldSetValueAsInteger(
#    DB_INDEX, PLAYERS_TABLE, "PCTH", 0, int(first_player_dict['CATCHING']))
#if value_was_set_as_int:
#    int_value_set = TDBACCESS_DLL.TDBFieldGetValueAsInteger(DB_INDEX, PLAYERS_TABLE, "PCTH", 0)
#    print("Set Player 0's PCTH field to %d" % int_value_set)
#else:
#    print("\nError in setting Player 0's PCTH field.")

# Set Player 0's agility (PAGI).
set_player_integer_attribute(b'PAGI', 0, int(first_player_dict['Agility']))
#value_was_set_as_int = TDBACCESS_DLL.TDBFieldSetValueAsInteger(
#    DB_INDEX, PLAYERS_TABLE, "PAGI", 0, int(first_player_dict['AGILITY']))
#if value_was_set_as_int:
#    int_value_set = TDBACCESS_DLL.TDBFieldGetValueAsInteger(DB_INDEX, PLAYERS_TABLE, "PAGI", 0)
#    print("Set Player 0's PAGI field to %d" % int_value_set)
#else:
#    print("\nError in setting Player 0's PAGI field.")

# Set Player 0's injury (PINJ).
set_player_integer_attribute(b'PINJ', 0, int(first_player_dict['Injury']))
#value_was_set_as_int = TDBACCESS_DLL.TDBFieldSetValueAsInteger(
#    DB_INDEX, PLAYERS_TABLE, "PINJ", 0, int(first_player_dict['INJURY']))
#if value_was_set_as_int:
#    int_value_set = TDBACCESS_DLL.TDBFieldGetValueAsInteger(DB_INDEX, PLAYERS_TABLE, "PINJ", 0)
#    print("Set Player 0's PINJ field to %d" % int_value_set)
#else:
#    print("\nError in setting Player 0's PINJ field.")

# Set Player 0's tackling (PTAK).
set_player_integer_attribute(b'PTAK', 0, int(first_player_dict['Tackle']))
#value_was_set_as_int = TDBACCESS_DLL.TDBFieldSetValueAsInteger(
#    DB_INDEX, PLAYERS_TABLE, "PTAK", 0, int(first_player_dict['TACKLE']))
#if value_was_set_as_int:
#    int_value_set = TDBACCESS_DLL.TDBFieldGetValueAsInteger(DB_INDEX, PLAYERS_TABLE, "PTAK", 0)
#    print("Set Player 0's PTAK field to %d" % int_value_set)
#else:
#    print("\nError in setting Player 0's PTAK field.")

# Set Player 0's pass blocking (PPBK).
set_player_integer_attribute(b'PPBK', 0, int(first_player_dict['Pass Block']))
#value_was_set_as_int = TDBACCESS_DLL.TDBFieldSetValueAsInteger(
#    DB_INDEX, PLAYERS_TABLE, "PPBK", 0, int(first_player_dict['PASS BLOCK']))
#if value_was_set_as_int:
#    int_value_set = TDBACCESS_DLL.TDBFieldGetValueAsInteger(DB_INDEX, PLAYERS_TABLE, "PPBK", 0)
#    print("Set Player 0's PPBK field to %d" % int_value_set)
#else:
#    print("\nError in setting Player 0's PPBK field.")

# Set Player 0's run blocking (PRBK).
set_player_integer_attribute(b'PRBK', 0, int(first_player_dict['Run Block']))
#value_was_set_as_int = TDBACCESS_DLL.TDBFieldSetValueAsInteger(
#    DB_INDEX, PLAYERS_TABLE, "PRBK", 0, int(first_player_dict['RUN BLOCK']))
#if value_was_set_as_int:
#    int_value_set = TDBACCESS_DLL.TDBFieldGetValueAsInteger(DB_INDEX, PLAYERS_TABLE, "PRBK", 0)
#    print("Set Player 0's PRBK field to %d" % int_value_set)
#else:
#    print("\nError in setting Player 0's PRBK field.")

# Set Player 0's break tackle (PBTK).
set_player_integer_attribute(b'PBTK', 0, int(first_player_dict['Trucking']))
#value_was_set_as_int = TDBACCESS_DLL.TDBFieldSetValueAsInteger(
#    DB_INDEX, PLAYERS_TABLE, "PBTK", 0, int(first_player_dict['TRUCKING']))
#if value_was_set_as_int:
#    int_value_set = TDBACCESS_DLL.TDBFieldGetValueAsInteger(DB_INDEX, PLAYERS_TABLE, "PBTK", 0)
#    print("Set Player 0's PBTK field to %d" % int_value_set)
#else:
#    print("\nError in setting Player 0's PBTK field.")

# Set Player 0's Player Role 1 (PROL) to 35 (Go-To Guy).
set_player_integer_attribute(b'PROL', 0, 35)
#value_was_set_as_int = TDBACCESS_DLL.TDBFieldSetValueAsInteger(DB_INDEX, PLAYERS_TABLE, "PROL", 0, 35)
#if value_was_set_as_int:
#    int_value_set = TDBACCESS_DLL.TDBFieldGetValueAsInteger(DB_INDEX, PLAYERS_TABLE, "PROL", 0)
#    print("Set Player 0's PROL field to %d" % int_value_set)
#else:
#    print("\nError in setting Player 0's PROL field.")

# Set Player 0's jersey number (PJEN).
set_player_integer_attribute(b'PJEN', 0, int(first_player_dict['Jersey']))
#value_was_set_as_int = TDBACCESS_DLL.TDBFieldSetValueAsInteger(
#    DB_INDEX, PLAYERS_TABLE, "PJEN", 0, int(first_player_dict['JERSEY']))
#if value_was_set_as_int:
#    int_value_set = TDBACCESS_DLL.TDBFieldGetValueAsInteger(DB_INDEX, PLAYERS_TABLE, "PJEN", 0)
#    print("Set Player 0's PJEN field to %d" % int_value_set)
#else:
#    print("\nError in setting Player 0's PJEN field.")

# Set Player 0's throwing power (PTHP).
set_player_integer_attribute(b'PTHP', 0, int(first_player_dict['Throw Power']))
#value_was_set_as_int = TDBACCESS_DLL.TDBFieldSetValueAsInteger(
#    DB_INDEX, PLAYERS_TABLE, "PTHP", 0, int(first_player_dict['THROW POWER']))
#if value_was_set_as_int:
#    int_value_set = TDBACCESS_DLL.TDBFieldGetValueAsInteger(DB_INDEX, PLAYERS_TABLE, "PTHP", 0)
#    print("Set Player 0's PTHP field to %d" % int_value_set)
#else:
#    print("\nError in setting Player 0's PTHP field.")

# Set Player 0's jumping (PJMP).
set_player_integer_attribute(b'PJMP', 0, int(first_player_dict['Jumping']))
#value_was_set_as_int = TDBACCESS_DLL.TDBFieldSetValueAsInteger(
#    DB_INDEX, PLAYERS_TABLE, "PJMP", 0, int(first_player_dict['JUMPING']))
#if value_was_set_as_int:
#    int_value_set = TDBACCESS_DLL.TDBFieldGetValueAsInteger(DB_INDEX, PLAYERS_TABLE, "PJMP", 0)
#    print("Set Player 0's PJMP field to %d" % int_value_set)
#else:
#    print("\nError in setting Player 0's PJMP field.")

# Set Player 0's portrait ID (PSXP).
set_player_integer_attribute(b'PSXP', 0, 0)
#value_was_set_as_int = TDBACCESS_DLL.TDBFieldSetValueAsInteger(DB_INDEX, PLAYERS_TABLE, "PSXP", 0, 0)
#if value_was_set_as_int:
#    int_value_set = TDBACCESS_DLL.TDBFieldGetValueAsInteger(DB_INDEX, PLAYERS_TABLE, "PSXP", 0)
#    print("Set Player 0's PSXP field to %d" % int_value_set)
#else:
#    print("\nError in setting Player 0's PSXP field.")

# Set Player 0's carrying (PCAR).
set_player_integer_attribute(b'PCAR', 0, int(first_player_dict['Carrying']))
#value_was_set_as_int = TDBACCESS_DLL.TDBFieldSetValueAsInteger(
#    DB_INDEX, PLAYERS_TABLE, "PCAR", 0, int(first_player_dict['CARRYING']))
#if value_was_set_as_int:
#    int_value_set = TDBACCESS_DLL.TDBFieldGetValueAsInteger(DB_INDEX, PLAYERS_TABLE, "PCAR", 0)
#    print("Set Player 0's PCAR field to %d" % int_value_set)
#else:
#    print("\nError in setting Player 0's PCAR field.")

# Set Player 0's kicking power (PKPR).
set_player_integer_attribute(b'PKPR', 0, int(first_player_dict['Kick Power']))
#value_was_set_as_int = TDBACCESS_DLL.TDBFieldSetValueAsInteger(
#    DB_INDEX, PLAYERS_TABLE, "PKPR", 0, int(first_player_dict['KICK POWER']))
#if value_was_set_as_int:
#    int_value_set = TDBACCESS_DLL.TDBFieldGetValueAsInteger(DB_INDEX, PLAYERS_TABLE, "PKPR", 0)
#    print("Set Player 0's PKPR field to %d" % int_value_set)
#else:
#    print("\nError in setting Player 0's PKPR field.")

# Set Player 0's strength (PSTR).
set_player_integer_attribute(b'PSTR', 0, int(first_player_dict['Strength']))
#value_was_set_as_int = TDBACCESS_DLL.TDBFieldSetValueAsInteger(
#    DB_INDEX, PLAYERS_TABLE, "PSTR", 0, int(first_player_dict['STRENGTH']))
#if value_was_set_as_int:
#    int_value_set = TDBACCESS_DLL.TDBFieldGetValueAsInteger(DB_INDEX, PLAYERS_TABLE, "PSTR", 0)
#    print("Set Player 0's PSTR field to %d" % int_value_set)
#else:
#    print("\nError in setting Player 0's PSTR field.")

# Set Player 0's overall rating (POVR).
set_player_integer_attribute(b'POVR', 0, 25)
#value_was_set_as_int = TDBACCESS_DLL.TDBFieldSetValueAsInteger(DB_INDEX, PLAYERS_TABLE, "POVR", 0, 25)
#if value_was_set_as_int:
#    int_value_set = TDBACCESS_DLL.TDBFieldGetValueAsInteger(DB_INDEX, PLAYERS_TABLE, "POVR", 0)
#    print("Set Player 0's POVR field to %d" % int_value_set)
#else:
#    print("\nError in setting Player 0's POVR field.")

# Set Player 0's awareness (PAWR).
set_player_integer_attribute(b'PAWR', 0, int(first_player_dict['Awareness']))
#value_was_set_as_int = TDBACCESS_DLL.TDBFieldSetValueAsInteger(
#    DB_INDEX, PLAYERS_TABLE, "PAWR", 0, int(first_player_dict['AWARENESS']))
#if value_was_set_as_int:
#    int_value_set = TDBACCESS_DLL.TDBFieldGetValueAsInteger(DB_INDEX, PLAYERS_TABLE, "PAWR", 0)
#    print("Set Player 0's PAWR field to %d" % int_value_set)
#else:
#    print("\nError in setting Player 0's PAWR field.")

# Set Player 0's Position ID (PPOS) to 3 (WR).
set_player_integer_attribute(b'PPOS', 0, 3)
#value_was_set_as_int = TDBACCESS_DLL.TDBFieldSetValueAsInteger(DB_INDEX, PLAYERS_TABLE, "PPOS", 0, 3)
#if value_was_set_as_int:
#    int_value_set = TDBACCESS_DLL.TDBFieldGetValueAsInteger(DB_INDEX, PLAYERS_TABLE, "PPOS", 0)
#    print("Set Player 0's PPOS field to %d" % int_value_set)
#else:
#    print("\nError in setting Player 0's PPOS field.")

# Set Player 0's Other Position ID (POPS) to 3 (WR).
set_player_integer_attribute(b'POPS', 0, 3)
#value_was_set_as_int = TDBACCESS_DLL.TDBFieldSetValueAsInteger(DB_INDEX, PLAYERS_TABLE, "POPS", 0, 3)
#if value_was_set_as_int:
#    int_value_set = TDBACCESS_DLL.TDBFieldGetValueAsInteger(DB_INDEX, PLAYERS_TABLE, "POPS", 0)
#    print("Set Player 0's POPS field to %d" % int_value_set)
#else:
#    print("\nError in setting Player 0's POPS field.")

# Set Player 0's kick returns (PKRT).
set_player_integer_attribute(b'PKRT', 0, int(first_player_dict['Kick Return']))
#value_was_set_as_int = TDBACCESS_DLL.TDBFieldSetValueAsInteger(
#    DB_INDEX, PLAYERS_TABLE, "PKRT", 0, int(first_player_dict['RETURN']))
#if value_was_set_as_int:
#    int_value_set = TDBACCESS_DLL.TDBFieldGetValueAsInteger(DB_INDEX, PLAYERS_TABLE, "PKRT", 0)
#    print("Set Player 0's PKRT field to %d" % int_value_set)
#else:
#    print("\nError in setting Player 0's PKRT field.")


# ------------ PRINT THE FIELDS IN THE "PLAY" TABLE AND THEIR TYPES ------------

# Create a dict to hold the player's attributes. Keys will be field Names, values will be field values.
#dictPlayer0Attributes = {}

# Loop over the fields in the PLAY table and get the values out, calling the appropriate ...GetValueAs... methods for each type.
#for i, structFieldProperties in enumerate(listTDBFieldPropertiesStructsLists[6]):
    # See what methods we need to call.
#    if structFieldProperties.FieldType == 0: # tdbString
        # First, create the string where we will hold the value.
#        str_value_set = cast((c_char * ((structFieldProperties.Size / 8) + 1))(), c_char_p)
#        got_str_value = TDBACCESS_DLL.TDBFieldGetValueAsString(DB_INDEX, table_property_structs_list[6].Name, structFieldProperties.Name, 0, byref(str_value_set))
#        if got_str_value:
#            dictPlayer0Attributes[structFieldProperties.Name] = str_value_set.value
#            print("%d: str_value_set for player 0's %s field = %s" % (i, structFieldProperties.Name, dictPlayer0Attributes[structFieldProperties.Name]))
#        else:
#            print("%d: Field %s is a string. UNABLE TO GET STRING VALUE." % (i, structFieldProperties.Name))
#    elif structFieldProperties.FieldType == 2: # tdbSInt
#        print("%d: Field %s is a signed int." % (i, structFieldProperties.Name))
#    elif structFieldProperties.FieldType == 3: # tdbUInt
#        print("%d: Field %s is an unsigned int." % (i, structFieldProperties.Name))

#print("\ndictPlayer0Attributes = %r" % dictPlayer0Attributes)


# ------------  FINAL ACTIONS: Compact, save, and close the DB. ------------

# Compact the DB.
boolCompactedTDBDatabase = TDBACCESS_DLL.TDBDatabaseCompact(DB_INDEX)
if boolCompactedTDBDatabase:
    print("\nCompacted the TDBDatabase.")
else:
    print("\nWarning: Failed to compact the TDBDatabase.")

# Save the DB.
boolSavedTDBDatabase = TDBACCESS_DLL.TDBSave(DB_INDEX)
if boolSavedTDBDatabase:
    print("\nSaved the TDBDatabase.")
else:
    print("\nWarning: Failed to save the TDBDatabase.")

# Close the DB.
boolClosedTDBDatabase = TDBACCESS_DLL.TDBClose(DB_INDEX)
if boolClosedTDBDatabase:
    print("\nClosed the TDBDatabase.")
else:
    print("\nWarning: Failed to close the TDBDatabase.")
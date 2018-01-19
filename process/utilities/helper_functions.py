""" helper_functions.py

This is the only python sub-module used by the script "step_5_update_roster_file.py". It contains functions to perform 
any task that is repeated in the logic of that script's main function.
"""

# --------------------------------------------------- SECTION 1 -------------------------------------------------------
# ---------------------------------------- IMPORTS, SETTINGS, AND CONSTANTS -------------------------------------------
# 1 - Standard library imports
import logging, os, math
from ctypes import byref, cast, c_bool, c_wchar, c_wchar_p, c_int, POINTER, Structure, WinDLL
from shutil import copyfile

# 2 - Third-party imports

# 3 - Application-specific imports

# 4 - Global settings

# 5 - Global constants

PLAYERS_TABLE = 'PLAY'

# Set the base path we will use to keep other paths relative, and shorter :^)
# This will be the directory above the directory above the directory this file is in.
BASE_MADDEN_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Get a handle for our DLL.
TDBACCESS_DLL = WinDLL(os.path.join(BASE_MADDEN_PATH, r"process\utilities\tdbaccess\new\tdbaccess.dll"))

# Copy the input file into our destination folder and rename on the way.
copyfile(
   	os.path.join(BASE_MADDEN_PATH, r"process\inputs\base.ros"), 
	   os.path.join(BASE_MADDEN_PATH, r"process\outputs\latest.ros")
)

# Open the roster file through the DLL and get its index.
DB_INDEX = TDBACCESS_DLL.TDBOpen(os.path.join(BASE_MADDEN_PATH, r"process\outputs\latest.ros"))


# ----------------------------------------------------- SECTION 2 -----------------------------------------------------
# ------------------------------------------------ Class Declarations -------------------------------------------------

class TDBTablePropertiesStruct(Structure):
    """Structure whose fields hold all the properties of a table in the roster file."""
    _fields_ = [
        ('Name', c_wchar_p),
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
        self.Name = cast((c_wchar * 8)(), c_wchar_p)
        Structure.__init__(self, *args)

# Add the argtype and restype definitions here for the DLL functions we'll use.

TDBACCESS_DLL.TDBClose.argtypes = [c_int]
TDBACCESS_DLL.TDBClose.restype = c_bool

TDBACCESS_DLL.TDBDatabaseCompact.argtypes = [c_int]
TDBACCESS_DLL.TDBDatabaseCompact.restype = c_bool

TDBACCESS_DLL.TDBFieldGetValueAsInteger.argtypes = [c_int, c_wchar_p, c_wchar_p, c_int]
TDBACCESS_DLL.TDBFieldGetValueAsInteger.restype = c_int

TDBACCESS_DLL.TDBFieldGetValueAsString.argtypes = [c_int, c_wchar_p, c_wchar_p, c_int, POINTER(c_wchar_p)]
TDBACCESS_DLL.TDBFieldGetValueAsString.restype = c_bool

TDBACCESS_DLL.TDBFieldSetValueAsInteger.argtypes = [c_int, c_wchar_p, c_wchar_p, c_int, c_int]
TDBACCESS_DLL.TDBFieldSetValueAsInteger.restype = c_bool

TDBACCESS_DLL.TDBFieldSetValueAsString.argtypes = [c_int, c_wchar_p, c_wchar_p, c_int, c_wchar_p]
TDBACCESS_DLL.TDBFieldSetValueAsString.restype = c_bool

TDBACCESS_DLL.TDBOpen.argtypes = [c_wchar_p]
TDBACCESS_DLL.TDBOpen.restype = c_int

TDBACCESS_DLL.TDBSave.argtypes = [c_int]
TDBACCESS_DLL.TDBSave.restype = c_bool

TDBACCESS_DLL.TDBTableGetProperties.argtypes = [c_int, c_int, POINTER(TDBTablePropertiesStruct)]
TDBACCESS_DLL.TDBTableGetProperties.restype = c_bool

TDBACCESS_DLL.TDBTableRecordAdd.argtypes = [c_int, c_wchar_p, c_bool]
TDBACCESS_DLL.TDBTableRecordAdd.restype = c_int

TDBACCESS_DLL.TDBTableRecordChangeDeleted.argtypes = [c_int, c_wchar_p, c_int, c_bool]
TDBACCESS_DLL.TDBTableRecordChangeDeleted.restype = c_bool


# ----------------------------------------------------- SECTION 3 -----------------------------------------------------
# ------------------------------------------------- Helper Functions --------------------------------------------------

def set_player_integer_field(field_name, player_index, field_int_value):
    """ Sets a given field on a given player's record to a given integer value. """
    value_was_set_as_int = TDBACCESS_DLL.TDBFieldSetValueAsInteger(
        DB_INDEX, PLAYERS_TABLE, field_name, player_index, field_int_value)
#    if value_was_set_as_int:
#        int_value_set = TDBACCESS_DLL.TDBFieldGetValueAsInteger(DB_INDEX, PLAYERS_TABLE, field_name, player_index)
#        logging.info("Set Player %d's %s field to %d", player_index, field_name.decode(), int_value_set)
#    else:
    if not value_was_set_as_int:
        logging.error("\tFailed in setting player %d's %s field as integer!", player_index, field_name)

def set_player_string_field(field_name, player_index, field_str_value):
    """ Sets a given field on a given player's record to a given string value. """
    value_was_set_as_string = TDBACCESS_DLL.TDBFieldSetValueAsString(
        DB_INDEX, PLAYERS_TABLE, field_name, player_index, field_str_value)
#    if value_was_set_as_string:
#        value_as_string = cast((c_wchar * 14)(), c_wchar_p)
#        got_str_value = TDBACCESS_DLL.TDBFieldGetValueAsString(
#            DB_INDEX, PLAYERS_TABLE, field_name, player_index, byref(value_as_string))
#        if got_str_value:
#            logging.info("Set Player %d's %s field to %s", 
#                         player_index, 
#                         field_name.decode(), 
#                         value_as_string.value)
#        else:
#            logging.error(
#                "\tFailed in getting Player %d's %s field back out as string!", 
#                player_index, 
#                field_name)
#    else:
    if not value_was_set_as_string:
        logging.error("\tFailed in setting player %d's %s field as string!", player_index, field_name)

def get_team_id(team_name):
    """ Returns the Madden ID corresponding to a given team name. """
    if "BEARS" in team_name.upper():
        return 1
    if "BENGALS" in team_name.upper():
        return 2
    if "BILLS" in team_name.upper():
        return 3
    if "BRONCOS" in team_name.upper():
        return 4
    if "BROWNS" in team_name.upper():
        return 5
    if "BUCCANEERS" in team_name.upper():
        return 6
    if "CARDINALS" in team_name.upper():
        return 7
    if "CHARGERS" in team_name.upper():
        return 8
    if "CHIEFS" in team_name.upper():
        return 9
    if "COLTS" in team_name.upper():
        return 10
    if "COWBOYS" in team_name.upper():
        return 11
    if "DOLPHINS" in team_name.upper():
        return 12
    if "EAGLES" in team_name.upper():
        return 13
    if "FALCONS" in team_name.upper():
        return 14
    if "49ERS" in team_name.upper():
        return 15
    if "GIANTS" in team_name.upper():
        return 16
    if "JAGUARS" in team_name.upper():
        return 17
    if "JETS" in team_name.upper():
        return 18
    if "LIONS" in team_name.upper():
        return 19
    if "PACKERS" in team_name.upper():
        return 20
    if "PANTHERS" in team_name.upper():
        return 21
    if "PATRIOTS" in team_name.upper():
        return 22
    if "RAIDERS" in team_name.upper():
        return 23
    if "RAMS" in team_name.upper():
        return 24
    if "RAVENS" in team_name.upper():
        return 25
    if "REDSKINS" in team_name.upper():
        return 26
    if "SAINTS" in team_name.upper():
        return 27
    if "SEAHAWKS" in team_name.upper():
        return 28
    if "STEELERS" in team_name.upper():
        return 29
    if "TITANS" in team_name.upper():
        return 30
    if "VIKINGS" in team_name.upper():
        return 31
    if "TEXANS" in team_name.upper():
        return 32
    return 1023

def get_college_id(college_name):
    """  """
    return 0

# ----------------------------------------------------- SECTION 4 -----------------------------------------------------
# ------------------------------------------------ Main Functionality -------------------------------------------------


# Create a struct to hold the properties for the PLAY table.
PLAYER_TABLE_PROPERTIES = TDBTablePropertiesStruct()


def create_quarterback(player_dict, index):
    """
    Given a dictionary of a new player and the index of the related record to modify in the DB, performs all of 
    the calculations and updates necessary to create the player as a QB in the DB.
    """
    # For all of the following fields, we simply use 0.
    # PCPH, PFHO, PJTY, PMPC, PMUS, POPS, PPOS, PSTM, PSTY, PSXP, PTSL, PUCL, TLEL, TLHA, TLWR, TREL, TRHA, TRWR, 
    set_player_integer_field('PCPH', index, 0)
    set_player_integer_field('PFHO', index, 0)
    set_player_integer_field('PJTY', index, 0)
    set_player_integer_field('PMPC', index, 0)
    set_player_integer_field('PMUS', index, 0)
    set_player_integer_field('POPS', index, 0)
    set_player_integer_field('PPOS', index, 0)
    set_player_integer_field('PSTM', index, 0)
    set_player_integer_field('PSTY', index, 0)
    set_player_integer_field('PSXP', index, 0)
    set_player_integer_field('PTSL', index, 0)
    set_player_integer_field('PUCL', index, 0)
    set_player_integer_field('TLEL', index, 0)
    set_player_integer_field('TLHA', index, 0)
    set_player_integer_field('TLWR', index, 0)
    set_player_integer_field('TREL', index, 0)
    set_player_integer_field('TRHA', index, 0)
    set_player_integer_field('TRWR', index, 0)
    
    # PCMT gets 999, PJER gets a 1, PLHY gets -31, PLPL gets 100, and PPTI will always get 1009.
    set_player_integer_field('PCMT', index, 999)
    set_player_integer_field('PJER', index, 1)
    set_player_integer_field('PLHY', index, -31)
    set_player_integer_field('PLPL', index, 100)
    set_player_integer_field('PPTI', index, 1009)
    
    # For most attributes which are in 'Latest Player Attributes.csv', simply use the value in the file.
    set_player_integer_field('PAGE', index, int(player_dict["age"]))
    set_player_integer_field('PDPI', index, int(player_dict["draft_pick"]))
    set_player_integer_field('PDRO', index, int(player_dict["draft_round"]))
    set_player_integer_field('PFEx', index, int(player_dict["face_id"]))
    set_player_integer_field('PFPB', index, int(player_dict["pro_bowl"]))
    set_player_integer_field('PHED', index, int(player_dict["hair_style"]))
    set_player_integer_field('PHCL', index, int(player_dict["hair_color"]))
    set_player_integer_field('PHGT', index, int(player_dict["height"]))
    set_player_integer_field('PICN', index, int(player_dict["nfl_icon"]))
    set_player_integer_field('PJEN', index, int(player_dict["jersey_number"]))
    set_player_integer_field('PLEL', index, int(player_dict["left_elbow"]))
    set_player_integer_field('PLHA', index, int(player_dict["left_hand"]))
    set_player_integer_field('PLSH', index, int(player_dict["left_shoe"]))
    set_player_integer_field('PLTH', index, int(player_dict["left_knee"]))
    set_player_integer_field('PNEK', index, int(player_dict["neck_pad"]))
    set_player_integer_field('PREL', index, int(player_dict["right_elbow"]))
    set_player_integer_field('PRHA', index, int(player_dict["right_hand"]))
    set_player_integer_field('PRSH', index, int(player_dict["right_shoe"]))
    set_player_integer_field('PRTH', index, int(player_dict["right_knee"]))
    set_player_integer_field('PSKI', index, int(player_dict["skin_color"]))
    set_player_integer_field('PVIS', index, int(player_dict["visor_style"]))
    set_player_integer_field('PYRP', index, int(player_dict["years_pro"]))
    set_player_integer_field('PYWT', index, int(player_dict["years_pro"]))
    
    # For these attributes, the calculations are simple.
    
    # Get the first 11 characters of the first name.
    if len(player_dict["first_name"]) < 12:
        set_player_string_field('PFNA', index, player_dict["first_name"])
    else:
        set_player_string_field('PFNA', index, player_dict["first_name"][:11])
    # Get the first 13 characters of the last name.
    if len(player_dict["last_name"]) < 14:
        set_player_string_field('PLNA', index, player_dict["last_name"])
    else:
        set_player_string_field('PLNA', index, player_dict["last_name"][:13])
    # Subtract 160 from the players weight, unless he is already under 160.
    if int(player_dict["weight"]) > 159:
        set_player_integer_field('PWGT', index, (int(player_dict["weight"]) - 160))
    else:
        set_player_integer_field('PWGT', index, 0)
    # The team ID is straightforward.
    set_player_integer_field('TGID', index, get_team_id(player_dict["team"]))
    # The college ID is also fairly straightforward.
    set_player_integer_field('PCOL', index, get_college_id(player_dict["college"]))
    # The handedness is 0 for right, 1 for left.
    if "RIGHT" in player_dict["handedness"].upper():
        set_player_integer_field('PHAN', index, 0)
    else:
        set_player_integer_field('PHAN', index, 1)
    
    # For some attributes, we will use formulas to determine what value to use. 
    
def create_halfback(player_dict, index):
    """ 
    Given a dictionary of a new player and the index of the related record to modify in the DB, performs all of 
    the calculations and updates necessary to create the player as a QB in the DB.
    """
    # For all of the following fields, we simply use 0.
    # TLHA, TRHA, PCPH, PLSH, PRSH, PLTH, PRTH, PUCL, TLEL, TREL, PTSL, PSTM, PFHO, PSXP, TLWR, TRWR, PMUS, PJTY, PSTY
    set_player_integer_field('TLHA', index, 0)
    
    # PPTI will always get 1009, PLPL gets 100, PJER gets a 1, PCMT gets 999, PLHY gets -31, 
    
    # For attributes which have a column in the 'Latest Player Attributes.csv' file, use the value if it differs from 
    # the default value we put in that column. If not, we will use formulas to determine what value to use. 
    
def create_fullback(player_dict, index):
    """ 
    Given a dictionary of a new player and the index of the related record to modify in the DB, performs all of 
    the calculations and updates necessary to create the player as a QB in the DB.
    """
    # For all of the following fields, we simply use 0.
    # TLHA, TRHA, PCPH, PLSH, PRSH, PLTH, PRTH, PUCL, TLEL, TREL, PTSL, PSTM, PFHO, PSXP, TLWR, TRWR, PMUS, PJTY, PSTY
    set_player_integer_field('TLHA', index, 0)
    
    # PPTI will always get 1009, PLPL gets 100, PJER gets a 1, PCMT gets 999, PLHY gets -31, 
    
    # For attributes which have a column in the 'Latest Player Attributes.csv' file, use the value if it differs from 
    # the default value we put in that column. If not, we will use formulas to determine what value to use. 
    
def create_wide_receiver(player_dict, index):
    """ 
    Given a dictionary of a new player and the index of the related record to modify in the DB, performs all of 
    the calculations and updates necessary to create the player as a QB in the DB.
    """
    # For all of the following fields, we simply use 0.
    # TLHA, TRHA, PCPH, PLSH, PRSH, PLTH, PRTH, PUCL, TLEL, TREL, PTSL, PSTM, PFHO, PSXP, TLWR, TRWR, PMUS, PJTY, PSTY
    set_player_integer_field('TLHA', index, 0)
    
    # PPTI will always get 1009, PLPL gets 100, PJER gets a 1, PCMT gets 999, PLHY gets -31, 
    
    # For attributes which have a column in the 'Latest Player Attributes.csv' file, use the value if it differs from 
    # the default value we put in that column. If not, we will use formulas to determine what value to use. 
    
def create_tight_end(player_dict, index):
    """ 
    Given a dictionary of a new player and the index of the related record to modify in the DB, performs all of 
    the calculations and updates necessary to create the player as a QB in the DB.
    """
    # For all of the following fields, we simply use 0.
    # TLHA, TRHA, PCPH, PLSH, PRSH, PLTH, PRTH, PUCL, TLEL, TREL, PTSL, PSTM, PFHO, PSXP, TLWR, TRWR, PMUS, PJTY, PSTY
    set_player_integer_field('TLHA', index, 0)
    
    # PPTI will always get 1009, PLPL gets 100, PJER gets a 1, PCMT gets 999, PLHY gets -31, 
    
    # For attributes which have a column in the 'Latest Player Attributes.csv' file, use the value if it differs from 
    # the default value we put in that column. If not, we will use formulas to determine what value to use. 
    
def create_left_tackle(player_dict, index):
    """ 
    Given a dictionary of a new player and the index of the related record to modify in the DB, performs all of 
    the calculations and updates necessary to create the player as a QB in the DB.
    """
    # For all of the following fields, we simply use 0.
    # TLHA, TRHA, PCPH, PLSH, PRSH, PLTH, PRTH, PUCL, TLEL, TREL, PTSL, PSTM, PFHO, PSXP, TLWR, TRWR, PMUS, PJTY, PSTY
    set_player_integer_field('TLHA', index, 0)
    
    # PPTI will always get 1009, PLPL gets 100, PJER gets a 1, PCMT gets 999, PLHY gets -31, 
    
    # For attributes which have a column in the 'Latest Player Attributes.csv' file, use the value if it differs from 
    # the default value we put in that column. If not, we will use formulas to determine what value to use. 
    
def create_left_guard(player_dict, index):
    """ 
    Given a dictionary of a new player and the index of the related record to modify in the DB, performs all of 
    the calculations and updates necessary to create the player as a QB in the DB.
    """
    # For all of the following fields, we simply use 0.
    # TLHA, TRHA, PCPH, PLSH, PRSH, PLTH, PRTH, PUCL, TLEL, TREL, PTSL, PSTM, PFHO, PSXP, TLWR, TRWR, PMUS, PJTY, PSTY
    set_player_integer_field('TLHA', index, 0)
    
    # PPTI will always get 1009, PLPL gets 100, PJER gets a 1, PCMT gets 999, PLHY gets -31, 
    
    # For attributes which have a column in the 'Latest Player Attributes.csv' file, use the value if it differs from 
    # the default value we put in that column. If not, we will use formulas to determine what value to use. 
    
def create_center(player_dict, index):
    """ 
    Given a dictionary of a new player and the index of the related record to modify in the DB, performs all of 
    the calculations and updates necessary to create the player as a QB in the DB.
    """
    # For all of the following fields, we simply use 0.
    # TLHA, TRHA, PCPH, PLSH, PRSH, PLTH, PRTH, PUCL, TLEL, TREL, PTSL, PSTM, PFHO, PSXP, TLWR, TRWR, PMUS, PJTY, PSTY
    set_player_integer_field('TLHA', index, 0)
    
    # PPTI will always get 1009, PLPL gets 100, PJER gets a 1, PCMT gets 999, PLHY gets -31, 
    
    # For attributes which have a column in the 'Latest Player Attributes.csv' file, use the value if it differs from 
    # the default value we put in that column. If not, we will use formulas to determine what value to use. 
    
def create_right_guard(player_dict, index):
    """ 
    Given a dictionary of a new player and the index of the related record to modify in the DB, performs all of 
    the calculations and updates necessary to create the player as a QB in the DB.
    """
    # For all of the following fields, we simply use 0.
    # TLHA, TRHA, PCPH, PLSH, PRSH, PLTH, PRTH, PUCL, TLEL, TREL, PTSL, PSTM, PFHO, PSXP, TLWR, TRWR, PMUS, PJTY, PSTY
    set_player_integer_field('TLHA', index, 0)
    
    # PPTI will always get 1009, PLPL gets 100, PJER gets a 1, PCMT gets 999, PLHY gets -31, 
    
    # For attributes which have a column in the 'Latest Player Attributes.csv' file, use the value if it differs from 
    # the default value we put in that column. If not, we will use formulas to determine what value to use. 
    
def create_right_tackle(player_dict, index):
    """ 
    Given a dictionary of a new player and the index of the related record to modify in the DB, performs all of 
    the calculations and updates necessary to create the player as a QB in the DB.
    """
    # For all of the following fields, we simply use 0.
    # TLHA, TRHA, PCPH, PLSH, PRSH, PLTH, PRTH, PUCL, TLEL, TREL, PTSL, PSTM, PFHO, PSXP, TLWR, TRWR, PMUS, PJTY, PSTY
    set_player_integer_field('TLHA', index, 0)
    
    # PPTI will always get 1009, PLPL gets 100, PJER gets a 1, PCMT gets 999, PLHY gets -31, 
    
    # For attributes which have a column in the 'Latest Player Attributes.csv' file, use the value if it differs from 
    # the default value we put in that column. If not, we will use formulas to determine what value to use. 
    
def create_left_end(player_dict, index):
    """ 
    Given a dictionary of a new player and the index of the related record to modify in the DB, performs all of 
    the calculations and updates necessary to create the player as a QB in the DB.
    """
    # For all of the following fields, we simply use 0.
    # TLHA, TRHA, PCPH, PLSH, PRSH, PLTH, PRTH, PUCL, TLEL, TREL, PTSL, PSTM, PFHO, PSXP, TLWR, TRWR, PMUS, PJTY, PSTY
    set_player_integer_field('TLHA', index, 0)
    
    # PPTI will always get 1009, PLPL gets 100, PJER gets a 1, PCMT gets 999, PLHY gets -31, 
    
    # For attributes which have a column in the 'Latest Player Attributes.csv' file, use the value if it differs from 
    # the default value we put in that column. If not, we will use formulas to determine what value to use. 
    
def create_right_end(player_dict, index):
    """ 
    Given a dictionary of a new player and the index of the related record to modify in the DB, performs all of 
    the calculations and updates necessary to create the player as a QB in the DB.
    """
    # For all of the following fields, we simply use 0.
    # TLHA, TRHA, PCPH, PLSH, PRSH, PLTH, PRTH, PUCL, TLEL, TREL, PTSL, PSTM, PFHO, PSXP, TLWR, TRWR, PMUS, PJTY, PSTY
    set_player_integer_field('TLHA', index, 0)
    
    # PPTI will always get 1009, PLPL gets 100, PJER gets a 1, PCMT gets 999, PLHY gets -31, 
    
    # For attributes which have a column in the 'Latest Player Attributes.csv' file, use the value if it differs from 
    # the default value we put in that column. If not, we will use formulas to determine what value to use. 
    
def create_defensive_tackle(player_dict, index):
    """ 
    Given a dictionary of a new player and the index of the related record to modify in the DB, performs all of 
    the calculations and updates necessary to create the player as a QB in the DB.
    """
    # For all of the following fields, we simply use 0.
    # TLHA, TRHA, PCPH, PLSH, PRSH, PLTH, PRTH, PUCL, TLEL, TREL, PTSL, PSTM, PFHO, PSXP, TLWR, TRWR, PMUS, PJTY, PSTY
    set_player_integer_field('TLHA', index, 0)
    
    # PPTI will always get 1009, PLPL gets 100, PJER gets a 1, PCMT gets 999, PLHY gets -31, 
    
    # For attributes which have a column in the 'Latest Player Attributes.csv' file, use the value if it differs from 
    # the default value we put in that column. If not, we will use formulas to determine what value to use. 
    
def create_left_outside_linebacker(player_dict, index):
    """ 
    Given a dictionary of a new player and the index of the related record to modify in the DB, performs all of 
    the calculations and updates necessary to create the player as a QB in the DB.
    """
    # For all of the following fields, we simply use 0.
    # TLHA, TRHA, PCPH, PLSH, PRSH, PLTH, PRTH, PUCL, TLEL, TREL, PTSL, PSTM, PFHO, PSXP, TLWR, TRWR, PMUS, PJTY, PSTY
    set_player_integer_field('TLHA', index, 0)
    
    # PPTI will always get 1009, PLPL gets 100, PJER gets a 1, PCMT gets 999, PLHY gets -31, 
    
    # For attributes which have a column in the 'Latest Player Attributes.csv' file, use the value if it differs from 
    # the default value we put in that column. If not, we will use formulas to determine what value to use. 
    
def create_middle_linebacker(player_dict, index):
    """ 
    Given a dictionary of a new player and the index of the related record to modify in the DB, performs all of 
    the calculations and updates necessary to create the player as a QB in the DB.
    """
    # For all of the following fields, we simply use 0.
    # TLHA, TRHA, PCPH, PLSH, PRSH, PLTH, PRTH, PUCL, TLEL, TREL, PTSL, PSTM, PFHO, PSXP, TLWR, TRWR, PMUS, PJTY, PSTY
    set_player_integer_field('TLHA', index, 0)
    
    # PPTI will always get 1009, PLPL gets 100, PJER gets a 1, PCMT gets 999, PLHY gets -31, 
    
    # For attributes which have a column in the 'Latest Player Attributes.csv' file, use the value if it differs from 
    # the default value we put in that column. If not, we will use formulas to determine what value to use. 
    
def create_right_outside_linebacker(player_dict, index):
    """ 
    Given a dictionary of a new player and the index of the related record to modify in the DB, performs all of 
    the calculations and updates necessary to create the player as a QB in the DB.
    """
    # For all of the following fields, we simply use 0.
    # TLHA, TRHA, PCPH, PLSH, PRSH, PLTH, PRTH, PUCL, TLEL, TREL, PTSL, PSTM, PFHO, PSXP, TLWR, TRWR, PMUS, PJTY, PSTY
    set_player_integer_field('TLHA', index, 0)
    
    # PPTI will always get 1009, PLPL gets 100, PJER gets a 1, PCMT gets 999, PLHY gets -31, 
    
    # For attributes which have a column in the 'Latest Player Attributes.csv' file, use the value if it differs from 
    # the default value we put in that column. If not, we will use formulas to determine what value to use. 
    
def create_cornerback(player_dict, index):
    """ 
    Given a dictionary of a new player and the index of the related record to modify in the DB, performs all of 
    the calculations and updates necessary to create the player as a QB in the DB.
    """
    # For all of the following fields, we simply use 0.
    # TLHA, TRHA, PCPH, PLSH, PRSH, PLTH, PRTH, PUCL, TLEL, TREL, PTSL, PSTM, PFHO, PSXP, TLWR, TRWR, PMUS, PJTY, PSTY
    set_player_integer_field('TLHA', index, 0)
    
    # PPTI will always get 1009, PLPL gets 100, PJER gets a 1, PCMT gets 999, PLHY gets -31, 
    
    # For attributes which have a column in the 'Latest Player Attributes.csv' file, use the value if it differs from 
    # the default value we put in that column. If not, we will use formulas to determine what value to use. 
    
def create_free_safety(player_dict, index):
    """ 
    Given a dictionary of a new player and the index of the related record to modify in the DB, performs all of 
    the calculations and updates necessary to create the player as a QB in the DB.
    """
    # For all of the following fields, we simply use 0.
    # TLHA, TRHA, PCPH, PLSH, PRSH, PLTH, PRTH, PUCL, TLEL, TREL, PTSL, PSTM, PFHO, PSXP, TLWR, TRWR, PMUS, PJTY, PSTY
    set_player_integer_field('TLHA', index, 0)
    
    # PPTI will always get 1009, PLPL gets 100, PJER gets a 1, PCMT gets 999, PLHY gets -31, 
    
    # For attributes which have a column in the 'Latest Player Attributes.csv' file, use the value if it differs from 
    # the default value we put in that column. If not, we will use formulas to determine what value to use. 
    
def create_strong_safety(player_dict, index):
    """ 
    Given a dictionary of a new player and the index of the related record to modify in the DB, performs all of 
    the calculations and updates necessary to create the player as a QB in the DB.
    """
    # For all of the following fields, we simply use 0.
    # TLHA, TRHA, PCPH, PLSH, PRSH, PLTH, PRTH, PUCL, TLEL, TREL, PTSL, PSTM, PFHO, PSXP, TLWR, TRWR, PMUS, PJTY, PSTY
    set_player_integer_field('TLHA', index, 0)
    
    # PPTI will always get 1009, PLPL gets 100, PJER gets a 1, PCMT gets 999, PLHY gets -31, 
    
    # For attributes which have a column in the 'Latest Player Attributes.csv' file, use the value if it differs from 
    # the default value we put in that column. If not, we will use formulas to determine what value to use. 
    
def create_kicker(player_dict, index):
    """ 
    Given a dictionary of a new player and the index of the related record to modify in the DB, performs all of 
    the calculations and updates necessary to create the player as a QB in the DB.
    """
    # For all of the following fields, we simply use 0.
    # TLHA, TRHA, PCPH, PLSH, PRSH, PLTH, PRTH, PUCL, TLEL, TREL, PTSL, PSTM, PFHO, PSXP, TLWR, TRWR, PMUS, PJTY, PSTY
    set_player_integer_field('TLHA', index, 0)
    
    # PPTI will always get 1009, PLPL gets 100, PJER gets a 1, PCMT gets 999, PLHY gets -31, 
    
    # For attributes which have a column in the 'Latest Player Attributes.csv' file, use the value if it differs from 
    # the default value we put in that column. If not, we will use formulas to determine what value to use. 
    
def create_punter(player_dict, index):
    """ 
    Given a dictionary of a new player and the index of the related record to modify in the DB, performs all of 
    the calculations and updates necessary to create the player as a QB in the DB.
    """
    # For all of the following fields, we simply use 0.
    # TLHA, TRHA, PCPH, PLSH, PRSH, PLTH, PRTH, PUCL, TLEL, TREL, PTSL, PSTM, PFHO, PSXP, TLWR, TRWR, PMUS, PJTY, PSTY
    set_player_integer_field('TLHA', index, 0)
    
    # PPTI will always get 1009, PLPL gets 100, PJER gets a 1, PCMT gets 999, PLHY gets -31, 
    
    # For attributes which have a column in the 'Latest Player Attributes.csv' file, use the value if it differs from 
    # the default value we put in that column. If not, we will use formulas to determine what value to use. 
    
def delete_players(number_to_delete):
    """ Marks the given number of player records (from the end of the PLAY table) for deletion. """
    logging.info("Deleting %d player records.", number_to_delete)
    for index in range(
            PLAYER_TABLE_PROPERTIES.RecordCount - number_to_delete, 
            PLAYER_TABLE_PROPERTIES.RecordCount):
        record_was_marked_deleted = TDBACCESS_DLL.TDBTableRecordChangeDeleted(
            DB_INDEX, 
            PLAYERS_TABLE, 
            index, 
            True
        )
        if not record_was_marked_deleted:
            logging.error("\tFailed to mark record #%d for deletion!", index)

def add_players(number_to_add):
    """ Adds the given number of player records to the end of the PLAY table. """
    logging.info("Adding %d player records.", number_to_add)
    for index in range(number_to_add):
        added_player_record = TDBACCESS_DLL.TDBTableRecordAdd(
            DB_INDEX, 
            PLAYERS_TABLE,
            False
        )
        if added_player_record == 65535:
            logging.error("\tFailed to add record #%d!", index)
    TDBACCESS_DLL.TDBTableGetProperties(DB_INDEX, 6, byref(PLAYER_TABLE_PROPERTIES))
    logging.info("PLAY table now has %d player records.", PLAYER_TABLE_PROPERTIES.RecordCount)

def get_existing_player_count():
    """ Returns the number of player records currently in the roster file. """
    
    # Call the getter for the PLAY table's properties.
    got_table_properties = TDBACCESS_DLL.TDBTableGetProperties(DB_INDEX, 6, byref(PLAYER_TABLE_PROPERTIES))
    
    if got_table_properties:
        
        logging.info("PLAYER_TABLE_PROPERTIES.Name = %s", PLAYER_TABLE_PROPERTIES.Name)
        logging.info("PLAYER_TABLE_PROPERTIES.FieldCount = %d", PLAYER_TABLE_PROPERTIES.FieldCount)
        logging.info("PLAYER_TABLE_PROPERTIES.Capacity = %d", PLAYER_TABLE_PROPERTIES.Capacity)
        logging.info("PLAYER_TABLE_PROPERTIES.RecordCount = %d", PLAYER_TABLE_PROPERTIES.RecordCount)
        logging.info("PLAYER_TABLE_PROPERTIES.DeletedCount = %d", PLAYER_TABLE_PROPERTIES.DeletedCount)
        logging.info("PLAYER_TABLE_PROPERTIES.NextDeletedRecord = %d", PLAYER_TABLE_PROPERTIES.NextDeletedRecord)
        
        # Return the number in the field RecordCount minus the value in DeletedCount.
        return PLAYER_TABLE_PROPERTIES.RecordCount - PLAYER_TABLE_PROPERTIES.DeletedCount
        
    logging.error("\tFailed to read properties of PLAY table!")
    return -1

def compact_save_close_db():
    """ Compacts, saves, and closes the DB via the TDBACCESS_DLL. """
    # Compact the DB.
    compacted_database = TDBACCESS_DLL.TDBDatabaseCompact(DB_INDEX)
    if compacted_database:
        logging.info("Compacted the TDBDatabase.")
    else:
        logging.error("\tFailed to compact the TDBDatabase!")

    # Save the DB.
    saved_database = TDBACCESS_DLL.TDBSave(DB_INDEX)
    if saved_database:
        logging.info("Saved the TDBDatabase.")
    else:
        logging.error("\tFailed to save the TDBDatabase!")

    # Close the DB.
    closed_database = TDBACCESS_DLL.TDBClose(DB_INDEX)
    if closed_database:
        logging.info("Closed the TDBDatabase.")
    else:
        logging.error("\tFailed to close the TDBDatabase!")

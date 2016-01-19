r""" 04_update_roster_file.py

This is one of the two main Python scripts called when updating the base Madden 
NFL '08 roster file, to be called using the syntax: 
    > python 04_update_roster_file.py

This script is only one part of the process for generating an updated Madden 
NFL '08 Roster file. Prior to running this script, the first three steps of the 
process need to be performed. Please refer to the document "00 README for 
Madden_08_Updater.docx" for more information. 

This script requires the following files to be placed in the "utilities" folder 
alongside it, meaning in 
 os.path.join(os.path.dirname(os.path.abspath(__file__)), r"utilities\") : 
    1) The helper file, 'helper_functions.py' 
    2) The folder and file 'tdbaccess\old\tdbaccess.dll' 
Additionally, the below files must be in the 'inputs' folder, meaning in 
 os.path.join(os.path.dirname(os.path.abspath(__file__)), r"inputs\") : 
    1) The base Madden '08 Roster file to update, named 'base.ros' 
    2) The latest set of Madden ratings as CSV, 'Latest Madden Ratings.csv' 
    3) The latest NFL/FBG bio/ratings CSV file, named 'NFL and FBG.csv' 

This script will generate the file "latest.ros" in the folder 'outputs'.
"""

# --------------------------------- SECTION 1 ---------------------------------
# --------------------- IMPORTS, SETTINGS, AND CONSTANTS ----------------------
# 1 - Standard library imports
import os
import csv
#import math
from ctypes import Structure, c_char_p, c_int, c_bool, c_char, c_float, WinDLL, 
                   POINTER, 
from enum import Enum


# 2 - Third-party imports

# 3 - Application-specific imports
#from utilities.helper_functions import *

# 4 - Global settings


# 5 - Global constants
# Set the base path we will use to keep other paths relative, and shorter :^)
BASE_MADDEN_PATH = r"C:\Home\madden_08_updater"


# --------------------------------- SECTION 2 ---------------------------------
# ---------------------------- Class Declarations -----------------------------

# The structure for structTDBTableProperties.
class structTDBTableProperties(Structure):
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
#        super(structTDBTableProperties, self).__init__(*args)

# The structure for structTDBFieldProperties.
class structTDBFieldProperties(Structure):
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
#        super(structTDBFieldProperties, self).__init__(*args)


# --------------------------------- SECTION 3 ---------------------------------
# ----------------------------- Helper Functions ------------------------------

def SetPlayerIntegerAttribute(int_player_index, str_attribute, int_value): 
    """ 
    """
    bool_value_was_set = dllTDBAccess.TDBFieldSetValueAsInteger(intDBIndex, 
                         "PLAY", str_attribute, int_player_index, int_value)
    if bool_value_was_set:
        int_value_returned = dllTDBAccess.TDBFieldGetValueAsInteger(intDBIndex, 
                             "PLAY", str_attribute, int_player_index)
        print("\nSet Player %d's %s field to %d" % (int_player_index, 
                                                    str_attribute, 
                                                    int_value_returned))
    else:
        print("\nError in setting Player %d's %s field." % (int_player_index, 
                                                            str_attribute))

def SetPlayerStringAttribute(int_player_index, str_attribute, strValue):
    """ 
        TODO: REWRITE THIS FUNC USING PYTHON CONVENTIONS.
    """
    boolSetValueAsString = dllTDBAccess.TDBFieldSetValueAsString(intDBIndex, "PLAY", str_attribute, int_player_index, strValue)
    if boolSetValueAsString:
        stringVal = cast((c_char * 14)(), c_char_p)
        boolGotValueAsString = dllTDBAccess.TDBFieldGetValueAsString(intDBIndex, "PLAY", str_attribute, int_player_index, byref(stringVal))
        if boolGotValueAsString:
            print("Set Player %d's %s field to %s" % (int_player_index, str_attribute, stringVal.value))
        else:
            print("\nError in setting Player %d's %s field." % (int_player_index, str_attribute))
    else:
        print("\nError in setting Player %d's %s field." % (int_player_index, str_attribute))


# --------------------------------- SECTION 4 ---------------------------------
# ------------------------------ Main Function --------------------------------

# -------------- Step 1 - READ FROM THE MADDEN RATINGS .csv FILE --------------

# Open the CSV file with all the players and their Madden ratings.
file_Madden_ratings = open(os.path.join(BASE_MADDEN_PATH, 
                         r"process\inputs\Latest Madden Ratings.csv"))

# Get a DictReader to read the rows into dicts using the header row as keys.
iter_Madden_ratings_dict_reader = csv.DictReader(file_Madden_ratings)

# Get the dict representing the first row.
dict_first_Madden_player_ratings = iter_Madden_ratings_dict_reader.next()

# Show what we got.
print("\ndict_first_Madden_player_ratings = %r" % 
      dict_first_Madden_player_ratings)

# Close the Madden Ratings .csv file.
file_Madden_ratings.close()


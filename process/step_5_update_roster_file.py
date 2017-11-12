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
        2) The latest set of Madden ratings as CSV, 'Latest Madden Ratings.csv' 
        3) The latest NFL roster bios CSV file, named 'NFL rosters.csv' 
    
    This script will generate the file "latest.ros" in the folder 'outputs'.
"""


# ----------------------------------------------------- SECTION 1 -----------------------------------------------------
# ----------------------------------------- IMPORTS, SETTINGS, AND CONSTANTS ------------------------------------------
# 1 - Standard library imports

import csv, os, sys
#import math
from ctypes import byref, cast, c_bool, c_char, c_char_p, c_float, c_int, POINTER, Structure, WinDLL
from enum import Enum


# 2 - Third-party imports


# 3 - Application-specific imports

#from utilities.helper_functions import *


# 4 - Global settings


# 5 - Global constants

# Set the base path we will use to keep other paths relative, and shorter :^)
# like "E:\Home\Working Files\madden_08_updater"
BASE_MADDEN_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ----------------------------------------------------- SECTION 2 -----------------------------------------------------
# ------------------------------------------------ Class Declarations -------------------------------------------------

class TDBTableProperties(Structure):
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
#        super(TDBTableProperties, self).__init__(*args)

class TDBFieldProperties(Structure):
    """Structure whose fields hold all the properties of a field from a table in the roster file."""
    _fields_ = [
        ('Name', c_char_p),
        ('Size', c_int),
        ('FieldType', c_int),
    ]
    
    def __init__(self, *args):
        self.Name = cast((c_char * 8)(), c_char_p)
        Structure.__init__(self, *args)
#        super(TDBFieldProperties, self).__init__(*args)


# ----------------------------------------------------- SECTION 3 -----------------------------------------------------
# ------------------------------------------------- Helper Functions --------------------------------------------------

def set_player_integer_attribute(intPlayerIndex, strAttribute, intValue): 
    """ 
    """
    boolValueWasSet = TDBAccessDLL.TDBFieldSetValueAsInteger(
            intDBIndex, "PLAY", strAttribute, intPlayerIndex, intValue)
    
    if boolValueWasSet:
        intValue_returned = TDBAccessDLL.TDBFieldGetValueAsInteger(
                                intDBIndex, "PLAY", strAttribute, intPlayerIndex)
        
        print("\nSet Player %d's %s field to %d" % (intPlayerIndex, strAttribute, intValue_returned))
    else:
        print("\nError in setting Player %d's %s field." % (intPlayerIndex, strAttribute))


def set_player_string_attribute(intPlayerIndex, strAttribute, strValue):
    """ 
    """
    boolSetValueAsString = TDBAccessDLL.TDBFieldSetValueAsString(
                            intDBIndex, "PLAY", strAttribute, intPlayerIndex, strValue)
    
    if boolSetValueAsString:
        stringVal = cast((c_char * 14)(), c_char_p)
        boolGotValueAsString = TDBAccessDLL.TDBFieldGetValueAsString(
                                intDBIndex, "PLAY", strAttribute, intPlayerIndex, byref(stringVal))

        if boolGotValueAsString:
            print("Set Player %d's %s field to %s" % (intPlayerIndex, strAttribute, stringVal.value))
        else:
            print("\nError in setting Player %d's %s field." % (intPlayerIndex, strAttribute))
    else:
        print("\nError in setting Player %d's %s field." % (intPlayerIndex, strAttribute))


# ----------------------------------------------------- SECTION 4 -----------------------------------------------------
# ------------------------------------------------ Main Functionality -------------------------------------------------

# Local variables.
# TODO: Wrap this WinDLL call in error checking. (Google 'python windll error handling')
TDBAccessDLL = WinDLL(os.path.join(BASE_MADDEN_PATH, r"process\utilities\tdbaccess\old\tdbaccess.dll"))

# STEP 1 - SET UP OUR DLL OBJECT WITH THE CORRECT ARGTYPES AND RESTYPES.

# TODO: Add the restype definitions here for each of the 21 functions.
TDBAccessDLL.TDBClose.argtypes = [c_int]
TDBAccessDLL.TDBClose.restype = c_bool

TDBAccessDLL.TDBDatabaseCompact.argtypes = [c_int]
TDBAccessDLL.TDBDatabaseCompact.restype = c_bool

TDBAccessDLL.TDBDatabaseGetTableCount.argtypes = [c_int]
TDBAccessDLL.TDBDatabaseGetTableCount.restype = c_int

TDBAccessDLL.TDBFieldGetProperties.argtypes = [c_int, c_char_p, c_int, POINTER(TDBFieldProperties)]
TDBAccessDLL.TDBFieldGetProperties.restype = c_bool

#TDBAccessDLL.TDBFieldGetValueAsBinary.argtypes = [c_int, c_char_p, c_char_p, c_int, POINTER(c_char_p)]

#TDBAccessDLL.TDBFieldGetValueAsFloat.argtypes = [c_int, c_char_p, c_char_p, c_int]

TDBAccessDLL.TDBFieldGetValueAsInteger.argtypes = [c_int, c_char_p, c_char_p, c_int]
TDBAccessDLL.TDBFieldGetValueAsInteger.restype = c_int

TDBAccessDLL.TDBFieldGetValueAsString.argtypes = [c_int, c_char_p, c_char_p, c_int, POINTER(c_char_p)]
TDBAccessDLL.TDBFieldGetValueAsString.restype = c_bool

TDBAccessDLL.TDBFieldSetValueAsFloat.argtypes = [c_int, c_char_p, c_char_p, c_int, c_float]

TDBAccessDLL.TDBFieldSetValueAsInteger.argtypes = [c_int, c_char_p, c_char_p, c_int, c_int]

TDBAccessDLL.TDBFieldSetValueAsString.argtypes = [c_int, c_char_p, c_char_p, c_int, c_char_p]
TDBAccessDLL.TDBFieldSetValueAsString.restype = c_bool

TDBAccessDLL.TDBOpen.argtypes = [c_char_p]
TDBAccessDLL.TDBOpen.restype = c_int

#TDBAccessDLL.TDBQueryFindUnsignedInt.argtypes = [c_int, c_char_p, c_char_p, c_int]

#TDBAccessDLL.TDBQueryGetResult.argtypes = [c_int]

#TDBAccessDLL.TDBQueryGetResultSize.argtypes = []

TDBAccessDLL.TDBSave.argtypes = [c_int]
TDBAccessDLL.TDBSave.restype = c_bool

TDBAccessDLL.TDBTableGetProperties.argtypes = [c_int, c_int, POINTER(TDBTableProperties)]
TDBAccessDLL.TDBTableGetProperties.restype = c_bool

#TDBAccessDLL.TDBTableRecordAdd.argtypes = [c_int, c_char_p, c_bool]

#TDBAccessDLL.TDBTableRecordChangeDeleted.argtypes = [c_int, c_char_p, c_int, c_bool]

#TDBAccessDLL.TDBTableRecordDeleted.argtypes = [c_int, c_char_p, c_int]

#TDBAccessDLL.TDBTableRecordRemove.argtypes = [c_int, c_char_p, c_int]


# STEP 2 - OPEN THE ROSTER FILE THROUGH THE DLL.
intDBIndex = TDBAccessDLL.TDBOpen(os.path.join(BASE_MADDEN_PATH, r"process\inputs\base.ros").encode('utf-8'))
print("\nintDBIndex = %d" % intDBIndex)


# STEP 3 - READ IN THE TABLE PROPERTIES.

# We'll use this to control a loop over the tables.
intNumberOfTables = TDBAccessDLL.TDBDatabaseGetTableCount(intDBIndex)
print("\nintNumberOfTables = %d" % intNumberOfTables)

# Create a list to hold all our table properties structs.
listTDBTablePropertiesStructs = []

# Loop over the tables and get their properties.
for i in range(intNumberOfTables):
    listTDBTablePropertiesStructs.append(TDBTableProperties())
    boolGotTableProperties = TDBAccessDLL.TDBTableGetProperties(intDBIndex, i, byref(listTDBTablePropertiesStructs[i]))
    if boolGotTableProperties:
        print("\nlistTDBTablePropertiesStructs[%d].Name = %s" % (i, listTDBTablePropertiesStructs[i].Name))
        print("listTDBTablePropertiesStructs[%d].FieldCount = %d" % (i, listTDBTablePropertiesStructs[i].FieldCount))
        print("listTDBTablePropertiesStructs[%d].Capacity = %d" % (i, listTDBTablePropertiesStructs[i].Capacity))
        print("listTDBTablePropertiesStructs[%d].RecordCount = %d" % (i, listTDBTablePropertiesStructs[i].RecordCount))
        print("listTDBTablePropertiesStructs[%d].DeletedCount = %d" % 
                (i, listTDBTablePropertiesStructs[i].DeletedCount))
        print("listTDBTablePropertiesStructs[%d].NextDeletedRecord = %d" % 
                (i, listTDBTablePropertiesStructs[i].NextDeletedRecord))

# A list to hold the properties structs for each field in table 6, the "PLAY" table.
listTDBTable6FieldPropertiesStructs = []

# A list to hold the field names, needed only for writing the CSV file later.
#listTDBTable6FieldNames = []

# Get the properties of each of the fields for the table.
for i in range(listTDBTablePropertiesStructs[6].FieldCount):
    listTDBTable6FieldPropertiesStructs.append(TDBFieldProperties())
    boolGotTableFieldProperties = TDBAccessDLL.TDBFieldGetProperties(
            intDBIndex, listTDBTablePropertiesStructs[6].Name, i, byref(listTDBTable6FieldPropertiesStructs[i]))
    if boolGotTableFieldProperties:
        # Add each field name to our list.
        #listTDBTable6FieldNames.append(listTDBTable6FieldPropertiesStructs[i].Name)
        print("\nlistTDBTable6FieldPropertiesStructs[%d].Name = %s" % (i, listTDBTable6FieldPropertiesStructs[i].Name.decode()))
        print("listTDBTable6FieldPropertiesStructs[%d].Size = %d" % (i, listTDBTable6FieldPropertiesStructs[i].Size))
        print("listTDBTable6FieldPropertiesStructs[%d].FieldType = %d" % 
                (i, listTDBTable6FieldPropertiesStructs[i].FieldType))
    else:
        print("\nERROR: Unable to get field properties for element %d in listTDBTable6FieldPropertiesStructs." % i)

# Give us some breathing space before the next section.
print("\n\n")


# STEP 4 - EDIT PLAYER 0's FIRST NAME.

boolSetValueAsString = TDBAccessDLL.TDBFieldSetValueAsString(
        intDBIndex, listTDBTablePropertiesStructs[6].Name, b"PFNA", 0, b"SOMEONE")
if boolSetValueAsString:
    # Try getting the new name back out using the Get method.
    stringVal = cast((c_char * 12)(), c_char_p)
    boolGotValueAsString = TDBAccessDLL.TDBFieldGetValueAsString(
            intDBIndex, listTDBTablePropertiesStructs[6].Name, b"PFNA", 0, byref(stringVal))
    if boolGotValueAsString:
        print("We've set the string for player 0's PFNA field to %s." % stringVal.value.decode())
    else:
        print("UNABLE TO GET STRING VALUE FROM FIELD 'PFNA' AFTER SETTING IT.")
else:
    print("UNABLE TO SET STRING VALUE IN FIELD 'PFNA'.")

# Give us some breathing space before the next section.
print()




#----------------------------------------------------------------------------------------------------------------------

# Get the info on the player at index 0.
stringLastName = cast((c_char * 14)(), c_char_p) # Since PLNA.Size = 104, we need 14 bytes (104/8, +1 for terminator)
boolGotValueAsString = TDBAccessDLL.TDBFieldGetValueAsString(
        intDBIndex, listTDBTablePropertiesStructs[6].Name, b"PLNA", 0, byref(stringLastName))
if boolGotValueAsString:
    print("Player 0's PLNA field is %s." % stringLastName.value.decode())
else:
    print("UNABLE TO GET STRING VALUE FROM FIELD 'PLNA'.")

#sys.exit()

#----------------------------------------------------------------------------------------------------------------------




# STEP 5 - COMPACT, SAVE, AND CLOSE THE DB.

# Compact the DB.
boolCompactedTDBDatabase = TDBAccessDLL.TDBDatabaseCompact(intDBIndex)
if boolCompactedTDBDatabase:
    print("\nCompacted the TDBDatabase.")
else:
    print("\nWarning: Failed to compact the TDBDatabase.")

# Save the DB.
boolSavedTDBDatabase = TDBAccessDLL.TDBSave(intDBIndex)
if boolSavedTDBDatabase:
    print("\nSaved the TDBDatabase.")
else:
    print("\nWarning: Failed to save the TDBDatabase.")

# Close the DB.
boolClosedTDBDatabase = TDBAccessDLL.TDBClose(intDBIndex)
if boolClosedTDBDatabase:
    print("\nClosed the TDBDatabase.")
else:
    print("\nWarning: Failed to close the TDBDatabase.")


# TESTING OUR ABILITY TO READ FROM THE MADDEN RATINGS .csv FILE.

# Open the CSV file with all the players and their Madden ratings.
#fileMaddenRatings = open(os.path.join(BASE_MADDEN_PATH, r"process\inputs\Latest Madden Ratings.csv"))

# Get a DictReader to read the rows into dicts using the header row as keys.
#iterMaddenRatingsReader = csv.DictReader(fileMaddenRatings)

    # Get the dict representing the first row.
    #dictFirstMaddenPlayerRatings = iterMaddenRatingsReader.next()

# Create a list to hold our dicts.
#listMaddenRatingsDicts = []

# Loop over the rows in the CSV file and make a dict for each in our list of dicts.
#for row in iterMaddenRatingsReader:
#   listMaddenRatingsDicts.append(row)

# TODO - Figure out how to search for a player by name (eg. Reggie Bush).

#print("\nlistMaddenRatingsDicts[2325] = %r" % listMaddenRatingsDicts[2325])

# Close the Madden Ratings .csv file.
#fileMaddenRatings.close()

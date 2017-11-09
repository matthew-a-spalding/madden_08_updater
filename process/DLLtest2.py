r""" DLLtest2.py
    
    This file currently opens the file "base.ros", calls TDBTableGetProperties on each of the tables, gets the 
    properties of each field in table 6 (the "PLAY" table of player info), and then writes all of the 110 attributes 
    of each player to a CSV file named "players_current.csv".
"""

# ----------------------------------------------------- SECTION 1 -----------------------------------------------------
# ----------------------------------------- IMPORTS, SETTINGS, AND CONSTANTS ------------------------------------------

# 1.1 - Standard library imports
import os, csv
from ctypes import WinDLL, Structure, c_char_p, c_int, c_bool, cast, c_char, c_float, POINTER, byref

# 1.2 - Third-party imports

# 1.3 - Application-specific imports

# 1.4 - Global settings

# 1.5 - Global constants
# Set the base path to our files.
BASE_MADDEN_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ----------------------------------------------------- SECTION 2 -----------------------------------------------------
# ------------------------------------------------ Class Declarations -------------------------------------------------

class TDBTableProperties(Structure):
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
#        super(TDBTableProperties, self).__init__(*args)

class TDBFieldProperties(Structure):
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
#        super(TDBFieldProperties, self).__init__(*args)


# ----------------------------------------------------- SECTION 3 -----------------------------------------------------
# ------------------------------------------------- Helper Functions --------------------------------------------------


# ----------------------------------------------------- SECTION 4 -----------------------------------------------------
# -------------------------------------------------- Main Function ----------------------------------------------------

# 4.1 - Read from the Madden ratings .csv file.

# Open the CSV file with all the latest Madden player ratings.
#fileMaddenRatings = open(os.path.join(BASE_MADDEN_PATH, r"process\inputs\Latest Madden Ratings.csv")

# Get a DictReader to read the rows into dicts using the header row as keys.
#iterMaddenRatingsReader = csv.DictReader(fileMaddenRatings)

# Create a list to hold our dicts.
#listMaddenRatingsDicts = []

# Loop over the rows in the CSV file and make a dict for each in our list of dicts.
#for row in iterMaddenRatingsReader:
#   listMaddenRatingsDicts.append(row)

#fileMaddenRatings.close()

# ------------- 4.2 -  Access the Madden '08 roster file. ---------------------

# Get a handle for our DLL.
TDBAccessDLL = WinDLL(os.path.join(BASE_MADDEN_PATH, r"process\utilities\tdbaccess\old\tdbaccess.dll"))

# Open the roster file through the DLL.
intDBIndex = TDBAccessDLL.TDBOpen(os.path.join(BASE_MADDEN_PATH, r"process\inputs\base.ros").encode('utf-8'))
print("\nintDBIndex = %d" % intDBIndex)

# Add the argtypes and restype definitions here for the functions we'll use.
TDBAccessDLL.TDBClose.argtypes = [c_int]
TDBAccessDLL.TDBClose.restype = c_bool

TDBAccessDLL.TDBDatabaseCompact.argtypes = [c_int]
TDBAccessDLL.TDBDatabaseCompact.restype = c_bool

TDBAccessDLL.TDBDatabaseGetTableCount.argtypes = [c_int]
TDBAccessDLL.TDBDatabaseGetTableCount.restype = c_int

TDBAccessDLL.TDBFieldGetProperties.argtypes = [c_int, c_char_p, c_int, POINTER(TDBFieldProperties)]
#TDBAccessDLL.TDBFieldGetProperties.argtypes = [c_int, c_wchar_p, c_int, POINTER(TDBFieldProperties)]
TDBAccessDLL.TDBFieldGetProperties.restype = c_int

#TDBAccessDLL.TDBFieldGetValueAsBinary.argtypes = [c_int, c_char_p, c_char_p, c_int, POINTER(c_char_p)]
#TDBAccessDLL.TDBFieldGetValueAsBinary.restype = c_int

#TDBAccessDLL.TDBFieldGetValueAsFloat.argtypes = [c_int, c_char_p, c_char_p, c_int]

TDBAccessDLL.TDBFieldGetValueAsInteger.argtypes = [c_int, c_char_p, c_char_p, c_int]
TDBAccessDLL.TDBFieldGetValueAsInteger.restype = c_int

TDBAccessDLL.TDBFieldGetValueAsString.argtypes = [c_int, c_char_p, c_char_p, c_int, POINTER(c_char_p)]
TDBAccessDLL.TDBFieldGetValueAsString.restype = c_bool

#TDBAccessDLL.TDBFieldSetValueAsFloat.argtypes = [c_int, c_char_p, c_char_p, c_int, c_float]

#TDBAccessDLL.TDBFieldSetValueAsInteger.argtypes = [c_int, c_char_p, c_char_p, c_int, c_int]

TDBAccessDLL.TDBFieldSetValueAsString.argtypes = [c_int, c_char_p, c_char_p, c_int, c_char_p]
TDBAccessDLL.TDBFieldSetValueAsString.restype = c_bool

TDBAccessDLL.TDBOpen.argtypes = [c_char_p]
#TDBAccessDLL.TDBOpen.argtypes = [c_wchar_p]
TDBAccessDLL.TDBOpen.restype = c_int

TDBAccessDLL.TDBSave.argtypes = [c_int]
TDBAccessDLL.TDBSave.restype = c_bool

TDBAccessDLL.TDBTableGetProperties.argtypes = [c_int, c_int, POINTER(TDBTableProperties)]
TDBAccessDLL.TDBTableGetProperties.restype = c_bool


# ------------------ 4.3 -  Read in the table properties. ---------------------

# We'll use this to control a loop over the tables.
intNumberOfTables = TDBAccessDLL.TDBDatabaseGetTableCount(intDBIndex)
print("\nintNumberOfTables = %d" % intNumberOfTables)

# Create a list to hold all our table properties structs.
listTDBTablePropertiesStructs = []

# Loop over the tables and get their properties.
for i in range(intNumberOfTables):
    listTDBTablePropertiesStructs.append(TDBTableProperties())
    boolGotTableProperties = TDBAccessDLL.TDBTableGetProperties(intDBIndex, i, byref(listTDBTablePropertiesStructs[i]))
#    if boolGotTableProperties:
#        print("\nlistTDBTablePropertiesStructs[%d].Name = %s" % (i, listTDBTablePropertiesStructs[i].Name))
#        print("listTDBTablePropertiesStructs[%d].FieldCount = %d" % (i, listTDBTablePropertiesStructs[i].FieldCount))
#        print("listTDBTablePropertiesStructs[%d].Capacity = %d" % (i, listTDBTablePropertiesStructs[i].Capacity))
#        print("listTDBTablePropertiesStructs[%d].RecordCount = %d" % (i, listTDBTablePropertiesStructs[i].RecordCount))
#        print("listTDBTablePropertiesStructs[%d].DeletedCount = %d" % (i, listTDBTablePropertiesStructs[i].DeletedCount))
#        print("listTDBTablePropertiesStructs[%d].NextDeletedRecord = %d" % (i, listTDBTablePropertiesStructs[i].NextDeletedRecord))

# ------------ OPTION 1: A list to hold the properties structs for each field in table 6, the "PLAY" table ------------

# A list to hold the field properties structs for table 6, "PLAY"
listTDBTable6FieldPropertiesStructs = []

# A list to hold the field names, needed only for writing the CSV file later.
listTDBTable6FieldNames = []

# Get the properties of each of the fields for the table.
for i in range(listTDBTablePropertiesStructs[6].FieldCount):
    listTDBTable6FieldPropertiesStructs.append(TDBFieldProperties())
    boolGotTableFieldProperties = TDBAccessDLL.TDBFieldGetProperties(intDBIndex, listTDBTablePropertiesStructs[6].Name, i, byref(listTDBTable6FieldPropertiesStructs[i]))
    if boolGotTableFieldProperties:
        # Want to add each field name to our list.
        listTDBTable6FieldNames.append(listTDBTable6FieldPropertiesStructs[i].Name.decode())
        print("\nlistTDBTable6FieldPropertiesStructs[%d].Name = %r" % (i, listTDBTable6FieldNames[i]))
#        print("listTDBTable6FieldPropertiesStructs[%d].Size = %d" % (i, listTDBTable6FieldPropertiesStructs[i].Size))
#        print("listTDBTable6FieldPropertiesStructs[%d].FieldType = %d" % (i, listTDBTable6FieldPropertiesStructs[i].FieldType))
    else:
        print("\nERROR: Unable to get field properties for element %d in listTDBTable6FieldPropertiesStructs." % i)

# -------------- OPTION 2: A list of lists to hold the properties structs for all 10 of the tables --------------

# A list to hold lists of all our field properties structs for each table.
#listTDBFieldPropertiesStructsLists = [[] for x in range(intNumberOfTables)]

# Get the properties of each of the fields for each table.
#for i in range(intNumberOfTables):
#    print("\n")
#    for j in range(listTDBTablePropertiesStructs[i].FieldCount):
#        listTDBFieldPropertiesStructsLists[i].append(TDBFieldProperties())
#        boolGotTableFieldProperties = TDBAccessDLL.TDBFieldGetProperties(intDBIndex, listTDBTablePropertiesStructs[i].Name, j, byref(listTDBFieldPropertiesStructsLists[i][j]))
#        if boolGotTableFieldProperties and i == 6:
#            print("\nlistTDBFieldPropertiesStructsLists[%d][%d].Name = %r" % (i, j, listTDBFieldPropertiesStructsLists[i][j].Name))
#            print("listTDBFieldPropertiesStructsLists[%d][%d].Size = %d" % (i, j, listTDBFieldPropertiesStructsLists[i][j].Size))
#            print("listTDBFieldPropertiesStructsLists[%d][%d].FieldType = %d" % (i, j, listTDBFieldPropertiesStructsLists[i][j].FieldType))

# Give us some breathing space before the next section.
#print("\n")


# ------------------ WRITE PLAYERS' ATTRIBUTES TO A FILE ------------------

# We want to write all of the 110 attributes of each player to a CSV file.
# So, we will need a list of dicts to keep the field.Name keys paired with their values for each player.
listPlayerAttributeDicts = []

# Start the loop over the players.
for i in range(listTDBTablePropertiesStructs[6].RecordCount):
    # Append to the list a new empty dict for this player.
    listPlayerAttributeDicts.append({})
    # Loop over the list of structs for the fields in the PLAY table.
    for j, structFieldProperties in enumerate(listTDBTable6FieldPropertiesStructs):
        if structFieldProperties.FieldType == 0: # tdbString
            # First, create the string where we will hold the value.
            stringVal = cast((c_char * ((structFieldProperties.Size // 8) + 1))(), c_char_p)
            boolGotValueAsString = TDBAccessDLL.TDBFieldGetValueAsString(intDBIndex, listTDBTablePropertiesStructs[6].Name, structFieldProperties.Name, i, byref(stringVal))
            if boolGotValueAsString:
                listPlayerAttributeDicts[i][structFieldProperties.Name.decode()] = stringVal.value.decode()
                if i == 0:
                    print("%d: stringVal for player 0's %s field = %s" % (j, structFieldProperties.Name, listPlayerAttributeDicts[i][structFieldProperties.Name.decode()]))
            else:
                if i == 0:
                    print("%d: Field %s is a string. UNABLE TO GET STRING VALUE." % (j, structFieldProperties.Name))
        elif structFieldProperties.FieldType == 2 or structFieldProperties.FieldType == 3: # tdbSInt or tdbUInt
            # Just call the function to get an int value.
            listPlayerAttributeDicts[i][structFieldProperties.Name.decode()] = TDBAccessDLL.TDBFieldGetValueAsInteger(intDBIndex, listTDBTablePropertiesStructs[6].Name, structFieldProperties.Name, i)
            if i == 0:
                print("%d: Field %s is an int = %d" % (j, structFieldProperties.Name, listPlayerAttributeDicts[i][structFieldProperties.Name.decode()]))

# Open a file to write to.
filePlayersAttributes = open("players_current.csv", "w", newline='')

# Create our DictWriter.
writerPlayerAttributeDicts = csv.DictWriter(filePlayersAttributes, listTDBTable6FieldNames)

# Write the header first.
writerPlayerAttributeDicts.writeheader()

# Loop over the list of dicts and write them out.
for dictPlayerAttributes in listPlayerAttributeDicts:
    writerPlayerAttributeDicts.writerow(dictPlayerAttributes)

# Close the file.
filePlayersAttributes.close()



# ------------------ EDIT PLAYER 0's FIRST NAME ------------------

# Try to edit Player 0's name.
#boolSetValueAsString = TDBAccessDLL.TDBFieldSetValueAsString(intDBIndex, listTDBTablePropertiesStructs[6].Name, "PFNA", 0, "Joe")
#if boolSetValueAsString:
#    stringVal = cast((c_char * 12)(), c_char_p)
#    boolGotValueAsString = TDBAccessDLL.TDBFieldGetValueAsString(intDBIndex, listTDBTablePropertiesStructs[6].Name, "PFNA", 0, byref(stringVal))
#    if boolGotValueAsString:
#        print("We've set the string for player 0's PFNA field to %s." % stringVal.value)
#    else:
#        print("UNABLE TO GET STRING VALUE FROM FIELD 'PFNA' AFTER SETTING IT.")
#else:
#    print("UNABLE TO SET STRING VALUE IN FIELD 'PFNA'.")

# Give us some breathing space before the next section.
#print("\n")


# ------------ PRINT THE FIELDS IN THE "PLAY" TABLE AND THEIR TYPES ------------

# Create a dict to hold the player's attributes. Keys will be field Names, values will be field values.
#dictPlayer0Attributes = {}

# Loop over the fields in the PLAY table and get the values out, calling the appropriate ...GetValueAs... methods for each type.
#for i, structFieldProperties in enumerate(listTDBFieldPropertiesStructsLists[6]):
    # See what methods we need to call.
#    if structFieldProperties.FieldType == 0: # tdbString
        # First, create the string where we will hold the value.
#        stringVal = cast((c_char * ((structFieldProperties.Size / 8) + 1))(), c_char_p)
#        boolGotValueAsString = TDBAccessDLL.TDBFieldGetValueAsString(intDBIndex, listTDBTablePropertiesStructs[6].Name, structFieldProperties.Name, 0, byref(stringVal))
#        if boolGotValueAsString:
#            dictPlayer0Attributes[structFieldProperties.Name] = stringVal.value
#            print("%d: stringVal for player 0's %s field = %s" % (i, structFieldProperties.Name, dictPlayer0Attributes[structFieldProperties.Name]))
#        else:
#            print("%d: Field %s is a string. UNABLE TO GET STRING VALUE." % (i, structFieldProperties.Name))
#    elif structFieldProperties.FieldType == 2: # tdbSInt
#        print("%d: Field %s is a signed int." % (i, structFieldProperties.Name))
#    elif structFieldProperties.FieldType == 3: # tdbUInt
#        print("%d: Field %s is an unsigned int." % (i, structFieldProperties.Name))

#print("\ndictPlayer0Attributes = %r" % dictPlayer0Attributes)


# ------------  FINAL ACTIONS: Compact, save, and close the DB. ------------

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

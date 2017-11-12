r""" DLLtest2.py
    
    This file currently opens the file "base.ros", calls TDBTableGetProperties on each of the tables, gets the 
    properties of each field in table 6 (the "PLAY" table of player info), and then writes all of the 110 attributes 
    of each player in table 6 to a CSV file named "current_players.csv".
"""

# ----------------------------------------------------- SECTION 1 -----------------------------------------------------
# ----------------------------------------- IMPORTS, SETTINGS, AND CONSTANTS ------------------------------------------

# 1.1 - Standard library imports

import csv, os
from ctypes import byref, cast, c_bool, c_char, c_char_p, c_float, c_int, POINTER, Structure, WinDLL


# 1.2 - Third-party imports


# 1.3 - Application-specific imports


# 1.4 - Global settings


# 1.5 - Global constants

PLAYERS_TABLE = b'PLAY'

# Set the base path we will use to keep other paths relative, and shorter :^)
# This will be the directory above the directory above the directory this file is in.
BASE_MADDEN_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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


# ----------------------------------------------------- SECTION 4 -----------------------------------------------------
# -------------------------------------------------- Main Function ----------------------------------------------------

# ------------------ 4.3 -  Read in the table properties. ---------------------

# We'll use this to control a loop over the tables.
table_count = TDBACCESS_DLL.TDBDatabaseGetTableCount(DB_INDEX)
print("\ntable_count = %d" % table_count)

# Create a list to hold all our table properties structs.
table_property_structs_list = []

# Loop over the tables and get their properties.
for i in range(table_count):
    table_property_structs_list.append(TDBTablePropertiesStruct())
    boolGotTableProperties = TDBACCESS_DLL.TDBTableGetProperties(DB_INDEX, i, byref(table_property_structs_list[i]))
#    if boolGotTableProperties:
#        print("\ntable_property_structs_list[%d].Name = %s" % (i, table_property_structs_list[i].Name))
#        print("table_property_structs_list[%d].FieldCount = %d" % (i, table_property_structs_list[i].FieldCount))
#        print("table_property_structs_list[%d].Capacity = %d" % (i, table_property_structs_list[i].Capacity))
#        print("table_property_structs_list[%d].RecordCount = %d" % (i, table_property_structs_list[i].RecordCount))
#        print("table_property_structs_list[%d].DeletedCount = %d" % (i, table_property_structs_list[i].DeletedCount))
#        print("table_property_structs_list[%d].NextDeletedRecord = %d" % (i, table_property_structs_list[i].NextDeletedRecord))

# ------------ OPTION 1: A list to hold the properties structs for each field in table 6, the "PLAY" table ------------

# A list to hold the field properties structs for table 6, "PLAY"
table_6_field_properties_structs_list = []

# A list to hold the field names, needed only for writing the CSV file later.
table_6_field_names_list = []

# Get the properties of each of the fields for the table.
for i in range(table_property_structs_list[6].FieldCount):
    table_6_field_properties_structs_list.append(TDBFieldPropertiesStruct())
    got_table_field_properties = TDBACCESS_DLL.TDBFieldGetProperties(
        DB_INDEX, table_property_structs_list[6].Name, i, byref(table_6_field_properties_structs_list[i]))
    if got_table_field_properties:
        # Want to add each field name to our list.
        table_6_field_names_list.append(table_6_field_properties_structs_list[i].Name.decode())
        print("\ntable_6_field_properties_structs_list[%d].Name = %r" % (i, table_6_field_names_list[i]))
#        print("table_6_field_properties_structs_list[%d].Size = %d" 
#            % (i, table_6_field_properties_structs_list[i].Size))
#        print("table_6_field_properties_structs_list[%d].FieldType = %d" 
#            % (i, table_6_field_properties_structs_list[i].FieldType))
    else:
        print("\nERROR: Unable to get field properties for element %d in table_6_field_properties_structs_list." % i)

# -------------- OPTION 2: A list of lists to hold the properties structs for all 10 of the tables --------------

# A list to hold lists of all our field properties structs for each table.
#field_properties_structs_lists_list = [[] for x in range(table_count)]

# Get the properties of each of the fields for each table.
#for i in range(table_count):
#    print("\n")
#    for j in range(table_property_structs_list[i].FieldCount):
#        field_properties_structs_lists_list[i].append(TDBFieldPropertiesStruct())
#        got_table_field_properties = TDBACCESS_DLL.TDBFieldGetProperties(
#            DB_INDEX, table_property_structs_list[i].Name, j, byref(field_properties_structs_lists_list[i][j]))
#        if got_table_field_properties and i == 6:
#            print("\nfield_properties_structs_lists_list[%d][%d].Name = %r" 
#                % (i, j, field_properties_structs_lists_list[i][j].Name.decode()))
#            print("field_properties_structs_lists_list[%d][%d].Size = %d" 
#                % (i, j, field_properties_structs_lists_list[i][j].Size))
#            print("field_properties_structs_lists_list[%d][%d].FieldType = %d" 
#                % (i, j, field_properties_structs_lists_list[i][j].FieldType))

# Give us some breathing space before the next section.
#print("\n")


# ------------------ WRITE PLAYERS' ATTRIBUTES TO A FILE ------------------

# We want to write all of the 110 attributes of each player to a CSV file.
# So, we will need a list of dicts to keep the field.Name keys paired with their values for each player.
listPlayerAttributeDicts = []

# Start the loop over the players.
for i in range(table_property_structs_list[6].RecordCount):
    # Append to the list a new empty dict for this player.
    listPlayerAttributeDicts.append({})
    # Loop over the list of structs for the fields in the PLAY table.
    for j, structFieldProperties in enumerate(table_6_field_properties_structs_list):
        if structFieldProperties.FieldType == 0: # tdbString
            # First, create the string where we will hold the value.
            stringVal = cast((c_char * ((structFieldProperties.Size // 8) + 1))(), c_char_p)
            boolGotValueAsString = TDBACCESS_DLL.TDBFieldGetValueAsString(DB_INDEX, table_property_structs_list[6].Name, structFieldProperties.Name, i, byref(stringVal))
            if boolGotValueAsString:
                listPlayerAttributeDicts[i][structFieldProperties.Name.decode()] = stringVal.value.decode()
                if i == 0:
                    print("%d: stringVal for player 0's %s field = %s" % (j, structFieldProperties.Name.decode(), listPlayerAttributeDicts[i][structFieldProperties.Name.decode()]))
            else:
                if i == 0:
                    print("%d: Field %s is a string. UNABLE TO GET STRING VALUE." % (j, structFieldProperties.Name))
        elif structFieldProperties.FieldType == 2 or structFieldProperties.FieldType == 3: # tdbSInt or tdbUInt
            # Just call the function to get an int value.
            listPlayerAttributeDicts[i][structFieldProperties.Name.decode()] = TDBACCESS_DLL.TDBFieldGetValueAsInteger(DB_INDEX, table_property_structs_list[6].Name, structFieldProperties.Name, i)
            if i == 0:
                print("%d: Field %s is an int = %d" % (j, structFieldProperties.Name.decode(), listPlayerAttributeDicts[i][structFieldProperties.Name.decode()]))

# Open a file to write to.
filePlayersAttributes = open(os.path.join(BASE_MADDEN_PATH, r"process\outputs\current_players.csv"), "w", newline='')

# Create our DictWriter.
writerPlayerAttributeDicts = csv.DictWriter(filePlayersAttributes, table_6_field_names_list)

# Write the header first.
writerPlayerAttributeDicts.writeheader()

# Loop over the list of dicts and write them out.
for dictPlayerAttributes in listPlayerAttributeDicts:
    writerPlayerAttributeDicts.writerow(dictPlayerAttributes)

# Close the file.
filePlayersAttributes.close()



# ------------------ EDIT PLAYER 0's FIRST NAME ------------------

# Try to edit Player 0's name.
#boolSetValueAsString = TDBACCESS_DLL.TDBFieldSetValueAsString(DB_INDEX, table_property_structs_list[6].Name, "PFNA", 0, "Joe")
#if boolSetValueAsString:
#    stringVal = cast((c_char * 12)(), c_char_p)
#    boolGotValueAsString = TDBACCESS_DLL.TDBFieldGetValueAsString(DB_INDEX, table_property_structs_list[6].Name, "PFNA", 0, byref(stringVal))
#    if boolGotValueAsString:
#        print("We've set the string for player 0's PFNA field to %s." % stringVal.value)
#    else:
#        print("UNABLE TO GET STRING VALUE FROM FIELD 'PFNA' AFTER SETTING IT.")
#else:
#    print("UNABLE TO SET STRING VALUE IN FIELD 'PFNA'.")

# Give us some breathing space before the next section.
#print("\n")


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

r""" dump_roster_to_csv.py
    
    This file currently: opens the file "base.ros" (found in "[BASE_MADDEN_PATH]\process\inputs\"); calls method 
    TDBTableGetProperties on each of the tables; gets the properties of each field in table 6 (the "PLAY" table, with 
    player attribute info); and then writes all of the 110 attributes of each player to "current_players.csv".
"""

# ----------------------------------------------------- SECTION 1 -----------------------------------------------------
# ----------------------------------------- IMPORTS, SETTINGS, AND CONSTANTS ------------------------------------------

# 1.1 - Standard library imports

import csv, logging, os
from ctypes import byref, cast, c_bool, c_char, c_char_p, c_int, POINTER, Structure, WinDLL


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
    """Structure whose fields hold all the properties of a table in a roster file."""
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
    """Structure whose fields hold all the properties of a field from a table in a roster file."""
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

TDBACCESS_DLL.TDBDatabaseGetTableCount.argtypes = [c_int]
TDBACCESS_DLL.TDBDatabaseGetTableCount.restype = c_int

TDBACCESS_DLL.TDBFieldGetProperties.argtypes = [c_int, c_char_p, c_int, POINTER(TDBFieldPropertiesStruct)]
TDBACCESS_DLL.TDBFieldGetProperties.restype = c_int

TDBACCESS_DLL.TDBFieldGetValueAsInteger.argtypes = [c_int, c_char_p, c_char_p, c_int]
TDBACCESS_DLL.TDBFieldGetValueAsInteger.restype = c_int

TDBACCESS_DLL.TDBFieldGetValueAsString.argtypes = [c_int, c_char_p, c_char_p, c_int, POINTER(c_char_p)]
TDBACCESS_DLL.TDBFieldGetValueAsString.restype = c_bool

TDBACCESS_DLL.TDBOpen.argtypes = [c_char_p]
TDBACCESS_DLL.TDBOpen.restype = c_int

TDBACCESS_DLL.TDBSave.argtypes = [c_int]
TDBACCESS_DLL.TDBSave.restype = c_bool

TDBACCESS_DLL.TDBTableGetProperties.argtypes = [c_int, c_int, POINTER(TDBTablePropertiesStruct)]
TDBACCESS_DLL.TDBTableGetProperties.restype = c_bool


# ----------------------------------------------------- SECTION 3 -----------------------------------------------------
# ------------------------------------------------- Helper Functions --------------------------------------------------


# ----------------------------------------------------- SECTION 4 -----------------------------------------------------
# -------------------------------------------------- Main Function ----------------------------------------------------

# ------------------ Read in the table properties. ---------------------

# We'll use this to control a loop over the tables.
table_count = TDBACCESS_DLL.TDBDatabaseGetTableCount(DB_INDEX)
logging.info("\ntable_count = %d",table_count)

# Create a list to hold all our table properties structs.
table_property_structs_list = []

# Loop over the tables and get their properties.
for i in range(table_count):
    table_property_structs_list.append(TDBTablePropertiesStruct())
    got_table_properties = TDBACCESS_DLL.TDBTableGetProperties(DB_INDEX, i, byref(table_property_structs_list[i]))

# A list to hold the field properties structs for table 6, "PLAY"
table_6_field_properties_structs_list = []

# A list to hold the field names, needed only for writing the CSV file later.
table_6_field_names_list = []

# Get the properties of each of the fields for the table.
for i in range(table_property_structs_list[6].FieldCount):
    table_6_field_properties_structs_list.append(TDBFieldPropertiesStruct())
    got_table_field_properties = TDBACCESS_DLL.TDBFieldGetProperties(
        DB_INDEX, PLAYERS_TABLE, i, byref(table_6_field_properties_structs_list[i]))
    if got_table_field_properties:
        # Add each field name to our list.
        table_6_field_names_list.append(table_6_field_properties_structs_list[i].Name.decode())
        logging.info("\ntable_6_field_properties_structs_list[%d].Name = %r", i, table_6_field_names_list[i])
    else:
        logging.error("\nERROR: Unable to get field properties for element %d "
                      "in table_6_field_properties_structs_list.", i)

# ------------------ WRITE PLAYERS' ATTRIBUTES TO A FILE ------------------

# We want to write all of the 110 attributes of each player to a CSV file.
# So, we will need a list of dicts to keep the field.Name keys paired with their values for each player.
player_attribute_dicts_list = []

# Start the loop over the players.
for i in range(table_property_structs_list[6].RecordCount):
    # Append to the list a new empty dict for this player.
    player_attribute_dicts_list.append({})
    # Loop over the list of structs for the fields in the PLAY table.
    for j, field_properties_struct in enumerate(table_6_field_properties_structs_list):
        if field_properties_struct.FieldType == 0: # tdbString
            # First, create the string where we will hold the value.
            value_as_string = cast((c_char * ((field_properties_struct.Size // 8) + 1))(), c_char_p)
            got_value_as_string = TDBACCESS_DLL.TDBFieldGetValueAsString(
                DB_INDEX, PLAYERS_TABLE, field_properties_struct.Name, i, byref(value_as_string))
            if got_value_as_string:
                player_attribute_dicts_list[i][field_properties_struct.Name.decode()] = value_as_string.value.decode()
                if i == 0:
                    logging.info("%d: value_as_string for player 0's %s field = %s", 
                                 j, 
                                 field_properties_struct.Name.decode(), 
                                 player_attribute_dicts_list[i][field_properties_struct.Name.decode()])
            else:
                if i == 0:
                    logging.error("%d: Field %s is a string. UNABLE TO GET STRING VALUE.", 
                                  j, field_properties_struct.Name)
        elif field_properties_struct.FieldType == 2 or field_properties_struct.FieldType == 3: # tdbSInt or tdbUInt
            # Just call the function to get an int value.
            player_attribute_dicts_list[i][field_properties_struct.Name.decode()] = \
                TDBACCESS_DLL.TDBFieldGetValueAsInteger(DB_INDEX, PLAYERS_TABLE, field_properties_struct.Name, i)
            if i == 0:
                logging.info("%d: Field %s is an int = %d", 
                             j, 
                             field_properties_struct.Name.decode(), 
                             player_attribute_dicts_list[i][field_properties_struct.Name.decode()])

# Open a file to write to.
player_attributes_file = open(os.path.join(BASE_MADDEN_PATH, r"process\outputs\current_players.csv"), "w", newline='')

# Create our DictWriter.
player_attribute_dict_writer = csv.DictWriter(player_attributes_file, table_6_field_names_list)

# Write the header first.
player_attribute_dict_writer.writeheader()

# Loop over the list of dicts and write them out.
for dictPlayerAttributes in player_attribute_dicts_list:
    player_attribute_dict_writer.writerow(dictPlayerAttributes)

# Close the file.
player_attributes_file.close()


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

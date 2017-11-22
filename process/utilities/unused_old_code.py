r""" unused_old_code.py
    
    This file contains snippets of code that were helpful when investigating the format and funcitonality of the 
    various files, such as Madden's .ros roster files and the TDBAccess DLL, but are no longer needed in the final 
    process of updating rosters.
"""

# ----------------------------------------------------- SECTION 1 -----------------------------------------------------
# ----------------------------------------- IMPORTS, SETTINGS, AND CONSTANTS ------------------------------------------

# 1.1 - Standard library imports

import logging, os
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
    """Structure whose fields hold all the properties of a table in a roster file."""
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
    """Structure whose fields hold all the properties of a field from a table in a roster file."""
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

# We'll use this to control a loop over the tables.
table_count = TDBACCESS_DLL.TDBDatabaseGetTableCount(DB_INDEX)
logging.info("\ntable_count = %d", table_count)

# Create a list to hold all our table properties structs.
table_property_structs_list = []

# Loop over the tables and get their properties.
for i in range(table_count):
    table_property_structs_list.append(TDBTablePropertiesStruct())
    got_table_properties = TDBACCESS_DLL.TDBTableGetProperties(DB_INDEX, i, byref(table_property_structs_list[i]))
    if got_table_properties:
        logging.info("\ntable_property_structs_list[%d].Name = %s", 
                     i, table_property_structs_list[i].Name)
        logging.info("table_property_structs_list[%d].FieldCount = %d", 
                     i, table_property_structs_list[i].FieldCount)
        logging.info("table_property_structs_list[%d].Capacity = %d", 
                     i, table_property_structs_list[i].Capacity)
        logging.info("table_property_structs_list[%d].RecordCount = %d", 
                     i, table_property_structs_list[i].RecordCount)
        logging.info("table_property_structs_list[%d].DeletedCount = %d", 
                     i, table_property_structs_list[i].DeletedCount)
        logging.info("table_property_structs_list[%d].NextDeletedRecord = %d", 
                     i, table_property_structs_list[i].NextDeletedRecord)

# A list to hold the properties structs for each field in table 6, the "PLAY" table.
table_6_field_property_structs_list = []

# Get the properties of each of the fields for the table.
for i in range(table_property_structs_list[6].FieldCount):
    table_6_field_property_structs_list.append(TDBFieldPropertiesStruct())
    got_field_properties = TDBACCESS_DLL.TDBFieldGetProperties(
        DB_INDEX, table_property_structs_list[6].Name, i, byref(table_6_field_property_structs_list[i]))
    if got_field_properties:
        logging.info("\ntable_6_field_property_structs_list[%d].Name = %s", 
                     i, table_6_field_property_structs_list[i].Name.decode())
        logging.info("table_6_field_property_structs_list[%d].Size = %d", 
                     i, table_6_field_property_structs_list[i].Size)
        logging.info("table_6_field_property_structs_list[%d].FieldType = %d", 
                     i, table_6_field_property_structs_list[i].FieldType)
    else:
        logging.info("\nERROR: Unable to get field properties for element %d "
                     "in table_6_field_property_structs_list.", i)

# Give us some breathing space before the next section.
logging.info("\n\n")


# ------------ PRINT THE FIELDS IN THE "PLAY" TABLE AND THEIR TYPES ------------

# Create a dict to hold the player's attributes. Keys will be field Names, values will be field values.
player_0_attributes_dict = {}

# Loop over the fields in the PLAY table and get the values out, 
# calling the appropriate ...GetValueAs... methods for each type.
for i, field_property_struct in enumerate(table_6_field_property_structs_list):
    # See what methods we need to call.
    if field_property_struct.FieldType == 0: # tdbString
        # First, create the string where we will hold the value.
        value_as_string = cast((c_char * ((field_property_struct.Size // 8) + 1))(), c_char_p)
        got_string_value = TDBACCESS_DLL.TDBFieldGetValueAsString(
            DB_INDEX, table_property_structs_list[6].Name, field_property_struct.Name, 0, byref(value_as_string))
        if got_string_value:
            player_0_attributes_dict[field_property_struct.Name] = value_as_string.value.decode()
            logging.info("%d: value_as_string for player 0's %s field = %s", 
                         i, field_property_struct.Name, player_0_attributes_dict[field_property_struct.Name])
        else:
            logging.error("%d: Field %s is a string. UNABLE TO GET STRING VALUE.", i, field_property_struct.Name)
    elif field_property_struct.FieldType == 2: # tdbSInt
        logging.info("%d: Field %s is a signed int.", i, field_property_struct.Name)
    elif field_property_struct.FieldType == 3: # tdbUInt
        logging.info("%d: Field %s is an unsigned int.", i, field_property_struct.Name)

logging.info("\nplayer_0_attributes_dict = %r", player_0_attributes_dict)


# -------------- OPTION 2: A list of lists to hold the properties structs for all 10 of the tables --------------

# A list to hold lists of all our field properties structs for each table.
#field_properties_structs_lists_list = [[] for x in range(table_count)]

# Get the properties of each of the fields for each table.
#for i in range(table_count):
#    logging.info("\n")
#    for j in range(table_property_structs_list[i].FieldCount):
#        field_properties_structs_lists_list[i].append(TDBFieldPropertiesStruct())
#        got_table_field_properties = TDBACCESS_DLL.TDBFieldGetProperties(
#            DB_INDEX, table_property_structs_list[i].Name, j, byref(field_properties_structs_lists_list[i][j]))
#        if got_table_field_properties and i == 6:
#            logging.info("\nfield_properties_structs_lists_list[%d][%d].Name = %r" 
#                % (i, j, field_properties_structs_lists_list[i][j].Name.decode()))
#            logging.info("field_properties_structs_lists_list[%d][%d].Size = %d" 
#                % (i, j, field_properties_structs_lists_list[i][j].Size))
#            logging.info("field_properties_structs_lists_list[%d][%d].FieldType = %d" 
#                % (i, j, field_properties_structs_lists_list[i][j].FieldType))

# Give us some breathing space before the next section.
#logging.info("\n")


# ------------ Edit player 0's first name. ------------

value_was_set_as_string = TDBACCESS_DLL.TDBFieldSetValueAsString(
    DB_INDEX, table_property_structs_list[6].Name, b"PFNA", 0, b"SOMEONE")

if value_was_set_as_string:
    # Try getting the new name back out using the Get method.
    value_as_string = cast((c_char * 12)(), c_char_p)
    got_value_as_string = TDBACCESS_DLL.TDBFieldGetValueAsString(
        DB_INDEX, table_property_structs_list[6].Name, b"PFNA", 0, byref(value_as_string))
    if got_value_as_string:
        logging.info("We've set the string for player 0's PFNA field to %s.", value_as_string.value.decode())
    else:
        logging.error("UNABLE TO GET STRING VALUE FROM FIELD 'PFNA' AFTER SETTING IT.")
else:
    logging.error("UNABLE TO SET STRING VALUE IN FIELD 'PFNA'.")

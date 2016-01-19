import os
import csv
from ctypes import *

# ------------------ CLASS DECLARATIONS ------------------

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


# ------------ READING FROM THE MADDEN RATINGS .csv FILE ------------

# Open the CSV file with all the players and their Madden ratings.
#fileMaddenRatings = open(r"C:\Users\spalding\Desktop\Various\For Home\for Madden\My Updater\Madden 15 Player Ratings.csv")

# Get a DictReader to read the rows into dicts using the header row as keys.
#iterMaddenRatingsDictReader = csv.DictReader(fileMaddenRatings)

# Create a list to hold our dicts.
#listMaddenRatingsDicts = []

# 
#for row in iterMaddenRatingsDictReader:
#    i += 1
#    if i < 20:
#        listMaddenRatingsDicts.append(row)
#    else:
#        break

#fileMaddenRatings.close()


# ------------ ACCESSING THE Madden '08 ROSTER FILE ------------

# Get a handle for our DLL.
#dllTDBAccess = WinDLL(r"C:\Users\spalding\Desktop\Various\For Home\for Madden\My Updater\OLD tdbaccess\tdbaccess.dll")
dllTDBAccess = WinDLL(r"D:\My Updater - WORKING COPY\OLD tdbaccess\tdbaccess.dll")

# Open the roster file through the DLL.
#intDBIndex = dllTDBAccess.TDBOpen(r"C:\Users\spalding\Desktop\Various\For Home\for Madden\My Updater\pcph.ros")
#intDBIndex = dllTDBAccess.TDBOpen(r"C:\Users\spalding\Desktop\Various\For Home\for Madden\My Updater\j_wilkerson.ros")
intDBIndex = dllTDBAccess.TDBOpen(r"D:\My Updater - WORKING COPY\current.ros")
print("\nintDBIndex = %d" % intDBIndex)

# Add the argtypes and restype definitions here for the functions we'll use.
dllTDBAccess.TDBClose.argtypes = [c_int]
dllTDBAccess.TDBClose.restype = c_bool

dllTDBAccess.TDBDatabaseCompact.argtypes = [c_int]
dllTDBAccess.TDBDatabaseCompact.restype = c_bool

dllTDBAccess.TDBDatabaseGetTableCount.argtypes = [c_int]
dllTDBAccess.TDBDatabaseGetTableCount.restype = c_int

dllTDBAccess.TDBFieldGetProperties.argtypes = [c_int, c_char_p, c_int, POINTER(structTDBFieldProperties)]
#dllTDBAccess.TDBFieldGetProperties.argtypes = [c_int, c_wchar_p, c_int, POINTER(structTDBFieldProperties)]
dllTDBAccess.TDBFieldGetProperties.restype = c_int

#dllTDBAccess.TDBFieldGetValueAsBinary.argtypes = [c_int, c_char_p, c_char_p, c_int, POINTER(c_char_p)]

#dllTDBAccess.TDBFieldGetValueAsFloat.argtypes = [c_int, c_char_p, c_char_p, c_int]

dllTDBAccess.TDBFieldGetValueAsInteger.argtypes = [c_int, c_char_p, c_char_p, c_int]
dllTDBAccess.TDBFieldGetValueAsInteger.restype = c_int

dllTDBAccess.TDBFieldGetValueAsString.argtypes = [c_int, c_char_p, c_char_p, c_int, POINTER(c_char_p)]
dllTDBAccess.TDBFieldGetValueAsString.restype = c_bool

#dllTDBAccess.TDBFieldSetValueAsFloat.argtypes = [c_int, c_char_p, c_char_p, c_int, c_float]

#dllTDBAccess.TDBFieldSetValueAsInteger.argtypes = [c_int, c_char_p, c_char_p, c_int, c_int]

dllTDBAccess.TDBFieldSetValueAsString.argtypes = [c_int, c_char_p, c_char_p, c_int, c_char_p]
dllTDBAccess.TDBFieldSetValueAsString.restype = c_bool

dllTDBAccess.TDBOpen.argtypes = [c_char_p]
#dllTDBAccess.TDBOpen.argtypes = [c_wchar_p]
dllTDBAccess.TDBOpen.restype = c_int

dllTDBAccess.TDBSave.argtypes = [c_int]
dllTDBAccess.TDBSave.restype = c_bool

dllTDBAccess.TDBTableGetProperties.argtypes = [c_int, c_int, POINTER(structTDBTableProperties)]
dllTDBAccess.TDBTableGetProperties.restype = c_bool


# ------------------ READING IN THE TABLE PROPERTIES ------------------

# We'll use this to control a loop over the tables.
intNumberOfTables = dllTDBAccess.TDBDatabaseGetTableCount(intDBIndex)
print("\nintNumberOfTables = %d" % intNumberOfTables)

# Create a list to hold all our table properties structs.
listTDBTablePropertiesStructs = []

# Loop over the tables and get their properties.
for i in range(intNumberOfTables):
    listTDBTablePropertiesStructs.append(structTDBTableProperties())
    boolGotTableProperties = dllTDBAccess.TDBTableGetProperties(intDBIndex, i, byref(listTDBTablePropertiesStructs[i]))
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
    listTDBTable6FieldPropertiesStructs.append(structTDBFieldProperties())
    boolGotTableFieldProperties = dllTDBAccess.TDBFieldGetProperties(intDBIndex, listTDBTablePropertiesStructs[6].Name, i, byref(listTDBTable6FieldPropertiesStructs[i]))
    if boolGotTableFieldProperties:
        # Want to add each field name to our list.
        listTDBTable6FieldNames.append(listTDBTable6FieldPropertiesStructs[i].Name)
        print("\nlistTDBTable6FieldPropertiesStructs[%d].Name = %r" % (i, listTDBTable6FieldPropertiesStructs[i].Name))
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
#        listTDBFieldPropertiesStructsLists[i].append(structTDBFieldProperties())
#        boolGotTableFieldProperties = dllTDBAccess.TDBFieldGetProperties(intDBIndex, listTDBTablePropertiesStructs[i].Name, j, byref(listTDBFieldPropertiesStructsLists[i][j]))
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
            stringVal = cast((c_char * ((structFieldProperties.Size / 8) + 1))(), c_char_p)
            boolGotValueAsString = dllTDBAccess.TDBFieldGetValueAsString(intDBIndex, listTDBTablePropertiesStructs[6].Name, structFieldProperties.Name, i, byref(stringVal))
            if boolGotValueAsString:
                listPlayerAttributeDicts[i][structFieldProperties.Name] = stringVal.value
                if i == 0:
                    print("%d: stringVal for player 0's %s field = %s" % (j, structFieldProperties.Name, listPlayerAttributeDicts[i][structFieldProperties.Name]))
            else:
                if i == 0:
                    print("%d: Field %s is a string. UNABLE TO GET STRING VALUE." % (j, structFieldProperties.Name))
        elif structFieldProperties.FieldType == 2 or structFieldProperties.FieldType == 3: # tdbSInt or tdbUInt
            # Just call the function to get an int value.
            listPlayerAttributeDicts[i][structFieldProperties.Name] = dllTDBAccess.TDBFieldGetValueAsInteger(intDBIndex, listTDBTablePropertiesStructs[6].Name, structFieldProperties.Name, i)
            if i == 0:
                print("%d: Field %s is an int = %d" % (j, structFieldProperties.Name, listPlayerAttributeDicts[i][structFieldProperties.Name]))

# Open a file to write to.
filePlayersAttributes = open("players_current.csv", "wb")

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
#boolSetValueAsString = dllTDBAccess.TDBFieldSetValueAsString(intDBIndex, listTDBTablePropertiesStructs[6].Name, "PFNA", 0, "Joe")
#if boolSetValueAsString:
#    stringVal = cast((c_char * 12)(), c_char_p)
#    boolGotValueAsString = dllTDBAccess.TDBFieldGetValueAsString(intDBIndex, listTDBTablePropertiesStructs[6].Name, "PFNA", 0, byref(stringVal))
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
#        boolGotValueAsString = dllTDBAccess.TDBFieldGetValueAsString(intDBIndex, listTDBTablePropertiesStructs[6].Name, structFieldProperties.Name, 0, byref(stringVal))
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
boolCompactedTDBDatabase = dllTDBAccess.TDBDatabaseCompact(intDBIndex)
if boolCompactedTDBDatabase:
    print("\nCompacted the TDBDatabase.")
else:
    print("\nWarning: Failed to compact the TDBDatabase.")

# Save the DB.
boolSavedTDBDatabase = dllTDBAccess.TDBSave(intDBIndex)
if boolSavedTDBDatabase:
    print("\nSaved the TDBDatabase.")
else:
    print("\nWarning: Failed to save the TDBDatabase.")

# Close the DB.
boolClosedTDBDatabase = dllTDBAccess.TDBClose(intDBIndex)
if boolClosedTDBDatabase:
    print("\nClosed the TDBDatabase.")
else:
    print("\nWarning: Failed to close the TDBDatabase.")
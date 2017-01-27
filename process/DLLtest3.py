import os
import csv
import math
from ctypes import *

# ------------------      FUNCTIONS     ------------------
def SetPlayerIntegerAttribute(intPlayerIndex, strAttribute, intValue):
    boolSetValueAsInt = dllTDBAccess.TDBFieldSetValueAsInteger(intDBIndex, "PLAY", strAttribute, intPlayerIndex, intValue)
    if boolSetValueAsInt:
        intGotValueAsInt = dllTDBAccess.TDBFieldGetValueAsInteger(intDBIndex, "PLAY", strAttribute, intPlayerIndex)
        print("\nSet Player %d's %s field to %d" % (intPlayerIndex, strAttribute, intGotValueAsInt))
    else:
        print("\nError in setting Player %d's %s field." % (intPlayerIndex, strAttribute))

def SetPlayerStringAttribute(intPlayerIndex, strAttribute, strValue):
    boolSetValueAsString = dllTDBAccess.TDBFieldSetValueAsString(intDBIndex, "PLAY", strAttribute, intPlayerIndex, strValue)
    if boolSetValueAsString:
        stringVal = cast((c_char * 14)(), c_char_p)
        boolGotValueAsString = dllTDBAccess.TDBFieldGetValueAsString(intDBIndex, "PLAY", strAttribute, intPlayerIndex, byref(stringVal))
        if boolGotValueAsString:
            print("Set Player %d's %s field to %s" % (intPlayerIndex, strAttribute, stringVal.value))
        else:
            print("\nError in setting Player %d's %s field." % (intPlayerIndex, strAttribute))
    else:
        print("\nError in setting Player %d's %s field." % (intPlayerIndex, strAttribute))

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


# ------------ READ FROM THE MADDEN RATINGS .csv FILE ------------

# Open the CSV file with all the players and their Madden ratings.
fileMaddenRatings = open(r"C:\Users\spalding\Desktop\Various\For Home\for Madden\My Updater\Madden 15 Player Ratings.csv")

# Get a DictReader to read the rows into dicts using the header row as keys.
iterMaddenRatingsDictReader = csv.DictReader(fileMaddenRatings)

# Get the dict representing the first row.
dictFirstMaddenPlayerRatings = iterMaddenRatingsDictReader.next()

# Show what we got.
print("\ndictFirstMaddenPlayerRatings = %r" % dictFirstMaddenPlayerRatings)

# Close the Madden Ratings .csv file.
fileMaddenRatings.close()


# ------------ ACCESSING THE Madden '08 ROSTER FILE ------------

# Get a handle for our DLL.
dllTDBAccess = WinDLL(r"C:\Users\spalding\Desktop\Various\For Home\for Madden\My Updater\OLD tdbaccess\tdbaccess.dll")
#dllTDBAccess = WinDLL(r"C:\Users\spalding\Desktop\Various\For Home\for Madden\My Updater\NEW tdbaccess\tdbaccess.dll")

# Open the roster file through the DLL.
intDBIndex = dllTDBAccess.TDBOpen(r"C:\Users\spalding\Desktop\Various\For Home\for Madden\My Updater\pcph.ros")
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

dllTDBAccess.TDBFieldSetValueAsInteger.argtypes = [c_int, c_char_p, c_char_p, c_int, c_int]
dllTDBAccess.TDBFieldSetValueAsInteger.restype = c_bool

dllTDBAccess.TDBFieldSetValueAsString.argtypes = [c_int, c_char_p, c_char_p, c_int, c_char_p]
dllTDBAccess.TDBFieldSetValueAsString.restype = c_bool

dllTDBAccess.TDBOpen.argtypes = [c_char_p]
#dllTDBAccess.TDBOpen.argtypes = [c_wchar_p]
dllTDBAccess.TDBOpen.restype = c_int

dllTDBAccess.TDBSave.argtypes = [c_int]
dllTDBAccess.TDBSave.restype = c_bool

dllTDBAccess.TDBTableGetProperties.argtypes = [c_int, c_int, POINTER(structTDBTableProperties)]
dllTDBAccess.TDBTableGetProperties.restype = c_bool


# ------------------ READING IN THE PROPERTIES ------------------

# We'll use this to control a loop over the tables.
intNumberOfTables = dllTDBAccess.TDBDatabaseGetTableCount(intDBIndex)
print("\nintNumberOfTables = %d" % intNumberOfTables)

# Create a list to hold all our table properties structs.
listTDBTablePropertiesStructs = []

# Loop over the tables and get their properties.
for i in range(intNumberOfTables):
    listTDBTablePropertiesStructs.append(structTDBTableProperties())
    boolGotTableProperties = dllTDBAccess.TDBTableGetProperties(intDBIndex, i, byref(listTDBTablePropertiesStructs[i]))
    if boolGotTableProperties:
        print("\nlistTDBTablePropertiesStructs[%d].Name = %s" % (i, listTDBTablePropertiesStructs[i].Name))
#        print("listTDBTablePropertiesStructs[%d].FieldCount = %d" % (i, listTDBTablePropertiesStructs[i].FieldCount))
#        print("listTDBTablePropertiesStructs[%d].Capacity = %d" % (i, listTDBTablePropertiesStructs[i].Capacity))
#        print("listTDBTablePropertiesStructs[%d].RecordCount = %d" % (i, listTDBTablePropertiesStructs[i].RecordCount))
#        print("listTDBTablePropertiesStructs[%d].DeletedCount = %d" % (i, listTDBTablePropertiesStructs[i].DeletedCount))
#        print("listTDBTablePropertiesStructs[%d].NextDeletedRecord = %d" % (i, listTDBTablePropertiesStructs[i].NextDeletedRecord))

# A list to hold the field properties structs for table 6, "PLAY"
#listTDBTable6FieldPropertiesStructs = []

# A list to hold the field names.
#listTDBTable6FieldNames = []

# Get the properties of each of the fields for the table.
#for i in range(listTDBTablePropertiesStructs[6].FieldCount):
#    listTDBTable6FieldPropertiesStructs.append(structTDBFieldProperties())
#    boolGotTableFieldProperties = dllTDBAccess.TDBFieldGetProperties(intDBIndex, listTDBTablePropertiesStructs[6].Name, i, byref(listTDBTable6FieldPropertiesStructs[i]))
#    if boolGotTableFieldProperties:
        # Want to add each field name to our list.
#        listTDBTable6FieldNames.append(listTDBTable6FieldPropertiesStructs[i].Name)
#        print("\listTDBTable6FieldPropertiesStructs[%d].Name = %r" % (i, listTDBTable6FieldPropertiesStructs[i].Name))
#        print("listTDBTable6FieldPropertiesStructs[%d].Size = %d" % (i, listTDBTable6FieldPropertiesStructs[i].Size))
#        print("listTDBTable6FieldPropertiesStructs[%d].FieldType = %d" % (i, listTDBTable6FieldPropertiesStructs[i].FieldType))
#    else:
#        print("ERROR: Unable to get field properties for element %d in listTDBTable6FieldPropertiesStructs." % i)

# ------------------ WRITE NEW VALUES FOR IMPORTANT ATTRIBUTES OF THE FIRST PLAYER ------------------

# NOTE: Looks like I was testing various values for the "PCPH" field here, probably while trying to determine what 
# exaactly the field was for. I think the longer section immediately following, commented out in the docstring format, 
# was the code I used to prove that it was possible to edit a player in the .ros file so completely that he was an 
# entirely new character. See if that is the case by uncommenting that section and trying to do it again.

for x in range(0, 11):
    SetPlayerIntegerAttribute(x, "PCPH", 0)

for x in range(11, 21):
    SetPlayerIntegerAttribute(x, "PCPH", 1)

for x in range(21, 31):
    SetPlayerIntegerAttribute(x, "PCPH", 2)

for x in range(31, 41):
    SetPlayerIntegerAttribute(x, "PCPH", 3)

'''
# Start by setting Player 0's PRL2 (Player Role 2) to 37, Possession Receiver.
boolSetValueAsInt = dllTDBAccess.TDBFieldSetValueAsInteger(intDBIndex, "PLAY", "PRL2", 0, 37)
if boolSetValueAsInt:
    intGotValueAsInt = dllTDBAccess.TDBFieldGetValueAsInteger(intDBIndex, "PLAY", "PRL2", 0)
    print("\nSet Player 0's PRL2 field to %d" % intGotValueAsInt)
else:
    print("\nError in setting Player 0's PRL2 field.")

# Set his gloves (PLHA and PRHA) to White RB gloves (5).
boolSetValueAsInt = dllTDBAccess.TDBFieldSetValueAsInteger(intDBIndex, "PLAY", "PLHA", 0, 5)
if boolSetValueAsInt:
    intGotValueAsInt = dllTDBAccess.TDBFieldGetValueAsInteger(intDBIndex, "PLAY", "PLHA", 0)
    print("Set Player 0's PLHA field to %d" % intGotValueAsInt)
else:
    print("\nError in setting Player 0's PLHA field.")

boolSetValueAsInt = dllTDBAccess.TDBFieldSetValueAsInteger(intDBIndex, "PLAY", "PRHA", 0, 5)
if boolSetValueAsInt:
    intGotValueAsInt = dllTDBAccess.TDBFieldGetValueAsInteger(intDBIndex, "PLAY", "PRHA", 0)
    print("Set Player 0's PRHA field to %d" % intGotValueAsInt)
else:
    print("\nError in setting Player 0's PRHA field.")

# Set Player 0's throwing accuracy (PTHA) to ceil((2 * (m_tas + m_tam + m_tad) - min(m_tas, m_tam, m_tad))/5).
# Start by getting a list of the values we want out of the player dict, for the keys 'THROW ACCURACY SHORT', 'THROW ACCURACY MED', and 'THROW ACCURACY DEEP'.
listTHAKeys = ['THROW ACCURACY SHORT', 'THROW ACCURACY MED', 'THROW ACCURACY DEEP']
listTHAValues = [int(dictFirstMaddenPlayerRatings[x]) for x in listTHAKeys]
# Now to calculate the PTHA value we want.
intPlayer0THA = int(math.ceil((2 * (int(dictFirstMaddenPlayerRatings['THROW ACCURACY SHORT']) + int(dictFirstMaddenPlayerRatings['THROW ACCURACY MED']) + int(dictFirstMaddenPlayerRatings['THROW ACCURACY DEEP'])) - min(listTHAValues)) / 5))
# Set the value.
boolSetValueAsInt = dllTDBAccess.TDBFieldSetValueAsInteger(intDBIndex, "PLAY", "PTHA", 0, intPlayer0THA)
if boolSetValueAsInt:
    intGotValueAsInt = dllTDBAccess.TDBFieldGetValueAsInteger(intDBIndex, "PLAY", "PTHA", 0)
    print("Set Player 0's PTHA field to %d" % intGotValueAsInt)
else:
    print("\nError in setting Player 0's PTHA field.")

# Set Player 0's first name (PFNA).
boolSetValueAsString = dllTDBAccess.TDBFieldSetValueAsString(intDBIndex, "PLAY", "PFNA", 0, dictFirstMaddenPlayerRatings['FIRST'])
if boolSetValueAsString:
    stringVal = cast((c_char * 12)(), c_char_p)
    boolGotValueAsString = dllTDBAccess.TDBFieldGetValueAsString(intDBIndex, "PLAY", "PFNA", 0, byref(stringVal))
    if boolGotValueAsString:
        print("Set Player 0's PFNA field to %s" % stringVal.value)
    else:
        print("\nError in setting Player 0's PFNA field.")
else:
    print("\nError in setting Player 0's PFNA field.")

# Set Player 0's last name (PLNA).
boolSetValueAsString = dllTDBAccess.TDBFieldSetValueAsString(intDBIndex, "PLAY", "PLNA", 0, dictFirstMaddenPlayerRatings['LAST'])
if boolSetValueAsString:
    stringVal = cast((c_char * 14)(), c_char_p)
    boolGotValueAsString = dllTDBAccess.TDBFieldGetValueAsString(intDBIndex, "PLAY", "PLNA", 0, byref(stringVal))
    if boolGotValueAsString:
        print("Set Player 0's PLNA field to %s" % stringVal.value)
    else:
        print("\nError in setting Player 0's PLNA field.")
else:
    print("\nError in setting Player 0's PLNA field.")

# Set Player 0's stamina (PSTA).
boolSetValueAsInt = dllTDBAccess.TDBFieldSetValueAsInteger(intDBIndex, "PLAY", "PSTA", 0, int(dictFirstMaddenPlayerRatings['STAMINA']))
if boolSetValueAsInt:
    intGotValueAsInt = dllTDBAccess.TDBFieldGetValueAsInteger(intDBIndex, "PLAY", "PSTA", 0)
    print("Set Player 0's PSTA field to %d" % intGotValueAsInt)
else:
    print("\nError in setting Player 0's PSTA field.")

# Set Player 0's kicking accuracy (PKAC).
boolSetValueAsInt = dllTDBAccess.TDBFieldSetValueAsInteger(intDBIndex, "PLAY", "PKAC", 0, int(dictFirstMaddenPlayerRatings['KICK ACCURACY']))
if boolSetValueAsInt:
    intGotValueAsInt = dllTDBAccess.TDBFieldGetValueAsInteger(intDBIndex, "PLAY", "PKAC", 0)
    print("Set Player 0's PKAC field to %d" % intGotValueAsInt)
else:
    print("\nError in setting Player 0's PKAC field.")

# Set Player 0's acceleration (PACC).
boolSetValueAsInt = dllTDBAccess.TDBFieldSetValueAsInteger(intDBIndex, "PLAY", "PACC", 0, int(dictFirstMaddenPlayerRatings['ACCELERATION']))
if boolSetValueAsInt:
    intGotValueAsInt = dllTDBAccess.TDBFieldGetValueAsInteger(intDBIndex, "PLAY", "PACC", 0)
    print("Set Player 0's PACC field to %d" % intGotValueAsInt)
else:
    print("\nError in setting Player 0's PACC field.")

# Set Player 0's speed (PSPD).
boolSetValueAsInt = dllTDBAccess.TDBFieldSetValueAsInteger(intDBIndex, "PLAY", "PSPD", 0, int(dictFirstMaddenPlayerRatings['SPEED']))
if boolSetValueAsInt:
    intGotValueAsInt = dllTDBAccess.TDBFieldGetValueAsInteger(intDBIndex, "PLAY", "PSPD", 0)
    print("Set Player 0's PSPD field to %d" % intGotValueAsInt)
else:
    print("\nError in setting Player 0's PSPD field.")

# Set Player 0's toughness (PTGH).
boolSetValueAsInt = dllTDBAccess.TDBFieldSetValueAsInteger(intDBIndex, "PLAY", "PTGH", 0, int(dictFirstMaddenPlayerRatings['TOUGHNESS']))
if boolSetValueAsInt:
    intGotValueAsInt = dllTDBAccess.TDBFieldGetValueAsInteger(intDBIndex, "PLAY", "PTGH", 0)
    print("Set Player 0's PTGH field to %d" % intGotValueAsInt)
else:
    print("\nError in setting Player 0's PTGH field.")

# Set Player 0's catching (PCTH).
boolSetValueAsInt = dllTDBAccess.TDBFieldSetValueAsInteger(intDBIndex, "PLAY", "PCTH", 0, int(dictFirstMaddenPlayerRatings['CATCHING']))
if boolSetValueAsInt:
    intGotValueAsInt = dllTDBAccess.TDBFieldGetValueAsInteger(intDBIndex, "PLAY", "PCTH", 0)
    print("Set Player 0's PCTH field to %d" % intGotValueAsInt)
else:
    print("\nError in setting Player 0's PCTH field.")

# Set Player 0's agility (PAGI).
boolSetValueAsInt = dllTDBAccess.TDBFieldSetValueAsInteger(intDBIndex, "PLAY", "PAGI", 0, int(dictFirstMaddenPlayerRatings['AGILITY']))
if boolSetValueAsInt:
    intGotValueAsInt = dllTDBAccess.TDBFieldGetValueAsInteger(intDBIndex, "PLAY", "PAGI", 0)
    print("Set Player 0's PAGI field to %d" % intGotValueAsInt)
else:
    print("\nError in setting Player 0's PAGI field.")

# Set Player 0's injury (PINJ).
boolSetValueAsInt = dllTDBAccess.TDBFieldSetValueAsInteger(intDBIndex, "PLAY", "PINJ", 0, int(dictFirstMaddenPlayerRatings['INJURY']))
if boolSetValueAsInt:
    intGotValueAsInt = dllTDBAccess.TDBFieldGetValueAsInteger(intDBIndex, "PLAY", "PINJ", 0)
    print("Set Player 0's PINJ field to %d" % intGotValueAsInt)
else:
    print("\nError in setting Player 0's PINJ field.")

# Set Player 0's tackling (PTAK).
boolSetValueAsInt = dllTDBAccess.TDBFieldSetValueAsInteger(intDBIndex, "PLAY", "PTAK", 0, int(dictFirstMaddenPlayerRatings['TACKLE']))
if boolSetValueAsInt:
    intGotValueAsInt = dllTDBAccess.TDBFieldGetValueAsInteger(intDBIndex, "PLAY", "PTAK", 0)
    print("Set Player 0's PTAK field to %d" % intGotValueAsInt)
else:
    print("\nError in setting Player 0's PTAK field.")

# Set Player 0's pass blocking (PPBK).
boolSetValueAsInt = dllTDBAccess.TDBFieldSetValueAsInteger(intDBIndex, "PLAY", "PPBK", 0, int(dictFirstMaddenPlayerRatings['PASS BLOCK']))
if boolSetValueAsInt:
    intGotValueAsInt = dllTDBAccess.TDBFieldGetValueAsInteger(intDBIndex, "PLAY", "PPBK", 0)
    print("Set Player 0's PPBK field to %d" % intGotValueAsInt)
else:
    print("\nError in setting Player 0's PPBK field.")

# Set Player 0's run blocking (PRBK).
boolSetValueAsInt = dllTDBAccess.TDBFieldSetValueAsInteger(intDBIndex, "PLAY", "PRBK", 0, int(dictFirstMaddenPlayerRatings['RUN BLOCK']))
if boolSetValueAsInt:
    intGotValueAsInt = dllTDBAccess.TDBFieldGetValueAsInteger(intDBIndex, "PLAY", "PRBK", 0)
    print("Set Player 0's PRBK field to %d" % intGotValueAsInt)
else:
    print("\nError in setting Player 0's PRBK field.")

# Set Player 0's break tackle (PBTK).
boolSetValueAsInt = dllTDBAccess.TDBFieldSetValueAsInteger(intDBIndex, "PLAY", "PBTK", 0, int(dictFirstMaddenPlayerRatings['TRUCKING']))
if boolSetValueAsInt:
    intGotValueAsInt = dllTDBAccess.TDBFieldGetValueAsInteger(intDBIndex, "PLAY", "PBTK", 0)
    print("Set Player 0's PBTK field to %d" % intGotValueAsInt)
else:
    print("\nError in setting Player 0's PBTK field.")

# Set Player 0's Player Role 1 (PROL) to 35 (Go-To Guy).
boolSetValueAsInt = dllTDBAccess.TDBFieldSetValueAsInteger(intDBIndex, "PLAY", "PROL", 0, 35)
if boolSetValueAsInt:
    intGotValueAsInt = dllTDBAccess.TDBFieldGetValueAsInteger(intDBIndex, "PLAY", "PROL", 0)
    print("Set Player 0's PROL field to %d" % intGotValueAsInt)
else:
    print("\nError in setting Player 0's PROL field.")

# Set Player 0's jersey number (PJEN).
boolSetValueAsInt = dllTDBAccess.TDBFieldSetValueAsInteger(intDBIndex, "PLAY", "PJEN", 0, int(dictFirstMaddenPlayerRatings['JERSEY']))
if boolSetValueAsInt:
    intGotValueAsInt = dllTDBAccess.TDBFieldGetValueAsInteger(intDBIndex, "PLAY", "PJEN", 0)
    print("Set Player 0's PJEN field to %d" % intGotValueAsInt)
else:
    print("\nError in setting Player 0's PJEN field.")

# Set Player 0's throwing power (PTHP).
boolSetValueAsInt = dllTDBAccess.TDBFieldSetValueAsInteger(intDBIndex, "PLAY", "PTHP", 0, int(dictFirstMaddenPlayerRatings['THROW POWER']))
if boolSetValueAsInt:
    intGotValueAsInt = dllTDBAccess.TDBFieldGetValueAsInteger(intDBIndex, "PLAY", "PTHP", 0)
    print("Set Player 0's PTHP field to %d" % intGotValueAsInt)
else:
    print("\nError in setting Player 0's PTHP field.")

# Set Player 0's jumping (PJMP).
boolSetValueAsInt = dllTDBAccess.TDBFieldSetValueAsInteger(intDBIndex, "PLAY", "PJMP", 0, int(dictFirstMaddenPlayerRatings['JUMPING']))
if boolSetValueAsInt:
    intGotValueAsInt = dllTDBAccess.TDBFieldGetValueAsInteger(intDBIndex, "PLAY", "PJMP", 0)
    print("Set Player 0's PJMP field to %d" % intGotValueAsInt)
else:
    print("\nError in setting Player 0's PJMP field.")

# Set Player 0's portrait ID (PSXP).
boolSetValueAsInt = dllTDBAccess.TDBFieldSetValueAsInteger(intDBIndex, "PLAY", "PSXP", 0, 0)
if boolSetValueAsInt:
    intGotValueAsInt = dllTDBAccess.TDBFieldGetValueAsInteger(intDBIndex, "PLAY", "PSXP", 0)
    print("Set Player 0's PSXP field to %d" % intGotValueAsInt)
else:
    print("\nError in setting Player 0's PSXP field.")

# Set Player 0's carrying (PCAR).
boolSetValueAsInt = dllTDBAccess.TDBFieldSetValueAsInteger(intDBIndex, "PLAY", "PCAR", 0, int(dictFirstMaddenPlayerRatings['CARRYING']))
if boolSetValueAsInt:
    intGotValueAsInt = dllTDBAccess.TDBFieldGetValueAsInteger(intDBIndex, "PLAY", "PCAR", 0)
    print("Set Player 0's PCAR field to %d" % intGotValueAsInt)
else:
    print("\nError in setting Player 0's PCAR field.")

# Set Player 0's kicking power (PKPR).
boolSetValueAsInt = dllTDBAccess.TDBFieldSetValueAsInteger(intDBIndex, "PLAY", "PKPR", 0, int(dictFirstMaddenPlayerRatings['KICK POWER']))
if boolSetValueAsInt:
    intGotValueAsInt = dllTDBAccess.TDBFieldGetValueAsInteger(intDBIndex, "PLAY", "PKPR", 0)
    print("Set Player 0's PKPR field to %d" % intGotValueAsInt)
else:
    print("\nError in setting Player 0's PKPR field.")

# Set Player 0's strength (PSTR).
boolSetValueAsInt = dllTDBAccess.TDBFieldSetValueAsInteger(intDBIndex, "PLAY", "PSTR", 0, int(dictFirstMaddenPlayerRatings['STRENGTH']))
if boolSetValueAsInt:
    intGotValueAsInt = dllTDBAccess.TDBFieldGetValueAsInteger(intDBIndex, "PLAY", "PSTR", 0)
    print("Set Player 0's PSTR field to %d" % intGotValueAsInt)
else:
    print("\nError in setting Player 0's PSTR field.")

# Set Player 0's overall rating (POVR).
boolSetValueAsInt = dllTDBAccess.TDBFieldSetValueAsInteger(intDBIndex, "PLAY", "POVR", 0, 25)
if boolSetValueAsInt:
    intGotValueAsInt = dllTDBAccess.TDBFieldGetValueAsInteger(intDBIndex, "PLAY", "POVR", 0)
    print("Set Player 0's POVR field to %d" % intGotValueAsInt)
else:
    print("\nError in setting Player 0's POVR field.")

# Set Player 0's awareness (PAWR).
boolSetValueAsInt = dllTDBAccess.TDBFieldSetValueAsInteger(intDBIndex, "PLAY", "PAWR", 0, int(dictFirstMaddenPlayerRatings['AWARENESS']))
if boolSetValueAsInt:
    intGotValueAsInt = dllTDBAccess.TDBFieldGetValueAsInteger(intDBIndex, "PLAY", "PAWR", 0)
    print("Set Player 0's PAWR field to %d" % intGotValueAsInt)
else:
    print("\nError in setting Player 0's PAWR field.")

# Set Player 0's Position ID (PPOS) to 3 (WR).
boolSetValueAsInt = dllTDBAccess.TDBFieldSetValueAsInteger(intDBIndex, "PLAY", "PPOS", 0, 3)
if boolSetValueAsInt:
    intGotValueAsInt = dllTDBAccess.TDBFieldGetValueAsInteger(intDBIndex, "PLAY", "PPOS", 0)
    print("Set Player 0's PPOS field to %d" % intGotValueAsInt)
else:
    print("\nError in setting Player 0's PPOS field.")

# Set Player 0's Other Position ID (POPS) to 3 (WR).
boolSetValueAsInt = dllTDBAccess.TDBFieldSetValueAsInteger(intDBIndex, "PLAY", "POPS", 0, 3)
if boolSetValueAsInt:
    intGotValueAsInt = dllTDBAccess.TDBFieldGetValueAsInteger(intDBIndex, "PLAY", "POPS", 0)
    print("Set Player 0's POPS field to %d" % intGotValueAsInt)
else:
    print("\nError in setting Player 0's POPS field.")

# Set Player 0's kick returns (PKRT).
boolSetValueAsInt = dllTDBAccess.TDBFieldSetValueAsInteger(intDBIndex, "PLAY", "PKRT", 0, int(dictFirstMaddenPlayerRatings['RETURN']))
if boolSetValueAsInt:
    intGotValueAsInt = dllTDBAccess.TDBFieldGetValueAsInteger(intDBIndex, "PLAY", "PKRT", 0)
    print("Set Player 0's PKRT field to %d" % intGotValueAsInt)
else:
    print("\nError in setting Player 0's PKRT field.")

'''
    

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
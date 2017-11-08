r""" read_tables.py
    
    This was one of the original three DLLTest files. Code from this file which can be used in the creation of the 
    script "step_5_update_roster_file.py" will be taken and used there. 
    
    This file currently opens the file "latest.ros", calls TDBTableGetProperties on each of the tables, and then calls 
    TDBFieldGetProperties for each field of each table, printing out the results along the way.

"""
import os
from ctypes import WinDLL, Structure, c_char_p, c_int, c_bool, cast, c_char, c_float, POINTER, byref
from enum import Enum

# Set the base path we will use to keep other paths relative, and shorter :^)
BASE_MADDEN_PATH = r"C:\Home\Working Files\madden_08_updater"

# Define the 'enum' and structures we will need, per the TDBAccess Reference.
# First, the tuple that will act as the enum for TDBFieldType.
# In Hex, tdbVarchar = 0xD, tdbLongVarchar = 0xE, and tdbInt = 0x2CE.
# (tdbString, tdbBinary, tdbSInt, tdbUInt, tdbFloat, tdbVarchar, tdbLongVarchar, tdbInt) = (0, 1, 2, 3, 4, 13, 14, 718)
#class TDBFieldType(Enum):
#    tdbString = 0
#    tdbBinary = 1
#    tdbSInt = 2
#    tdbUInt = 3
#    tdbFloat = 4
#    tdbVarchar = 0xD
#    tdbLongVarchar = 0xE
#    tdbInt = 0x2CE


# The structure for TDBTableProperties.
class TDBTableProperties(Structure):
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


# The structure for TDBFieldProperties.
class TDBFieldProperties(Structure):
    _fields_ = [
        ('Name', c_char_p),
        ('Size', c_int),
        ('FieldType', c_int),
    ]
    
    def __init__(self, *args):
        self.Name = cast((c_char * 8)(), c_char_p)
        Structure.__init__(self, *args)


# TODO: Wrap this WinDLL call in error checking. (Google 'python windll error handling')
dllTDBAccess = WinDLL(os.path.join(BASE_MADDEN_PATH, r"process\utilities\tdbaccess\old\tdbaccess.dll"))

# TODO: Add the restype definitions here for each of the 21 functions.
#dllTDBAccess.TDBClose.argtypes = [c_int]
#dllTDBAccess.TDBDatabaseCompact.argtypes = [c_int]
#dllTDBAccess.TDBDatabaseGetTableCount.argtypes = [c_int]
dllTDBAccess.TDBFieldGetProperties.argtypes = [c_int, c_char_p, c_int, POINTER(TDBFieldProperties)]
dllTDBAccess.TDBFieldGetProperties.restype = c_bool
#dllTDBAccess.TDBFieldGetValueAsBinary.argtypes = [c_int, c_char_p, c_char_p, c_int, POINTER(c_char_p)]
#dllTDBAccess.TDBFieldGetValueAsFloat.argtypes = [c_int, c_char_p, c_char_p, c_int]
#dllTDBAccess.TDBFieldGetValueAsInteger.argtypes = [c_int, c_char_p, c_char_p, c_int]
#dllTDBAccess.TDBFieldGetValueAsString.argtypes = [c_int, c_char_p, c_char_p, c_int, POINTER(c_char_p)]
#dllTDBAccess.TDBFieldSetValueAsFloat.argtypes = [c_int, c_char_p, c_char_p, c_int, c_float]
#dllTDBAccess.TDBFieldSetValueAsInteger.argtypes = [c_int, c_char_p, c_char_p, c_int, c_int]
#dllTDBAccess.TDBFieldSetValueAsString.argtypes = [c_int, c_char_p, c_char_p, c_int, c_char_p]
#dllTDBAccess.TDBOpen.argtypes = [c_char_p]
#dllTDBAccess.TDBQueryFindUnsignedInt.argtypes = [c_int, c_char_p, c_char_p, c_int]
#dllTDBAccess.TDBQueryGetResult.argtypes = [c_int]
#dllTDBAccess.TDBQueryGetResultSize.argtypes = []
#dllTDBAccess.TDBSave.argtypes = [c_int]
dllTDBAccess.TDBTableGetProperties.argtypes = [c_int, c_int, POINTER(TDBTableProperties)]
dllTDBAccess.TDBTableGetProperties.restype = c_bool
#dllTDBAccess.TDBTableRecordAdd.argtypes = [c_int, c_char_p, c_bool]
#dllTDBAccess.TDBTableRecordChangeDeleted.argtypes = [c_int, c_char_p, c_int, c_bool]
#dllTDBAccess.TDBTableRecordDeleted.argtypes = [c_int, c_char_p, c_int]
#dllTDBAccess.TDBTableRecordRemove.argtypes = [c_int, c_char_p, c_int]


# Here we open the roster file we want to work on.
# TODO: Wrap this TDBOpen call in error checking. 
# (e.g. intDBIndex = -1
#       intDBIndex = [result of func call]
#       if intDBIndex == -1:
#           [error handling]
intDBIndex = dllTDBAccess.TDBOpen(os.path.join(BASE_MADDEN_PATH, r"rosters\latest.ros"))
print("\nintDBIndex = %d\n" % intDBIndex)

# We'll want to use this to control a loop over the tables.
intNumberOfTables = dllTDBAccess.TDBDatabaseGetTableCount(intDBIndex)
print("intNumberOfTables = %d\n" % intNumberOfTables)

# Get the table properties of each of the tables.
listTableProperties = []
for i in range(intNumberOfTables):
    listTableProperties.append(TDBTableProperties())
    boolGotTableProperties = dllTDBAccess.TDBTableGetProperties(intDBIndex, i, byref(listTableProperties[i]))
    #print("boolGotTableProperties = %r" % boolGotTableProperties)
    print("listTableProperties[%d].Name = %r" % (i, listTableProperties[i].Name))
    print("listTableProperties[%d].FieldCount = %d" % (i, listTableProperties[i].FieldCount))
    print("listTableProperties[%d].Capacity = %d" % (i, listTableProperties[i].Capacity))
    print("listTableProperties[%d].RecordCount = %d\n" % (i, listTableProperties[i].RecordCount))
    #print("listTableProperties[%d].DeletedCount = %d" % (i, listTableProperties[i].DeletedCount))
    #print("listTableProperties[%d].NextDeletedRecord = %d" % (i, listTableProperties[i].NextDeletedRecord))
    #print("listTableProperties[%d].Flag0 = %r" % (i, listTableProperties[i].Flag0))
    #print("listTableProperties[%d].Flag1 = %r" % (i, listTableProperties[i].Flag1))
    #print("listTableProperties[%d].Flag2 = %r" % (i, listTableProperties[i].Flag2))
    #print("listTableProperties[%d].Flag3 = %r" % (i, listTableProperties[i].Flag3))
    #print("listTableProperties[%d].NonAllocated = %r" % (i, listTableProperties[i].NonAllocated))
    #print("listTableProperties[%d].HasVarchar = %r" % (i, listTableProperties[i].HasVarchar))
    #print("listTableProperties[%d].HasCompressedVarchar = %r" % (i, listTableProperties[i].HasCompressedVarchar))

# Loop over the fields in each table and get the properties of each field.
listTableFieldPropertiesLists = [[] for x in range(intNumberOfTables)]

for i in range(intNumberOfTables):
    print("\n")
    for j in range(listTableProperties[i].FieldCount):
        listTableFieldPropertiesLists[i].append(TDBFieldProperties())
        boolGotTableFieldProperties = dllTDBAccess.TDBFieldGetProperties(
            intDBIndex, 
            listTableProperties[i].Name, 
            j, 
            byref(listTableFieldPropertiesLists[i][j]))
#        print("boolGotTableFieldProperties = %r" % boolGotTableFieldProperties)
        print("listTableFieldPropertiesLists[%d][%d].Name = %r" % (i, j, listTableFieldPropertiesLists[i][j].Name))
#        print("listTableFieldPropertiesLists[%d][%d].Size = %d" % (i, j, listTableFieldPropertiesLists[i][j].Size))
#        print("listTableFieldPropertiesLists[%d][%d].FieldType = %d" 
#           % (i, j, listTableFieldPropertiesLists[i][j].FieldType))

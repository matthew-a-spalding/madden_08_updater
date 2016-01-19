""" read_tables.py
    
    This was one of the original three DDLTest files. Code from this file which 
    can be used in the creation of the script "04_update_roster_file.py" will 
    be taken and used there. This file should not be added to the original Git 
    repository, as it and the contents of the other two DLLTest files overlap.

"""
import os
from ctypes import  WinDLL, Structure, c_char_p, c_int, c_bool, c_float, 
                    POINTER, 
from enum import Enum

# Set the base path we will use to keep other paths relative, and shorter :^)
base_madden_path = r"C:\Home\madden_08_updater"

# TODO: Wrap this WinDLL call in error checking. (Google python windll error handling)
tdbaccessDLL = WinDLL(os.path.join(base_madden_path, r"tdbaccess\old\tdbaccess.dll"))

# Here we define the 'enum' and structures that we will need, per the TDBAccess Reference help file.

# First, the tuple that will act as the enum for tdbFieldType.
# In Hex, tdbVarchar = 0xD, tdbLongVarchar = 0xE, and tdbInt = 0x2CE.
#(tdbString, tdbBinary, tdbSInt, tdbUInt, tdbFloat, tdbVarchar, tdbLongVarchar, tdbInt) = (0, 1, 2, 3, 4, 13, 14, 718)
#class tdbFieldType(Enum):
#    tdbString = 0
#    tdbBinary = 1
#    tdbSInt = 2
#    tdbUInt = 3
#    tdbFloat = 4
#    tdbVarchar = 0xD
#    tdbLongVarchar = 0xE
#    tdbInt = 0x2CE

# The structure for tdbTableProperties.
class tdbTableProperties(Structure):
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

# The structure for tdbFieldProperties.
class tdbFieldProperties(Structure):
    _fields_ = [
        ('Name', c_char_p),
        ('Size', c_int),
        ('FieldType', c_int),
    ]

# TODO: Add the restype definitions here for each of the 21 functions.
#tdbaccessDLL.TDBClose.argtypes = [c_int]
#tdbaccessDLL.TDBDatabaseCompact.argtypes = [c_int]
#tdbaccessDLL.TDBDatabaseGetTableCount.argtypes = [c_int]
tdbaccessDLL.TDBFieldGetProperties.argtypes = [c_int, c_char_p, c_int, POINTER(tdbFieldProperties)]
tdbaccessDLL.TDBFieldGetProperties.restype = c_int
#tdbaccessDLL.TDBFieldGetValueAsBinary.argtypes = [c_int, c_char_p, c_char_p, c_int, POINTER(c_char_p)]
#tdbaccessDLL.TDBFieldGetValueAsFloat.argtypes = [c_int, c_char_p, c_char_p, c_int]
#tdbaccessDLL.TDBFieldGetValueAsInteger.argtypes = [c_int, c_char_p, c_char_p, c_int]
#tdbaccessDLL.TDBFieldGetValueAsString.argtypes = [c_int, c_char_p, c_char_p, c_int, POINTER(c_char_p)]
#tdbaccessDLL.TDBFieldSetValueAsFloat.argtypes = [c_int, c_char_p, c_char_p, c_int, c_float]
#tdbaccessDLL.TDBFieldSetValueAsInteger.argtypes = [c_int, c_char_p, c_char_p, c_int, c_int]
#tdbaccessDLL.TDBFieldSetValueAsString.argtypes = [c_int, c_char_p, c_char_p, c_int, c_char_p]
#tdbaccessDLL.TDBOpen.argtypes = [c_char_p]
#tdbaccessDLL.TDBQueryFindUnsignedInt.argtypes = [c_int, c_char_p, c_char_p, c_int]
#tdbaccessDLL.TDBQueryGetResult.argtypes = [c_int]
#tdbaccessDLL.TDBQueryGetResultSize.argtypes = []
#tdbaccessDLL.TDBSave.argtypes = [c_int]
#tdbaccessDLL.TDBTableGetProperties.argtypes = [c_int, c_int, POINTER(tdbTableProperties)]
#tdbaccessDLL.TDBTableRecordAdd.argtypes = [c_int, c_char_p, c_bool]
#tdbaccessDLL.TDBTableRecordChangeDeleted.argtypes = [c_int, c_char_p, c_int, c_bool]
#tdbaccessDLL.TDBTableRecordDeleted.argtypes = [c_int, c_char_p, c_int]
#tdbaccessDLL.TDBTableRecordRemove.argtypes = [c_int, c_char_p, c_int]


# Here we open the roster file we want to work on.
# TODO: Wrap this TDBOpen call in error checking. (e.g. intDBIndex = -1 ; intDBIndex = [result of func call] ; if intDBIndex == -1: ; [error handling]
intDBIndex = tdbaccessDLL.TDBOpen(os.path.join(base_madden_path, r"rosters\latest.ros"))
print("intDBIndex = %d" % intDBIndex)

# We'll want to use this to control a loop over the tables.
intNumberOfTables = tdbaccessDLL.TDBDatabaseGetTableCount(intDBIndex)
print("intNumberOfTables = %d" % intNumberOfTables)

# For now, just get the table properties of the first table.
# NOTE: The Name field MUST BE INITIALIZED WITH A VALUE OF AT LEAST 4 CHARS (PER THE TDBAccess Reference HELP FILE), 
# and no, the Name field in the tdbTableProperties(Structure) does NOT need to be mutable, since it is part of a 
# structure that is being passed by reference and will be completely overwritten.
tdbtpTableProperties = []
for i in range(intNumberOfTables):
    tdbtpTableProperties.append(tdbTableProperties(Name="DwNVJrOSSDFKARGHWRKGH"))
    boolGotTableProperties = tdbaccessDLL.TDBTableGetProperties(intDBIndex, i, byref(tdbtpTableProperties[i]))
    #print("boolGotTableProperties = %r" % boolGotTableProperties)
    print("tdbtpTableProperties[%d].Name = %r" % (i, tdbtpTableProperties[i].Name))
    print("tdbtpTableProperties[%d].FieldCount = %d" % (i, tdbtpTableProperties[i].FieldCount))
    print("tdbtpTableProperties[%d].Capacity = %d" % (i, tdbtpTableProperties[i].Capacity))
    print("tdbtpTableProperties[%d].RecordCount = %d\n" % (i, tdbtpTableProperties[i].RecordCount))
    #print("tdbtpTableProperties[%d].DeletedCount = %d" % (i, tdbtpTableProperties[i].DeletedCount))
    #print("tdbtpTableProperties[%d].NextDeletedRecord = %d" % (i, tdbtpTableProperties[i].NextDeletedRecord))
    #print("tdbtpTableProperties[%d].Flag0 = %r" % (i, tdbtpTableProperties[i].Flag0))
    #print("tdbtpTableProperties[%d].Flag1 = %r" % (i, tdbtpTableProperties[i].Flag1))
    #print("tdbtpTableProperties[%d].Flag2 = %r" % (i, tdbtpTableProperties[i].Flag2))
    #print("tdbtpTableProperties[%d].Flag3 = %r" % (i, tdbtpTableProperties[i].Flag3))
    #print("tdbtpTableProperties[%d].NonAllocated = %r" % (i, tdbtpTableProperties[i].NonAllocated))
    #print("tdbtpTableProperties[%d].HasVarchar = %r" % (i, tdbtpTableProperties[i].HasVarchar))
    #print("tdbtpTableProperties[%d].HasCompressedVarchar = %r" % (i, tdbtpTableProperties[i].HasCompressedVarchar))

# See what the fields are for the PLAY table (index 6 in tdbtpTableProperties).
# To do this, loop over the fields in tdbtpTableProperties[6] and get the properties of each field.
tdbfpTableFieldProperties = [[] for x in range(intNumberOfTables)]

for i in range(intNumberOfTables):
    print("\n")
    for j in range(tdbtpTableProperties[i].FieldCount):
        tdbfpTableFieldProperties[i].append(tdbFieldProperties(Name="Blah"))
        print("tdbfpTableFieldProperties[%d][%d].Name BEFORE = %r" % (i, j, tdbfpTableFieldProperties[i][j].Name))
        boolGotTableFieldProperties = tdbaccessDLL.TDBFieldGetProperties(intDBIndex, tdbtpTableProperties[i].Name, j, byref(tdbfpTableFieldProperties[i][j]))
#        print("boolGotTableFieldProperties = %r" % boolGotTableFieldProperties)
        print("tdbfpTableFieldProperties[%d][%d].Name AFTER = %r" % (i, j, tdbfpTableFieldProperties[i][j].Name))
#        print("tdbfpTableFieldProperties[%d][%d].Size = %d" % (i, j, tdbfpTableFieldProperties[i][j].Size))
#        print("tdbfpTableFieldProperties[%d][%d].FieldType = %d" % (i, j, tdbfpTableFieldProperties[i][j].FieldType))
#tdbfpTable6FieldProperties.append(tdbFieldProperties(Name=""))
#boolGotTable6FieldProperties = tdbaccessDLL.TDBFieldGetProperties(intDBIndex, tdbtpTableProperties[6].Name, 120, byref(tdbfpTable6FieldProperties[0]))
#print("boolGotTable6FieldProperties = %r" % boolGotTable6FieldProperties)
#print("tdbfpTable6FieldProperties[0].Name = %s" % tdbfpTable6FieldProperties[0].Name)
#print("tdbfpTable6FieldProperties[0].Size = %d" % tdbfpTable6FieldProperties[0].Size)
#print("tdbfpTable6FieldProperties[0].FieldType = %d" % tdbfpTable6FieldProperties[0].FieldType)

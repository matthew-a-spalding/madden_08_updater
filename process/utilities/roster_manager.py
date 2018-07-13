r"""roster_manager.py
    
    This is the only python sub-module used by the script "step_5_update_roster_file.py". It contains the 
    RosterManager class which has methods that perform the logic of that script's main function.
"""

# --------------------------------------------------- SECTION 1 -------------------------------------------------------
# ---------------------------------------- IMPORTS, SETTINGS, AND CONSTANTS -------------------------------------------
# 1 - Standard library imports
import csv, logging, os, sys
from ctypes import byref, cast, c_bool, c_wchar, c_wchar_p, c_int, POINTER, Structure, WinDLL
from shutil import copyfile

# 2 - Third-party imports

# 3 - Application-specific imports

# 4 - Global settings

# 5 - Global constants


# ----------------------------------------------------- SECTION 2 -----------------------------------------------------
# ------------------------------------------------ Class Declarations -------------------------------------------------

class TDBTablePropertiesStruct(Structure):
    """Structure whose fields hold all the properties of a table in the roster file."""
    _fields_ = [
        ('Name', c_wchar_p),
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
        self.Name = cast((c_wchar * 8)(), c_wchar_p)
        Structure.__init__(self, *args)

class RosterManager:
    """ Class that encapsulates all of the properties and methods needed to work on the roster file. """
    
    # Define our class attributes.
    players_table = 'PLAY'
    # Set the base path we will use to keep other paths relative, and shorter :^)
    # This will be the directory above the directory above the directory this file is in.
    base_madden_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    def __init__(self):
        
        # Define our instance attributes.
        self.player_table_properties = TDBTablePropertiesStruct()
        
        # Set up our DDL file.
        self.initialize_dll()
        
        # Copy the input file into our destination folder and rename on the way.
        copyfile(
            os.path.join(RosterManager.base_madden_path, r"process\inputs\step5\base.ros"), 
            os.path.join(RosterManager.base_madden_path, r"process\outputs\step5\latest.ros")
        )
        
        # Open the roster file through the DLL and get its index.
        self.db_index = self.tdbaccess_dll.TDBOpen(
            os.path.join(RosterManager.base_madden_path, r"process\outputs\step5\latest.ros")
        )
        if self.db_index == -1:
            sys.exit()
        logging.info("self.db_index = %d", self.db_index)
        
        # Get the number of existing players in the roster file via the getter for the PLAY table's properties.
        self.got_table_properties = self.tdbaccess_dll.TDBTableGetProperties(
            self.db_index, 
            6, 
            byref(self.player_table_properties)
        )
        
        if not self.got_table_properties:
            logging.critical("\tFailed to read properties of PLAY table! Exiting.")
            raise RuntimeError
        
        # Read colleges_and_ids.csv into a list of dicts.
        with open(os.path.join(
            RosterManager.base_madden_path, 
            r"process\utilities\colleges_and_ids.csv")
                 ) as colleges_file: 
            # Get a DictReader to read the rows into dicts using the header row as keys.
            colleges_dict_reader = csv.DictReader(colleges_file)
            # Pull our records into a list so we can count them and iterate over them as often as needed.
            self.colleges_list = list(colleges_dict_reader)
        
        # Read teams_and_ids.csv into a list of dicts.
        with open(os.path.join(RosterManager.base_madden_path, r"process\utilities\teams_and_ids.csv")) as teams_file: 
            # Get a DictReader to read the rows into dicts using the header row as keys.
            teams_dict_reader = csv.DictReader(teams_file)
            # Pull our records into a list so we can count them and iterate over them as often as needed.
            self.teams_list = list(teams_dict_reader)
    
    def __del__(self):
        if self.db_index > -1:
            self.compact_save_close_db()
    
    def initialize_dll(self):
        """ Gets a handle to the TDBAccess DLL and sets the DLL's functions' arg/restypes. """
        
         # Get a handle for our DLL.
        self.tdbaccess_dll = WinDLL(
            os.path.join(RosterManager.base_madden_path, r"process\utilities\tdbaccess\new\tdbaccess.dll")
        )
        
        # Add the argtype and restype definitions here for the DLL functions we'll use.
        self.tdbaccess_dll.TDBClose.argtypes = [c_int]
        self.tdbaccess_dll.TDBClose.restype = c_bool
        
        self.tdbaccess_dll.TDBDatabaseCompact.argtypes = [c_int]
        self.tdbaccess_dll.TDBDatabaseCompact.restype = c_bool
        
        self.tdbaccess_dll.TDBFieldGetValueAsInteger.argtypes = [c_int, c_wchar_p, c_wchar_p, c_int]
        self.tdbaccess_dll.TDBFieldGetValueAsInteger.restype = c_int
        
        self.tdbaccess_dll.TDBFieldGetValueAsString.argtypes = [c_int, c_wchar_p, c_wchar_p, c_int, POINTER(c_wchar_p)]
        self.tdbaccess_dll.TDBFieldGetValueAsString.restype = c_bool
        
        self.tdbaccess_dll.TDBFieldSetValueAsInteger.argtypes = [c_int, c_wchar_p, c_wchar_p, c_int, c_int]
        self.tdbaccess_dll.TDBFieldSetValueAsInteger.restype = c_bool
        
        self.tdbaccess_dll.TDBFieldSetValueAsString.argtypes = [c_int, c_wchar_p, c_wchar_p, c_int, c_wchar_p]
        self.tdbaccess_dll.TDBFieldSetValueAsString.restype = c_bool
        
        self.tdbaccess_dll.TDBOpen.argtypes = [c_wchar_p]
        self.tdbaccess_dll.TDBOpen.restype = c_int
        
        self.tdbaccess_dll.TDBSave.argtypes = [c_int]
        self.tdbaccess_dll.TDBSave.restype = c_bool
        
        self.tdbaccess_dll.TDBTableGetProperties.argtypes = [c_int, c_int, POINTER(TDBTablePropertiesStruct)]
        self.tdbaccess_dll.TDBTableGetProperties.restype = c_bool
        
        self.tdbaccess_dll.TDBTableRecordAdd.argtypes = [c_int, c_wchar_p, c_bool]
        self.tdbaccess_dll.TDBTableRecordAdd.restype = c_int
        
        self.tdbaccess_dll.TDBTableRecordChangeDeleted.argtypes = [c_int, c_wchar_p, c_int, c_bool]
        self.tdbaccess_dll.TDBTableRecordChangeDeleted.restype = c_bool
    
    def size_player_table(self, new_player_count):
        """ Sizes the PLAY table in the roster file to match the given number of players. """
        
        logging.info(
            "self.player_table_properties.Name = %s", 
            self.player_table_properties.Name
        )
        logging.info(
            "self.player_table_properties.FieldCount = %d", 
            self.player_table_properties.FieldCount
        )
        logging.info(
            "self.player_table_properties.Capacity = %d", 
            self.player_table_properties.Capacity
        )
        logging.info(
            "self.player_table_properties.RecordCount = %d", 
            self.player_table_properties.RecordCount
        )
        logging.info(
            "self.player_table_properties.DeletedCount = %d", 
            self.player_table_properties.DeletedCount
        )
        logging.info(
            "self.player_table_properties.NextDeletedRecord = %d", 
            self.player_table_properties.NextDeletedRecord
        )
        
        # The existing player count is the number in RecordCount minus the value in DeletedCount.
        existing_player_count = self.player_table_properties.RecordCount - self.player_table_properties.DeletedCount
        logging.info("existing_player_count = %d", existing_player_count)
        
        # If we have fewer new players than existing players, delete the excess. If more, create records for them.
        if new_player_count < existing_player_count:
            self.delete_players(existing_player_count - new_player_count)
        elif new_player_count > existing_player_count:
            self.add_players(new_player_count - existing_player_count)
    
    def delete_players(self, number_to_delete):
        """ Marks the given number of player records (from the end of the PLAY table) for deletion. """
        
        logging.info("Deleting %d player records.", number_to_delete)
        for index in range(
                self.player_table_properties.RecordCount - number_to_delete, 
                self.player_table_properties.RecordCount):
            record_was_marked_deleted = self.tdbaccess_dll.TDBTableRecordChangeDeleted(
                self.db_index, 
                RosterManager.players_table, 
                index, 
                True
            )
            if not record_was_marked_deleted:
                logging.error("\tFailed to mark record #%d for deletion!", index)
    
    def add_players(self, number_to_add):
        """ Adds the given number of player records to the end of the PLAY table. """
        
        logging.info("Adding %d player records.", number_to_add)
        for index in range(number_to_add):
            added_player_record = self.tdbaccess_dll.TDBTableRecordAdd(
                self.db_index, 
                RosterManager.players_table,
                False
            )
            if added_player_record == 65535:
                logging.error("\tFailed to add record #%d!", index)
        self.tdbaccess_dll.TDBTableGetProperties(self.db_index, 6, byref(self.player_table_properties))
        logging.info("PLAY table now has %d player records.", self.player_table_properties.RecordCount)
    
    def compact_save_close_db(self):
        """ Compacts, saves, and closes the DB via the self.tdbaccess_dll. """
        
        # Compact the DB.
        compacted_database = self.tdbaccess_dll.TDBDatabaseCompact(self.db_index)
        if compacted_database:
            logging.info("Compacted the TDBDatabase.")
        else:
            logging.error("\tFailed to compact the TDBDatabase!")

        # Save the DB.
        saved_database = self.tdbaccess_dll.TDBSave(self.db_index)
        if saved_database:
            logging.info("Saved the TDBDatabase.")
        else:
            logging.error("\tFailed to save the TDBDatabase!")

        # Close the DB.
        closed_database = self.tdbaccess_dll.TDBClose(self.db_index)
        if closed_database:
            # Invalidate our db_index so we don't try to do this again (if python calls __del__).
            self.db_index = -1
            logging.info("Closed the TDBDatabase.")
        else:
            logging.error("\tFailed to close the TDBDatabase!")
    
    def set_player_integer_field(self, field_name, player_index, field_int_value):
        """ Sets a given field on a given player's record to a given integer value. """
        value_was_set_as_int = self.tdbaccess_dll.TDBFieldSetValueAsInteger(
            self.db_index, RosterManager.players_table, field_name, player_index, field_int_value)
        if not value_was_set_as_int:
            logging.error("\tFailed in setting player %d's %s field as integer!", player_index, field_name)
    
    def set_player_string_field(self, field_name, player_index, field_str_value):
        """ Sets a given field on a given player's record to a given string value. """
        value_was_set_as_string = self.tdbaccess_dll.TDBFieldSetValueAsString(
            self.db_index, RosterManager.players_table, field_name, player_index, field_str_value)
        if not value_was_set_as_string:
            logging.error("\tFailed in setting player %d's %s field as string!", player_index, field_name)
    
    def get_team_id(self, team_name):
        """ Returns the Madden ID corresponding to a given team name. """
        # Use the generator expression 'next' to get the team with the given name, or None if not found.
        team_dict = next((team for team in self.teams_list if team["name"].upper() in team_name.upper()), None)
        if team_dict is not None:
            return int(team_dict["id"])
        return 1023
    
    def get_college_id(self, college_name):
        """ Returns the Madden ID corresponding to a given college name. """
        # Use the generator expression 'next' to get the college with the given name, or None if not found.
        college_dict = next(
            (college for college in self.colleges_list if college["name"].upper() == college_name.upper()), 
            None
        )
        if college_dict is not None:
            return int(college_dict["id"])
        return 265
    
    from ._quarterback import create_quarterback
    
    from ._halfback import create_halfback
    
    from ._fullback import create_fullback
    
    from ._wide_receiver import create_wide_receiver
    
    from ._tight_end import create_tight_end
    
    from ._left_tackle import create_left_tackle
    
    from ._left_guard import create_left_guard
    
    from ._center import create_center
    
    from ._right_guard import create_right_guard
    
    from ._right_tackle import create_right_tackle
    
    from ._left_end import create_left_end
    
    from ._right_end import create_right_end
    
    from ._defensive_tackle import create_defensive_tackle
    
    from ._left_outside_linebacker import create_left_outside_linebacker
    
    from ._middle_linebacker import create_middle_linebacker
    
    from ._right_outside_linebacker import create_right_outside_linebacker
    
    from ._cornerback import create_cornerback
    
    from ._free_safety import create_free_safety
    
    from ._strong_safety import create_strong_safety
    
    from ._kicker import create_kicker
    
    from ._punter import create_punter
    

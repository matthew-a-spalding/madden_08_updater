r""" helper.py
    
    This is the only python sub-module used by the script "step_5_update_roster_file.py". It contains the Helper class 
    which has methods that perform the logic of that script's main function.
"""

# --------------------------------------------------- SECTION 1 -------------------------------------------------------
# ---------------------------------------- IMPORTS, SETTINGS, AND CONSTANTS -------------------------------------------
# 1 - Standard library imports
import csv, logging, os, math, sys
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

class Helper:
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
            os.path.join(Helper.base_madden_path, r"process\inputs\base.ros"), 
            os.path.join(Helper.base_madden_path, r"process\outputs\latest.ros")
        )
        
        # Open the roster file through the DLL and get its index.
        self.db_index = self.tdbaccess_dll.TDBOpen(
            os.path.join(Helper.base_madden_path, r"process\outputs\latest.ros")
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
        with open(os.path.join(Helper.base_madden_path, r"process\utilities\colleges_and_ids.csv")) as colleges_file: 
            # Get a DictReader to read the rows into dicts using the header row as keys.
            colleges_dict_reader = csv.DictReader(colleges_file)
            # Pull our records into a list so we can count them and iterate over them as often as needed.
            self.colleges_list = list(colleges_dict_reader)
        
        # Read teams_and_ids.csv into a list of dicts.
        with open(os.path.join(Helper.base_madden_path, r"process\utilities\teams_and_ids.csv")) as teams_file: 
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
            os.path.join(Helper.base_madden_path, r"process\utilities\tdbaccess\new\tdbaccess.dll")
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
        
        # If we have fewer new players than existing players, delete the excess. If we have more, create records for them.
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
                Helper.players_table, 
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
                Helper.players_table,
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
            self.db_index, Helper.players_table, field_name, player_index, field_int_value)
        if not value_was_set_as_int:
            logging.error("\tFailed in setting player %d's %s field as integer!", player_index, field_name)
    
    def set_player_string_field(self, field_name, player_index, field_str_value):
        """ Sets a given field on a given player's record to a given string value. """
        value_was_set_as_string = self.tdbaccess_dll.TDBFieldSetValueAsString(
            self.db_index, Helper.players_table, field_name, player_index, field_str_value)
        if not value_was_set_as_string:
            logging.error("\tFailed in setting player %d's %s field as string!", player_index, field_name)
    
    def get_team_id(self, team_name):
        """ Returns the Madden ID corresponding to a given team name. """
        # Use the generator expression 'next' to get the team with the given name, or None if not found.
        team_dict = next((team for team in self.teams_list if team["name"].upper() in team_name.upper()), None)
        if team_dict is not None:
            return int(team_dict["id"])
        return 1023
        # if "BEARS" in team_name.upper():
        #     return 1
        # if "BENGALS" in team_name.upper():
        #     return 2
        # if "BILLS" in team_name.upper():
        #     return 3
        # if "BRONCOS" in team_name.upper():
        #     return 4
        # if "BROWNS" in team_name.upper():
        #     return 5
        # if "BUCCANEERS" in team_name.upper():
        #     return 6
        # if "CARDINALS" in team_name.upper():
        #     return 7
        # if "CHARGERS" in team_name.upper():
        #     return 8
        # if "CHIEFS" in team_name.upper():
        #     return 9
        # if "COLTS" in team_name.upper():
        #     return 10
        # if "COWBOYS" in team_name.upper():
        #     return 11
        # if "DOLPHINS" in team_name.upper():
        #     return 12
        # if "EAGLES" in team_name.upper():
        #     return 13
        # if "FALCONS" in team_name.upper():
        #     return 14
        # if "49ERS" in team_name.upper():
        #     return 15
        # if "GIANTS" in team_name.upper():
        #     return 16
        # if "JAGUARS" in team_name.upper():
        #     return 17
        # if "JETS" in team_name.upper():
        #     return 18
        # if "LIONS" in team_name.upper():
        #     return 19
        # if "PACKERS" in team_name.upper():
        #     return 20
        # if "PANTHERS" in team_name.upper():
        #     return 21
        # if "PATRIOTS" in team_name.upper():
        #     return 22
        # if "RAIDERS" in team_name.upper():
        #     return 23
        # if "RAMS" in team_name.upper():
        #     return 24
        # if "RAVENS" in team_name.upper():
        #     return 25
        # if "REDSKINS" in team_name.upper():
        #     return 26
        # if "SAINTS" in team_name.upper():
        #     return 27
        # if "SEAHAWKS" in team_name.upper():
        #     return 28
        # if "STEELERS" in team_name.upper():
        #     return 29
        # if "TITANS" in team_name.upper():
        #     return 30
        # if "VIKINGS" in team_name.upper():
        #     return 31
        # if "TEXANS" in team_name.upper():
        #     return 32
        # return 1023
    
    def get_college_id(self, college_name):
        """ Returns the Madden ID corresponding to a given college name. """
        # Use the generator expression 'next' to get the college with the given name, or None if not found.
        college_dict = next(
            (college for college in self.colleges_list if college["name"].upper() in college_name.upper()), 
            None
        )
        if college_dict is not None:
            return int(college_dict["id"])
        return 265
    
    def create_quarterback(self, player_dict, index):
        """
        Given a dictionary of a new player and the index of the related record to modify in the DB, performs all of 
        the calculations and updates necessary to create the player as a QB in the DB.
        """
        # For all of the following fields, we simply use 0.
        # PCPH, PFHO, PJTY, PMPC, PMUS, POPS, PPOS, PSTM, PSTY, PSXP, PTSL, PUCL, TLEL, TLHA, TLWR, TREL, TRHA, TRWR, 
        self.set_player_integer_field('PCPH', index, 0)
        self.set_player_integer_field('PFHO', index, 0)
        self.set_player_integer_field('PJTY', index, 0)
        self.set_player_integer_field('PMPC', index, 0)
        self.set_player_integer_field('PMUS', index, 0)
        self.set_player_integer_field('POPS', index, 0)
        self.set_player_integer_field('PPOS', index, 0)
        self.set_player_integer_field('PSTM', index, 0)
        self.set_player_integer_field('PSTY', index, 0)
        self.set_player_integer_field('PSXP', index, 0)
        self.set_player_integer_field('PTSL', index, 0)
        self.set_player_integer_field('PUCL', index, 0)
        self.set_player_integer_field('TLEL', index, 0)
        self.set_player_integer_field('TLHA', index, 0)
        self.set_player_integer_field('TLWR', index, 0)
        self.set_player_integer_field('TREL', index, 0)
        self.set_player_integer_field('TRHA', index, 0)
        self.set_player_integer_field('TRWR', index, 0)
        
        # PCMT gets 999, PJER gets a 1, PLHY gets -31, PLPL gets 100, and PPTI will always get 1009.
        self.set_player_integer_field('PCMT', index, 999)
        self.set_player_integer_field('PJER', index, 1)
        self.set_player_integer_field('PLHY', index, -31)
        self.set_player_integer_field('PLPL', index, 100)
        self.set_player_integer_field('PPTI', index, 1009)
        
        # For most attributes which are in 'Latest Player Attributes.csv', simply use the value in the file.
        self.set_player_integer_field('PAGE', index, int(player_dict["age"]))
        self.set_player_integer_field('PDPI', index, int(player_dict["draft_pick"]))
        self.set_player_integer_field('PDRO', index, int(player_dict["draft_round"]))
        self.set_player_integer_field('PFEx', index, int(player_dict["face_id"]))
        self.set_player_integer_field('PFPB', index, int(player_dict["pro_bowl"]))
        self.set_player_integer_field('PHED', index, int(player_dict["hair_style"]))
        self.set_player_integer_field('PHCL', index, int(player_dict["hair_color"]))
        self.set_player_integer_field('PHGT', index, int(player_dict["height"]))
        self.set_player_integer_field('PICN', index, int(player_dict["nfl_icon"]))
        self.set_player_integer_field('PJEN', index, int(player_dict["jersey_number"]))
        self.set_player_integer_field('PLEL', index, int(player_dict["left_elbow"]))
        self.set_player_integer_field('PLHA', index, int(player_dict["left_hand"]))
        self.set_player_integer_field('PLSH', index, int(player_dict["left_shoe"]))
        self.set_player_integer_field('PLTH', index, int(player_dict["left_knee"]))
        self.set_player_integer_field('PNEK', index, int(player_dict["neck_pad"]))
        self.set_player_integer_field('PREL', index, int(player_dict["right_elbow"]))
        self.set_player_integer_field('PRHA', index, int(player_dict["right_hand"]))
        self.set_player_integer_field('PRSH', index, int(player_dict["right_shoe"]))
        self.set_player_integer_field('PRTH', index, int(player_dict["right_knee"]))
        self.set_player_integer_field('PSKI', index, int(player_dict["skin_color"]))
        self.set_player_integer_field('PVIS', index, int(player_dict["visor_style"]))
        self.set_player_integer_field('PYRP', index, int(player_dict["years_pro"]))
        self.set_player_integer_field('PYWT', index, int(player_dict["years_pro"]))
        
        # For these attributes, the calculations are simple.
        
        # The college ID is simply picked from a list.
        self.set_player_integer_field('PCOL', index, self.get_college_id(player_dict["college"]))
        # Get the first 11 characters of the first name.
        if len(player_dict["first_name"]) < 12:
            self.set_player_string_field('PFNA', index, player_dict["first_name"])
        else:
            self.set_player_string_field('PFNA', index, player_dict["first_name"][:11])
        # The handedness is 0 for right, 1 for left.
        if "RIGHT" in player_dict["handedness"].upper():
            self.set_player_integer_field('PHAN', index, 0)
        else:
            self.set_player_integer_field('PHAN', index, 1)
        # Get the first 13 characters of the last name.
        if len(player_dict["last_name"]) < 14:
            self.set_player_string_field('PLNA', index, player_dict["last_name"])
        else:
            self.set_player_string_field('PLNA', index, player_dict["last_name"][:13])
        # Subtract 160 from the players weight, unless he is already under 160.
        if int(player_dict["weight"]) > 159:
            self.set_player_integer_field('PWGT', index, (int(player_dict["weight"]) - 160))
        else:
            self.set_player_integer_field('PWGT', index, 0)
        # The team ID is simply picked from a list.
        self.set_player_integer_field('TGID', index, self.get_team_id(player_dict["team"]))
        
        # For some attributes, we will use formulas to determine what value to use. 
        
    def create_halfback(self, player_dict, index):
        """ 
        Given a dictionary of a new player and the index of the related record to modify in the DB, performs all of 
        the calculations and updates necessary to create the player as a HB in the DB.
        """
        # For all of the following fields, we simply use 0.
        # TLHA, TRHA, PCPH, PLSH, PRSH, PLTH, PRTH, PUCL, TLEL, TREL, PTSL, PSTM, PFHO, PSXP, TLWR, TRWR, PMUS, PJTY, PSTY
        self.set_player_integer_field('TLHA', index, 0)
        
        # PPTI will always get 1009, PLPL gets 100, PJER gets a 1, PCMT gets 999, PLHY gets -31, 
        
        # For attributes which have a column in the 'Latest Player Attributes.csv' file, use the value if it differs from 
        # the default value we put in that column. If not, we will use formulas to determine what value to use. 
        
    def create_fullback(self, player_dict, index):
        """ 
        Given a dictionary of a new player and the index of the related record to modify in the DB, performs all of 
        the calculations and updates necessary to create the player as a FB in the DB.
        """
        # For all of the following fields, we simply use 0.
        # TLHA, TRHA, PCPH, PLSH, PRSH, PLTH, PRTH, PUCL, TLEL, TREL, PTSL, PSTM, PFHO, PSXP, TLWR, TRWR, PMUS, PJTY, PSTY
        self.set_player_integer_field('TLHA', index, 0)
        
        # PPTI will always get 1009, PLPL gets 100, PJER gets a 1, PCMT gets 999, PLHY gets -31, 
        
        # For attributes which have a column in the 'Latest Player Attributes.csv' file, use the value if it differs from 
        # the default value we put in that column. If not, we will use formulas to determine what value to use. 
        
    def create_wide_receiver(self, player_dict, index):
        """ 
        Given a dictionary of a new player and the index of the related record to modify in the DB, performs all of 
        the calculations and updates necessary to create the player as a QB in the DB.
        """
        # For all of the following fields, we simply use 0.
        # TLHA, TRHA, PCPH, PLSH, PRSH, PLTH, PRTH, PUCL, TLEL, TREL, PTSL, PSTM, PFHO, PSXP, TLWR, TRWR, PMUS, PJTY, PSTY
        self.set_player_integer_field('TLHA', index, 0)
        
        # PPTI will always get 1009, PLPL gets 100, PJER gets a 1, PCMT gets 999, PLHY gets -31, 
        
        # For attributes which have a column in the 'Latest Player Attributes.csv' file, use the value if it differs from 
        # the default value we put in that column. If not, we will use formulas to determine what value to use. 
        
    def create_tight_end(self, player_dict, index):
        """ 
        Given a dictionary of a new player and the index of the related record to modify in the DB, performs all of 
        the calculations and updates necessary to create the player as a QB in the DB.
        """
        # For all of the following fields, we simply use 0.
        # TLHA, TRHA, PCPH, PLSH, PRSH, PLTH, PRTH, PUCL, TLEL, TREL, PTSL, PSTM, PFHO, PSXP, TLWR, TRWR, PMUS, PJTY, PSTY
        self.set_player_integer_field('TLHA', index, 0)
        
        # PPTI will always get 1009, PLPL gets 100, PJER gets a 1, PCMT gets 999, PLHY gets -31, 
        
        # For attributes which have a column in the 'Latest Player Attributes.csv' file, use the value if it differs from 
        # the default value we put in that column. If not, we will use formulas to determine what value to use. 
        
    def create_left_tackle(self, player_dict, index):
        """ 
        Given a dictionary of a new player and the index of the related record to modify in the DB, performs all of 
        the calculations and updates necessary to create the player as a QB in the DB.
        """
        # For all of the following fields, we simply use 0.
        # TLHA, TRHA, PCPH, PLSH, PRSH, PLTH, PRTH, PUCL, TLEL, TREL, PTSL, PSTM, PFHO, PSXP, TLWR, TRWR, PMUS, PJTY, PSTY
        self.set_player_integer_field('TLHA', index, 0)
        
        # PPTI will always get 1009, PLPL gets 100, PJER gets a 1, PCMT gets 999, PLHY gets -31, 
        
        # For attributes which have a column in the 'Latest Player Attributes.csv' file, use the value if it differs from 
        # the default value we put in that column. If not, we will use formulas to determine what value to use. 
        
    def create_left_guard(self, player_dict, index):
        """ 
        Given a dictionary of a new player and the index of the related record to modify in the DB, performs all of 
        the calculations and updates necessary to create the player as a QB in the DB.
        """
        # For all of the following fields, we simply use 0.
        # TLHA, TRHA, PCPH, PLSH, PRSH, PLTH, PRTH, PUCL, TLEL, TREL, PTSL, PSTM, PFHO, PSXP, TLWR, TRWR, PMUS, PJTY, PSTY
        self.set_player_integer_field('TLHA', index, 0)
        
        # PPTI will always get 1009, PLPL gets 100, PJER gets a 1, PCMT gets 999, PLHY gets -31, 
        
        # For attributes which have a column in the 'Latest Player Attributes.csv' file, use the value if it differs from 
        # the default value we put in that column. If not, we will use formulas to determine what value to use. 
        
    def create_center(self, player_dict, index):
        """ 
        Given a dictionary of a new player and the index of the related record to modify in the DB, performs all of 
        the calculations and updates necessary to create the player as a QB in the DB.
        """
        # For all of the following fields, we simply use 0.
        # TLHA, TRHA, PCPH, PLSH, PRSH, PLTH, PRTH, PUCL, TLEL, TREL, PTSL, PSTM, PFHO, PSXP, TLWR, TRWR, PMUS, PJTY, PSTY
        self.set_player_integer_field('TLHA', index, 0)
        
        # PPTI will always get 1009, PLPL gets 100, PJER gets a 1, PCMT gets 999, PLHY gets -31, 
        
        # For attributes which have a column in the 'Latest Player Attributes.csv' file, use the value if it differs from 
        # the default value we put in that column. If not, we will use formulas to determine what value to use. 
        
    def create_right_guard(self, player_dict, index):
        """ 
        Given a dictionary of a new player and the index of the related record to modify in the DB, performs all of 
        the calculations and updates necessary to create the player as a QB in the DB.
        """
        # For all of the following fields, we simply use 0.
        # TLHA, TRHA, PCPH, PLSH, PRSH, PLTH, PRTH, PUCL, TLEL, TREL, PTSL, PSTM, PFHO, PSXP, TLWR, TRWR, PMUS, PJTY, PSTY
        self.set_player_integer_field('TLHA', index, 0)
        
        # PPTI will always get 1009, PLPL gets 100, PJER gets a 1, PCMT gets 999, PLHY gets -31, 
        
        # For attributes which have a column in the 'Latest Player Attributes.csv' file, use the value if it differs from 
        # the default value we put in that column. If not, we will use formulas to determine what value to use. 
        
    def create_right_tackle(self, player_dict, index):
        """ 
        Given a dictionary of a new player and the index of the related record to modify in the DB, performs all of 
        the calculations and updates necessary to create the player as a QB in the DB.
        """
        # For all of the following fields, we simply use 0.
        # TLHA, TRHA, PCPH, PLSH, PRSH, PLTH, PRTH, PUCL, TLEL, TREL, PTSL, PSTM, PFHO, PSXP, TLWR, TRWR, PMUS, PJTY, PSTY
        self.set_player_integer_field('TLHA', index, 0)
        
        # PPTI will always get 1009, PLPL gets 100, PJER gets a 1, PCMT gets 999, PLHY gets -31, 
        
        # For attributes which have a column in the 'Latest Player Attributes.csv' file, use the value if it differs from 
        # the default value we put in that column. If not, we will use formulas to determine what value to use. 
        
    def create_left_end(self, player_dict, index):
        """ 
        Given a dictionary of a new player and the index of the related record to modify in the DB, performs all of 
        the calculations and updates necessary to create the player as a QB in the DB.
        """
        # For all of the following fields, we simply use 0.
        # TLHA, TRHA, PCPH, PLSH, PRSH, PLTH, PRTH, PUCL, TLEL, TREL, PTSL, PSTM, PFHO, PSXP, TLWR, TRWR, PMUS, PJTY, PSTY
        self.set_player_integer_field('TLHA', index, 0)
        
        # PPTI will always get 1009, PLPL gets 100, PJER gets a 1, PCMT gets 999, PLHY gets -31, 
        
        # For attributes which have a column in the 'Latest Player Attributes.csv' file, use the value if it differs from 
        # the default value we put in that column. If not, we will use formulas to determine what value to use. 
        
    def create_right_end(self, player_dict, index):
        """ 
        Given a dictionary of a new player and the index of the related record to modify in the DB, performs all of 
        the calculations and updates necessary to create the player as a QB in the DB.
        """
        # For all of the following fields, we simply use 0.
        # TLHA, TRHA, PCPH, PLSH, PRSH, PLTH, PRTH, PUCL, TLEL, TREL, PTSL, PSTM, PFHO, PSXP, TLWR, TRWR, PMUS, PJTY, PSTY
        self.set_player_integer_field('TLHA', index, 0)
        
        # PPTI will always get 1009, PLPL gets 100, PJER gets a 1, PCMT gets 999, PLHY gets -31, 
        
        # For attributes which have a column in the 'Latest Player Attributes.csv' file, use the value if it differs from 
        # the default value we put in that column. If not, we will use formulas to determine what value to use. 
        
    def create_defensive_tackle(self, player_dict, index):
        """ 
        Given a dictionary of a new player and the index of the related record to modify in the DB, performs all of 
        the calculations and updates necessary to create the player as a QB in the DB.
        """
        # For all of the following fields, we simply use 0.
        # TLHA, TRHA, PCPH, PLSH, PRSH, PLTH, PRTH, PUCL, TLEL, TREL, PTSL, PSTM, PFHO, PSXP, TLWR, TRWR, PMUS, PJTY, PSTY
        self.set_player_integer_field('TLHA', index, 0)
        
        # PPTI will always get 1009, PLPL gets 100, PJER gets a 1, PCMT gets 999, PLHY gets -31, 
        
        # For attributes which have a column in the 'Latest Player Attributes.csv' file, use the value if it differs from 
        # the default value we put in that column. If not, we will use formulas to determine what value to use. 
        
    def create_left_outside_linebacker(self, player_dict, index):
        """ 
        Given a dictionary of a new player and the index of the related record to modify in the DB, performs all of 
        the calculations and updates necessary to create the player as a QB in the DB.
        """
        # For all of the following fields, we simply use 0.
        # TLHA, TRHA, PCPH, PLSH, PRSH, PLTH, PRTH, PUCL, TLEL, TREL, PTSL, PSTM, PFHO, PSXP, TLWR, TRWR, PMUS, PJTY, PSTY
        self.set_player_integer_field('TLHA', index, 0)
        
        # PPTI will always get 1009, PLPL gets 100, PJER gets a 1, PCMT gets 999, PLHY gets -31, 
        
        # For attributes which have a column in the 'Latest Player Attributes.csv' file, use the value if it differs from 
        # the default value we put in that column. If not, we will use formulas to determine what value to use. 
        
    def create_middle_linebacker(self, player_dict, index):
        """ 
        Given a dictionary of a new player and the index of the related record to modify in the DB, performs all of 
        the calculations and updates necessary to create the player as a QB in the DB.
        """
        # For all of the following fields, we simply use 0.
        # TLHA, TRHA, PCPH, PLSH, PRSH, PLTH, PRTH, PUCL, TLEL, TREL, PTSL, PSTM, PFHO, PSXP, TLWR, TRWR, PMUS, PJTY, PSTY
        self.set_player_integer_field('TLHA', index, 0)
        
        # PPTI will always get 1009, PLPL gets 100, PJER gets a 1, PCMT gets 999, PLHY gets -31, 
        
        # For attributes which have a column in the 'Latest Player Attributes.csv' file, use the value if it differs from 
        # the default value we put in that column. If not, we will use formulas to determine what value to use. 
        
    def create_right_outside_linebacker(self, player_dict, index):
        """ 
        Given a dictionary of a new player and the index of the related record to modify in the DB, performs all of 
        the calculations and updates necessary to create the player as a QB in the DB.
        """
        # For all of the following fields, we simply use 0.
        # TLHA, TRHA, PCPH, PLSH, PRSH, PLTH, PRTH, PUCL, TLEL, TREL, PTSL, PSTM, PFHO, PSXP, TLWR, TRWR, PMUS, PJTY, PSTY
        self.set_player_integer_field('TLHA', index, 0)
        
        # PPTI will always get 1009, PLPL gets 100, PJER gets a 1, PCMT gets 999, PLHY gets -31, 
        
        # For attributes which have a column in the 'Latest Player Attributes.csv' file, use the value if it differs from 
        # the default value we put in that column. If not, we will use formulas to determine what value to use. 
        
    def create_cornerback(self, player_dict, index):
        """ 
        Given a dictionary of a new player and the index of the related record to modify in the DB, performs all of 
        the calculations and updates necessary to create the player as a QB in the DB.
        """
        # For all of the following fields, we simply use 0.
        # TLHA, TRHA, PCPH, PLSH, PRSH, PLTH, PRTH, PUCL, TLEL, TREL, PTSL, PSTM, PFHO, PSXP, TLWR, TRWR, PMUS, PJTY, PSTY
        self.set_player_integer_field('TLHA', index, 0)
        
        # PPTI will always get 1009, PLPL gets 100, PJER gets a 1, PCMT gets 999, PLHY gets -31, 
        
        # For attributes which have a column in the 'Latest Player Attributes.csv' file, use the value if it differs from 
        # the default value we put in that column. If not, we will use formulas to determine what value to use. 
        
    def create_free_safety(self, player_dict, index):
        """ 
        Given a dictionary of a new player and the index of the related record to modify in the DB, performs all of 
        the calculations and updates necessary to create the player as a QB in the DB.
        """
        # For all of the following fields, we simply use 0.
        # TLHA, TRHA, PCPH, PLSH, PRSH, PLTH, PRTH, PUCL, TLEL, TREL, PTSL, PSTM, PFHO, PSXP, TLWR, TRWR, PMUS, PJTY, PSTY
        self.set_player_integer_field('TLHA', index, 0)
        
        # PPTI will always get 1009, PLPL gets 100, PJER gets a 1, PCMT gets 999, PLHY gets -31, 
        
        # For attributes which have a column in the 'Latest Player Attributes.csv' file, use the value if it differs from 
        # the default value we put in that column. If not, we will use formulas to determine what value to use. 
        
    def create_strong_safety(self, player_dict, index):
        """ 
        Given a dictionary of a new player and the index of the related record to modify in the DB, performs all of 
        the calculations and updates necessary to create the player as a QB in the DB.
        """
        # For all of the following fields, we simply use 0.
        # TLHA, TRHA, PCPH, PLSH, PRSH, PLTH, PRTH, PUCL, TLEL, TREL, PTSL, PSTM, PFHO, PSXP, TLWR, TRWR, PMUS, PJTY, PSTY
        self.set_player_integer_field('TLHA', index, 0)
        
        # PPTI will always get 1009, PLPL gets 100, PJER gets a 1, PCMT gets 999, PLHY gets -31, 
        
        # For attributes which have a column in the 'Latest Player Attributes.csv' file, use the value if it differs from 
        # the default value we put in that column. If not, we will use formulas to determine what value to use. 
        
    def create_kicker(self, player_dict, index):
        """ 
        Given a dictionary of a new player and the index of the related record to modify in the DB, performs all of 
        the calculations and updates necessary to create the player as a QB in the DB.
        """
        # For all of the following fields, we simply use 0.
        # TLHA, TRHA, PCPH, PLSH, PRSH, PLTH, PRTH, PUCL, TLEL, TREL, PTSL, PSTM, PFHO, PSXP, TLWR, TRWR, PMUS, PJTY, PSTY
        self.set_player_integer_field('TLHA', index, 0)
        
        # PPTI will always get 1009, PLPL gets 100, PJER gets a 1, PCMT gets 999, PLHY gets -31, 
        
        # For attributes which have a column in the 'Latest Player Attributes.csv' file, use the value if it differs from 
        # the default value we put in that column. If not, we will use formulas to determine what value to use. 
        
    def create_punter(self, player_dict, index):
        """ 
        Given a dictionary of a new player and the index of the related record to modify in the DB, performs all of 
        the calculations and updates necessary to create the player as a QB in the DB.
        """
        # For all of the following fields, we simply use 0.
        # TLHA, TRHA, PCPH, PLSH, PRSH, PLTH, PRTH, PUCL, TLEL, TREL, PTSL, PSTM, PFHO, PSXP, TLWR, TRWR, PMUS, PJTY, PSTY
        self.set_player_integer_field('TLHA', index, 0)
        
        # PPTI will always get 1009, PLPL gets 100, PJER gets a 1, PCMT gets 999, PLHY gets -31, 
        
        # For attributes which have a column in the 'Latest Player Attributes.csv' file, use the value if it differs from 
        # the default value we put in that column. If not, we will use formulas to determine what value to use. 
        

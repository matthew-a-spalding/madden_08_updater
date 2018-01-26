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
from numpy import array, random

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
    
    def create_quarterback(self, player_dict, index):
        """
        Given a dictionary of a new player and the index of the related record to modify in the DB, performs all of 
        the calculations and updates necessary to create the player as a QB in the DB.
        """
        # For all of the following fields, we simply use 0.
        # PCPH, PFHO, PJTY, PMPC, PMUS, POPS, PPOS, PSTM, PSTY, PSXP, PTSL, PUCL, TLEL, TLHA, TLWR, TREL, TRHA, TRWR 
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
        
        # For many attributes in 'Latest Player Attributes.csv', we simply use the exact value from the file.
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
        self.set_player_integer_field('PNEK', index, int(player_dict["neck_pad"]))
        self.set_player_integer_field('PSKI', index, int(player_dict["skin_color"]))
        self.set_player_integer_field('PVIS', index, int(player_dict["visor_style"]))
        self.set_player_integer_field('PYRP', index, int(player_dict["years_pro"]))
        # This is correct - we are intentionally setting the years with team to the number of years pro.
        self.set_player_integer_field('PYWT', index, int(player_dict["years_pro"]))
        
        
        # For these next attributes, the calculations involve the value from a column in the player dict.
        
        # The college ID is simply picked from a list.
        self.set_player_integer_field('PCOL', index, self.get_college_id(player_dict["college"]))
        
        # For eye_black, if the CSV says -1, give 80% a 0 (none) and 20% a 1 (black).
        if int(player_dict["eye_black"]) == -1:
            elements = [0, 1]
            weights = [0.8, 0.2]
            eye_black = get_weighted_random(elements, weights)
        else:
            eye_black = int(player_dict["eye_black"])
        self.set_player_integer_field('PEYE', index, eye_black)
        
        # Get the first 11 characters of the first name.
        if len(player_dict["first_name"]) < 12:
            self.set_player_string_field('PFNA', index, player_dict["first_name"])
        else:
            self.set_player_string_field('PFNA', index, player_dict["first_name"][:11])
        
        # The handedness is 0 for right, 1 for left.
        if "RIGHT" in player_dict["handedness"].upper():
            handedness = 0
        else:
            handedness = 1
        self.set_player_integer_field('PHAN', index, handedness)
        
        # For left_elbow, if the CSV says -1, give 85% a 0 (none), 5% a 7 (black wrist), 5% a 8 (white wrist), and 
        # 5% a 9 (team-color wrist).
        if int(player_dict["left_elbow"]) == -1:
            elements = [0, 7, 8, 9]
            weights = [0.85, 0.05, 0.05, 0.05]
            left_elbow = get_weighted_random(elements, weights)
        else:
            left_elbow = int(player_dict["left_elbow"])
        self.set_player_integer_field('PLEL', index, left_elbow)
        
        # For left_hand, if the CSV says -1 and the player's handedness is right, set 70% to 0 (none), 5% to 2 
        # (black glove), 5% to 3 (white glove), 5% to 4 (team-color glove), 5% to 5 (white RB glove), 5% to 6 (black 
        # RB glove), and 5% to 7 (team-color RB glove).
        if int(player_dict["left_hand"]) == -1:
            if handedness == 0:
                elements = [0, 2, 3, 4, 5, 6, 7]
                weights = [0.70, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05]
                left_hand = get_weighted_random(elements, weights)
            else:
                left_hand = 0
        else:
            left_hand = int(player_dict["left_hand"])
        self.set_player_integer_field('PLHA', index, left_hand)
        
        # Get the first 13 characters of the last name.
        if len(player_dict["last_name"]) < 14:
            self.set_player_string_field('PLNA', index, player_dict["last_name"])
        else:
            self.set_player_string_field('PLNA', index, player_dict["last_name"][:13])
        
        # For left_shoe, if the CSV says -1, give 90% a 0 (none) and 10% a 1 (white tape).
        if int(player_dict["left_shoe"]) == -1:
            elements = [0, 1]
            weights = [0.9, 0.1]
            left_shoe = get_weighted_random(elements, weights)
        else:
            left_shoe = int(player_dict["left_shoe"])
        self.set_player_integer_field('PLSH', index, left_shoe)
        
        # For left_knee, if the CSV says -1, always use 0. Otherwise, just use what is in the file.
        if int(player_dict["left_knee"]) == -1:
            left_knee = 0
        else:
            left_knee = int(player_dict["left_knee"])
        self.set_player_integer_field('PLTH', index, left_knee)
        
        # For right_elbow, if the CSV says -1: If the left_elbow was 0, set 85% to 0 (none), 5% to 7 (black wrist), 5% 
        # to 8 (white wrist), and 5% to 9 (team-color wrist). If left_elbow was non-zero, set 80% to the same value, 
        # and 20% to 0. If the CSV value is not -1, just use what is in there.
        if int(player_dict["right_elbow"]) == -1:
            if left_elbow == 0:
                elements = [0, 7, 8, 9]
                weights = [0.85, 0.05, 0.05, 0.05]
                right_elbow = get_weighted_random(elements, weights)
            else:
                elements = [left_elbow, 0]
                weights = [0.80, 0.2]
                right_elbow = get_weighted_random(elements, weights)
        else:
            right_elbow = int(player_dict["right_elbow"])
        self.set_player_integer_field('PREL', index, right_elbow)
        
        # For right_hand, if the CSV says -1 and the player's handedness is left, set 70% to 0 (none), 5% to 2 
        # (black glove), 5% to 3 (white glove), 5% to 4 (team-color glove), 5% to 5 (white RB glove), 5% to 6 (black 
        # RB glove), and 5% to 7 (team-color RB glove).
        if int(player_dict["right_hand"]) == -1:
            if handedness == 1:
                elements = [0, 2, 3, 4, 5, 6, 7]
                weights = [0.70, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05]
                right_hand = get_weighted_random(elements, weights)
            else:
                right_hand = 0
        else:
            right_hand = int(player_dict["right_hand"])
        self.set_player_integer_field('PRHA', index, right_hand)
        
        # For right_shoe, if the CSV says -1, just match it to the left_shoe.
        if int(player_dict["right_shoe"]) == -1:
            right_shoe = left_shoe
        else:
            right_shoe = int(player_dict["right_shoe"])
        self.set_player_integer_field('PRSH', index, right_shoe)
        
        # For right_knee, if the CSV says -1, always use 0. Otherwise, just use what is in the file.
        if int(player_dict["right_knee"]) == -1:
            right_knee = 0
        else:
            right_knee = int(player_dict["right_knee"])
        self.set_player_integer_field('PRTH', index, right_knee)
        
        # Subtract 160 from the players weight, unless he is already under 160.
        if int(player_dict["weight"]) > 159:
            self.set_player_integer_field('PWGT', index, (int(player_dict["weight"]) - 160))
        else:
            self.set_player_integer_field('PWGT', index, 0)
        
        # The team ID is simply picked from a list.
        self.set_player_integer_field('TGID', index, self.get_team_id(player_dict["team"]))
        
        
        # Here is where we set the main attributes used by this position. See the file 'Methods for Setting Field 
        # Values.xlsx' for details on the calculations used.
        
        speed = max(min(int(player_dict["speed"]), 95), 45)
        self.set_player_integer_field('PSPD', index, speed)
        
        strength = max(min(int(player_dict["strength"]), 80), 45)
        self.set_player_integer_field('PSTR', index, strength)
        
        awareness = max(min(int(player_dict["awareness"]), 99), 40)
        self.set_player_integer_field('PAWR', index, awareness)
        
        agility = max(min(int(player_dict["agility"]), 97), 50)
        self.set_player_integer_field('PAGI', index, agility)
        
        acceleration = max(min(int(player_dict["acceleration"]), 95), 40)
        self.set_player_integer_field('PACC', index, acceleration)
        
        carrying = max(min(int(player_dict["carrying"]), 80), 25)
        self.set_player_integer_field('PCAR', index, carrying)
        
        catching = max(min(int(player_dict["catching"]), 85), 15)
        self.set_player_integer_field('PCTH', index, catching)
        
        jumping = max(min(int(player_dict["jumping"]), 95), 40)
        self.set_player_integer_field('PJMP', index, jumping)
        
        break_tackles = max(min(math.ceil(
            (int(player_dict["elusiveness"]) + int(player_dict["trucking"])) / 2
        ), 85), 35)
        self.set_player_integer_field('PBTK', index, break_tackles)
        
        tackle = max(min(int(player_dict["tackle"]), 50), 10)
        self.set_player_integer_field('PTAK', index, tackle)
        
        throw_power = max(min(int(player_dict["throw_power"]), 99), 70)
        self.set_player_integer_field('PTHP', index, throw_power)
        
        throw_accuracy = max(min(math.ceil(
            ((2 * (
                int(player_dict["throw_accuracy_short"]) + 
                int(player_dict["throw_accuracy_mid"]) + 
                int(player_dict["throw_accuracy_deep"]) + 
                int(player_dict["throw_on_the_run"]) + 
                int(player_dict["throw_accuracy"])
            )
             ) - min(
                 int(player_dict["throw_accuracy_short"]), 
                 int(player_dict["throw_accuracy_mid"]), 
                 int(player_dict["throw_accuracy_deep"]), 
                 int(player_dict["throw_on_the_run"]), 
                 int(player_dict["throw_accuracy"])
             )
            ) / 9
        ), 99), 60)
        self.set_player_integer_field('PTHA', index, throw_accuracy)
        
        pass_block = max(min(math.ceil(
            (
                int(player_dict["pass_block"]) + 
                int(player_dict["pass_block_strength"]) + 
                int(player_dict["pass_block_footwork"])
            ) / 3
        ), 60), 5)
        self.set_player_integer_field('PPBK', index, pass_block)
        
        run_block = max(min(math.ceil(
            (
                int(player_dict["run_block"]) + 
                int(player_dict["run_block_strength"]) + 
                int(player_dict["run_block_footwork"])
            ) / 3
        ), 60), 10)
        self.set_player_integer_field('PRBK', index, run_block)
        
        kick_power = max(min(int(player_dict["kick_power"]), 75), 5)
        self.set_player_integer_field('PKPR', index, kick_power)
        
        kick_accuracy = max(min(int(player_dict["kick_accuracy"]), 75), 5)
        self.set_player_integer_field('PKAC', index, kick_accuracy)
        
        kick_return = max(min(int(player_dict["kick_return"]), 60), 5)
        self.set_player_integer_field('PKRT', index, kick_return)
        
        stamina = max(min(int(player_dict["stamina"]), 99), 65)
        self.set_player_integer_field('PSTA', index, stamina)
        
        injury = max(min(int(player_dict["injury"]), 99), 50)
        self.set_player_integer_field('PINJ', index, injury)
        
        toughness = max(min(int(player_dict["toughness"]), 99), 45)
        self.set_player_integer_field('PTGH', index, toughness)
        
        
        # For other attributes, we will use more complicated formulas to determine the values. 
        
        # PCHS: A random distribution from 0 to 30, where the most likely value is 10 and the least likely is 30.
        elements = list(range(0, 31))
        weights = [1, 1, 1, 2, 2, 3, 3, 4, 5, 6, 7, 6, 6, 5, 5, \
                   4, 4, 4, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2, 2]
        
        chest_shelf = get_weighted_random(elements, weights)
        self.set_player_integer_field('PCHS', index, chest_shelf)
        
        # PEGO: A random distribution from 0 to 99, where the most likely value is 85 and the least likely is 0.
        elements = list(range(0, 100))
        weights = [0.03] + [.003]*20 + [.0015]*20 + [.003]*10 + [.02]*10 + [.0125]*20 + [.025]*10 + [.016667]*9
        
        ego = get_weighted_random(elements, weights)
        self.set_player_integer_field('PEGO', index, ego)
        
        # PFAS: A random distribution from 0 to 10, where the most likely value is 0 and the least likely is 10.
        elements = list(range(0, 11))
        weights = [0.24, 0.19, 0.15, 0.11, 0.08, 0.07, 0.06, 0.05, 0.03, 0.01, 0.01]
        
        arm_fat = get_weighted_random(elements, weights)
        self.set_player_integer_field('PFAS', index, arm_fat)
        
        # PFCS: A random distribution from 0 to 15, where the most likely value is 0 and the least likely is 15.
        elements = list(range(0, 16))
        weights = [0.17, 0.15, 0.13, 0.10, 0.08, 0.07, 0.06, 0.05, 0.04, 0.04, 0.03, 0.02, 0.02, 0.02, 0.01, 0.01]
        
        calf_fat = get_weighted_random(elements, weights)
        self.set_player_integer_field('PFCS', index, calf_fat)
        
        # PFGS: A random distribution from 0 to 20, where the most likely value is 5 and the least likely is 20.
        elements = list(range(0, 21))
        weights = [0.04, 0.04, 0.06, 0.08, 0.12, 0.15, 0.12, 0.08, 0.06, 0.04, \
                   0.03, 0.03, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.01, 0.01, 0.01]
        
        glute_fat = get_weighted_random(elements, weights)
        self.set_player_integer_field('PFGS', index, glute_fat)
        
        # PFHS: A random distribution from 0 to 20, where the most likely value is 5 and the least likely is 20.
        elements = list(range(0, 21))
        weights = [0.04, 0.04, 0.06, 0.08, 0.12, 0.15, 0.12, 0.08, 0.06, 0.04, \
                   0.03, 0.03, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.01, 0.01, 0.01]
        
        thigh_fat = get_weighted_random(elements, weights)
        self.set_player_integer_field('PFHS', index, thigh_fat)
        
        
        
        
    def create_halfback(self, player_dict, index):
        """ 
        Given a dictionary of a new player and the index of the related record to modify in the DB, performs all of 
        the calculations and updates necessary to create the player as a HB in the DB.
        """
        # For all of the following fields, we simply use 0: TLHA, TRHA, PCPH, PLSH, PRSH, PLTH, PRTH, PUCL, TLEL, 
        # TREL, PTSL, PSTM, PFHO, PSXP, TLWR, TRWR, PMUS, PJTY, PSTY
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


# ----------------------------------------------------- SECTION 3 -----------------------------------------------------
# ------------------------------------------------- Helper Functions --------------------------------------------------


def get_weighted_random(values_list, weights_list):
    """ Gets a random value from a list of possible values where each value is assigned a weighted probability. """
    weights_array = array(weights_list)
    normalized_weights = weights_array / weights_array.sum()
    return random.choice(values_list, p=normalized_weights)

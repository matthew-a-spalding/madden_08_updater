r"""pipelines.py
    
    This module contains the definition of the pipeline class and its methods. The pipeline is where each item found 
    by the spider during the crawl is processed. Our PlayerPipeline opens a CSV file for writing the player dicts, 
    and closes the file when the spider is closed.
"""
# -*- coding: utf-8 -*-

# Define your item pipelines here.
# Don't forget to add your pipeline to the ITEM_PIPELINES setting;
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import csv, os
from collections import OrderedDict
from datetime import datetime
from scraping.items import NFLPlayer


class PlayerPipeline(object):
    """
        This class is instantiated when the Spider starts its crawl. The spider then hands each item found to this 
        object for further handling. We will just write each item (player dict) to the output file.
    """
    def __init__(self):
        # Figure out the path we will use when placing our output file.
        output_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', r'outputs\step3'))
        # Open the file we will write to, and keep it in our object's scope.
        self.nfl_rosters_file = open(
            os.path.join(
                output_directory, "My {0} Player Attributes - Initial.csv".format(int(datetime.now().year))
            ), "w", newline='')
        # Create our ordered list of field names.
        ordered_fieldnames = OrderedDict(
            [('team', None), ('first_name', None), ('last_name', None), ('position', None), ('awareness', None), 
             ('speed', None), ('acceleration', None), ('agility', None), ('strength', None), ('elusiveness', None), 
             ('carrying', None), ('trucking', None), ('catching', None), ('jumping', None), ('throw_power', None), 
             ('throw_accuracy_short', None), ('throw_accuracy_mid', None), ('throw_accuracy_deep', None), 
             ('throw_on_the_run', None), ('playaction', None), ('pass_block', None), ('run_block', None), 
             ('tackle', None), ('kick_power', None), ('kick_accuracy', None), ('kick_return', None), 
             ('stamina', None), ('injury', None), ('run_block_power', None), ('run_block_finesse', None), 
             ('pass_block_power', None), ('pass_block_finesse', None), ('break_tackle', None), ('toughness', None), 
             ('handedness', None), ('jersey_number', None), ('height', None), ('weight', None), ('age', None), 
             ('birthdate', None), ('years_pro', None), ('college', None), ('draft_round', None), ('draft_pick', None), 
             ('contract_length', None), ('contract_years_left', None), ('total_salary', None), 
             ('signing_bonus', None), ('role_one', None), ('role_two', None), ('pro_bowl', None), ('nfl_icon', None), 
             ('hair_style', None), ('hair_color', None), ('skin_color', None), ('tattoo_left', None), 
             ('tattoo_right', None), ('tendency', None), ('face_id', None), ('sleeves', None), ('left_hand', None), 
             ('right_hand', None), ('left_wrist', None), ('right_wrist', None), ('left_elbow', None), 
             ('right_elbow', None), ('left_knee', None), ('right_knee', None), ('left_shoe', None), 
             ('right_shoe', None), ('neck_pad', None), ('mouthpiece', None), ('breathing_strip', None), 
             ('eye_black', None), ('helmet', None), ('face_mask', None), ('visor', None), ])
        #field_names = NFLPlayer.fields.keys()
        # Create a DictWriter in our object's scope, with the list of field names as the header row.
        self.player_attribute_dict_writer = csv.DictWriter(self.nfl_rosters_file, ordered_fieldnames)
        # Write the header first.
        self.player_attribute_dict_writer.writeheader()
        # We're done here. The rest of the writing will be done per-item in process_item.
    
    def process_item(self, item, spider):
        """
            Called with each item that the Spider processes. We just write each item as a dict to our output file.
        """
        # Write this player item as a dict.
        self.player_attribute_dict_writer.writerow(dict(item))
        # Per the docs here: 
        #    http://doc.scrapy.org/en/latest/topics/item-pipeline.html#process_item 
        # we must either return the item or raise a DropItem execption.
        return item
    
    def spider_closed(self):
        """
            Called when the spider closes. We just need to clean up here.
        """
        self.nfl_rosters_file.close()

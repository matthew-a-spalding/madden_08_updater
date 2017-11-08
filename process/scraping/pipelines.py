# -*- coding: utf-8 -*-

# Define your item pipelines here.
# Don't forget to add your pipeline to the ITEM_PIPELINES setting;
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

# ------------------------------------------------- OLD WAY - To JSON -------------------------------------------------
#import json

#class PlayerPipeline(object):
#    def __init__(self):
        # Open the file we will write to, and keep it in our object's scope.
#        self.jsonfileNFLandFBGDicts = open("NFL and FBG Dicts.json", "wb")
#    
#    def process_item(self, item, spider):
        # Write this player item as a dict, ending in a newline.
#        line = json.dumps(dict(item)) + "\n"
#        self.jsonfileNFLandFBGDicts.write(line)
        # Per the docs here: 
        #    http://doc.scrapy.org/en/latest/topics/item-pipeline.html#process_item 
        # we must either return the item or raise a DropItem execption.
#        return item
#    
#    def spider_closed():
        # Just close the file.
#        self.jsonfileNFLandFBGDicts.close()


# ------------------------------------------------- NEW WAY - To .csv -------------------------------------------------
import csv, os
from scraping.items import NFLPlayer


class PlayerPipeline(object):
    def __init__(self):
        # Figure out the path we will use when placing our output file.
        outputDirectory = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'outputs'))
        # Open the file we will write to, and keep it in our object's scope.
        self.csvNFLRostersFile = open(os.path.join(outputDirectory, "NFL rosters.csv"), "w")
        # Create our list of field names.
        listFieldNames = NFLPlayer.fields.keys()
        # Create a DictWriter in our object's scope, with the list of field names as the header row.
        self.writerPlayerAttributeDicts = csv.DictWriter(self.csvNFLRostersFile, listFieldNames)
        # Write the header first.
        self.writerPlayerAttributeDicts.writeheader()
        # We're done here. The rest of the writing will be done per-item in process_item.
    
    def process_item(self, item, spider):
        # Write this player item as a dict.
        self.writerPlayerAttributeDicts.writerow(dict(item))
        # Per the docs here: 
        #    http://doc.scrapy.org/en/latest/topics/item-pipeline.html#process_item 
        # we must either return the item or raise a DropItem execption.
        return item
    
    def spider_closed():
        # Just close the file.
        self.csvNFLRostersFile.close()

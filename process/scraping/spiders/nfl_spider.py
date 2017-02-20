r""" nfl_spider.py
    
    This script defines the spider class and related helper functions that will perform the actual crawl over the 
    entirety of the NFL team roster pages. It generates a CSV file named 'NFL rosters.csv' listing all current NFL 
    players, with their biographic and salary data.
    
"""

# TODO: Go through this code and make sure that we are assigning class, function, and variable names according to 
# generally accepted Pythonic conventions; be consistent in the use of CamelCase for class names, ALL_CAPS for 
# constants, and underscore_joined_names for functions and variables.

# ----------------------------------------------------- SECTION 1 -----------------------------------------------------
# ----------------------------------------- IMPORTS, SETTINGS, AND CONSTANTS ------------------------------------------
# 1 - Standard library imports
import logging
import re, math
#import urlparse
#from urlparse import urljoin

# 2 - Third-party imports
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

# 3 - Application-specific imports
from scraping import settings
from scraping.items import NFLPlayer

# 4 - Global settings


# 5 - Global constants


# ----------------------------------------------------- SECTION 2 -----------------------------------------------------
# ------------------------------------------------ Class Declarations -------------------------------------------------
class NFLSpider(CrawlSpider):
    
    name = "nfl_rosters"
    # The main variables are class-scoped variables, NOT instance variables. Thus, trying to set them (as I originally 
    # tried) by using self.[var_name] will NOT work. Now, I'm doing it the proper way, using 
    # [ClassName].[variable_name], as seen below.
    
    def __init__(self, **kwargs):
        
        # First, get the NFL_ROSTER_LINK_TEMPLATE from the settings module.
        nfl_roster_link_template = settings.NFL_ROSTER_LINK_TEMPLATE
        # Make the list we will populate with all the NFL.com team roster page URLs.
        nfl_roster_urls = []
        
        # Enumerate the items (dictionaries) in the list of NFL team dicts.
        for index, dictTeamInfo in enumerate(settings.NFL_TEAMS):
            # Put a new copy of the URL template for this team into the list.
            nfl_roster_urls.append(nfl_roster_link_template)
            # Iterate over the keys and values in the current team dict.
            for placeholder, value in dictTeamInfo.iteritems():
                # Replace any instances of the current key (placeholder) with the related value from the team's dict.
                nfl_roster_urls[index] = nfl_roster_urls[index].replace(placeholder, value)
        
        # Now we can set the start_urls class variable to our populated list of NFL.com team roster URLs.
        NFLSpider.start_urls = nfl_roster_urls
        # eg. ["http://www.nfl.com/teams/philadelphiaeagles/roster?team=phi"]
        
        # Set our allowed domains to make sure we can visit pages on NFL.com.
        NFLSpider.allowed_domains = ["nfl.com"]
        
        # Pass in the filtering regex using allow=() and/or restrict_xpaths=() to get the links for each player 
        # profile page, per documentation at http://doc.scrapy.org/en/latest/topics/link-extractors.html
        NFLSpider.rules = [Rule(
                LinkExtractor(allow=(settings.NFL_PROFILE_LINKS_REGEX, )), 
                callback="parse_NFL_profile_page"
                )]
        #logging.warning("NFLSpider initialized with start_urls = %s, 
        #       \n allow_rule = %s" % 
        #       (nfl_roster_urls, settings.NFL_PROFILE_LINKS_REGEX))
        
        # The only thing left to do is call the parent constructor.
        super(NFLSpider, self).__init__(**kwargs)
    
    
    def parse_NFL_profile_page(self, response):
        #logging.warning("Player profile page url: %s" % response.url)
        
        # Create a new item for this player.
        item = NFLPlayer()
        
    # CHECK AND UPDATE THIS WHOLE SECTION EACH YEAR AS NECESSARY.
    # Make sure the xpath expressions below can be used to find our text in the source of any player profile page.
        
        # Start by populating the team field.
        item["team"] = response.xpath(
                "//div[@class=\"article-decorator\"]/h1/a/text()"
                ).extract()[0] # eg. "Indianapolis Colts"
        
        # Next up is the player's first and last name.
        full_name = response.xpath(
                "//meta[@id=\"playerName\"]/@content"
                ).extract()[0].split(None, 1) # eg. ["Andrew", "Luck"]
        
    # TODO: Test putting a comma into the name fields for a player, and see if it gets escaped or whatnot. See how the 
    # "NFL rosters.csv" file we generate in the PlayerPipeline gets read in later when there is a commma in a field. 
    # If the comma gets into the .csv as is, we will probably just need to make sure these fields don't get populated 
    # with any commas in them. Fields that are most likely to be affected include first_name, last_name, and college. 
        
        item["first_name"] = full_name[0] # eg. "Andrew"
        item["last_name"] = full_name[1] # eg. "Luck"
        
        # Find the player's jersey number and position. If jersey number is empty, there must still be a '#' for this 
        # split to work.
        number_and_position = response.xpath(
                "//span[@class=\"player-number\"]/text()"
                ).extract()[0].split(None, 1) # eg. ["#12", "QB"]
        #logging.warning("number_and_position = %s" % number_and_position)
        
        # The [1:] below gets only the chars from position 1 to the end of the string (string char indices start at 0).
        item["jersey_number"] = number_and_position[0][1:] # eg. "12"
        item["position"] = number_and_position[1] # eg. "QB"
        
        # All of the remaining NFL.com info (height, weight, age, college, and experience) is found in the div with 
        # class="player-info". However, some players may be missing their birth / age info, which changes how we 
        # handle that div's contents. First, see if there are 7 or only 5 /p/strong tags in the player-info div.
        player_info_p_strong_tags = response.xpath("//div[@class=\"player-info\"]/p/strong/text()").extract()
        #logging.warning("player_info_p_tags = %s" % player_info_p_tags)
        
        if len(player_info_p_strong_tags) == 7:
            # The text() inside the third <p> tag in the <div class="player-info"> tag, which contains the height, 
            # weight, and age, also has a lot of whitespace chars, some of which are grouped into the first string by 
            # themselves, which is why the first string with real content (the height) is found at ...extract()[1], 
            # not ...extract()[0].
            height_weight_age_strings = response.xpath("//div[@class=\"player-info\"]/p[3]/text()").extract() #a list 
                # of 4 strings, eg. [u'\r\n\t\t\t\t\t', u': 6-4 \xa0 \r\n\t\t\t\t\t', 
                # u': 240 \xa0 \r\n\t [...] \t\t\t', u': 25\r\n\t\t\t\t\t\t\r\n\t\t\t\t\t\r\n\t\t\t\t']
            #logging.warning("height_weight_age_strings = %s" % 
            #height_weight_age_strings)
            
            height_strings = height_weight_age_strings[1].split()
            # eg. [":", "6-4"]
            weight_strings = height_weight_age_strings[2].split()
            # eg. [":", "240"]
            age_strings = height_weight_age_strings[3].split()
            # eg. [":", "25"]
            #logging.warning("height_strings = %s" % height_strings)
            #logging.warning("weight_strings = %s" % weight_strings)
            #logging.warning("age_strings = %s" % age_strings)
            
            item["height"] = height_strings[1] # eg. "6-4"
            item["weight"] = weight_strings[1] # eg. "240"
            item["age"] = age_strings[1] # eg. "25"
            
            # Get the player's college. This currently yields "No College" if the NFL.com page doesn't have that info.
            college_strings = response.xpath("//div[@class=\"player-info\"]/p[5]/text()").extract()[0].split(None, 1) 
            # eg. [u":", u"Stanford"]
            #logging.warning("college_strings = %s" % college_strings)
            item["college"] = college_strings[1] # eg. "Stanford"
            
            # Get the player's number of years of experience.
            experience_strings = response.xpath("//div[@class=\"player-info\"]/p[6]/text()"
                ).extract()[0].split(None, 1)
            # eg. [u':', u'Rookie '] or [u':', u'3rd season ']
            #logging.warning("experience_strings = %s" % experience_strings)
            
            if "ROOKIE" in experience_strings[1].upper():
                item["experience"] = "0"
            else:
                # Need to match the numeric chars at the start of the string.
                srematchObject = re.match("\d+", experience_strings[1])
                # eg. <_sre.SRE_Match object at 0x032D8100>
                #logging.warning("srematchObject = %s" % srematchObject)
                item["experience"] = srematchObject.group(0) # eg. "3"
            
        elif len(player_info_p_strong_tags) == 5:
            # The age info is missing, and we have no birth date <p> either.
            #logging.warning("Check the tags in the \"player-info\" div for this url:")
            #logging.warning(response.url)
            
            # For height, weight, and age, the text() inside the third <p> tag in the <div class="player-info"> tag 
            # has a lot of whitespace chars, some of which are grouped into the first string by themselves, which is 
            # why the first string with real content (for height) is found at ...extract()[1], not ...extract()[0].
            height_weight_strings = response.xpath("//div[@class=\"player-info\"]/p[3]/text()").extract() 
            # a list of 3 strings, 
            # eg. [u'\r\n\t\t\t\t\t', u': 6-6 \xa0 \r\n\t\t\t\t\t', 
            # u': 255 \xa0 \r\n\t\t\t\t\t\r\n\t\t\t\t\t\t\r\n\t\t\t\t\t\t\r\n\t\t\t\t\t\r\n\t\t\t\t']
            #logging.warning("height_weight_strings = %s" % height_weight_strings)
            
            height_strings = height_weight_strings[1].split() # eg. [":", "6-6"]
            weight_strings = height_weight_strings[2].split() # eg. [":", "255"]
            #logging.warning("height_strings = %s" % height_strings)
            #logging.warning("weight_strings = %s" % weight_strings)
            
            item["height"] = height_strings[1] # eg. "6-6"
            item["weight"] = weight_strings[1] # eg. "255"
            
            # Get the player's college. The NFL.com pages currently say "No College" when they don't have that info.
            college_strings = response.xpath("//div[@class=\"player-info\"]/p[4]/text()").extract()[0].split(None, 1) 
            # eg. [u":", u"Stanford"]
            #logging.warning("college_strings = %s" % college_strings)
            item["college"] = college_strings[1] # eg. "Stanford"
            
            # Get the player's number of years of experience.
            experience_strings = response.xpath("//div[@class=\"player-info\"]/p[5]/text()"
                ).extract()[0].split(None, 1) # eg. [u':', u'Rookie '] or [u':', u'3rd season ']
            #logging.warning("experience_strings = %s" % experience_strings)
            
            if "ROOKIE" in experience_strings[1].upper():
                item["experience"] = "0"
            else:
                # Need to match the numeric chars at the start of the string.
                srematchObject = re.match("\d+", experience_strings[1]) # eg. <_sre.SRE_Match object at 0x032D8100>
                #logging.warning("srematchObject = %s" % srematchObject)
                item["experience"] = srematchObject.group(0) # eg. "3"
        else:
            # We have yet another configuration, which we should investigate.
            logging.error("Found an NFL player profile page where len(player_info_p_strong_tags) == %d, "
                "which we have not seen before. " % len(player_info_p_strong_tags))
            logging.error("Check the tags in the \"player-info\" div for this url:")
            logging.error(response.url)
        
        return item


# ----------------------------------------------------- SECTION 3 -----------------------------------------------------
# ------------------------------------------------- Helper Functions --------------------------------------------------


# ----------------------------------------------------- SECTION 4 -----------------------------------------------------
# -------------------------------------------------- Main Function ----------------------------------------------------

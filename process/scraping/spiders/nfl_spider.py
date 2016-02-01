r""" nfl_spider.py
    
    This script crawls the entirety of the NFL team roster pages and the 
    related FBGRatings.com player pages and generates a CSV file named 
    'NFL and FBG.csv' containing the full list of current NFL players and their 
    biographic and salary data.
    
"""

# TODO: Go through this code and make sure that we are assigning class, 
# function, and variable names according to generally accepted Pythonic 
# conventions; be consistent in the use of CamelCase for class names, ALL_CAPS 
# for constants, and underscore_joined_names for functions and variables.

# --------------------------------- SECTION 1 ---------------------------------
# --------------------- IMPORTS, SETTINGS, AND CONSTANTS ----------------------
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


# --------------------------------- SECTION 2 ---------------------------------
# ---------------------------- Class Declarations -----------------------------
class NFLandFBGSpider(CrawlSpider):
    
    name = "nfl_and_fbg"
    # The main variables are class-scoped variables, NOT instance variables.
    # Thus, trying to set them (as I originally did) by using self.[var_name] 
    # will NOT work. Now, I'm doing it the proper way, using 
    # [ClassName].[variable_name], as seen below.
    
    def __init__(self, **kwargs):
        
        # First, get the NFL_ROSTER_LINK_TEMPLATE from the settings module.
        nfl_roster_link_template = settings.NFL_ROSTER_LINK_TEMPLATE
        # List we will populate with all the NFL.com team roster page URLs.
        nfl_roster_urls = []
        
        # Enumerate the items (dictionaries) in the list of NFL team dicts.
        for index, dictTeamInfo in enumerate(settings.NFL_TEAMS):
            # Put a new copy of the URL template for this team into the list.
            nfl_roster_urls.append(nfl_roster_link_template)
            # Iterate over the keys and values in the current team dict.
            for placeholder, value in dictTeamInfo.iteritems():
                # Replace any instances of the current key (placeholder) with 
                # the related value from the team's dict.
                nfl_roster_urls[index] = nfl_roster_urls[index].replace(
                        placeholder, value)
        
        # Now we can set the start_urls class variable to our populated list of 
        # NFL.com team roster URLs.
        NFLandFBGSpider.start_urls = nfl_roster_urls
        # eg. ["http://www.nfl.com/teams/philadelphiaeagles/roster?team=phi"]
        
        # Set our allowed domains to make sure we can visit pages on both 
        # NFL.com and FBGRatings.com.
        NFLandFBGSpider.allowed_domains = ["nfl.com", "fbgratings.com"]
        
        # Pass in the filtering regex using allow=() and/or restrict_xpaths=() 
        # to get the links for each player profile page, per documentation at 
        # http://doc.scrapy.org/en/latest/topics/link-extractors.html
        #       #module-scrapy.linkextractors.lxmlhtml
        NFLandFBGSpider.rules = [Rule(
                LinkExtractor(
                        allow=(settings.NFL_PROFILE_LINKS_REGEX, )
                        ), 
                callback="parse_NFL_profile_page")]
        #logging.warning("NFLandFBGSpider initialized with start_urls = %s, 
        #       \n allow_rule = %s" % 
        #       (nfl_roster_urls, settings.NFL_PROFILE_LINKS_REGEX))
        
        # We've now initialized the spider class with our values, so the only 
        # thing left to do is call the parent constructor.
        super(NFLandFBGSpider, self).__init__(**kwargs)
    
    
    def parse_NFL_profile_page(self, response):
        #logging.warning("Player profile page url: %s" % response.url)
        
        # Create a new item for this player.
        item = NFLPlayer()
        
    # CHECK AND UPDATE THIS WHOLE SECTION EACH YEAR AS NECESSARY.
    # Make sure that the xpath expressions below can be used to find the 
    # expected text in the source of any player profile page.
        
        # Start by populating the team field.
        item["team"] = response.xpath(
                "//div[@class=\"article-decorator\"]/h1/a/text()").extract()[0]
        # eg. "Indianapolis Colts"
        
        # Next up is the player's first and last name.
        full_name = response.xpath(
                "//meta[@id=\"playerName\"]/@content").extract()[0].split(
                        None, 1)
        # eg. ["Andrew", "Luck"]
        
    # TODO: Test putting a comma into the name fields for a player, and see if it gets escaped or 
    # whatnot. See how the "NFL and FBG.csv" file we generate in the PlayerPipeline gets read in 
    # later when there is a commma in a field. If the comma gets into the .csv as is, we will 
    # probably just need to make sure these fields don't get populated with any commas in them. 
    # Fields that are most likely to be affected include first_name, last_name, and college. 
        
        item["first_name"] = full_name[0] # eg. "Andrew"
        item["last_name"] = full_name[1] # eg. "Luck"
        
        # Find the player's jersey number and position. If jersey number is empty, there must still be a '#' for this split to work.
        number_and_position = response.xpath("//span[@class=\"player-number\"]/text()").extract()[0].split(None, 1) # eg. ["#12", "QB"]
        #logging.warning("number_and_position = %s" % number_and_position)
        # The [1:] below takes only the chars from position 1 to the end of the string (string char indices start with 0).
        item["jersey_number"] = number_and_position[0][1:] # eg. "12"
        item["position"] = number_and_position[1] # eg. "QB"
        
        # All of the remaining NFL.com info (height, weight, age, college, and experience) is found in the div with class="player-info".
        # However, some players may be missing their birth / age info, which changes how we handle that div's contents.
        # First, check to see if there are 7 or only 5 /p/strong tags in the player-info div.
        player_info_p_strong_tags = response.xpath("//div[@class=\"player-info\"]/p/strong/text()").extract()
        #logging.warning("player_info_p_tags = %s" % player_info_p_tags)
        
        if len(player_info_p_strong_tags) == 7:
            # We should have the age as the fourth string in the list of p[3]'s contents.
            
            # For height, weight, and age, the text() inside the third <p> tag in the <div class="player-info"> tag has a lot of whitespace chars, 
            # some of which are grouped into the first string by themselves, which is why the first string with real content (for the height) is 
            # found at ...extract()[1], not ...extract()[0].
            height_weight_age_strings = response.xpath("//div[@class=\"player-info\"]/p[3]/text()").extract() # a list of 4 strings, 
            # eg. [u'\r\n\t\t\t\t\t', u': 6-4 \xa0 \r\n\t\t\t\t\t', u': 240 \xa0 \r\n\t\t\t\t\t\r\n\t\t\t\t\t\t\r\n\t\t\t\t\t\t\r\n\t\t\t\t\t\t\t', 
            #    u': 25\r\n\t\t\t\t\t\t\r\n\t\t\t\t\t\r\n\t\t\t\t']
            #logging.warning("height_weight_age_strings = %s" % height_weight_age_strings)
            height_strings = height_weight_age_strings[1].split() # eg. [":", "6-4"]
            weight_strings = height_weight_age_strings[2].split() # eg. [":", "240"]
            age_strings = height_weight_age_strings[3].split() # eg. [":", "25"]
            #logging.warning("height_strings = %s" % height_strings)
            #logging.warning("weight_strings = %s" % weight_strings)
            #logging.warning("age_strings = %s" % age_strings)
            item["height"] = height_strings[1] # eg. "6-4"
            item["weight"] = weight_strings[1] # eg. "240"
            item["age"] = age_strings[1] # eg. "25"
            
            # Get the player's college. This currently yields "No College" if the NFL.com page doesn't have that info.
            college_strings = response.xpath("//div[@class=\"player-info\"]/p[5]/text()").extract()[0].split(None, 1) # eg. [u":", u"Stanford"]
            #logging.warning("college_strings = %s" % college_strings)
            item["college"] = college_strings[1] # eg. "Stanford"
            
            # Get the player's number of years of experience.
            experience_strings = response.xpath("//div[@class=\"player-info\"]/p[6]/text()").extract()[0].split(None, 1) # eg. [u':', u'Rookie '] or [u':', u'3rd season ']
            #logging.warning("experience_strings = %s" % experience_strings)
            if "ROOKIE" in experience_strings[1].upper():
                item["experience"] = "0"
            else:
                # Need to match the numeric chars at the start of the string.
                srematchObject = re.match("\d+", experience_strings[1]) # eg. <_sre.SRE_Match object at 0x032D8100>
                #logging.warning("srematchObject = %s" % srematchObject)
                item["experience"] = srematchObject.group(0) # eg. "3"
            
        elif len(player_info_p_strong_tags) == 5:
            # The age info is missing, and we have no birth date <p> either.
            #logging.warning("Check the tags in the \"player-info\" div for this url:")
            #logging.warning(response.url)
            # For height, weight, and age, the text() inside the third <p> tag in the <div class="player-info"> tag has a lot of whitespace chars, 
            # some of which are grouped into the first string by themselves, which is why the first string with real content (for the height) is 
            # found at ...extract()[1], not ...extract()[0].
            height_weight_strings = response.xpath("//div[@class=\"player-info\"]/p[3]/text()").extract() # a list of 3 strings, 
            # eg. [u'\r\n\t\t\t\t\t', u': 6-6 \xa0 \r\n\t\t\t\t\t', u': 255 \xa0 \r\n\t\t\t\t\t\r\n\t\t\t\t\t\t\r\n\t\t\t\t\t\t\r\n\t\t\t\t\t\r\n\t\t\t\t'
            #logging.warning("height_weight_strings = %s" % height_weight_strings)
            height_strings = height_weight_strings[1].split() # eg. [":", "6-4"]
            weight_strings = height_weight_strings[2].split() # eg. [":", "240"]
            #logging.warning("height_strings = %s" % height_strings)
            #logging.warning("weight_strings = %s" % weight_strings)
            item["height"] = height_strings[1] # eg. "6-4"
            item["weight"] = weight_strings[1] # eg. "240"
            
            # Get the player's college. The NFL.com pages currently say "No College" when they don't have that info.
            college_strings = response.xpath("//div[@class=\"player-info\"]/p[4]/text()").extract()[0].split(None, 1) # eg. [u":", u"Stanford"]
            #logging.warning("college_strings = %s" % college_strings)
            item["college"] = college_strings[1] # eg. "Stanford"
            
            # Get the player's number of years of experience.
            experience_strings = response.xpath("//div[@class=\"player-info\"]/p[5]/text()").extract()[0].split(None, 1) # eg. [u':', u'Rookie '] or [u':', u'3rd season ']
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
            logging.error("Found an NFL player profile page where len(player_info_p_strong_tags) == %d, which we have not seen before. " % len(player_info_p_strong_tags))
            logging.error("Check the tags in the \"player-info\" div for this url:")
            logging.error(response.url)
    
# UPDATED 2016_02_01: This next section which originally made the 
# subsequent request to the FBG team roster page has been removed, since 
# the FBG site is now locked down by login. When I can once again reach the 
# individual player ratings pages, I will attempt to alter and re-introduce 
# those portions of the code.
        
        # Now we need to create the FBG team roster page url from the template and this player's team.
    # TODO: Check that the team names found above at NFL.com ALWAYS work in the FBGRatings URL template, then fill in and indent the line below.
    # NOTE: I have confirmed that, as of 2015_XX_XX, the FBGRatings pages all work with the team nicknames as found at NFL.com.
    #    fbg_roster_url = settings.FBG_ROSTER_LINK_TEMPLATE.replace("[NICKNAME]", item["team"].rsplit(None, 1)[1])
        #logging.warning("fbg_roster_url = %s" % fbg_roster_url)
        # NOTE: The 'dont_filter=True' on the line below is CRITICAL, as omitting it will mean the spider only hits 
        # the main FBG Roster pages once apiece, due to it's default filtering rules preventing duplicates.
    #    fbg_roster_request = scrapy.Request(fbg_roster_url, callback=self.find_FBG_ratings_page, dont_filter=True)
    #    fbg_roster_request.meta["item"] = item
    #    return fbg_roster_request
        
        return item
    
    
    def find_FBG_ratings_page(self, response):
        #logging.warning("Inside find_FBG_ratings_page.")
        item = response.meta["item"]
        # First, parse the FBG_RATINGS_LINK_TEMPLATE to get the pattern we are going to look for in the roster page.
        # (We're using a pattern in case there is something in the middle of the names, like the Jr. in "Fields, Jr., Carlos")
        regexPattern = settings.FBG_RATINGS_LINK_TEMPLATE.replace("[LAST_NAME]", item["last_name"])
        regexPattern = regexPattern.replace("[FIRST_NAME]", item["first_name"])
        # If we can't find text that matches the pattern in an anchor tag, ...
        if not response.xpath("//a/text()").re(regexPattern):
            # ... then try matching the last name and the first initial. (This should work for players like Jeremiah/Jay Ratliff, Bears DT.)
            regexPattern = settings.FBG_RATINGS_LINK_TEMPLATE.replace("[LAST_NAME]", item["last_name"])
            regexPattern = regexPattern.replace("[FIRST_NAME]", item["first_name"][0])
            # If we still can't find a match, ... we're screwed.
            if not response.xpath("//a/text()").re(regexPattern):
                logging.error("Unable to find link for %s %s. Skipping FBG player ratings page." % (item["first_name"], item["last_name"]))
                # Before we return the item (to the pipeline for writing to the file), make sure we get either a Madden position or a TBD.
                item["position"] = choose_best_position(item["position"], item["position"])
                return item
            else:
                # We found a player with the same last name and same first letter of the first name.
                player_link_text = response.xpath("//a/text()").re(regexPattern)[0]
                position_xpath = "//a[contains(text(),\"" + player_link_text + "\")]/parent::*/following-sibling::*/text()"
                # See if the positions given by NFL.com and FBGRatings.com are similar enough that the match is likely.
                if positions_are_similar(item["position"], response.xpath(position_xpath).extract()[0]):
                    logging.warning("Using likely match for NFL.com's %s %s, %s %s;" % (item["first_name"], item["last_name"], item["team"], item["position"]))
                    logging.warning("FBGRatings.com player_link_text: %s ;" % (player_link_text))
                    logging.warning("FBGRatings.com position: %s ." % (response.xpath(position_xpath).extract()[0]))
                    # The positions match or are similar enough, so finalize the xpath we will use to get the URL for this player.
                    player_link_xpath = "//a[contains(text(),\"" + player_link_text + "\")]/@href"
                    player_ratings_url = response.urljoin(response.xpath(player_link_xpath).extract()[0]) # eg. "http://www.fbgratings.com/members/profile.php?pyid=54794"
                    logging.warning("player_ratings_url for %s %s, %s %s was: %s." % (item["first_name"], item["last_name"], item["team"], item["position"], player_ratings_url))
                    player_ratings_request = scrapy.Request(player_ratings_url, callback=self.parse_FBG_ratings_page)
                    player_ratings_request.meta["item"] = item
                    return player_ratings_request
                else:
                    # Skipping the rest of this player's info, as FBG had a different position for the player with a similar name.
                    logging.error("Found partial name match, but not position match for %s %s, %s %s. (FBG player was %s)." % (item["first_name"], item["last_name"], item["team"], item["position"], response.xpath(position_xpath).extract()[0]))
                    logging.error("Skipping FBG player ratings page.")
                    # Before we return the item (to the pipeline for writing to the file), make sure we get either a Madden position or a TBD.
                    item["position"] = choose_best_position(item["position"], item["position"])
                    return item
        else:
            # We found text that matches the pattern. Now use the string the regex matches as the value that the anchor tag's text must contain.
            #logging.warning("response.xpath(\"//a/text()\").re(regexPattern)[0] = %s" % response.xpath("//a/text()").re(regexPattern)[0])
            player_link_text = response.xpath("//a/text()").re(regexPattern)[0] # eg. 
            player_link_xpath = "//a[contains(text(),\"" + player_link_text + "\")]/@href"
            player_ratings_url = response.urljoin(response.xpath(player_link_xpath).extract()[0]) # eg. "http://www.fbgratings.com/members/profile.php?pyid=54794"
            #logging.warning("player_ratings_url = %s" % player_ratings_url)
            player_ratings_request = scrapy.Request(player_ratings_url, callback=self.parse_FBG_ratings_page)
            player_ratings_request.meta["item"] = item
            return player_ratings_request
            
    def parse_FBG_ratings_page(self, response):
        #logging.warning("Inside parse_FBG_ratings_page.")
        item = response.meta["item"]
        # Now to grab the info and ratings for this player.
        
    # TODO: If the player's jersey number has an empty string (was not on NFL.com), see if we can find it on FBGRatings.com.
    # Just be aware that FBGRatings tends to use 0 when they don't know the number. So, check for non-zero ones only.
        
        # Find the position that FBG assigns. This will be used in combination with the one from NFL.com in figuring out which Madden position to give the player.
        player_position_node = response.xpath("//strong[contains(translate(text(), 'POSITION', 'position'),\"position:\")][1]/following-sibling::font[1]/text()").extract() # eg. [u' LT ']
        #logging.warning("player_position_node = %s" % player_position_node)
        if player_position_node:
            player_position_text = response.xpath("//strong[contains(translate(text(), 'POSITION', 'position'),\"position:\")]/following-sibling::font/text()").extract()[0].strip() # eg. LT
            #logging.warning("player_position_text = %s" % player_position_text)
            # Call our function that chooses the best position for the player using the two versions given by NFL.com and FBGRatings.com.
            item["position"] = choose_best_position(item["position"], player_position_text)
            #logging.warning("item[\"position\"] = %s" % item["position"])
        
# NOTE: The attributes have all been commented out here AND in items.py because the FBG ratings pages are all empty right now. 
# TODO: Wait until they are re-populated and then uncomment these next three sections and the fields in items.py. They *might* work properly, or might need updating.
        
#        item["speed"] = response.xpath("//td/strong[contains(translate(text(), 'SPEED', 'speed'),\"speed:\")]/parent::*/following-sibling::*/text()").extract()[0].split()[0] # eg. "81"
#        item["strength"] = response.xpath("//td/strong[contains(translate(text(), 'STRENGTH', 'strength'),\"strength:\")]/parent::*/following-sibling::*/text()").extract()[0].split()[0] # eg. "33"
#        item["awareness"] = response.xpath("//td/strong[contains(translate(text(), 'AWARENESS', 'awareness'),\"awareness:\")]/parent::*/following-sibling::*/text()").extract()[0].split()[0] # eg. "75"
#        item["agility"] = response.xpath("//td/strong[contains(translate(text(), 'AGILITY', 'agility'),\"agility:\")]/parent::*/following-sibling::*/text()").extract()[0].split()[0] # eg. "80"
#        item["acceleration"] = response.xpath("//td/strong[contains(translate(text(), 'ACCELERATION', 'acceleration'),\"acceleration:\")]/parent::*/following-sibling::*/text()").extract()[0].split()[0] # eg. "72"
#        item["catching"] = response.xpath("//td/strong[contains(translate(text(), 'CATCHING', 'catching'),\"catching:\")]/parent::*/following-sibling::*/text()").extract()[0].split()[0] # eg. "48"
#        item["carrying"] = response.xpath("//td/strong[contains(translate(text(), 'CARRYING', 'carrying'),\"carrying:\")]/parent::*/following-sibling::*/text()").extract()[0].split()[0] # eg. "68"
#        item["jumping"] = response.xpath("//td/strong[contains(translate(text(), 'JUMPING', 'jumping'),\"jumping:\")]/parent::*/following-sibling::*/text()").extract()[0].split()[0] # eg. "72"
#        item["break_tackle"] = response.xpath("//td/strong[contains(translate(text(), 'TRUCKING', 'trucking'),\"trucking:\")]/parent::*/following-sibling::*/text()").extract()[0].split()[0] # eg. "48"
#        item["tackling"] = response.xpath("//td/strong[contains(translate(text(), 'TACKLING', 'tackling'),\"tackling:\")]/parent::*/following-sibling::*/text()").extract()[0].split()[0] # eg. "38"
#        item["throwing_power"] = response.xpath("//td/strong[contains(translate(text(), 'THROWING POWER', 'throwing power'),\"throwing power:\")]/parent::*/following-sibling::*/text()").extract()[0].split()[0] # eg. "89"
        
        # Scrape all three throwing accuracy ratings from FBG.
    # ---- OLD WAY ----
        #throwing_accuracy_strings = response.xpath("//td/strong[contains(text(),\"Throwing Accuracy\")]/parent::*/following-sibling::*/text()").extract() # eg. "[u'\xa0\xa087', u'\xa0\xa087', u'\xa0\xa083']"
        #sum_throwing_accuracy_ratings = 0
        #for index, accuracy_string in enumerate(throwing_accuracy_strings):
        #    rating = int(accuracy_string.split()[0]) # eg. 87
        #    sum_throwing_accuracy_ratings += rating
        #item["throwing_accuracy"] = str(int(math.ceil(sum_throwing_accuracy_ratings / 3.0))) # eg. "86"
        
    # ---- NEW WAY ----
    # TODO: CHECK THAT THIS FIX REFLECTS THE TEXT FOUND ON fbgratings.com ('Throwing Accuracy ...' is now 'THROW ACCURACY ...' ?? ).
#        item["throwing_accuracy_short"] = response.xpath("//td/strong[contains(translate(text(), 'THROW ACCURACY SHORT', 'throw accuracy short'),\"throw accuracy short\")]/parent::*/following-sibling::*/text()").extract()[0].split()[0] # eg. "87" ???
#        item["throwing_accuracy_medium"] = response.xpath("//td/strong[contains(translate(text(), 'THROW ACCURACY MEDIUM', 'throw accuracy medium'),\"throw accuracy medium\")]/parent::*/following-sibling::*/text()").extract()[0].split()[0] # eg. "87" ???
#        item["throwing_accuracy_deep"] = response.xpath("//td/strong[contains(translate(text(), 'THROW ACCURACY DEEP', 'throw accuracy deep'),\"throw accuracy deep\")]/parent::*/following-sibling::*/text()").extract()[0].split()[0] # eg. "87" ???

# TODO: Change this (and add the necessary fields in items.py) to grab the blocking strength and footwork ratings in addition to the overall blocking ratings.
        
        # These next two ratings are also areas where we could use some sort of formula to determine the value, 
        # since there are not only Pass Blocking and Run Blocking ratings at FBG, but also [Pass/Run Block] Strength and Footwork ratings.
        # If I can figure out a good formula to use, then it should be just as easy as getting the throwing_accuracy rating, like so:
        #pass_blocking_strings = response.xpath("//td/strong[contains(text(),\"Pass Block\")]/parent::*/following-sibling::*/text()").extract() # eg. "[u'\xa0\xa029', u'\xa0\xa030', u'\xa0\xa029']"
        #sum_pass_blocking_ratings = 0
        #for index, blocking_string in enumerate(pass_blocking_strings):
        #    rating = int(blocking_string.split()[0]) # eg. 30
        #    sum_pass_blocking_ratings += rating
        #item["pass_blocking"] = str(int(math.ceil(sum_pass_blocking_ratings / 3.0))) # eg. "30"
        
#        item["pass_blocking"] = response.xpath("//td/strong[contains(translate(text(), 'PASS BLOCKING', 'pass blocking'),\"pass blocking:\")]/parent::*/following-sibling::*/text()").extract()[0].split()[0] # eg. "29"
#        item["run_blocking"] = response.xpath("//td/strong[contains(translate(text(), 'RUN BLOCKING', 'run blocking'),\"run blocking:\")]/parent::*/following-sibling::*/text()").extract()[0].split()[0] # eg. "25"
#        item["kicking_power"] = response.xpath("//td/strong[contains(translate(text(), 'KICKING POWER', 'kicking power'),\"kicking power:\")]/parent::*/following-sibling::*/text()").extract()[0].split()[0] # eg. "20"
#        item["kicking_accuracy"] = response.xpath("//td/strong[contains(translate(text(), 'KICKING ACCURACY', 'kicking accuracy'),\"kicking accuracy:\")]/parent::*/following-sibling::*/text()").extract()[0].split()[0] # eg. "20"
#        item["kick_returns"] = response.xpath("//td/strong[contains(translate(text(), 'KICK RETURN', 'kick return'),\"kick return:\")]/parent::*/following-sibling::*/text()").extract()[0].split()[0] # eg. "16"
#        item["stamina"] = response.xpath("//td/strong[contains(translate(text(), 'STAMINA', 'stamina'),\"stamina:\")]/parent::*/following-sibling::*/text()").extract()[0].split()[0] # eg. "95"
#        item["injury"] = response.xpath("//td/strong[contains(translate(text(), 'INJURY', 'injury'),\"injury:\")]/parent::*/following-sibling::*/text()").extract()[0].split()[0] # eg. "86"
#        item["toughness"] = response.xpath("//td/strong[contains(translate(text(), 'TOUGHNESS', 'toughness'),\"toughness:\")]/parent::*/following-sibling::*/text()").extract()[0].split()[0] # eg. "88"
        #logging.warning("item[\"run_blocking\"] = %s" % item["run_blocking"])
        
        # The player's draft round and pick should be inside of a font tag, with the format "[NUMBER] - Round [NUMBER], pick [NUMBER]"
        # or, if undrafted, "Undrafted, [NUMBER] - Round , pick".
        draft_strings = response.xpath("//font/text()").re(r".+\d+ - Round \d+, pick \d+") # eg. "[u'     \tColts, 2012 - Round 1, pick 1']" or, for an undrafted player, "[]"
        #logging.warning("draft_strings = %s" % draft_strings)
        if not draft_strings:
            #Undrafted. Set draft_round = 15, draft_position = 33 (per the values used in Madden Amp to set a player as undrafted).
            item["draft_round"] = "15"
            item["draft_position"] = "33"
            #logging.warning("item[\"draft_round\"] = %s" % item["draft_round"])
            #logging.warning("item[\"draft_position\"] = %s" % item["draft_position"])
        else:
            item["draft_round"] = draft_strings[0].split()[4][0:1] # eg. "1"
            item["draft_position"] = draft_strings[0].split()[6] # eg. "1"
            #logging.warning("item[\"draft_round\"] = %s" % item["draft_round"])
            #logging.warning("item[\"draft_position\"] = %s" % item["draft_position"])
        return item

# --------------------------------- SECTION 3 ---------------------------------
# ----------------------------- Helper Functions ------------------------------
def positions_are_similar(NFL_position, FBG_position):
    """ This function is used in find_FBG_ratings_page, but only when the name 
        on the FBGRatings.com roster was not an exact match with the name on 
        NFL.com. It compares the positions of the two player pages to see if 
        they are similar enough to be considered a match.
    
    Args: 
        NFL_position: The abbreviation from the player's NFL profile page.
        FBG_position: The abbreviation from the player's FBG profile page.
    
    Returns:
        True if the positions can be considered similar enough; False if not.
    """
    # If either position is QB and the other isn't, the answer is no.
    if NFL_position.upper() == "QB":
        if FBG_position.upper() == "QB":
            return True
        else:
            return False
    # If the NFL_position is RB, HB, FB, WR, or TE, 
    # FBG_position can be: RB, HB, FB, WR, or TE.
    if (NFL_position.upper() == "RB" or NFL_position.upper() == "HB" or
            NFL_position.upper() == "FB" or NFL_position.upper() == "WR" or 
            NFL_position.upper() == "TE"):
        if (FBG_position.upper() == "RB" or FBG_position.upper() == "HB" or 
                FBG_position.upper() == "FB" or FBG_position.upper() == "WR" or 
                FBG_position.upper() == "TE"):
            return True
        else:
            return False
    # If the NFL_position is OL, T, OT, G, OG, LS, LT, LG, C, RG, or RT, 
    # FBG_position can be: OL, T, OT, G, OG, LS, LT, LG, C, RG, or RT.
    if (NFL_position.upper() == "OL" or NFL_position.upper() == "T" or 
            NFL_position.upper() == "OT" or NFL_position.upper() == "G" or 
            NFL_position.upper() == "OG" or NFL_position.upper() == "LS" or 
            NFL_position.upper() == "LT" or NFL_position.upper() == "LG" or 
            NFL_position.upper() == "C" or NFL_position.upper() == "RG" or 
            NFL_position.upper() == "RT"):
        if (FBG_position.upper() == "OL" or FBG_position.upper() == "T" or 
                FBG_position.upper() == "OT" or FBG_position.upper() == "G" or 
                FBG_position.upper() == "OG" or FBG_position.upper() == "LS" or 
                FBG_position.upper() == "LT" or FBG_position.upper() == "LG" or 
                FBG_position.upper() == "C" or FBG_position.upper() == "RG" or 
                FBG_position.upper() == "RT"):
            return True
        else:
            return False
    # If the NFL_position is DL, DE, LE, or RE, FBG_position can be: 
    # DL, DE, LE, RE, DT, NT, LB, OLB, LOLB, ROLB, ILB, or MLB.
    if (NFL_position.upper() == "DL" or NFL_position.upper() == "DE" or 
            NFL_position.upper() == "LE" or NFL_position.upper() == "RE"):
        if (FBG_position.upper() == "DL" or FBG_position.upper() == "DE" or 
                FBG_position.upper() == "LE" or FBG_position.upper() == "RE" or 
                FBG_position.upper() == "DT" or FBG_position.upper() == "NT" or 
                FBG_position.upper() == "LB" or 
                FBG_position.upper() == "OLB" or 
                FBG_position.upper() == "LOLB" or 
                FBG_position.upper() == "ROLB" or 
                FBG_position.upper() == "ILB" or 
                FBG_position.upper() == "MLB"):
            return True
        else:
            return False
    # If the NFL_position is DT or NT, 
    # FBG_position can be: DL, DE, LE, RE, DT, or NT.
    if NFL_position.upper() == "DT" or NFL_position.upper() == "NT":
        if (FBG_position.upper() == "DL" or FBG_position.upper() == "DE" or 
                FBG_position.upper() == "LE" or FBG_position.upper() == "RE" or 
                FBG_position.upper() == "DT" or FBG_position.upper() == "NT"):
            return True
        else:
            return False
    # If the NFL_position is LB, OLB, LOLB, ROLB, ILB, or MLB, 
    # FBG_position can be: DL, DE, LE, RE, LB, OLB, LOLB, ROLB, ILB, or MLB.
    if (NFL_position.upper() == "LB" or NFL_position.upper() == "OLB" or 
            NFL_position.upper() == "LOLB" or NFL_position.upper() == "ROLB" or 
            NFL_position.upper() == "ILB" or NFL_position.upper() == "MLB"):
        if (FBG_position.upper() == "DL" or FBG_position.upper() == "DE" or 
                FBG_position.upper() == "LE" or FBG_position.upper() == "RE" or 
                FBG_position.upper() == "LB" or 
                FBG_position.upper() == "OLB" or 
                FBG_position.upper() == "LOLB" or 
                FBG_position.upper() == "ROLB" or 
                FBG_position.upper() == "ILB" or FBG_position.upper() == "MLB"):
            return True
        else:
            return False
    # If the NFL_position is DB, CB, S, SAF, FS, or SS, 
    # FBG_position can be: DB, CB, S, SAF, FS, or SS.
    if (NFL_position.upper() == "DB" or NFL_position.upper() == "CB" or 
            NFL_position.upper() == "S" or NFL_position.upper() == "SAF" or 
            NFL_position.upper() == "FS" or NFL_position.upper() == "SS"):
        if (FBG_position.upper() == "DB" or FBG_position.upper() == "CB" or 
                FBG_position.upper() == "S" or FBG_position.upper() == "SAF" or 
                FBG_position.upper() == "FS" or FBG_position.upper() == "SS"):
            return True
        else:
            return False
    # If either position is K or P and the other isn't one of those, 
    # the answer is no.
    if NFL_position.upper() == "K" or NFL_position.upper() == "P":
        if FBG_position.upper() == "K" or FBG_position.upper() == "P":
            return True
        else:
            return False
    # If we still haven't seen a match for what the NFL gave as the position, 
    # we have some strange input.
    logging.error("Unknown NFL_position passed to positions_are_similar:")
    logging.error("NFL_position.upper() = %s" % NFL_position.upper())
    logging.error("FBG_position.upper() = %s" % FBG_position.upper())
    return False

def choose_best_position(position1, position2):
    """ This function takes in the two position strings for a player (found on 
        NFL.com and FBGRatings.com) and uses them in determining which Madden 
        position to assign this player. If the return value is either "TBD" or 
        "CONFLICT", we will need to manually replace it after the output file 
        has been fully generated.
    
    Args: 
        position1: The first position to use in the comparison. This may come 
        from either NFL.com or FBGRatings.com.
        position2: The second position to use in the comparison. This may come 
        from either NFL.com or FBGRatings.com.
    
    Returns: 
        A string containing either: the Madden position determined from the NFL 
        and FBG positions; "TDB" if no determination can be made, but the input 
        positions were in agreement; or "CONFLICT" if the positions are not in 
        agreement.
    """
    # QB is easy.
    if position1.upper() == "QB":
        if position2.upper() == "QB":
            return "QB"
        else:
            return "CONFLICT"
    # If position1 is RB, try to go off of what we have in position2.
    if position1.upper() == "RB":
        if (position2.upper() == "RB" or position2.upper() == "WR" or 
                position2.upper() == "TE"):
            return "TBD"
        elif position2.upper() == "HB":
            return "HB"
        elif position2.upper() == "FB":
            return "FB"
        else:
            return "CONFLICT"
    # If position1 is HB, we are similar to WR and TE, and can be specific with 
    # RB, HB, and FB.
    if position1.upper() == "HB":
        if position2.upper() == "WR" or position2.upper() == "TE":
            return "TBD"
        elif position2.upper() == "RB" or position2.upper() == "HB":
            return "HB"
        # FB is special - assume it is correct even over HB.
        elif position2.upper() == "FB":
            return "FB"
        else:
            return "CONFLICT"
    # FB is special - assume it is correct even over HB; it is also similar 
    # enough to WR and TE.
    if position1.upper() == "FB":
        if position2.upper() == "WR" or position2.upper() == "TE":
            return "TBD"
        if (position2.upper() == "RB" or position2.upper() == "HB" or 
                position2.upper() == "FB"):
            return "FB"
        else:
            return "CONFLICT"
    # If position1 is WR, we are similar to RB, HB, FB, and TE, and can be 
    # specific with only WR.
    if position1.upper() == "WR":
        if (position2.upper() == "RB" or position2.upper() == "HB" or 
                position2.upper() == "FB" or position2.upper() == "TE"):
            return "TBD"
        elif position2.upper() == "WR":
            return "WR"
        else:
            return "CONFLICT"
    # If position1 is TE, we are similar to RB, HB, FB, and WR, and can be 
    # specific with only TE.
    if position1.upper() == "TE":
        if (position2.upper() == "RB" or position2.upper() == "HB" or 
                position2.upper() == "FB" or position2.upper() == "WR"):
            return "TBD"
        elif position2.upper() == "TE":
            return "TE"
        else:
            return "CONFLICT"
    # If position1 is T, G, OT, OG, OL, or LS, try to go off of what we have in 
    # position2.
    if (position1.upper() == "T" or position1.upper() == "G" or 
            position1.upper() == "OT" or position1.upper() == "OG" or 
            position1.upper() == "OL" or position1.upper() == "LS"):
        if (position2.upper() == "T" or position2.upper() == "G" or 
                position2.upper() == "OT" or position2.upper() == "OG" or 
                position2.upper() == "OL" or position2.upper() == "LS"):
            return "TBD"
        elif position2.upper() == "LT":
            return "LT"
        elif position2.upper() == "LG":
            return "LG"
        elif position2.upper() == "C":
            return "C"
        elif position2.upper() == "RG":
            return "RG"
        elif position2.upper() == "RT":
            return "RT"
        else:
            return "CONFLICT"
    # If position1 is LT, see if position2 is a generic OL or T.
    if position1.upper() == "LT":
        if (position2.upper() == "LT" or position2.upper() == "T" or 
                position2.upper() == "OT" or position2.upper() == "OL"):
            return "LT"
        # If position2 is a different specific OL position, we have a TBD.
        elif (position2.upper() == "G" or position2.upper() == "OG" or 
                position2.upper() == "LS" or position2.upper() == "LG" or 
                position2.upper() == "C" or position2.upper() == "RG" or 
                position2.upper() == "RT"):
            return "TBD"
        else:
            return "CONFLICT"
    # If position1 is LG, see if position2 is a generic OL or G.
    if position1.upper() == "LG":
        if (position2.upper() == "LG" or position2.upper() == "G" or 
                position2.upper() == "OG" or position2.upper() == "OL"):
            return "LG"
        # If position2 is a different specific OL position, we have a TBD.
        elif (position2.upper() == "T" or position2.upper() == "OT" or 
                position2.upper() == "LS" or position2.upper() == "LT" or 
                position2.upper() == "C" or position2.upper() == "RG" or 
                position2.upper() == "RT"):
            return "TBD"
        else:
            return "CONFLICT"
    # If position1 is C, see if position2 is some sort of generic OL or C.
    if position1.upper() == "C":
        if (position2.upper() == "C" or position2.upper() == "G" or 
                position2.upper() == "OG" or position2.upper() == "OL"):
            return "C"
        # If position2 is a different specific OL position, we have a TBD.
        elif (position2.upper() == "T" or position2.upper() == "OT" or 
                position2.upper() == "LS" or position2.upper() == "LT" or 
                position2.upper() == "LG" or position2.upper() == "RG" or 
                position2.upper() == "RT"):
            return "TBD"
        else:
            return "CONFLICT"
    # If position1 is RG, see if position2 is some sort of generic OL or G.
    if position1.upper() == "RG":
        if (position2.upper() == "RG" or position2.upper() == "G" or 
                position2.upper() == "OG" or position2.upper() == "OL"):
            return "RG"
        # If position2 is a different specific OL position, we have a TBD.
        elif (position2.upper() == "T" or position2.upper() == "OT" or 
                position2.upper() == "LS" or position2.upper() == "LT" or 
                position2.upper() == "LG" or position2.upper() == "C" or 
                position2.upper() == "RT"):
            return "TBD"
        else:
            return "CONFLICT"
    # If position1 is RT, see if position2 is some sort of generic OL or T.
    if position1.upper() == "RT":
        if (position2.upper() == "RT" or position2.upper() == "T" or 
                position2.upper() == "OT" or position2.upper() == "OL"):
            return "RT"
        # If position2 is a different specific OL position, we have a TBD.
        elif (position2.upper() == "G" or position2.upper() == "OG" or 
                position2.upper() == "LS" or position2.upper() == "LT" or 
                position2.upper() == "LG" or position2.upper() == "C" or 
                position2.upper() == "RG"):
            return "TBD"
        else:
            return "CONFLICT"
    # If position1 is DL, try to go off of what we have in position2.
    if position1.upper() == "DL":
        if (position2.upper() == "DL" or position2.upper() == "DE" or 
                position2.upper() == "LB" or position2.upper() == "OLB"or 
                position2.upper() == "LOLB" or position2.upper() == "ROLB" or 
                position2.upper() == "ILB" or position2.upper() == "MLB"):
            return "TBD"
        elif position2.upper() == "LE":
            return "LE"
        elif position2.upper() == "RE":
            return "RE"
        elif position2.upper() == "DT" or position2.upper() == "NT":
            return "DT"
        else:
            return "CONFLICT"
    # If position1 is DE, try to go off of what we have in position2.
    if position1.upper() == "DE":
        if (position2.upper() == "DL" or position2.upper() == "DE" or 
                position2.upper() == "DT" or position2.upper() == "NT" or 
                position2.upper() == "LB" or position2.upper() == "OLB" or 
                position2.upper() == "LOLB" or position2.upper() == "ROLB" or 
                position2.upper() == "ILB" or position2.upper() == "MLB"):
            return "TBD"
        elif position2.upper() == "LE":
            return "LE"
        elif position2.upper() == "RE":
            return "RE"
        else:
            return "CONFLICT"
    # If position1 is LE, most others will be a TBD, except for DL, DE, or LE.
    if position1.upper() == "LE":
        if (position2.upper() == "RE" or position2.upper() == "DT" or 
                position2.upper() == "NT" or position2.upper() == "LB" or 
                position2.upper() == "OLB" or position2.upper() == "LOLB" or 
                position2.upper() == "ROLB" or position2.upper() == "ILB" or 
                position2.upper() == "MLB"):
            return "TBD"
        elif (position2.upper() == "DL" or position2.upper() == "DE" or 
                position2.upper() == "LE"):
            return "LE"
        else:
            return "CONFLICT"
    # If position1 is RE, most others will be a TBD, except for DL, DE, or RE.
    if position1.upper() == "RE":
        if (position2.upper() == "LE" or position2.upper() == "DT" or 
                position2.upper() == "NT" or position2.upper() == "LB" or 
                position2.upper() == "OLB" or position2.upper() == "LOLB" or 
                position2.upper() == "ROLB" or position2.upper() == "ILB" or 
                position2.upper() == "MLB"):
            return "TBD"
        elif (position2.upper() == "DL" or position2.upper() == "DE" or 
                position2.upper() == "RE"):
            return "RE"
        else:
            return "CONFLICT"
    # If position1 is DT or NT, we can match DT, NT, or the generic DL.
    if position1.upper() == "DT" or position1.upper() == "NT":
        if (position2.upper() == "DE" or position2.upper() == "LE" or 
                position2.upper() == "RE"):
            return "TBD"
        elif (position2.upper() == "DL" or position2.upper() == "DT" or 
                position2.upper() == "NT"):
            return "DT"
        else:
            return "CONFLICT"
    # If position1 is LB, try to go off of position2.
    if position1.upper() == "LB":
        if (position2.upper() == "DL" or position2.upper() == "DE" or 
                position2.upper() == "LE" or position2.upper() == "RE" or 
                position2.upper() == "LB" or position2.upper() == "OLB"):
            return "TBD"
        elif position2.upper() == "LOLB":
            return "LOLB"
        elif position2.upper() == "ROLB":
            return "ROLB"
        elif position2.upper() == "ILB" or position2.upper() == "MLB":
            return "MLB"
        else:
            return "CONFLICT"
    # If position1 is OLB, try to go off of position2.
    if position1.upper() == "OLB":
        if (position2.upper() == "DL" or position2.upper() == "DE" or 
                position2.upper() == "LE" or position2.upper() == "RE" or 
                position2.upper() == "LB" or position2.upper() == "OLB" or 
                position2.upper() == "ILB" or position2.upper() == "MLB"):
            return "TBD"
        elif position2.upper() == "LOLB":
            return "LOLB"
        elif position2.upper() == "ROLB":
            return "ROLB"
        else:
            return "CONFLICT"
    # If position1 is LOLB, we can match on LB, OLB, or LOLB.
    if position1.upper() == "LOLB":
        if (position2.upper() == "DL" or position2.upper() == "DE" or 
                position2.upper() == "LE" or position2.upper() == "RE" or 
                position2.upper() == "ROLB" or position2.upper() == "ILB" or 
                position2.upper() == "MLB"):
            return "TBD"
        elif (position2.upper() == "LB" or position2.upper() == "OLB" or 
                position2.upper() == "LOLB"):
            return "LOLB"
        else:
            return "CONFLICT"
    # If position1 is ROLB, we can match on LB, OLB, or ROLB.
    if position1.upper() == "ROLB":
        if (position2.upper() == "DL" or position2.upper() == "DE" or 
                position2.upper() == "LE" or position2.upper() == "RE" or 
                position2.upper() == "LOLB" or position2.upper() == "ILB" or 
                position2.upper() == "MLB"):
            return "TBD"
        elif (position2.upper() == "LB" or position2.upper() == "OLB" or 
                position2.upper() == "ROLB"):
            return "ROLB"
        else:
            return "CONFLICT"
    # If position1 is ILB or MLB, we can match on LB, ILB, or MLB.
    if position1.upper() == "ILB" or position1.upper() == "MLB":
        if (position2.upper() == "DL" or position2.upper() == "DE" or 
                position2.upper() == "LE" or position2.upper() == "RE" or 
                position2.upper() == "OLB" or position2.upper() == "LOLB" or 
                position2.upper() == "ROLB"):
            return "TBD"
        elif (position2.upper() == "LB" or position2.upper() == "ILB" or 
                position2.upper() == "MLB"):
            return "MLB"
        else:
            return "CONFLICT"
    # If position1 is DB, try to go off of what we have in position2.
    if position1.upper() == "DB":
        if (position2.upper() == "DB" or position2.upper() == "S" or 
                position2.upper() == "SAF"):
            return "TBD"
        elif position2.upper() == "CB":
            return "CB"
        elif position2.upper() == "FS":
            return "FS"
        elif position2.upper() == "SS":
            return "SS"
        else:
            return "CONFLICT"
    # If position1 is CB, we can only match DB or CB.
    if position1.upper() == "CB":
        if (position2.upper() == "S" or position2.upper() == "SAF" or 
                position2.upper() == "FS" or position2.upper() == "SS"):
            return "TBD"
        elif position2.upper() == "DB" or position2.upper() == "CB":
            return "CB"
        else:
            return "CONFLICT"
    # If position1 is S or SAF, try to go off of what we have in position2.
    if position1.upper() == "S" or position1.upper() == "SAF":
        if (position2.upper() == "DB" or position2.upper() == "CB" or 
                position2.upper() == "S" or position2.upper() == "SAF"):
            return "TBD"
        elif position2.upper() == "FS":
            return "FS"
        elif position2.upper() == "SS":
            return "SS"
        else:
            return "CONFLICT"
    # If position1 is FS, we can match DB, S, SAF, or FS.
    if position1.upper() == "FS":
        if position2.upper() == "CB" or position2.upper() == "SS":
            return "TBD"
        elif (position2.upper() == "DB" or position2.upper() == "S" or 
                position2.upper() == "SAF" or position2.upper() == "FS"):
            return "FS"
        else:
            return "CONFLICT"
    # If position1 is SS, we can match DB, S, SAF, or SS.
    if position1.upper() == "SS":
        if position2.upper() == "CB" or position2.upper() == "FS":
            return "TBD"
        elif (position2.upper() == "DB" or position2.upper() == "S" or 
                position2.upper() == "SAF" or position2.upper() == "SS"):
            return "SS"
        else:
            return "CONFLICT"
    # K is easy.
    if position1.upper() == "K":
        if position2.upper() == "K":
            return "K"
        elif position2.upper() == "P":
            return "TBD"
        else:
            return "CONFLICT"
    # P is easy.
    if position1.upper() == "P":
        if position2.upper() == "P":
            return "P"
        elif position2.upper() == "K":
            return "TBD"
        else:
            return "CONFLICT"
    logging.error("Unknown position1 passed to choose_best_position:")
    logging.error("position1.upper() = %s" % position1.upper())
    logging.error("position2.upper() = %s" % position2.upper())
    return "CONFLICT"


# --------------------------------- SECTION 4 ---------------------------------
# ------------------------------ Main Function --------------------------------

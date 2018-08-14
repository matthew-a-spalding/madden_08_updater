r"""nfl_spider.py
    
    This script defines the spider class and related helper functions that will perform the actual crawl over the 
    entirety of the NFL team roster pages. It (or more precisely, its processor, 'process\scraping\pipelines.py') 
    generates the CSV file 'process\outputs\step3\My 20[XX] Player Attributes - Initial.csv,' listing all current NFL 
    players, with their attributes determined from the combination of the NFL site, the values found in 
    'process\inputs\step3\Latest Madden Ratings.csv,' and 'process\inputs\step3\Previous Player Attributes.csv.'
"""

# ----------------------------------------------------- SECTION 1 -----------------------------------------------------
# ----------------------------------------- IMPORTS, SETTINGS, AND CONSTANTS ------------------------------------------
# 1 - Standard library imports
import csv, datetime, logging, math, os, re
#from urlparse import urljoin

# 2 - Third-party imports
from scrapy import Request
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
    """
        This class is the spider that does the actual crawling and, in its methods, the parsing of each player item. 
        The main variables are class-scoped variables, NOT instance variables. Thus, trying to set them (as I 
        originally tried) by using self.[var_name] will NOT work. Now, I'm doing it the proper way, using 
        [ClassName].[variable_name], as seen below.
    """
    
    name = "nfl_rosters"
    
    def __init__(self, **kwargs):
        
        # Use this switch to turn on more verbose logging for this method if desired.
        verbose_output = False
        
        # First, get the NFL_ROSTER_LINK_TEMPLATE from the settings module.
        nfl_roster_link_template = settings.NFL_ROSTER_LINK_TEMPLATE
        # Make the list we will populate with all the NFL.com team roster page URLs.
        nfl_roster_urls = []
        
        # Enumerate the items (dictionaries) in the list of NFL team dicts.
        for index, team_info_dict in enumerate(settings.NFL_TEAMS):
            # Put a new copy of the URL template for this team into the list.
            nfl_roster_urls.append(nfl_roster_link_template)
            # Iterate over the keys and values in the current team dict.
            for placeholder, value in team_info_dict.items():
                # Replace any instances of the current key (placeholder) with the related value from the team's dict.
                nfl_roster_urls[index] = nfl_roster_urls[index].replace(placeholder, value)
        
        # Now we can set the start_urls class variable to our populated list of NFL.com team roster URLs.
        NFLSpider.start_urls = nfl_roster_urls
        # eg. ["http://www.nfl.com/teams/philadelphiaeagles/roster?team=phi"]
        
        # Set our allowed domains to make sure we can visit pages on NFL.com and overthecap.com.
        NFLSpider.allowed_domains = ["nfl.com", "overthecap.com"]
        
        # Pass in the filtering regex using allow=() and/or restrict_xpaths=() to get the links for each player 
        # profile page, per documentation at http://doc.scrapy.org/en/latest/topics/link-extractors.html
        NFLSpider.rules = [Rule(
            LinkExtractor(allow=(settings.NFL_PROFILE_LINKS_REGEX, )), 
            callback="parse_NFL_profile_page"
            )]
        logging.info("NFLSpider initialized.")
        if verbose_output:
            logging.info("start_urls = %s", nfl_roster_urls)
            logging.info("allow_rule = %s", settings.NFL_PROFILE_LINKS_REGEX)
        
        # Open the "Latest Madden Ratings.csv" file with all the players and their Madden ratings for reading.
        self.madden_ratings_file = open(
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 
                r"process\inputs\step3\Latest Madden Ratings.csv"
            ), 'r'
        )
        
        # Get a DictReader to read the rows into dicts using the header row as keys.
        self.madden_ratings_dict_reader = csv.DictReader(self.madden_ratings_file)
        
        # Open the "Previous Player Attributes.csv" file with last year's players and their attributes for reading.
        self.previous_attributes_file = open(
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 
                r"process\inputs\step3\Previous Player Attributes.csv"
            ), 'r'
        )
        
        # Get a DictReader to read the rows into dicts using the header row as keys.
        self.previous_players_dict_reader = csv.DictReader(self.previous_attributes_file)
        
        # Finally, we will set initial values for the other class-scoped attributes.
        NFLSpider.choose_lt = False
        NFLSpider.choose_lg = False
        NFLSpider.choose_le = False
        NFLSpider.choose_lolb = False
        NFLSpider.choose_fs = False
        
        # The only thing left to do is call the parent constructor.
        super(NFLSpider, self).__init__(**kwargs)


    def __del__(self):
        if self.madden_ratings_file:
            logging.info("Closing the file self.madden_ratings_file.")
            self.madden_ratings_file.close()
            self.madden_ratings_file = None


    def parse_NFL_profile_page(self, response):
        """ Scrapes the NFL.com profile page for a player, putting associated attributes into the player object. """
        
        # Use this switch to turn on more verbose logging for this method if desired.
        verbose_output = False
        
        if verbose_output:
            logging.info("NFL.com: Player profile page url: %s", response.url)
        
        # Create a new item for this player.
        player = NFLPlayer()
        
    # CHECK AND UPDATE THIS WHOLE SECTION AS NECESSARY.
    # Make sure the xpath expressions below can be used to find our text in the source of any player profile page.
        
        #-------------------------------------------  Part 1: NFL.com info  -------------------------------------------
        
        # Start by populating the team field. The NFL page will be authoritative here; no need to check Madden.
        player["team"] = response.xpath(
            "//div[@class=\"article-decorator\"]/h1/a/text()"
            ).extract()[0].split()[-1] # eg. "Colts"
        
        # Next up is the player's first and last name.
        # Note: I tested putting a comma into the name fields for a player, and it seemed to be correctly escaped, as 
        # the comma made it from the Latest Madden Ratings file through to the output file. 
        # The NFL.com will not be canonical on names, esp. in situations where the Madden file has the suffix for the 
        # player's last name, like "Fowler III", and the NFL.com does not, so put NFL names into temp vars.
        nfl_full_name = response.xpath(
            "//meta[@id=\"playerName\"]/@content"
            ).extract()[0] # eg. "Prince Charles Iworah"
        
        if len(nfl_full_name.split()) > 2:
            logging.info("NFL.com: Found a player with three or more name parts: \"%s\"\n", nfl_full_name)
        
        nfl_first_name = get_first_name(nfl_full_name) # eg. "Prince Charles"
        if verbose_output:
            logging.info("NFL.com: nfl_first_name = %s", nfl_first_name)
        nfl_last_name = get_last_name(nfl_full_name) # eg. "Iworah"
        if verbose_output:
            logging.info("NFL.com: nfl_last_name = %s", nfl_last_name)
        
        
        # Use this section to only process one specific player for debugging.
        #if nfl_last_name != 'Davenport':
        #    logging.info("Skipping all players but Davenport.")
        #    return player
        
        
        # Use this section to turn on verbose logging for a specific player.
        #if player["last_name"] == 'Davenport':
        #    verbose_output = True
        
        
        # Find the player's jersey number and position. 
        # (If jersey number is empty, there must still be a '#' for this split to work.)
        number_and_position = response.xpath(
            "//span[@class=\"player-number\"]/text()"
            ).extract()[0].split(None, 1) # eg. ["#12", "QB"]
        
        # For jersey number, NFL.com is authoritative (and Madden doesn't always give us that anyway).
        # The [1:] below gets only the chars from position 1 to the end of the string (strings are 0-indexed).
        player["jersey_number"] = number_and_position[0][1:] # eg. "12"
        if verbose_output:
            logging.info("NFL.com: player[""jersey_number""] = %s", player["jersey_number"])
        
        # For position, since the NFL.com value may not be final, save it in a local var, not the player dict.
        nfl_position = number_and_position[1] # eg. "QB"
        if verbose_output:
            logging.info("NFL.com: nfl_position = %s", nfl_position)
        
        # All of the remaining NFL.com info (height, weight, age, college, and experience) is found in the div with 
        # class="player-info". However, some players may be missing their birth / age info, which changes how we 
        # handle that div's contents. First, see if there are 7 or only 5 /p/strong tags in the player-info div.
        player_info_p_strong_tags = response.xpath("//div[@class=\"player-info\"]/p/strong/text()").extract()
        #logging.info("NFL.com: player_info_p_strong_tags = %s", player_info_p_strong_tags)
        
        # Define the variables for height, weight, age, college, and experience, so they exist in all cases.
        nfl_height_inches = ""
        nfl_weight = ""
        nfl_age = ""
        nfl_birthdate = ""
        nfl_college = ""
        nfl_years_pro = ""
        
        if len(player_info_p_strong_tags) == 7:
            # The text() inside the third <p> tag in the <div class="player-info"> tag, which contains the height, 
            # weight, and age, also has a lot of whitespace chars, some of which are grouped into the first string by 
            # themselves. This is why the first string with real content (the height) is found at ...extract()[1], 
            # not ...extract()[0].
            height_weight_age_strings = response.xpath("//div[@class=\"player-info\"]/p[3]/text()").extract()
            # a list of 4 strings, eg. [u'\r\n\t\t\t\t\t', u': 6-4 \xa0 \r\n\t\t\t\t\t', 
            # u': 240 \xa0 \r\n\t [...] \t\t\t', u': 25\r\n\t\t\t\t\t\t\r\n\t\t\t\t\t\r\n\t\t\t\t']
            #logging.info("NFL.com: height_weight_age_strings = %s", height_weight_age_strings)
            
            # The text() inside the fourth <p> tag in the <div class="player-info"> tag contains the birth date as 
            # well as the location (usually city and state) of birth. The date itself can be found by getting the 
            # second string in the list extracted, splitting it, and taking the second string from that split.
            nfl_birthdate = response.xpath("//div[@class=\"player-info\"]/p[4]/text()").extract()[1].split()[1]
            if verbose_output:
                logging.info("NFL.com: nfl_birthdate = %s", nfl_birthdate)
            
            height_strings = height_weight_age_strings[1].split() # eg. [":", "6-4"]
            weight_strings = height_weight_age_strings[2].split() # eg. [":", "240"]
            age_strings = height_weight_age_strings[3].split() # eg. [":", "25"]
            if verbose_output:
                logging.info("NFL.com: height_strings[1] = %s", height_strings[1])
            
            # Since we will not consider the NFL to be authoritative on the height, weight, or age, don't put these 
            # values directly into the player dict. Also, convert height to inches, since inches is the format used in 
            # the roster file and is our standard going forward.
            nfl_height_inches = (int(height_strings[1][0]) * 12) + int(height_strings[1][2:])
            nfl_weight = weight_strings[1] # eg. "240"
            nfl_age = age_strings[1] # eg. "25"
            if verbose_output:
                logging.info("NFL.com: nfl_height_inches = %d", nfl_height_inches)
                logging.info("NFL.com: nfl_weight = %d", nfl_weight)
                logging.info("NFL.com: nfl_age = %d", nfl_age)
            
            # Get the player's college. The NFL.com pages report "No College" if they don't have that info.
            college_strings = response.xpath("//div[@class=\"player-info\"]/p[5]/text()").extract()[0].split(None, 1) 
            # eg. [u":", u"Stanford"]
            #logging.info("NFL.com: college_strings = %s", college_strings)
            nfl_college = college_strings[1] # eg. "Stanford"
            if verbose_output:
                logging.info("NFL.com: nfl_college = %d", nfl_college)
            
            # Get the player's number of years of experience.
            experience_strings = response.xpath(
                "//div[@class=\"player-info\"]/p[6]/text()"
                ).extract()[0].split(None, 1)
            # eg. [u':', u'Rookie '] or [u':', u'12th season ']
            #logging.info("NFL.com: experience_strings = %s", experience_strings)
            
            if "ROOKIE" in experience_strings[1].upper():
                nfl_years_pro = "0"
            else:
                # Need to match the numeric chars at the start of the string.
                regex_match_object = re.match("\d+", experience_strings[1])
                # eg. <_sre.SRE_Match object at 0x032D8100>
                #logging.info("NFL.com: regex_match_object = %s", regex_match_object)
                
                # Since the numbers on NFL.com generally include this season, we want one less than what they say.
                # ... However, when NFL.com says 1st season, they usually mean second.
                nfl_years_pro = (int(regex_match_object.group(0)) - 1) if (int(regex_match_object.group(0)) > 1) else 1
                
            if verbose_output:
                logging.info("NFL.com: nfl_years_pro = %d", nfl_years_pro)
            
        elif len(player_info_p_strong_tags) == 5:
            # The age info is missing, and we have no birth date <p> either.
            # For height, weight, and age, the text() inside the third <p> tag in the <div class="player-info"> tag 
            # has a lot of whitespace chars, some of which are grouped into the first string by themselves, which is 
            # why the first string with real content (for height) is found at ...extract()[1], not ...extract()[0].
            height_weight_strings = response.xpath("//div[@class=\"player-info\"]/p[3]/text()").extract() 
            # a list of 3 strings, 
            # eg. [u'\r\n\t\t\t\t\t', u': 6-6 \xa0 \r\n\t\t\t\t\t', 
            # u': 255 \xa0 \r\n\t\t\t\t\t\r\n\t\t\t\t\t\t\r\n\t\t\t\t\t\t\r\n\t\t\t\t\t\r\n\t\t\t\t']
            #logging.info("NFL.com: height_weight_strings = %s", height_weight_strings)
            
            height_strings = height_weight_strings[1].split() # eg. [":", "6-6"]
            weight_strings = height_weight_strings[2].split() # eg. [":", "255"]
            if verbose_output:
                logging.info("NFL.com: height_strings[1] = %s", height_strings[1])
            
            nfl_height_inches = (int(height_strings[1][0]) * 12) + int(height_strings[1][2:])
            nfl_weight = weight_strings[1] # eg. "255"
            if verbose_output:
                logging.info("NFL.com: nfl_height_inches = %d", nfl_height_inches)
                logging.info("NFL.com: nfl_weight = %d", nfl_weight)
            
            # Get the player's college. The NFL.com pages currently say "No College" when they don't have that info.
            college_strings = response.xpath("//div[@class=\"player-info\"]/p[4]/text()").extract()[0].split(None, 1) 
            # eg. [u":", u"Stanford"]
            #logging.info("NFL.com: college_strings = %s", college_strings)
            nfl_college = college_strings[1] # eg. "Stanford"
            if verbose_output:
                logging.info("NFL.com: nfl_college = %d", nfl_college)
            
            # Get the player's number of years of experience.
            experience_strings = response.xpath(
                "//div[@class=\"player-info\"]/p[5]/text()"
                ).extract()[0].split(None, 1) # eg. [u':', u'Rookie '] or [u':', u'12th season ']
            #logging.info("NFL.com: experience_strings = %s", experience_strings)
            
            if "ROOKIE" in experience_strings[1].upper():
                nfl_years_pro = "0"
            else:
                # Need to match the numeric chars at the start of the string.
                regex_match_object = re.match("\d+", experience_strings[1])
                # eg. <_sre.SRE_Match object at 0x032D8100>
                #logging.info("NFL.com: regex_match_object = %s", regex_match_object)
                nfl_years_pro = (int(regex_match_object.group(0)) - 1) if (int(regex_match_object.group(0)) > 1) else 1
            
            if verbose_output:
                logging.info("NFL.com: nfl_years_pro = %d", nfl_years_pro)
        
        else:
            # We have yet another configuration, which we should investigate.
            logging.error("Found an NFL player profile page where len(player_info_p_strong_tags) == %d, "
                          "which we have not seen before. ", len(player_info_p_strong_tags))
            logging.error("Check the tags in the \"player-info\" div for this url:")
            logging.error("%s \n", response.url)
        
        
        # Now that we have all the info from NFL.com, we can search in the new Madden Ratings and the "Previous Player 
        # Attributes.csv" file for this player.
        
        
        #-------------------------------------------  Part 2: Madden info  --------------------------------------------
        
        
        # Create the dict into which we'll copy the row from the Madden CSV with this player's info, if we find it.
        madden_player_dict = {}
        
        # If we have either birthdate or age from NFL.com, try uing those first.
        if nfl_birthdate:
            
            # Loop over the rows in the Madden file to compare them with the NFL.com info.
            for player_dict in self.madden_ratings_dict_reader:
                
                # We do our comparisons without suffixes.
                madden_last_name = remove_suffix(player_dict["Last Name"])
                
                # We should be able to match the birthdate and full name.
                if (nfl_last_name.lower() == madden_last_name.lower() and 
                        nfl_first_name.lower() == player_dict["First Name"].lower() and 
                        nfl_birthdate == player_dict["Birthdate"]):
                    
                    if verbose_output:
                        logging.info("NFL & Madden: BEST MATCH (by full name, birthdate) for %s %s, %s %s.", 
                                     nfl_first_name, nfl_last_name, player["team"], nfl_position)
                    
                    madden_player_dict = player_dict
                    
                    # Once we match, reset our file record pointer and break the 'for' loop.
                    # (Need to reset our file's record pointer, or else subsequent loops over this dict_reader 
                    # will start where this call left off, and never check any of the records before this record.)
                    self.madden_ratings_file.seek(1)
                    break
            
            else:
                
                # Reset our file's record pointer.
                self.madden_ratings_file.seek(1)
                
                # Try once more, seeing if we can find a birhtdate, position, last name, and first initial match.
                for player_dict in self.madden_ratings_dict_reader:
                
                    # We do our comparisons without suffixes.
                    madden_last_name = remove_suffix(player_dict["Last Name"])
                    
                    # We should be able to match the birthdate, last name, and at least first initial.
                    if (nfl_last_name.lower() == madden_last_name.lower() and 
                            nfl_first_name[0].lower() == player_dict["First Name"][0].lower() and 
                            nfl_birthdate == player_dict["Birthdate"] and 
                            positions_are_similar(nfl_position, player_dict["Position"])):
                        
                        logging.warning("NFL & Madden: Likely match by birthdate, position, last name, and first "
                            "initial for %s %s, %s %s.", 
                            nfl_first_name, nfl_last_name, player["team"], nfl_position)
                        logging.warning("Madden CSV values: %s %s, %s %s", 
                                        player_dict["First Name"], 
                                        player_dict["Last Name"], 
                                        player_dict["Team"], 
                                        player_dict["Position"])
                        logging.warning("NFL profile page: %s \n", response.url)
                        
                        madden_player_dict = player_dict
                        
                        # Once we match, reset our file record pointer and break the 'for' loop, as above.
                        self.madden_ratings_file.seek(1)
                        break
                else:
                    # As was necessary above, we now need to reset our file's record pointer.
                    self.madden_ratings_file.seek(1)
                    
                    # Made it through the whole Madden file with a birthdate from NFL.com, but could not find a match.
                    if verbose_output:
                        logging.info("NFL & Madden 1: Unable to find a match for %s %s, %s %s.", 
                                     nfl_first_name, nfl_last_name, player["team"], nfl_position)
                        logging.info("NFL.com: Player profile page url: %s\n", response.url)
        
        elif nfl_age:
            
            # No birthdate on NFL.com. Try matching on full name, age, and position.
            # Loop over the rows in the Madden file to compare them with the NFL.com info.
            for player_dict in self.madden_ratings_dict_reader:
                
                # We do our comparisons without suffixes.
                madden_last_name = remove_suffix(player_dict["Last Name"])
                
                if (nfl_last_name.lower() == madden_last_name.lower() and 
                        nfl_first_name.lower() == player_dict["First Name"].lower() and 
                        abs(int(nfl_age) - int(player_dict["Age"])) < 2 and 
                        positions_are_similar(nfl_position, player_dict["Position"])):
                    
                    logging.warning(
                        "NFL & Madden: Likely match by full name, age, & pos. for NFL.com's %s %s, %s %s.", 
                        nfl_first_name, nfl_last_name, player["team"], nfl_position
                    )
                    logging.warning("Madden CSV values: %s %s, %s %s", 
                                    player_dict["First Name"], 
                                    player_dict["Last Name"], 
                                    player_dict["Team"], 
                                    player_dict["Position"])
                    logging.warning("NFL profile page: %s \n", response.url)
                    
                    madden_player_dict = player_dict
                    
                    # As above, once we match, reset our file record pointer and break the 'for' loop.
                    self.madden_ratings_file.seek(1)
                    break
            else:
                # As was necessary above, we now need to reset our file's record pointer.
                self.madden_ratings_file.seek(1)
                
                # We made it through the whole Madden file with an age from NFL.com, but could not find a match.
                if verbose_output:
                    logging.info("NFL & Madden 2: Unable to find a match for %s %s, %s %s.", 
                                 nfl_first_name, nfl_last_name, player["team"], nfl_position)
                    logging.info("NFL.com: Player profile page url: %s\n", response.url)
        
        else:
            logging.info("NFL.com: No birthdate or age for %s %s, %s %s.", 
                         nfl_first_name, nfl_last_name, player["team"], nfl_position)
            
            # Loop over the rows in the Madden file to compare them with the NFL.com info.
            for player_dict in self.madden_ratings_dict_reader:
                
                # Take any suffix off the last name in Madden when doing our comparisons.
                madden_last_name = remove_suffix(player_dict["Last Name"])
                
                # Try finding a record with the same full name, position, and college.
                if (nfl_last_name.lower() == madden_last_name.lower() and 
                        nfl_first_name.lower() == player_dict["First Name"].lower() and 
                        positions_are_similar(nfl_position, player_dict["Position"]) and 
                        nfl_college[:5].lower() == player_dict["College"][:5].lower()):
                    
                    logging.warning(
                        "NFL & Madden: Possible match by full name, pos, & college for NFL.com's %s %s, %s %s;", 
                        nfl_first_name, nfl_last_name, player["team"], nfl_position)
                    logging.warning("Madden CSV values: %s %s, %s %s", 
                                    player_dict["First Name"], 
                                    player_dict["Last Name"], 
                                    player_dict["Team"], 
                                    player_dict["Position"])
                    logging.warning("NFL profile page: %s \n", response.url)
                    
                    # Attributes are similar enough, so set this record as the player's Madden dict.
                    madden_player_dict = player_dict
                    
                    # Once we match, reset our file record pointer and break the 'for' loop.
                    self.madden_ratings_file.seek(1)
                    break
                
            else:
                # As was necessary above, we now need to reset our file's record pointer.
                self.madden_ratings_file.seek(1)
                
                if verbose_output:
                    logging.info("NFL & Madden 3: Unable to find a match for %s %s, %s %s.", 
                                 nfl_first_name, nfl_last_name, player["team"], nfl_position)
                    logging.info("NFL.com: Player profile page url: %s\n", response.url)
        
        
        #-----------------------------------------  Part 3: Last Year's info  -----------------------------------------
        
        
        # Create the dict into which we'll copy the row from last year's file with this player's info, if we find it.
        existing_player_dict = {}
        
        # If we have either birthdate or age from NFL.com, try uing those first.
        if nfl_birthdate:
            
            # Loop over the rows in last year's file to compare them with the NFL.com info.
            for existing_dict in self.previous_players_dict_reader:
                
                # We do our comparisons without suffixes. We also need to check if the last name was too long for 
                # Madden '08 and got shortened in our file.
                existing_last_name = check_for_shortened_last_name(remove_suffix(existing_dict["last_name"]))
                
                # Need to check if the first name was too long for Madden '08 and got shortened in our file.
                existing_first_name = check_for_shortened_first_name(existing_dict["first_name"])
                
                # We should be able to match the birthdate and full name.
                if (nfl_last_name.lower() == existing_last_name.lower() and 
                        nfl_first_name.lower() == existing_first_name.lower() and 
                        nfl_birthdate == existing_dict["birthdate"]):
                    
                    if verbose_output:
                        logging.info("NFL & Last Year: BEST MATCH (by full name, birthdate) for %s %s, %s %s.", 
                                     nfl_first_name, nfl_last_name, player["team"], nfl_position)
                    
                    existing_player_dict = existing_dict
                    
                    # Once we match, reset our file record pointer and break the 'for' loop.
                    self.previous_attributes_file.seek(1)
                    break
            
            else:
                
                # As was necessary above, we now need to reset our file's record pointer.
                self.previous_attributes_file.seek(1)
                
                # Loop over the rows in last year's file to compare them with the NFL.com info.
                for existing_dict in self.previous_players_dict_reader:
                    
                    # We do our comparisons without suffixes. We also need to check if the last name was too long for 
                    # Madden '08 and got shortened in our file.
                    existing_last_name = check_for_shortened_last_name(remove_suffix(existing_dict["last_name"]))
                    
                    # Need to check if the first name was too long for Madden '08 and got shortened in our file.
                    existing_first_name = check_for_shortened_first_name(existing_dict["first_name"])
                    
                    # We should be able to match the birthdate, position, last name, and at least first initial.
                    if (nfl_last_name.lower() == existing_last_name.lower() and 
                            nfl_first_name[0].lower() == existing_first_name[0].lower() and 
                            nfl_birthdate == existing_dict["birthdate"] and 
                            positions_are_similar(nfl_position, existing_dict["position"])):
                        
                        logging.warning("NFL & Last Year: Likely match by birthdate, position, last name, and first "
                            "initial for %s %s, %s %s.",
                            nfl_first_name, nfl_last_name, player["team"], nfl_position)
                        logging.warning("Last year's values: %s %s, %s %s", 
                                        existing_dict["first_name"], 
                                        existing_dict["last_name"], 
                                        existing_dict["team"], 
                                        existing_dict["position"])
                        logging.warning("NFL profile page: %s \n", response.url)
                        
                        existing_player_dict = existing_dict
                        
                        # Once we match, reset our file record pointer and break the 'for' loop.
                        # (Need to reset our file's record pointer, or else subsequent loops over this dict_reader 
                        # will start where this call left off, and never check any of the records before this record.)
                        self.previous_attributes_file.seek(1)
                        break
                
                else:
                    # As was necessary above, we now need to reset our file's record pointer.
                    self.previous_attributes_file.seek(1)
                    
                    # We somehow made it through the whole file, with a birthdate and/or age from NFL.com, but 
                    # still could not find a match. This is a situation we will want to investigate.
                    if verbose_output:
                        logging.info("NFL & Last Year 1: Unable to find a match for %s %s, %s %s.", 
                                     nfl_first_name, nfl_last_name, player["team"], nfl_position)
                        logging.info("NFL.com: Player profile page url: %s\n", response.url)
            
        elif nfl_age:
            
            # Loop over the rows in last year's file to compare them with the NFL.com info.
            for existing_dict in self.previous_players_dict_reader:
                
                # We do our comparisons without suffixes. We also need to check if the last name was too long for 
                # Madden '08 and got shortened in our file.
                existing_last_name = check_for_shortened_last_name(remove_suffix(existing_dict["last_name"]))
                
                # Need to check if the first name was too long for Madden '08 and got shortened in our file.
                existing_first_name = check_for_shortened_first_name(existing_dict["first_name"])
                
                # Try matching on full name, age, and position.
                if (nfl_last_name.lower() == existing_last_name.lower() and 
                        nfl_first_name.lower() == existing_first_name.lower() and 
                        abs(int(nfl_age) - int(existing_dict["age"])) < 2 and 
                        positions_are_similar(nfl_position, existing_dict["position"])):
                    
                    logging.warning(
                        "NFL & Last Year: Likely match by full name, age, & pos. for NFL.com's %s %s, %s %s.", 
                        nfl_first_name, nfl_last_name, player["team"], nfl_position
                    )
                    logging.warning("Last year's values: %s %s, %s %s", 
                                    existing_dict["first_name"], 
                                    existing_dict["last_name"], 
                                    existing_dict["team"], 
                                    existing_dict["position"])
                    logging.warning("NFL profile page: %s \n", response.url)
                    
                    existing_player_dict = existing_dict
                    
                    # As above, once we match, reset our file record pointer and break the 'for' loop.
                    self.previous_attributes_file.seek(1)
                    break
                
            else:
                
                # As was necessary above, we now need to reset our file's record pointer.
                self.previous_attributes_file.seek(1)
                
                # We made it through the whole Madden file with an age from NFL.com, but could not find a match.
                if verbose_output:
                    logging.info("NFL & Last Year 2: Unable to find a match for %s %s, %s %s.", 
                                 nfl_first_name, nfl_last_name, player["team"], nfl_position)
                    logging.info("NFL.com: Player profile page url: %s\n", response.url)
            
        else:
            
            # Loop over the rows in last year's file to compare them with the NFL.com info.
            for existing_dict in self.previous_players_dict_reader:
                
                # We do our comparisons without suffixes. We also need to check if the last name was too long for 
                # Madden '08 and got shortened in our file.
                existing_last_name = check_for_shortened_last_name(remove_suffix(existing_dict["last_name"]))
                
                # Need to check if the first name was too long for Madden '08 and got shortened in our file.
                existing_first_name = check_for_shortened_first_name(existing_dict["first_name"])
                
                # Try finding a record with the same full name, position, and college.
                if (nfl_last_name.lower() == existing_last_name.lower() and 
                        nfl_first_name.lower() == existing_first_name.lower() and 
                        positions_are_similar(nfl_position, existing_dict["position"]) and 
                        nfl_college[:5].lower() == existing_dict["college"][:5].lower()):
                    
                    logging.warning(
                        "NFL & Last Year: Possible match by name, pos, & college for NFL.com's %s %s, %s %s;", 
                        nfl_first_name, nfl_last_name, player["team"], nfl_position)
                    logging.warning("Last year's values: %s %s, %s %s", 
                                    existing_dict["first_name"], 
                                    existing_dict["last_name"], 
                                    existing_dict["team"], 
                                    existing_dict["position"])
                    logging.warning("NFL profile page: %s \n", response.url)
                    
                    # Attributes are similar enough, so set this record as the player's existing dict.
                    existing_player_dict = existing_dict
                    
                    # Once we match, reset our file record pointer and break the 'for' loop.
                    self.previous_attributes_file.seek(1)
                    break
                
            else:
                # As was necessary above, we now need to reset our file's record pointer.
                self.previous_attributes_file.seek(1)
                
                if verbose_output:
                    logging.info("NFL & Last Year 2: Unable to find a match for %s %s, %s %s.", 
                                 nfl_first_name, nfl_last_name, player["team"], nfl_position)
                    logging.info("NFL.com: Player profile page url: %s\n", response.url)
        
        
        #------------------------------------  Part 4: Setting Initial Attributes  ------------------------------------
        
        
        # See if we were able to find a dictionary for this player in both the previous attributes file and Madden.
        if existing_player_dict and madden_player_dict:
            
            # Since Madden '08 has stricter name length requirements than current Maddens and the NFL.com, we will 
            # want to keep any shortened versions from the existing player dict.
            player["first_name"] = existing_player_dict["first_name"]
            if len(existing_player_dict["first_name"]) > 11:
                logging.error("Found an existing first name longer than 11 chars: %s %s, %s %s;", 
                                existing_player_dict["first_name"], 
                                existing_player_dict["last_name"], 
                                player["team"], 
                                existing_player_dict["position"])
                logging.error("NFL profile page: %s \n", response.url)
            
            player["last_name"] = existing_player_dict["last_name"]
            if len(existing_player_dict["last_name"]) > 13:
                logging.error("Found an existing last name longer than 13 chars: %s %s, %s %s;", 
                                existing_player_dict["first_name"], 
                                existing_player_dict["last_name"], 
                                player["team"], 
                                existing_player_dict["position"])
                logging.error("NFL profile page: %s \n", response.url)
            
            # If the player's position has changed since last year, we only want to keep it as what it was before if
            # the player was listed as a FB in our previous file and HB in the current Madden.
            if (existing_player_dict["position"] != madden_player_dict["Position"] and 
                    existing_player_dict["position"] == "FB" and madden_player_dict["Position"] == "HB"):
                player["position"] = "FB"
            else:
                player["position"] = choose_best_position(
                    nfl_position, 
                    madden_player_dict["Position"], 
                    player["first_name"], 
                    player["last_name"]
                )
            
            # Try to average the current Madden values with the ones from NFL.com for height and weight.
            # However, if the difference between the heights is more than 3 inches, we might have a problem.
            if abs(int(nfl_height_inches) - int(madden_player_dict["Height"])) > 3:
                logging.error("Heights for %s %s in NFL and Madden differ by more than 3 in!", 
                              player["first_name"], player["last_name"])
                logging.error("NFL profile page: %s \n", response.url)
            
            # Use the ceiling of the average of the NFL and Madden heights.
            player["height"] = int(math.ceil((int(nfl_height_inches) + int(madden_player_dict["Height"])) / 2))
            
            # If the difference between the weights is more than 30 lbs, we might have a problem.
            if abs(int(nfl_weight) - int(madden_player_dict["Weight"])) > 30:
                logging.error("Weights for %s %s in NFL and Madden differ by more than 30 lbs!", 
                              player["first_name"], player["last_name"])
                logging.error("NFL profile page: %s \n", response.url)
            
            # Use the ceiling of the average of the NFL and Madden weights.
            player["weight"] = int(math.ceil((int(nfl_weight) + int(madden_player_dict["Weight"])) / 2))
            
            # For birthdate, age and college, try the NFL values first.
            if nfl_birthdate:
                player["birthdate"] = nfl_birthdate
            else:
                player["birthdate"] = madden_player_dict["Birthdate"]
            
            if nfl_age:
                player["age"] = nfl_age
            else:
                player["age"] = madden_player_dict["Age"]
                
            if nfl_college:
                player["college"] = nfl_college
            else:
                player["college"] = madden_player_dict["College"]
            
            # In cases where we have a conflict over the number of years pro, resolve things later. 
            if int(nfl_years_pro) != int(madden_player_dict["Years Pro"]):
                # If we have a big discrepency in years pro, we need to know about this.
                if abs(int(nfl_years_pro) - int(madden_player_dict["Years Pro"])) > 1:
                    logging.info("Years pro for %s %s in NFL and Madden differ by more than 1.", 
                                 player["first_name"], player["last_name"])
                    logging.info("Years pro in NFL: %s; in Madden: %s", 
                                 nfl_years_pro, madden_player_dict["Years Pro"])
                    logging.info("NFL profile page: %s \n", response.url)
                player["years_pro"] = "CONFLICT"
            else:
                player["years_pro"] = madden_player_dict["Years Pro"]
            
            # For roles, just use 45 (none) so we can set some manually while having most of them re-calculated in 
            # Step 5, since the attributes the roles are based on most likely have changed since last year.
            player["role_one"] = 45
            player["role_two"] = 45
            
            # Set the values for the fields listed in both the current and previous Madden using the current values. 
            player["awareness"] = madden_player_dict["Awareness"]
            player["speed"] = madden_player_dict["Speed"]
            player["acceleration"] = madden_player_dict["Acceleration"]
            player["agility"] = madden_player_dict["Agility"]
            player["strength"] = madden_player_dict["Strength"]
            player["elusiveness"] = madden_player_dict["Elusiveness"]
            player["carrying"] = madden_player_dict["Carrying"]
            player["trucking"] = madden_player_dict["Trucking"]
            player["catching"] = madden_player_dict["Catching"]
            player["jumping"] = madden_player_dict["Jumping"]
            player["throw_power"] = madden_player_dict["Throw Power"]
            player["throw_accuracy_short"] = madden_player_dict["Throw Accuracy Short"]
            player["throw_accuracy_mid"] = madden_player_dict["Throw Accuracy Mid"]
            player["throw_accuracy_deep"] = madden_player_dict["Throw Accuracy Deep"]
            player["throw_on_the_run"] = madden_player_dict["Throw on the Run"]
            player["playaction"] = madden_player_dict["Playaction"]
            player["pass_block"] = madden_player_dict["Pass Block"]
            player["run_block"] = madden_player_dict["Run Block"]
            player["tackle"] = madden_player_dict["Tackle"]
            player["kick_power"] = madden_player_dict["Kick Power"]
            player["kick_accuracy"] = madden_player_dict["Kick Accuracy"]
            player["kick_return"] = madden_player_dict["Kick Return"]
            player["stamina"] = madden_player_dict["Stamina"]
            player["injury"] = madden_player_dict["Injury"]
            player["run_block_power"] = madden_player_dict["Run Block Power"]
            player["run_block_finesse"] = madden_player_dict["Run Block Finesse"]
            player["pass_block_power"] = madden_player_dict["Pass Block Power"]
            player["pass_block_finesse"] = madden_player_dict["Pass Block Finesse"]
            player["break_tackle"] = madden_player_dict["Break Tackle"]
            player["toughness"] = madden_player_dict["Toughness"]
            player["handedness"] = madden_player_dict["Handedness"]
            
            # For now, use the Total Salary and Signing Bonus values from the current Madden. (For most players, we 
            # will overwrite these with the values from OTC.com later.)
            player["total_salary"] = madden_player_dict["Total Salary"]
            player["signing_bonus"] = madden_player_dict["Signing Bonus"]
            
            # The remaining fields will be populated with the values from the previous attributes file.
            player["breathing_strip"] = existing_player_dict["breathing_strip"]
            player["eye_black"] = existing_player_dict["eye_black"]
            player["face_id"] = existing_player_dict["face_id"]
            player["face_mask"] = existing_player_dict["face_mask"]
            player["hair_color"] = existing_player_dict["hair_color"]
            player["hair_style"] = existing_player_dict["hair_style"]
            player["helmet"] = existing_player_dict["helmet"]
            player["left_elbow"] = existing_player_dict["left_elbow"]
            player["left_hand"] = existing_player_dict["left_hand"]
            player["left_knee"] = existing_player_dict["left_knee"]
            player["left_shoe"] = existing_player_dict["left_shoe"]
            player["left_wrist"] = existing_player_dict["left_wrist"]
            player["mouthpiece"] = existing_player_dict["mouthpiece"]
            player["neck_pad"] = existing_player_dict["neck_pad"]
            player["nfl_icon"] = existing_player_dict["nfl_icon"]
            player["pro_bowl"] = existing_player_dict["pro_bowl"]
            player["right_elbow"] = existing_player_dict["right_elbow"]
            player["right_hand"] = existing_player_dict["right_hand"]
            player["right_knee"] = existing_player_dict["right_knee"]
            player["right_shoe"] = existing_player_dict["right_shoe"]
            player["right_wrist"] = existing_player_dict["right_wrist"]
            player["skin_color"] = existing_player_dict["skin_color"]
            player["sleeves"] = existing_player_dict["sleeves"]
            player["tattoo_left"] = existing_player_dict["tattoo_left"]
            player["tattoo_right"] = existing_player_dict["tattoo_right"]
            player["tendency"] = existing_player_dict["tendency"]
            player["visor"] = existing_player_dict["visor"]
            
            # Construct the next request, for the 'OverTheCap' contracts list page, and pass it the current player.
            # NOTE: The 'dont_filter=True' in the assignment below is CRITICAL, as omitting it will mean the spider 
            # only hits the OTC list once, due to it's default filtering rules preventing duplicates.
            otc_contracts_list_request = Request(
                settings.OTC_CONTRACTS_URL, 
                callback=self.find_contract_pages, 
                dont_filter=True
            )
            otc_contracts_list_request.meta["player"] = player
            return otc_contracts_list_request
        
        # Now handle the cases where we actually had this player in our list last year but the current Madden does not 
        # have a record for him.
        if existing_player_dict:
            
            # Again, since Madden '08 has stricter name length requirements than current Maddens and the NFL.com, we 
            # will want to keep any shortened versions from the existing player dict.
            player["first_name"] = existing_player_dict["first_name"]
            if len(existing_player_dict["first_name"]) > 11:
                logging.error("Found an existing first name longer than 11 chars: %s %s, %s %s;", 
                                existing_player_dict["first_name"], 
                                existing_player_dict["last_name"], 
                                player["team"], 
                                existing_player_dict["position"])
                logging.error("NFL profile page: %s \n", response.url)
            
            player["last_name"] = existing_player_dict["last_name"]
            if len(existing_player_dict["last_name"]) > 13:
                logging.error("Found an existing last name longer than 13 chars: %s %s, %s %s;", 
                                existing_player_dict["first_name"], 
                                existing_player_dict["last_name"], 
                                player["team"], 
                                existing_player_dict["position"])
                logging.error("NFL profile page: %s \n", response.url)
            
            # Choose the best position for this player.
            player["position"] = choose_best_position(
                nfl_position, 
                existing_player_dict["position"], 
                player["first_name"], 
                player["last_name"]
            )
            
            # Try to average the previous Madden values with the ones from NFL.com for height and weight.
            # However, if the difference between the heights is more than 3 inches, we might have a problem.
            if abs(int(nfl_height_inches) - int(existing_player_dict["height"])) > 3:
                logging.error("Heights for %s %s in NFL and Last Year differ by more than 3 in!", 
                              player["first_name"], player["last_name"])
                logging.error("NFL profile page: %s \n", response.url)
            
            # Use the ceiling of the average of the NFL and previous heights.
            player["height"] = int(math.ceil((int(nfl_height_inches) + int(existing_player_dict["height"])) / 2))
            
            # If the difference between the weights is more than 30 lbs, we might have a problem.
            if abs(int(nfl_weight) - int(existing_player_dict["weight"])) > 30:
                logging.error("Weights for %s %s in NFL and Last Year differ by more than 30 lbs!", 
                              player["first_name"], player["last_name"])
                logging.error("NFL profile page: %s \n", response.url)
            
            # Use the ceiling of the average of the NFL and previous weights.
            player["weight"] = int(math.ceil((int(nfl_weight) + int(existing_player_dict["weight"])) / 2))
            
            # For birthdate, age and college, try the NFL values first.
            if nfl_birthdate:
                player["birthdate"] = nfl_birthdate
            else:
                player["birthdate"] = existing_player_dict["birthdate"]
            
            if nfl_age:
                player["age"] = nfl_age
            else:
                player["age"] = existing_player_dict["age"]
                
            if nfl_college:
                player["college"] = nfl_college
            else:
                player["college"] = existing_player_dict["college"]
            
            # In cases where we have a conflict over the number of years pro, resolve things later. 
            if int(nfl_years_pro) != (int(existing_player_dict["years_pro"]) + 1):
                # If we have a big discrepency in years pro, we need to know about this.
                if abs(int(nfl_years_pro) - (int(existing_player_dict["years_pro"]) + 1)) > 1:
                    logging.info("Years pro for %s %s in NFL and (Last Year +1) differ by more than 1.", 
                                 player["first_name"], player["last_name"])
                    logging.info("Years pro in NFL: %s; in Last Year +1: %s", 
                                 nfl_years_pro, int(existing_player_dict["years_pro"]) + 1)
                    logging.info("NFL profile page: %s \n", response.url)
                player["years_pro"] = "CONFLICT"
            else:
                player["years_pro"] = int(existing_player_dict["years_pro"]) + 1
            
            # For roles, just use 45 (none) so we can set some manually while having most of them re-calculated in 
            # Step 5, since the attributes the roles are based on most likely have changed since last year.
            player["role_one"] = 45
            player["role_two"] = 45
            
            # Set the values for the fields listed in the previous year's file using the old values. 
            player["awareness"] = existing_player_dict["awareness"]
            player["speed"] = existing_player_dict["speed"]
            player["acceleration"] = existing_player_dict["acceleration"]
            player["agility"] = existing_player_dict["agility"]
            player["strength"] = existing_player_dict["strength"]
            player["elusiveness"] = existing_player_dict["elusiveness"]
            player["carrying"] = existing_player_dict["carrying"]
            player["trucking"] = existing_player_dict["trucking"]
            player["catching"] = existing_player_dict["catching"]
            player["jumping"] = existing_player_dict["jumping"]
            player["throw_power"] = existing_player_dict["throw_power"]
            player["throw_accuracy_short"] = existing_player_dict["throw_accuracy_short"]
            player["throw_accuracy_mid"] = existing_player_dict["throw_accuracy_mid"]
            player["throw_accuracy_deep"] = existing_player_dict["throw_accuracy_deep"]
            player["throw_on_the_run"] = existing_player_dict["throw_on_the_run"]
            player["playaction"] = existing_player_dict["throw_accuracy"]
            player["pass_block"] = existing_player_dict["pass_block"]
            player["run_block"] = existing_player_dict["run_block"]
            player["tackle"] = existing_player_dict["tackle"]
            player["kick_power"] = existing_player_dict["kick_power"]
            player["kick_accuracy"] = existing_player_dict["kick_accuracy"]
            player["kick_return"] = existing_player_dict["kick_return"]
            player["stamina"] = existing_player_dict["stamina"]
            player["injury"] = existing_player_dict["injury"]
            player["run_block_power"] = existing_player_dict["run_block_strength"]
            player["run_block_finesse"] = existing_player_dict["run_block_footwork"]
            player["pass_block_power"] = existing_player_dict["pass_block_strength"]
            player["pass_block_finesse"] = existing_player_dict["pass_block_footwork"]
            player["break_tackle"] = -1
            player["toughness"] = existing_player_dict["toughness"]
            player["handedness"] = existing_player_dict["handedness"]
            
            # For now, use the Total Salary and Signing Bonus values from the previous year. (For most players, we 
            # will overwrite these with the values from OTC.com later.)
            player["total_salary"] = existing_player_dict["total_salary"]
            player["signing_bonus"] = existing_player_dict["signing_bonus"]
            
            # The remaining fields will be populated with the values from the previous attributes file.
            player["breathing_strip"] = existing_player_dict["breathing_strip"]
            player["eye_black"] = existing_player_dict["eye_black"]
            player["face_id"] = existing_player_dict["face_id"]
            player["face_mask"] = existing_player_dict["face_mask"]
            player["hair_color"] = existing_player_dict["hair_color"]
            player["hair_style"] = existing_player_dict["hair_style"]
            player["helmet"] = existing_player_dict["helmet"]
            player["left_elbow"] = existing_player_dict["left_elbow"]
            player["left_hand"] = existing_player_dict["left_hand"]
            player["left_knee"] = existing_player_dict["left_knee"]
            player["left_shoe"] = existing_player_dict["left_shoe"]
            player["left_wrist"] = existing_player_dict["left_wrist"]
            player["mouthpiece"] = existing_player_dict["mouthpiece"]
            player["neck_pad"] = existing_player_dict["neck_pad"]
            player["nfl_icon"] = existing_player_dict["nfl_icon"]
            player["pro_bowl"] = existing_player_dict["pro_bowl"]
            player["right_elbow"] = existing_player_dict["right_elbow"]
            player["right_hand"] = existing_player_dict["right_hand"]
            player["right_knee"] = existing_player_dict["right_knee"]
            player["right_shoe"] = existing_player_dict["right_shoe"]
            player["right_wrist"] = existing_player_dict["right_wrist"]
            player["skin_color"] = existing_player_dict["skin_color"]
            player["sleeves"] = existing_player_dict["sleeves"]
            player["tattoo_left"] = existing_player_dict["tattoo_left"]
            player["tattoo_right"] = existing_player_dict["tattoo_right"]
            player["tendency"] = existing_player_dict["tendency"]
            player["visor"] = existing_player_dict["visor"]
            
            # Construct the next request, for the 'OverTheCap' contracts list page, and pass it the current player.
            # NOTE: The 'dont_filter=True' in the assignment below is CRITICAL, as omitting it will mean the spider 
            # only hits the OTC list once, due to it's default filtering rules preventing duplicates.
            otc_contracts_list_request = Request(
                settings.OTC_CONTRACTS_URL, 
                callback=self.find_contract_pages, 
                dont_filter=True
            )
            otc_contracts_list_request.meta["player"] = player
            return otc_contracts_list_request
        
        # Next up, we handle the cases where we have only a current Madden record for this player, with nothing in our 
        # previous list.
        if madden_player_dict:
            
            # When we have a difference in names, it is usually because Madden included the suffix on the last name, 
            # but the NFL.com did not. In those cases, we want to keep the suffix, so go with Madden.
            player["first_name"] = madden_player_dict["First Name"]
            if len(madden_player_dict["First Name"]) > 11:
                logging.error("Found a Madden first name longer than 11 chars: %s %s, %s %s;", 
                                madden_player_dict["First Name"], 
                                madden_player_dict["Last Name"], 
                                player["team"], 
                                madden_player_dict["Position"])
                logging.error("NFL profile page: %s \n", response.url)
            
            player["last_name"] = madden_player_dict["Last Name"]
            if len(madden_player_dict["Last Name"]) > 13:
                logging.error("Found a Madden last name longer than 13 chars: %s %s, %s %s;", 
                                madden_player_dict["First Name"], 
                                madden_player_dict["Last Name"], 
                                player["team"], 
                                madden_player_dict["Position"])
                logging.error("NFL profile page: %s \n", response.url)
            
            # Choose the best position for the player using our helper function.
            player["position"] = choose_best_position(
                nfl_position, 
                madden_player_dict["Position"], 
                player["first_name"], 
                player["last_name"]
            )
            
            # If the difference between the heights is more than 3 inches, we might have a problem.
            if abs(int(nfl_height_inches) - int(madden_player_dict["Height"])) > 3:
                logging.error("Heights for %s %s in NFL and Madden differ by more than 3 in!", 
                              player["first_name"], player["last_name"])
                logging.error("NFL profile page: %s \n", response.url)
            
            # Use the ceiling of the average of the two heights.
            player["height"] = int(math.ceil((int(nfl_height_inches) + int(madden_player_dict["Height"])) / 2))
            
            # If the difference between the weights is more than 30 lbs, we might have a problem.
            if abs(int(nfl_weight) - int(madden_player_dict["Weight"])) > 30:
                logging.error("Weights for %s %s in NFL and Madden differ by more than 30 lbs!", 
                              player["first_name"], player["last_name"])
                logging.error("NFL profile page: %s \n", response.url)
            
            # Use the ceiling of the average of the two weights.
            player["weight"] = int(math.ceil((int(nfl_weight) + int(madden_player_dict["Weight"])) / 2))
            
            # For birthdate, age and college, try the NFL values first.
            if nfl_birthdate:
                player["birthdate"] = nfl_birthdate
            else:
                player["birthdate"] = madden_player_dict["Birthdate"]
            
            if nfl_age:
                player["age"] = nfl_age
            else:
                player["age"] = madden_player_dict["Age"]
                
            if nfl_college:
                player["college"] = nfl_college
            else:
                player["college"] = madden_player_dict["College"]
            
            # In cases where we have a conflict over the number of years pro, resolve things later. 
            if int(nfl_years_pro) != int(madden_player_dict["Years Pro"]):
                # If we have a big discrepency in years pro, we need to know about this.
                if abs(int(nfl_years_pro) - int(madden_player_dict["Years Pro"])) > 1:
                    logging.info("Years pro for %s %s in NFL and Madden differ by more than 1.", 
                                 player["first_name"], player["last_name"])
                    logging.info("Years pro in NFL: %s; in Madden: %s", 
                                 nfl_years_pro, madden_player_dict["Years Pro"])
                    logging.info("NFL profile page: %s \n", response.url)
                player["years_pro"] = "CONFLICT"
            else:
                player["years_pro"] = madden_player_dict["Years Pro"]
            
            # For roles, just use 45 (none) so we can set some manually while having most of them re-calculated in 
            # Step 5, since the attributes the roles are based on most likely have changed since last year.
            player["role_one"] = 45
            player["role_two"] = 45
            
            # Set the values for the remaining fields listed in "items.py" as simple pass-throughs from Madden. 
            
            player["awareness"] = madden_player_dict["Awareness"]
            player["speed"] = madden_player_dict["Speed"]
            player["acceleration"] = madden_player_dict["Acceleration"]
            player["agility"] = madden_player_dict["Agility"]
            player["strength"] = madden_player_dict["Strength"]
            player["elusiveness"] = madden_player_dict["Elusiveness"]
            player["carrying"] = madden_player_dict["Carrying"]
            player["trucking"] = madden_player_dict["Trucking"]
            player["catching"] = madden_player_dict["Catching"]
            player["jumping"] = madden_player_dict["Jumping"]
            player["throw_power"] = madden_player_dict["Throw Power"]
            player["throw_accuracy_short"] = madden_player_dict["Throw Accuracy Short"]
            player["throw_accuracy_mid"] = madden_player_dict["Throw Accuracy Mid"]
            player["throw_accuracy_deep"] = madden_player_dict["Throw Accuracy Deep"]
            player["throw_on_the_run"] = madden_player_dict["Throw on the Run"]
            player["playaction"] = madden_player_dict["Playaction"]
            player["pass_block"] = madden_player_dict["Pass Block"]
            player["run_block"] = madden_player_dict["Run Block"]
            player["tackle"] = madden_player_dict["Tackle"]
            player["kick_power"] = madden_player_dict["Kick Power"]
            player["kick_accuracy"] = madden_player_dict["Kick Accuracy"]
            player["kick_return"] = madden_player_dict["Kick Return"]
            player["stamina"] = madden_player_dict["Stamina"]
            player["injury"] = madden_player_dict["Injury"]
            player["run_block_power"] = madden_player_dict["Run Block Power"]
            player["run_block_finesse"] = madden_player_dict["Run Block Finesse"]
            player["pass_block_power"] = madden_player_dict["Pass Block Power"]
            player["pass_block_finesse"] = madden_player_dict["Pass Block Finesse"]
            player["break_tackle"] = madden_player_dict["Break Tackle"]
            player["toughness"] = madden_player_dict["Toughness"]
            player["handedness"] = madden_player_dict["Handedness"]
            player["total_salary"] = madden_player_dict["Total Salary"]
            player["signing_bonus"] = madden_player_dict["Signing Bonus"]
            
            # The remaining fields will be populated with default values.
            player["breathing_strip"] = -1
            player["eye_black"] = -1
            player["face_id"] = -1
            player["face_mask"] = -1
            player["hair_color"] = 0
            player["hair_style"] = 4
            player["helmet"] = -1
            player["left_elbow"] = -1
            player["left_hand"] = -1
            player["left_knee"] = -1
            player["left_shoe"] = -1
            player["left_wrist"] = -1
            player["mouthpiece"] = -1
            player["neck_pad"] = -1
            player["nfl_icon"] = 0
            player["pro_bowl"] = 0
            player["right_elbow"] = -1
            player["right_hand"] = -1
            player["right_knee"] = -1
            player["right_shoe"] = -1
            player["right_wrist"] = -1
            player["skin_color"] = 2
            player["sleeves"] = -1
            player["tattoo_left"] = 0
            player["tattoo_right"] = 0
            player["tendency"] = -1
            player["visor"] = -1
            
            # Construct the next request, for the 'OverTheCap' contracts list page, and pass it the current player.
            # NOTE: The 'dont_filter=True' in the assignment below is CRITICAL, as omitting it will mean the spider 
            # only hits the OTC list once, due to it's default filtering rules preventing duplicates.
            otc_contracts_list_request = Request(
                settings.OTC_CONTRACTS_URL, 
                callback=self.find_contract_pages, 
                dont_filter=True
            )
            otc_contracts_list_request.meta["player"] = player
            return otc_contracts_list_request
        
        
        # We couldn't find a match for this player in either last year's file or the current Madden.
        logging.info("NFL & BOTH FILES: Unable to find a match for %s %s, %s %s.", 
                     nfl_first_name, nfl_last_name, player["team"], nfl_position)
        logging.info("NFL.com: Player profile page url: %s\n", response.url)
        
        # All attributes will be either from NFL.com, OTC.com, or the default values.
        player["first_name"] = nfl_first_name
        if len(nfl_first_name) > 11:
            logging.error("Found an NFL first name longer than 11 chars: %s %s, %s %s;", 
                            nfl_first_name, 
                            nfl_last_name, 
                            player["team"], 
                            nfl_position)
            logging.error("NFL profile page: %s \n", response.url)
        
        player["last_name"] = nfl_last_name
        if len(nfl_last_name) > 13:
            logging.error("Found an NFL last name longer than 13 chars: %s %s, %s %s;", 
                            nfl_first_name, 
                            nfl_last_name, 
                            player["team"], 
                            nfl_position)
            logging.error("NFL profile page: %s \n", response.url)
        
        player["position"] = choose_best_position(
            nfl_position, 
            nfl_position, 
            player["first_name"], 
            player["last_name"]
        )
        player["awareness"] = ""
        player["speed"] = ""
        player["acceleration"] = ""
        player["agility"] = ""
        player["strength"] = ""
        player["elusiveness"] = ""
        player["carrying"] = ""
        player["trucking"] = ""
        player["catching"] = ""
        player["jumping"] = ""
        player["throw_power"] = ""
        player["throw_accuracy_short"] = ""
        player["throw_accuracy_mid"] = ""
        player["throw_accuracy_deep"] = ""
        player["throw_on_the_run"] = ""
        player["playaction"] = ""
        player["pass_block"] = ""
        player["run_block"] = ""
        player["tackle"] = ""
        player["kick_power"] = ""
        player["kick_accuracy"] = ""
        player["kick_return"] = ""
        player["stamina"] = ""
        player["injury"] = ""
        player["run_block_power"] = ""
        player["run_block_finesse"] = ""
        player["pass_block_power"] = ""
        player["pass_block_finesse"] = ""
        player["break_tackle"] = ""
        player["toughness"] = ""
        player["handedness"] = "Right"
        player["height"] = nfl_height_inches
        player["weight"] = nfl_weight
        if nfl_age:
            player["age"] = nfl_age 
        if nfl_birthdate:
            player["birthdate"] = nfl_birthdate
        player["years_pro"] = nfl_years_pro
        player["college"] = nfl_college
        player["total_salary"] = 0
        player["signing_bonus"] = 0
        player["role_one"] = 45
        player["role_two"] = 45
        player["pro_bowl"] = 0
        player["nfl_icon"] = 0
        player["hair_style"] = 4
        player["hair_color"] = 0
        player["tattoo_left"] = 0
        player["tattoo_right"] = 0
        player["tendency"] = -1
        player["face_id"] = -1
        player["sleeves"] = -1
        player["left_hand"] = -1
        player["right_hand"] = -1
        player["left_wrist"] = -1
        player["right_wrist"] = -1
        player["breathing_strip"] = -1
        player["eye_black"] = -1
        player["face_mask"] = -1
        player["helmet"] = -1
        player["left_elbow"] = -1
        player["left_knee"] = -1
        player["left_shoe"] = -1
        player["mouthpiece"] = -1
        player["neck_pad"] = -1
        player["right_elbow"] = -1
        player["right_knee"] = -1
        player["right_shoe"] = -1
        player["skin_color"] = 2
        player["visor"] = -1
        
        # Construct the next request, for the 'OverTheCap' contracts list page, and pass it the current player.
        # NOTE: The 'dont_filter=True' in the assignment below is CRITICAL, as omitting it will mean the spider 
        # only hits the OTC list once, due to it's default filtering rules preventing duplicates.
        otc_contracts_list_request = Request(
            settings.OTC_CONTRACTS_URL, 
            callback=self.find_contract_pages, 
            dont_filter=True
        )
        otc_contracts_list_request.meta["player"] = player
        return otc_contracts_list_request
        
        # These last three lines were what I was originally doing to skip this player record altogether.
        #logging.warning("\t\tSkipping player record altogether!\n")
        #player = NFLPlayer()
        #return player


    def find_contract_pages(self, response):
        """ Scrapes the OverTheCap contracts list page to get a list of links to potential matchs' contract pages. """
        
        # Get the player object out of the meta data for the response.
        player = response.meta["player"]
        
        # Use this section to turn on more verbose logging, even for a specific player.
        verbose_output = False
        # if player["last_name"] == 'Washington':
        #     verbose_output = True
        
        if verbose_output:
            logging.info("Inside find_contract_pages for %s %s, %s %s.\n", 
                         player["first_name"], player["last_name"], player["team"], player["position"])
        
        # Check last names for the presence of suffixes and remove them when found.
        last_name_minus_suffix = check_for_shortened_last_name(remove_suffix(player["last_name"]))
        
        # Fill in the OTC_CONTRACT_LINK_TEMPLATE to get the pattern we will search for in the contracts page.
        # Because OTC uses "curly" apostrophes in the player names, replace regular apostrophes with those.
        # (The pattern helps when we need to try a first initial match, if the full first name match fails.)
        otc_anchor_text_regex = settings.OTC_ANCHOR_REGEX_TEMPLATE.replace(
            "[FIRST_NAME]", player["first_name"].replace("'", u"\u2019"))
        otc_anchor_text_regex = otc_anchor_text_regex.replace(
            "[LAST_NAME]", last_name_minus_suffix.replace("'", u"\u2019"))
        if verbose_output:
            logging.info("%s %s: Initial otc_anchor_text_regex = %s\n", 
                         player["first_name"], player["last_name"], otc_anchor_text_regex)
        
        # Get the list of matches for this regex pattern.
        
        # WORKING!! This gives us a list of all <tr> tags containing the <td> tags which hold <a> tags where the 
        # text() matches the regex.
        # name_match_trs_list = response.xpath(
        #     "//tr/td/a[re:match(text(), \"" + otc_anchor_text_regex + "\")]/../..", 
        #     namespaces={"re": "http://exslt.org/regular-expressions"}
        # ).extract()
        # logging.info("%s %s: name_match_trs_list = %s", 
        #              player["first_name"], player["last_name"], name_match_trs_list)
        
        # This gives us the HREFs of the matched <a> tags in a list.
        urls_for_potential_matches_list = response.xpath(
            "//a[re:match(text(), \"" + otc_anchor_text_regex + "\", 'i')]/@href", 
            namespaces={"re": "http://exslt.org/regular-expressions"}
        ).extract()
        if verbose_output:
            logging.info("%s %s: Initial urls_for_potential_matches_list = %s\n", 
                         player["first_name"], player["last_name"], urls_for_potential_matches_list)
        
        # If we can't find text in an anchor tag that matches the full name, ...
        if not urls_for_potential_matches_list:
            
            if verbose_output:
                logging.info("OTC: Unable to find full first & last match for %s %s.\n", 
                             player["first_name"], player["last_name"])
            
            # ... then try matching the last name and just the first initial. 
            # (E.g. Matthew Stafford is called Matt Stafford on OTC.)
            otc_anchor_text_regex = settings.OTC_ANCHOR_REGEX_TEMPLATE.replace(
                "[FIRST_NAME]", player["first_name"][0])
            otc_anchor_text_regex = otc_anchor_text_regex.replace(
                "[LAST_NAME]", last_name_minus_suffix.replace("'", u"\u2019"))
            
            # Get the list of matches for this regex pattern.
            urls_for_potential_matches_list = response.xpath(
                "//a[re:match(text(), \"" + otc_anchor_text_regex + "\", 'i')]/@href",
                namespaces={"re": "http://exslt.org/regular-expressions"}
            ).extract()
            
            if not urls_for_potential_matches_list:
                
                logging.info("Unable to find even partial name match on OTC for %s %s, %s %s.", 
                             player["first_name"], 
                             player["last_name"], 
                             player["team"], 
                             player["position"])
                logging.info("Skipping OTC player contract page.\n")
                
                # Return the player to the pipeline for writing to the output file.
                return player
            
            if verbose_output:
                logging.info("%s %s: Secondary urls_for_potential_matches_list = %s\n", 
                             player["first_name"], player["last_name"], urls_for_potential_matches_list)
        
        # In either case (full name or first initial only), we must have at least one element in our 
        # urls_for_potential_matches_list now. (In fact, we will often have multiple matches.) 
        
        # Request the first link in the list, and pass along the player object and the rest of the list.
        otc_contract_page_request = Request(
            "https://overthecap.com" + urls_for_potential_matches_list[0], 
            callback=self.parse_otc_contract_page, 
            dont_filter=True
        )
        otc_contract_page_request.meta["player"] = player
        otc_contract_page_request.meta["urls_for_potential_matches_list"] = urls_for_potential_matches_list[1:]
        return otc_contract_page_request


    def parse_otc_contract_page(self, response):
        """ 
        Scrapes the OTC contract details page for a player to 1) see if this player is a match for our current player 
        object and, if so, 2) get details on his contract, years pro, and draft history. 
        """
        
        # Get the player object out of the response's meta data.
        player = response.meta["player"]
        
        # Check last names for the presence of suffixes and remove them when found.
        last_name_minus_suffix = check_for_shortened_last_name(remove_suffix(player["last_name"]))
        
        # Use this section to turn on more verbose logging for a specific player.
        verbose_output = False
        # if player["last_name"] == 'Washington':
        #     verbose_output = True
        
        # Also need to get the list with other URLs of potential matches for this player.
        urls_for_potential_matches_list = response.meta["urls_for_potential_matches_list"]
        if verbose_output:
            logging.info("Inside parse_otc_contract_page for %s %s.\n", player["first_name"], player["last_name"])
        
        # Initialize our OTC variables so we at least have them, even if they don't get real values.
        otc_age = ""
        otc_height_inches = ""
        otc_weight = ""
        otc_college = ""
        otc_first_name = ""
        otc_last_name = ""
        otc_position = ""
        otc_total_salary = ""
        otc_signing_bonus = ""
        
        # Get the values we need to have in order to try and match this page with the player object.
        # The player's age should be found in the <li class="age">.
        otc_age_list = response.xpath("//li[@class=\"age\"]/text()").extract()
        if otc_age_list:
            # These strings should be something like ['Age:', '28']
            otc_age_strings = otc_age_list[0].split(" ")
            if len(otc_age_strings) == 2:
                # This should give us something like "28".
                otc_age = otc_age_strings[1]
                if verbose_output:
                    logging.info("%s %s's OTC age = %s\n", player["first_name"], player["last_name"], otc_age)
            else:
                logging.warning("%s %s's len(otc_age_strings) was NOT 2, it was %d.", 
                                player["first_name"], player["last_name"], len(otc_age_strings))
                logging.warning("OTC contract page: %s \n", response.url)
        
        # The player's height should be found in the <li class="height">.
        otc_height_list = response.xpath("//li[@class=\"height\"]/text()").extract()
        if otc_height_list:
            otc_height_strings = otc_height_list[0].split(": ")
            if len(otc_height_strings) == 2 and len(otc_height_strings[1]) > 3:
                try:
                    otc_height_inches = (int(otc_height_strings[1][0]) * 12) + int(otc_height_strings[1][2:-1])
                except ValueError:
                    pass
                if verbose_output:
                    logging.info("%s %s's OTC height in inches = %s\n", 
                                 player["first_name"], player["last_name"], otc_height_inches)
            else:
                logging.warning("%s %s's otc_height_strings were not long enough. No otc_height for him.", 
                                player["first_name"], player["last_name"])
                logging.warning("OTC contract page: %s \n", response.url)
        
        # The player's weight should be found in the <li class="weight">.
        otc_weight_list = response.xpath("//li[@class=\"weight\"]/text()").extract()
        if otc_weight_list:
            otc_weight_strings = otc_weight_list[0].split(": ")
            if len(otc_weight_strings) == 2:
                otc_weight = otc_weight_strings[1]
                if verbose_output:
                    logging.info("%s %s's OTC weight = %s\n", player["first_name"], player["last_name"], otc_weight)
            else:
                logging.warning("%s %s's len(otc_weight_strings) was NOT 2, it was %d.", 
                                player["first_name"], player["last_name"], len(otc_weight_strings))
                logging.warning("OTC contract page: %s \n", response.url)
        
        # The player's college should be found in the <li class="college">.
        otc_college_list = response.xpath("//li[@class=\"college\"]/text()").extract()
        if otc_college_list:
            otc_college_strings = otc_college_list[0].split(": ")
            if len(otc_college_strings) == 2:
                otc_college = otc_college_strings[1]
                if verbose_output:
                    logging.info("%s %s's OTC college = %s", player["first_name"], player["last_name"], otc_college)
            else:
                logging.warning("%s %s's len(otc_college_strings) was NOT 2, it was %d.", 
                                player["first_name"], player["last_name"], len(otc_college_strings))
                logging.warning("OTC contract page: %s \n", response.url)
        
        # The player's name, position, total_salary ("Total"), and signing_bonus ("Guarantee") are all found inside 
        # the <div id="player-comparisons-data" ...>, in a nested <code> tag.
        otc_data_code_list = response.xpath("//div[@id=\"player-comparisons-data\"]/code/text()").extract()
        if verbose_output:
            logging.info(
                "%s %s otc_data_code_list = %s\n", 
                player["first_name"], 
                player["last_name"], 
                otc_data_code_list
            )
        
        if otc_data_code_list:
            
            # Furthermore, the <code> contains a comma-separated dict of keys and values.
            # Split the dict by element (on the commas, not any other delimiters else yet).
            otc_data_elements_list = otc_data_code_list[0].split('","')
            if verbose_output:
                logging.info("%s %s otc_data_elements_list = %s\n", 
                             player["first_name"], player["last_name"], otc_data_elements_list)
            
            # The player's name should be in the first element, as '{"Name":"Cam Newton'.
            if (otc_data_elements_list) and ("NAME" in otc_data_elements_list[0].upper()):
                
                # Split the name element on the ":".
                otc_name_text_list = otc_data_elements_list[0].split(":")
                
                if len(otc_name_text_list) == 2:
                    
                    # Take the quotes off the front of the name.
                    otc_full_name = otc_name_text_list[1][1:]
                    
                    # Use our helper functions to get the first and last names.
                    otc_first_name = get_first_name(otc_full_name) # eg. "Prince Charles"
                    otc_last_name = get_last_name(otc_full_name) # eg. "Iworah"
                    if verbose_output:
                        logging.info("%s %s's OTC name: %s %s\n", 
                                     player["first_name"], player["last_name"], otc_first_name, otc_last_name)
                    
                else:
                    logging.warning("%s %s's len(otc_name_text_list) was NOT 2, it was %d.", 
                                    player["first_name"], player["last_name"], len(otc_name_text_list))
                    logging.warning("OTC contract page: %s \n", response.url)
            else:
                logging.warning("No NAME element in %s %s's otc_data_elements_list: %s", 
                                player["first_name"], player["last_name"], otc_data_elements_list)
                logging.warning("OTC contract page: %s \n", response.url)
            
            # The position element should be second, as something like 'Position":"QB'.
            if len(otc_data_elements_list) > 1:
                
                # Split the position element on the ":".
                otc_pos_text_list = otc_data_elements_list[1].split(":")
                
                # The text in the second element should be something like '"QB', so extract it and remove the quotes.
                if len(otc_pos_text_list) == 2:
                    otc_position = otc_pos_text_list[1][1:]
                    if verbose_output:
                        logging.info("%s %s's OTC Position: %s\n", 
                                     player["first_name"], player["last_name"], otc_position)
                else:
                    logging.warning("%s %s's len(otc_pos_text_list) was NOT 2, it was %d.", 
                                    player["first_name"], player["last_name"], len(otc_pos_text_list))
                    logging.warning("OTC contract page: %s \n", response.url)
                
                # Now get the total salary.
                if len(otc_data_elements_list) > 2:
                    
                    # Split the total salary element on the ":".
                    otc_total_salary_text_list = otc_data_elements_list[2].split(":")
                    
                    # The text in the salary element should be something like '"103000000', so remove the quotes.
                    if len(otc_total_salary_text_list) == 2:
                        otc_total_salary = otc_total_salary_text_list[1][1:]
                        if verbose_output:
                            logging.info("%s %s's OTC Total Salary: %s\n", 
                                         player["first_name"], player["last_name"], otc_total_salary)
                    else:
                        logging.warning("%s %s's len(otc_total_salary_text_list) was NOT 2, it was %d.", 
                                        player["first_name"], player["last_name"], len(otc_total_salary_text_list))
                        logging.warning("OTC contract page: %s \n", response.url)
                    
                    # Now look for the signing bonus (guarantee).
                    if len(otc_data_elements_list) > 4:
                        
                        # Split the signing bonus element on the ":".
                        otc_signing_bonus_text_list = otc_data_elements_list[4].split(":")
                        
                        if len(otc_signing_bonus_text_list) == 2:
                            otc_signing_bonus = otc_signing_bonus_text_list[1][1:]
                            if verbose_output:
                                logging.info("%s %s's OTC Signing Bonus: %s", 
                                             player["first_name"], player["last_name"], otc_signing_bonus)
                        else:
                            logging.warning("%s %s's len(otc_signing_bonus_text_list) was NOT 2, it was %d.", 
                                            player["first_name"], 
                                            player["last_name"], 
                                            len(otc_signing_bonus_text_list))
                            logging.warning("OTC contract page: %s \n", response.url)
                    
                    else:
                        logging.warning("Less than 5 elements in %s %s's otc_data_elements_list: %s", 
                                        player["first_name"], player["last_name"], otc_data_elements_list)
                        logging.warning("OTC contract page: %s \n", response.url)
                
                else:
                    logging.warning("Only 2 elements in %s %s's otc_data_elements_list: %s", 
                                    player["first_name"], player["last_name"], otc_data_elements_list)
                    logging.warning("OTC contract page: %s \n", response.url)
            
            else:
                logging.warning("Only 1 element in %s %s's otc_data_elements_list: %s", 
                                player["first_name"], player["last_name"], otc_data_elements_list)
                logging.warning("OTC contract page: %s \n", response.url)
        
        else:
            logging.error("%s %s has no otc_data_code_list!", player["first_name"], player["last_name"])
            logging.error("OTC contract page: %s \n", response.url)
        
        # Now to try and make a match between the player object and the values from this page.
        otc_match = False
        
        # First, try to match on full name, age, and position.
        if otc_first_name and otc_last_name and otc_age and otc_position and ("age" in player):
            
            if (otc_first_name.lower() == player["first_name"].lower() and 
                    otc_last_name.lower() == last_name_minus_suffix.lower() and 
                    abs(int(otc_age) - int(player["age"])) < 2 and 
                    positions_are_similar(otc_position, player["position"])):
                
                # Declare a match.
                otc_match = True
                if verbose_output:
                    logging.info("OTC Match for %s %s: full name, age, and position.\n", 
                                 player["first_name"], player["last_name"])
        
        # If we don't have age, try full name, college, and position.
        if (not otc_match) and (not otc_age) and (otc_first_name and otc_last_name and otc_college and otc_position):
            
            if (otc_first_name.lower() == player["first_name"].lower() and 
                    otc_last_name.lower() == last_name_minus_suffix.lower() and 
                    otc_college[:5].lower() == player["college"][:5].lower() and 
                    positions_are_similar(otc_position, player["position"])):
                
                # Declare a match.
                otc_match = True
                if verbose_output:
                    logging.info("OTC Match for %s %s: full name, college, and position.\n", 
                                 player["first_name"], player["last_name"])
        
        # If full name didn't match, try just age, position, college, height, and weight.
        if (not otc_match) and (
                otc_age and otc_position and otc_college and otc_height_inches and otc_weight and ("age" in player)):
            
            if (abs(int(otc_age) - int(player["age"])) < 2 and 
                    positions_are_similar(otc_position, player["position"]) and 
                    otc_college[:5].lower() == player["college"][:5].lower() and 
                    abs(int(otc_height_inches) - int(player["height"])) < 2 and 
                    abs(int(otc_weight) - int(player["weight"])) < 20):
                
                # Declare a match.
                otc_match = True
                if verbose_output:
                    logging.info("OTC Match for %s %s: age, position, college, height, and weight.\n", 
                                 player["first_name"], player["last_name"])
        
        # If we don't have an age, but we have the other attributes, try with the other values.
        if (not otc_match) and (not otc_age) and (
                otc_position and otc_first_name and otc_last_name and otc_height_inches and otc_weight):
            
            if (positions_are_similar(otc_position, player["position"]) and 
                    otc_first_name.lower() == player["first_name"].lower() and 
                    otc_last_name.lower() == last_name_minus_suffix.lower() and 
                    abs(int(otc_height_inches) - int(player["height"])) < 2 and 
                    abs(int(otc_weight) - int(player["weight"])) < 25):
                
                # Declare a match.
                otc_match = True
                if verbose_output:
                    logging.info("OTC Match for %s %s: position, college, height, and weight.\n", 
                                 player["first_name"], player["last_name"])
        
        # If we STILL can't make a match, maybe it's time to concede that this page is not the page we're looking for.
        if not otc_match:
            
            # If we have more potential matches, build the request object with the necessary meta objects.
            if urls_for_potential_matches_list:
                next_contract_url = urls_for_potential_matches_list[0]
                next_contract_request = Request(
                    "https://overthecap.com" + next_contract_url, 
                    callback=self.parse_otc_contract_page, 
                    dont_filter=True
                )
                next_contract_request.meta["player"] = player
                next_contract_request.meta["urls_for_potential_matches_list"] = []
                if len(urls_for_potential_matches_list) > 1:
                    next_contract_request.meta["urls_for_potential_matches_list"] = \
                            urls_for_potential_matches_list[1:]
                
                # Pass along the next request for our spider to crawl.
                return next_contract_request
            
            # We are at the end of the list of potential matches, and couldn't find a match.
            logging.info("No OTC contract page match found for %s %s, %s %s.\n", 
                         player["first_name"], player["last_name"], player["team"], player["position"])
            return player
        
        # At this point, we have found a match. Before doing anything else, let the user know if there was missing 
        # information on this player's page.
        if (not otc_age) and verbose_output:
            logging.info("%s %s has no age on OTC.\n", otc_first_name, otc_last_name)
        
        if (not otc_height_inches) and verbose_output:
            logging.info("%s %s has no height on OTC.\n", otc_first_name, otc_last_name)
        
        if (not otc_weight) and verbose_output:
            logging.info("%s %s has no weight on OTC.\n", otc_first_name, otc_last_name)
        
        if (not otc_college) and verbose_output:
            logging.info("%s %s has no college on OTC.\n", otc_first_name, otc_last_name)
        
        # Now to grab the contract and draft into for this player.
        # Start with the total salary on this deal, which we scraped earlier.
        if otc_total_salary:
            player["total_salary"] = otc_total_salary
        
        # We also should have scraped the signing bonus total from the otc_data_elements_list above.
        if otc_signing_bonus:
            player["signing_bonus"] = otc_signing_bonus
        
        # Get the <li class="league-entry">. This and subsequent <li>s have draft, year signed, and contract info.
        league_entry_li_list = response.xpath("//li[@class=\"league-entry\"]/text()").extract()
        if verbose_output:
            logging.info("%s %s's OTC league_entry_li_list = %s\n", 
                         player["first_name"], player["last_name"], league_entry_li_list)
        
        if not league_entry_li_list:
            logging.info("%s %s's OTC league_entry_li_list is empty.", player["first_name"], player["last_name"])
            logging.info("Skipping draft_pick, draft_round, years_pro, contract_length, and years_left.")
            logging.info("OTC contract page: %s \n", response.url)
            return player
        
        # When not empty, the text is the first (and only) element in the list.
        otc_draft_text = league_entry_li_list[0]
        
        # First, see when this player was drafted, or if he is listed as having been undrafted.
        if "UNDRAFTED" in otc_draft_text.upper():
            # For the Madden roster file, undrafted requires draft round = 15 and draft pick = 63.
            player["draft_round"] = "15"
            if verbose_output:
                logging.info("%s %s's OTC draft_round = %s\n", 
                             player["first_name"], player["last_name"], player["draft_round"])
            player["draft_pick"] = "63"
            if verbose_output:
                logging.info("%s %s's OTC draft_pick = %s\n", 
                             player["first_name"], player["last_name"], player["draft_pick"])
        else:
            # Split the string on commas.
            otc_draft_strings_list = otc_draft_text.split(",")
            # We should have three strings in the list.
            if len(otc_draft_strings_list) != 3:
                logging.info("%s %s's OTC len(otc_draft_strings_list) is not 3; it's %d.", 
                             player["first_name"], player["last_name"], len(otc_draft_strings_list))
                logging.info("Skipping his draft info.")
                logging.info("OTC contract page: %s \n", response.url)
            else:
                # The draft round number should be in the second element, last character.
                player["draft_round"] = otc_draft_strings_list[1][-1:]
                if verbose_output:
                    logging.info("%s %s's OTC draft_round = %s\n", 
                                 player["first_name"], player["last_name"], player["draft_round"])
                
                # The draft pick number should be in the third string - all chars except the first one in the 
                # first element of the list made when we strip the string and split it on spaces.
                otc_pick_number = otc_draft_strings_list[2].strip().split(" ")[0][1:]
                # The number Madden expects is not the overall pick number, but the number in the given round.
                # So subtract (number of previous rounds * 32) from the pick to get Madden's number. 
                player["draft_pick"] = int(otc_pick_number) - ((int(otc_draft_strings_list[1][-1:]) - 1) * 32)
                if verbose_output:
                    logging.info("%s %s's OTC draft_pick = %s\n", 
                                 player["first_name"], player["last_name"], player["draft_pick"])
        
        # Get this player's number of years pro by calculating the differnce between this (football) year 
        # and the year he was (un)drafted.
        this_football_year = datetime.datetime.now().year if (datetime.datetime.now().month > 4) else \
                (datetime.datetime.now().year - 1)
        # The player's year of entry is always the second string in the text when split on whitespace.
        player["years_pro"] = this_football_year - int(otc_draft_text.split()[1])
        
        # The year this player will be a free agent is in the third <li> after the one with class="league-entry".
        otc_year_free_agency_list = response.xpath(
            "//li[@class=\"league-entry\"]/following-sibling::*[3]/text()"
        ).extract()
        if otc_year_free_agency_list:
            otc_year_free_agency = otc_year_free_agency_list[0].split()[2]
            # If this string has a comma on the end, ut it off.
            if len(otc_year_free_agency) == 5:
                otc_year_free_agency = otc_year_free_agency[:-1]
            
            # The year the current contract was signed is in the first <li> after the one with class="eague-entry".
            otc_year_contract_signed_list = response.xpath(
                "//li[@class=\"league-entry\"]/following-sibling::*[1]/text()"
            ).extract()
            if otc_year_contract_signed_list:
                otc_year_contract_signed = otc_year_contract_signed_list[0].split()[2]
                # The contract length is found by calculating the difference between the year of free agency and 
                # the year the contract was signed.
                player["contract_length"] = int(otc_year_free_agency) - int(otc_year_contract_signed)
                if verbose_output:
                    logging.info("%s %s's OTC contract_length = %s\n", 
                                 player["first_name"], player["last_name"], player["contract_length"])
                
                # The number of years left on the contract is found by calculating the difference between the year 
                # of free agency and the current (football) year.
                player["contract_years_left"] = int(otc_year_free_agency) - this_football_year
                if verbose_output:
                    logging.info("%s %s's OTC contract_years_left = %s\n", 
                                 player["first_name"], player["last_name"], player["contract_years_left"])
            
        # Return our player object for writing to the output CSV file.
        return player


# ----------------------------------------------------- SECTION 3 -----------------------------------------------------
# ------------------------------------------------- Helper Functions --------------------------------------------------


def remove_suffix(name):
    """ Removes any typical suffix (" Jr.", " III", etc.) from a last name. """
    suffixes = [" jr", " jr.", " sr", " sr.", " ii", " iii", " iv", " v", " vi", " vii", " viii", " ix", " x", " 3d"]
    for suffix in suffixes:
        if name.lower().endswith(suffix):
            return name[:-len(suffix)]
    return name


def get_first_name(full_name):
    """ Pulls the first name out of a string containing a FULL NAME (with first, last, suffix, etc). """
    
    # If the full name we are given is empty, we have a problem.
    if not full_name:
        logging.error("\nget_first_name: Found an empty full name.")
        logging.error("\t\tNEED TO FIX WHATEVER CAUSED THIS.\n")
        return full_name
    
    # If we have a name that can't be split on whitespace, something is wrong.
    if len(full_name.split()) == 1:
        logging.error("\nget_first_name: Found a full name that splits into only one part: %s", full_name)
        logging.error("\t\tNEED TO FIX WHATEVER CAUSED THIS.\n")
        return full_name
    
    # When the name has only two parts, we assume they are just the first and last name.
    if len(full_name.split()) == 2:
        return full_name.split()[0]
        
    # When we have more than 2 name parts, first get rid of any suffixes.
    split_name_without_suffix = remove_suffix(full_name).split()
    
    # If we now have a name with only two parts, assume they are just the first and last name.
    if len(split_name_without_suffix) == 2:
        return split_name_without_suffix[0]
    
    # Now we must have a name with three parts but no identified suffix.
    # If the middle name part is a last name prefix, treat it as part of the last name.
    if (split_name_without_suffix[1].lower() == "de" or 
            split_name_without_suffix[1].lower() == "jean" or 
            split_name_without_suffix[1].lower() == "van" or 
            split_name_without_suffix[1].lower() == "vander" or 
            split_name_without_suffix[1].lower() == "st."):
        return split_name_without_suffix[0]
    
    # In all other cases, treat the middle part as part of the first name.
    return split_name_without_suffix[0] + " " + split_name_without_suffix[1]


def get_last_name(full_name):
    """ Pulls the last name out of a string containing a FULL NAME (with first, last, suffix, etc). """
    
    # If the full name we are given is empty, we have a problem.
    if not full_name:
        logging.error("\nget_first_name: Found an empty full name.")
        logging.error("\t\tNEED TO FIX WHATEVER CAUSED THIS.\n")
        return full_name
    
    # If we have a name that can't be split on whitespace, something is wrong.
    if len(full_name.split()) == 1:
        logging.error("\nget_first_name: Found a full name that splits into only one part: %s", full_name)
        logging.error("\t\tNEED TO FIX WHATEVER CAUSED THIS.\n")
        return full_name
    
    # When the name has only two parts, we assume they are just the first and last name.
    if len(full_name.split()) == 2:
        return full_name.split()[1]
        
    # When we have more than 2 name parts, first get rid of any suffixes.
    split_name_without_suffix = remove_suffix(full_name).split()
    
    # If we now have a name with only two parts, assume they are just the first and last name.
    if len(split_name_without_suffix) == 2:
        return split_name_without_suffix[1]
    
    # Now we must have a name with three parts but no identified suffix.
    # If the middle name part is a last name prefix, treat it as part of the last name.
    if (split_name_without_suffix[1].lower() == "de" or 
            split_name_without_suffix[1].lower() == "jean" or 
            split_name_without_suffix[1].lower() == "van" or 
            split_name_without_suffix[1].lower() == "vander" or 
            split_name_without_suffix[1].lower() == "st."):
        return split_name_without_suffix[1] + " " + split_name_without_suffix[2]
    
    # In all other cases, treat the middle as part of the first name, and just return the third part.
    return split_name_without_suffix[2]


def check_for_shortened_first_name(existing_first_name):
    """
    This function compares the value of the first name from the previous year's attributes file to a list of those 
    first names which have been shortened, returning the original, longer name if found, and the supplied name if not.
    """
    # If this first name is in the list, return the original version (so it will match Madden and the NFL.com).
    if existing_first_name == "Charcandrk.":
        return "Charcandrick"
    if existing_first_name == "Pr. Charles":
        return "Prince Charles"
    if existing_first_name == "Charmeache.":
        return "Charmeachealle"
    if existing_first_name == "Halapouli.":
        return "Halapoulivaati"
    return existing_first_name


def check_for_shortened_last_name(existing_last_name):
    """
    This function compares the value of the last name from the previous year's attributes file to a list of those 
    last names which have been shortened, returning the original, longer name if found, and the supplied name if not.
    """
    # If this last name is in the list, return the original version (so it will match Madden and the NFL.com).
    if existing_last_name == "Duvernay-T.":
        return "Duvernay-Tardif"
    if existing_last_name == "Seferian-J.":
        return "Seferian-Jenkins"
    if existing_last_name == "Robertson-H.":
        return "Robertson-Harris"
    if existing_last_name == "Houston-Cars.":
        return "Houston-Carson"
    if existing_last_name == "Garcia-Wllms.":
        return "Garcia-Williams"
    if existing_last_name == "Rodgers-Crom.":
        return "Rodgers-Cromartie"
    if existing_last_name == "Harvey-Clmns.":
        return "Harvey-Clemons"
    if existing_last_name == "Roethlisberg.":
        return "Roethlisberger"
    if existing_last_name == "Smith-Schstr.":
        return "Smith-Schuster"
    return existing_last_name


def positions_are_similar(nfl_or_otc_position, second_position):
    """
    This function compares the value of either the NFL.com or OTC.com's position string to the value in a Madden 
    record to see if they are similar enough to be considered a match.
    """
    # If either position is QB and the other isn't, the answer is no.
    if nfl_or_otc_position.upper() == "QB":
        return bool(second_position.upper() == "QB")
    
    # If the first position is RB, HB, FB, WR, or TE, second_position can be: HB, FB, WR, or TE.
    if nfl_or_otc_position.upper() in ["RB", "HB", "FB", "WR", "TE"]:
        return bool(second_position.upper() in ["HB", "FB", "WR", "TE"])
    
    # If the first position is OL, T, OT, G, OG, LT, LG, C, RG, or RT, 
    # second_position can be: LT, LG, C, RG, or RT.
    if nfl_or_otc_position.upper() in ["OL", "T", "OT", "G", "OG", "LT", "LG", "C", "RG", "RT"]:
        return bool(second_position.upper() in ["LT", "LG", "C", "RG", "RT"])
    
    # If the first position is LS, 
    # second_position can be: LT, LG, C, RG, RT, or TE.
    if nfl_or_otc_position.upper() == "LS":
        return bool(second_position.upper() in ["LT", "LG", "C", "RG", "RT", "TE"])
    
    # If the first position is DL, DE, LE, RE, 34DE, 43DE,
    # second_position can be: LE, RE, DT, LOLB, ROLB, or MLB.
    if nfl_or_otc_position.upper() in ["DL", "DE", "LE", "RE", "34DE", "43DE"]:
        return bool(second_position.upper() in ["LE", "RE", "DT", "LOLB", "ROLB", "MLB"])
    
    # If the first position is DT, NT, 34DT, or 43DT, second_position can be: LE, RE, or DT.
    if nfl_or_otc_position.upper() in ["DT", "NT", "34DT", "43DT"]:
        return bool(second_position.upper() in ["LE", "RE", "DT"])
    
    # If the first position is LB, OLB, LOLB, ROLB, ILB, MLB, 34OLB, 43OLB
    # second_position can be: LE, RE, LOLB, ROLB, or MLB.
    if nfl_or_otc_position.upper() in ["LB", "OLB", "LOLB", "ROLB", "ILB", "MLB", "34OLB", "43OLB"]:
        return bool(second_position.upper() in ["LE", "RE", "LOLB", "ROLB", "MLB"])
    
    # If the first position is DB, CB, S, SAF, FS, or SS, second_position can be: CB, FS, or SS.
    if nfl_or_otc_position.upper() in ["DB", "CB", "S", "SAF", "FS", "SS"]:
        return bool(second_position.upper() in ["CB", "FS", "SS"])
    
    # If either position is K or P and the other isn't one of those, the answer is no.
    if nfl_or_otc_position.upper() in ["K", "P"]:
        return bool(second_position.upper() in ["K", "P"])
    
    logging.error("Unknown nfl_or_otc_position passed to positions_are_similar:")
    logging.error("nfl_or_otc_position.upper() = %s", nfl_or_otc_position.upper())
    logging.error("second_position.upper() = %s\n", second_position.upper())
    return False


def report_position_disagreement(severity, nfl_position, second_position, first_name, last_name):
    """
    This function is called when the function "choose_best_position" receives two position identifiers which are not 
    in full agreement. It prints a message as either a warning or an error (depending on the severity of the conflict) 
    and includes details on the player's name and reported positions.
    """
    if severity.upper() == "INFO":
        logging.info("choose_best_position: NFL and Madden in general agreement, but not matching for %s %s.", 
                     first_name, last_name)
        logging.info("nfl_position.upper() = %s", nfl_position.upper())
        logging.info("second_position.upper() = %s\n", second_position.upper())
    else:
        logging.error("choose_best_position: NFL and Madden are in conflict for %s %s.", 
                      first_name, last_name)
        logging.error("nfl_position.upper() = %s", nfl_position.upper())
        logging.error("second_position.upper() = %s\n", second_position.upper())


def choose_best_position(nfl_position, second_position, first_name, last_name):
    """
    This function takes in two position strings for a player (found on NFL.com and in the latest Madden ratings) and 
    uses them in determining which Madden position to assign to this player. If no determination can be made, but the 
    input positions were in general agreement, we assign the Madden position, and raise a warning. If the positions 
    are not in agreement, we assign "CONFLICT" and raise an error, since any "CONFLICT"s will require manual 
    reconciliation later.
    """
    # QB is easy.
    if nfl_position.upper() == "QB":
        if second_position.upper() == "QB":
            return "QB"
        report_position_disagreement("ERROR", nfl_position, second_position, first_name, last_name)
        return "CONFLICT"
    
    # If nfl_position is RB or HB, try to go off of what we have in second_position.
    if nfl_position.upper() == "RB" or nfl_position.upper() == "HB":
        if second_position.upper() in ["HB", "FB"]:
            return second_position.upper()
        if second_position.upper() in ["WR", "TE"]:
            report_position_disagreement("INFO", nfl_position, second_position, first_name, last_name)
            return second_position.upper()
        if second_position.upper() == "RB":
            return "HB"
        report_position_disagreement("ERROR", nfl_position, second_position, first_name, last_name)
        return "CONFLICT"
    
    # FB is special - assume it is correct even over HB; also similar enough to WR and TE.
    if nfl_position.upper() == "FB":
        if second_position.upper() in ["WR", "TE"]:
            report_position_disagreement("INFO", nfl_position, second_position, first_name, last_name)
            return "FB"
        if second_position.upper() in ["HB", "FB"]:
            return "FB"
        report_position_disagreement("ERROR", nfl_position, second_position, first_name, last_name)
        return "CONFLICT"
    
    # If nfl_position is WR, we are similar to HB and FB, and in agreement with WR and TE.
    if nfl_position.upper() == "WR":
        if second_position.upper() in ["HB", "FB"]:
            report_position_disagreement("INFO", nfl_position, second_position, first_name, last_name)
            return second_position.upper()
        if second_position.upper() in ["WR", "TE"]:
            return second_position.upper()
        report_position_disagreement("ERROR", nfl_position, second_position, first_name, last_name)
        return "CONFLICT"
    
    # If nfl_position is TE, we are similar to HB and WR, and in agreement with FB and TE.
    if nfl_position.upper() == "TE":
        if second_position.upper() in ["HB", "WR"]:
            report_position_disagreement("INFO", nfl_position, second_position, first_name, last_name)
            return second_position.upper()
        if second_position.upper() in ["FB", "TE"]:
            return second_position.upper()
        report_position_disagreement("ERROR", nfl_position, second_position, first_name, last_name)
        return "CONFLICT"
    
    # If nfl_position is any OL or LS, try to go off of what we have in second_position.
    if nfl_position.upper() in ["T", "OT", "LT", "RT", "G", "OG", "LG", "RG", "C", "OL", "LS"]:
        if second_position.upper() in ["LT", "LG", "C", "RG", "RT", "TE"]:
            return second_position.upper()
        if second_position.upper() in ["T", "OT"]:
            # Alternate between LT and RT when the second position is a T from NFL.com, but not specific enough. 
            if NFLSpider.choose_lt is True:
                NFLSpider.choose_lt = False
                return "LT"
            NFLSpider.choose_lt = True
            return "RT"
        if second_position.upper() in ["G", "OG", "OL"]:
            # Alternate between LG and RG when the second position is a G or OL from NFL.com, but not specific enough. 
            if NFLSpider.choose_lg is True:
                NFLSpider.choose_lg = False
                return "LG"
            NFLSpider.choose_lg = True
            return "RG"
        if second_position.upper() == "LS":
            # Use C when the second position is a LS from NFL.com. 
            return "C"
        report_position_disagreement("ERROR", nfl_position, second_position, first_name, last_name)
        return "CONFLICT"
    
    # If nfl_position is DL, try to go off of what we have in second_position.
    if nfl_position.upper() in ["DL", "DE", "LE", "RE", "DT", "NT"]:
        if second_position.upper() in ["LOLB", "ROLB", "MLB"]:
            report_position_disagreement("INFO", nfl_position, second_position, first_name, last_name)
            return second_position.upper()
        if second_position.upper() in ["LE", "RE", "DT"]:
            return second_position.upper()
        # Alternate between LE and RE when the second position is a DE or DL from NFL.com, but not specific enough.
        if second_position.upper() in ["DL", "DE"]:
            if NFLSpider.choose_le is True:
                NFLSpider.choose_le = False
                return "LE"
            NFLSpider.choose_le = True
            return "RE"
        # Use DT when the second position is also NT from NFL.com.
        if second_position.upper() == "NT":
            return "DT"
        report_position_disagreement("ERROR", nfl_position, second_position, first_name, last_name)
        return "CONFLICT"
    
    # If nfl_position is LB, try to go off of what we have in second_position.
    if nfl_position.upper() in ["LB", "OLB", "LOLB", "ROLB", "ILB", "MLB"]:
        if second_position.upper() in ["LE", "RE"]:
            report_position_disagreement("INFO", nfl_position, second_position, first_name, last_name)
            return second_position.upper()
        if second_position.upper() in ["LOLB", "ROLB", "MLB"]:
            return second_position.upper()
        # Alternate between LOLB and ROLB when the second position is LB or OLB from NFL.com, but not specific enough.
        if second_position.upper() in ["LB", "OLB"]:
            if NFLSpider.choose_lolb is True:
                NFLSpider.choose_lolb = False
                return "LOLB"
            NFLSpider.choose_lolb = True
            return "ROLB"
        # Use MLB when the second position is ILB from NFL.com.
        if second_position.upper() == "ILB":
            return "MLB"
        report_position_disagreement("ERROR", nfl_position, second_position, first_name, last_name)
        return "CONFLICT"
    
    # If nfl_position is DB, try to go off of what we have in second_position.
    if nfl_position.upper() in ["DB", "CB", "S", "SAF", "FS", "SS"]:
        if second_position.upper() in ["CB", "FS", "SS"]:
            return second_position.upper()
        # Alternate between FS and SS when the second position is DB, S, or SAF from NFL.com, but not specific enough.
        if second_position.upper() in ["DB", "S", "SAF"]:
            if NFLSpider.choose_fs is True:
                NFLSpider.choose_fs = False
                return "FS"
            NFLSpider.choose_fs = True
            return "SS"
        report_position_disagreement("ERROR", nfl_position, second_position, first_name, last_name)
        return "CONFLICT"
    
    # K is easy.
    if nfl_position.upper() == "K":
        if second_position.upper() == "K":
            return second_position.upper()
        elif second_position.upper() == "P":
            report_position_disagreement("INFO", nfl_position, second_position, first_name, last_name)
            return second_position.upper()
        report_position_disagreement("ERROR", nfl_position, second_position, first_name, last_name)
        return "CONFLICT"
    
    # P is easy.
    if nfl_position.upper() == "P":
        if second_position.upper() == "P":
            return second_position.upper()
        elif second_position.upper() == "K":
            report_position_disagreement("INFO", nfl_position, second_position, first_name, last_name)
            return second_position.upper()
        report_position_disagreement("ERROR", nfl_position, second_position, first_name, last_name)
        return "CONFLICT"
    
    logging.error("Unknown nfl_position passed to choose_best_position for %s %s:", 
                  first_name, 
                  last_name
                 )
    logging.error("nfl_position.upper() = %s", nfl_position.upper())
    logging.error("second_position.upper() = %s\n", second_position.upper())
    return "CONFLICT"

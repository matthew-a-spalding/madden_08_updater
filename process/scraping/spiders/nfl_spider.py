r""" nfl_spider.py
    
    This script defines the spider class and related helper functions that will perform the actual crawl over the 
    entirety of the NFL team roster pages. It generates a CSV file named 'NFL rosters.csv' listing all current NFL 
    players, with their attributes determined from the combination of the NFL site and the values found in "Latest 
    Madden Ratings.csv".
"""

# ----------------------------------------------------- SECTION 1 -----------------------------------------------------
# ----------------------------------------- IMPORTS, SETTINGS, AND CONSTANTS ------------------------------------------
# 1 - Standard library imports
import csv, logging, math, os, re
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
        logging.info("start_urls = %s", nfl_roster_urls)
        logging.info("allow_rule = %s", settings.NFL_PROFILE_LINKS_REGEX)
        
        # Open the "Latest Madden Ratings.csv" file with all the players and their Madden ratings for reading.
        self.madden_ratings_file = open(
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 
                r"process\inputs\Latest Madden Ratings.csv"
            ), 'r'
        )
        
        # Get a DictReader to read the rows into dicts using the header row as keys.
        self.madden_ratings_dict_reader = csv.DictReader(self.madden_ratings_file)
        
        # The only thing left to do is call the parent constructor.
        super(NFLSpider, self).__init__(**kwargs)


    def __del__(self):
        if self.madden_ratings_file:
            logging.info("Closing the file self.madden_ratings_file.")
            self.madden_ratings_file.close()
            self.madden_ratings_file = None


    def parse_NFL_profile_page(self, response):
        """ Scrapes the NFL.com profile page for a player, putting associated attributes into the player object. """
        #logging.info("NFL.com: Player profile page url: %s", response.url)
        
        # Create a new item for this player.
        player = NFLPlayer()
        
    # CHECK AND UPDATE THIS WHOLE SECTION AS NECESSARY.
    # Make sure the xpath expressions below can be used to find our text in the source of any player profile page.
        
        # Start by populating the team field. The NFL page will be authoritative here; no need to check Madden.
        player["team"] = response.xpath(
            "//div[@class=\"article-decorator\"]/h1/a/text()"
            ).extract()[0].split()[-1] # eg. "Colts"
        
        # Next up is the player's first and last name.
        # Note: I tested putting a comma into the name fields for a player, and it seemed to be correctly escaped, as 
        # the comma made it from the Latest Madden Ratings file through to the output file, NFL Rosters. 
        # The NFL.com might not be canonical on names, esp. in situations where the Madden file has the suffix for the 
        # player's last name, like "Fowler III", and the NFL.com does not, so put NFL names into temp vars.
        nfl_full_name = response.xpath(
            "//meta[@id=\"playerName\"]/@content"
            ).extract()[0] # eg. "Prince Charles Iworah"
        
        if len(nfl_full_name.split()) > 2:
            logging.info("NFL.com: Found a player with three or more name parts: \"%s\"", nfl_full_name)
        
        nfl_first_name = get_first_name(nfl_full_name) # eg. "Prince Charles"
        nfl_last_name = get_last_name(nfl_full_name) # eg. "Iworah"
        
        # Find the player's jersey number and position. 
        # (If jersey number is empty, there must still be a '#' for this split to work.)
        number_and_position = response.xpath(
            "//span[@class=\"player-number\"]/text()"
            ).extract()[0].split(None, 1) # eg. ["#12", "QB"]
        #logging.info("NFL.com: number_and_position = %s", number_and_position)
        
        # For jersey number, NFL.com is also authoritative (and Madden doesn't always give us that anyway).
        # The [1:] below gets only the chars from position 1 to the end of the string (strings are 0-indexed).
        player["jersey_number"] = number_and_position[0][1:] # eg. "12"
        
        # For position, since the NFL.com value may not be final, save it in a local var, not the player dict.
        nfl_position = number_and_position[1] # eg. "QB"
        
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
            #logging.info("NFL.com: nfl_birthdate = %s", nfl_birthdate)
            
            height_strings = height_weight_age_strings[1].split() # eg. [":", "6-4"]
            weight_strings = height_weight_age_strings[2].split() # eg. [":", "240"]
            age_strings = height_weight_age_strings[3].split() # eg. [":", "25"]
            #logging.info("NFL.com: height_strings = %s", height_strings)
            #logging.info("NFL.com: weight_strings = %s", weight_strings)
            #logging.info("NFL.com: age_strings = %s", age_strings)
            
            # Since the NFL might not be authoritative on the height, weight, or age, don't put these values directly 
            # into the player dict. Also, convert height to inches, since we will likely compare it to what Madden has 
            # for this player, and inches are what we will ultimately need to put into the DB anyway.
            nfl_height_inches = (int(height_strings[1][0]) * 12) + int(height_strings[1][2:])
            #logging.info("NFL.com: nfl_height_inches = %d", nfl_height_inches)
            nfl_weight = weight_strings[1] # eg. "240"
            nfl_age = age_strings[1] # eg. "25"
            
            # Get the player's college. The NFL.com pages report "No College" if they don't have that info.
            college_strings = response.xpath("//div[@class=\"player-info\"]/p[5]/text()").extract()[0].split(None, 1) 
            # eg. [u":", u"Stanford"]
            #logging.info("NFL.com: college_strings = %s", college_strings)
            nfl_college = college_strings[1] # eg. "Stanford"
            
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
                
        elif len(player_info_p_strong_tags) == 5:
            # The age info is missing, and we have no birth date <p> either.
            #logging.info("NFL.com: Check the tags in the \"player-info\" div for this url:")
            #logging.info(response.url)
            
            # For height, weight, and age, the text() inside the third <p> tag in the <div class="player-info"> tag 
            # has a lot of whitespace chars, some of which are grouped into the first string by themselves, which is 
            # why the first string with real content (for height) is found at ...extract()[1], not ...extract()[0].
            height_weight_strings = response.xpath("//div[@class=\"player-info\"]/p[3]/text()").extract() 
            # a list of 3 strings, 
            # eg. [u'\r\n\t\t\t\t\t', u': 6-6 \xa0 \r\n\t\t\t\t\t', 
            # u': 255 \xa0 \r\n\t\t\t\t\t\r\n\t\t\t\t\t\t\r\n\t\t\t\t\t\t\r\n\t\t\t\t\t\r\n\t\t\t\t']
            logging.info("NFL.com: height_weight_strings = %s", height_weight_strings)
            
            height_strings = height_weight_strings[1].split() # eg. [":", "6-6"]
            weight_strings = height_weight_strings[2].split() # eg. [":", "255"]
            #logging.info("NFL.com: height_strings = %s", height_strings)
            #logging.info("NFL.com: weight_strings = %s", weight_strings)
            
            nfl_height_inches = (int(height_strings[1][0]) * 12) + int(height_strings[1][2:])
            nfl_weight = weight_strings[1] # eg. "255"
            
            # Get the player's college. The NFL.com pages currently say "No College" when they don't have that info.
            college_strings = response.xpath("//div[@class=\"player-info\"]/p[4]/text()").extract()[0].split(None, 1) 
            # eg. [u":", u"Stanford"]
            logging.info("NFL.com: college_strings = %s", college_strings)
            nfl_college = college_strings[1] # eg. "Stanford"
            
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
        else:
            # We have yet another configuration, which we should investigate.
            logging.error("Found an NFL player profile page where len(player_info_p_strong_tags) == %d, "
                          "which we have not seen before. ", len(player_info_p_strong_tags))
            logging.error("Check the tags in the \"player-info\" div for this url:")
            logging.error(response.url)
        
        
        # Now that we have the info from NFL.com, we can search in Madden for this player.
        # Create the dict into which we'll copy the row from the Madden CSV with this player's info, if we find it.
        madden_player_dict = {}
        
        # Loop over the dicts in the Madden ratings DictReader and see if we can find this player.
        # If we have either birthdate or age from NFL.com, try uing those first.
        if nfl_birthdate or nfl_age:
            
            for player_dict in self.madden_ratings_dict_reader:
                
                # We do our comparisons without suffixes.
                madden_last_name = remove_suffix(player_dict["Last Name"])
                
                # The easiest matches are when we have a birth date from both NFL.com and Madden.
                if nfl_birthdate and player_dict["Birthdate"]:
                    
                    # We should be able to match the birthdate, last name, and at least first initial.
                    if (nfl_last_name.lower() == madden_last_name.lower() and 
                            nfl_first_name[0].lower() == player_dict["First Name"][0].lower() and 
                            nfl_birthdate == player_dict["Birthdate"]):
                        
                        #logging.info("NFL & Madden: Match by birthdate for %s %s, %s %s.", 
                        #             nfl_first_name, nfl_last_name, player["team"], nfl_position)
                        
                        madden_player_dict = player_dict
                        
                        # Once we match, reset our file record pointer and break the 'for' loop.
                        # (Need to reset our file's record pointer, or else subsequent loops over this dict_reader 
                        # will start where this call left off, and never check any of the records before this record.)
                        self.madden_ratings_file.seek(1)
                        break
                
                elif nfl_age:
                    
                    # Try matching on full name, age, and position.
                    if (nfl_last_name.lower() == madden_last_name.lower() and 
                            nfl_first_name.lower() == player_dict["First Name"].lower() and 
                            abs(int(nfl_age) - int(player_dict["Age"])) < 2 and 
                            positions_are_similar(nfl_position, player_dict["Position"])):
                        
                        logging.info("NFL & Madden: Match by name, age, & pos. for NFL.com's %s %s, %s %s.", 
                                     nfl_first_name, nfl_last_name, player["team"], nfl_position)
                        
                        madden_player_dict = player_dict
                        
                        # As above, once we match, reset our file record pointer and break the 'for' loop.
                        self.madden_ratings_file.seek(1)
                        break
            else:
                # As was necessary above, we now need to reset our file's record pointer.
                self.madden_ratings_file.seek(1)
                
                # We somehow made it through the whole Madden file, with a birthdate and/or age from NFL.com, but 
                # still could not find a match. This is a situation we will want to investigate.
                logging.error("NFL & Madden 1: Unable to find a match for %s %s, %s %s.", 
                              nfl_first_name, nfl_last_name, player["team"], nfl_position)
                logging.error("\t\tSkipping player record altogether!")
            
        else:
            logging.info("NFL: No birthdate or age for %s %s, %s %s.", 
                         nfl_first_name, nfl_last_name, player["team"], nfl_position)
        
            # Try finding a record with the same full name, position, and college.
            for player_dict in self.madden_ratings_dict_reader:
                
                # Take any suffix off the last name in Madden when doing our comparisons.
                madden_last_name = remove_suffix(player_dict["Last Name"])
                
                if (nfl_last_name.lower() == madden_last_name.lower() and 
                        nfl_first_name.lower() == player_dict["First Name"].lower() and 
                        positions_are_similar(nfl_position, player_dict["Position"]) and 
                        nfl_college[:5].lower() == player_dict["College"][:5].lower()):
                    
                    logging.warning("NFL & Madden: Match by name, pos, & college for NFL.com's %s %s, %s %s;", 
                                    nfl_first_name, nfl_last_name, player["team"], nfl_position)
                    logging.warning("\tMadden CSV values: %s %s, %s %s", 
                                    player_dict["First Name"], 
                                    player_dict["Last Name"], 
                                    player_dict["Team"], 
                                    player_dict["Position"])
                    logging.warning("\tNFL college = \"%s\", Madden college = \"%s\"", 
                                    nfl_college, player_dict["College"])
                    
                    # Attributes are similar enough, so set this record as the player's Madden dict.
                    madden_player_dict = player_dict
                    
                    # Once we match, reset our file record pointer and break the 'for' loop.
                    self.madden_ratings_file.seek(1)
                    break
                
            else:
                # As was necessary above, we now need to reset our file's record pointer.
                self.madden_ratings_file.seek(1)
                
                logging.error("NFL & Madden 2: Unable to find a match for %s %s, %s %s.", 
                              nfl_first_name, nfl_last_name, player["team"], nfl_position)
                logging.error("\t\tSkipping player record altogether!")
        
        # Now we have all the values we need, and a dict from the Madden file. Set the player's attributes.
        if madden_player_dict:
            
            # When we have a difference in names, it is usually because Madden included the suffix on the last name, 
            # but the NFL.com did not. In those cases, we want to keep the suffix, so go with Madden.
            player["first_name"] = madden_player_dict["First Name"]
            player["last_name"] = madden_player_dict["Last Name"]
            
            # Choose the best position for the player using our helper function.
            player["position"] = choose_best_position(nfl_position, madden_player_dict["Position"])
            
            # If the difference between the heights is more than 3 inches, we might have a problem.
            if abs(int(nfl_height_inches) - int(madden_player_dict["Height"])) > 3:
                player["height"] = "CONFLICT"
            else:
                # Use the ceiling of the average of the two heights.
                player["height"] = int(math.ceil((int(nfl_height_inches) + int(madden_player_dict["Height"])) / 2))
            
            # If the difference between the weights is more than 30 lbs, we might have a problem.
            if abs(int(nfl_weight) - int(madden_player_dict["Weight"])) > 30:
                player["weight"] = "CONFLICT"
            else:
                # Use the ceiling of the average of the two weights.
                player["weight"] = int(math.ceil((int(nfl_weight) + int(madden_player_dict["Weight"])) / 2))
            
            # For age and college, we can generally trust the Madden values.
            player["age"] = madden_player_dict["Age"]
            player["college"] = madden_player_dict["College"]
            
            # In cases where we have a conflict over the number of years pro, resolve things later. 
            if int(nfl_years_pro) != int(madden_player_dict["Years Pro"]):
                player["years_pro"] = "CONFLICT"
            else:
                player["years_pro"] = madden_player_dict["Years Pro"]
            
            # Set the values for the remaining fields listed in "items.py" as simple pass-throughs from Madden. 
            
            player["speed"] = madden_player_dict["Speed"]
            player["acceleration"] = madden_player_dict["Acceleration"]
            player["strength"] = madden_player_dict["Strength"]
            player["agility"] = madden_player_dict["Agility"]
            player["awareness"] = madden_player_dict["Awareness"]
            player["catching"] = madden_player_dict["Catching"]
            player["carrying"] = madden_player_dict["Carrying"]
            player["throw_power"] = madden_player_dict["Throw Power"]
            player["throw_accuracy"] = madden_player_dict["Throw Accuracy"]
            player["kick_power"] = madden_player_dict["Kick Power"]
            player["kick_accuracy"] = madden_player_dict["Kick Accuracy"]
            player["run_block"] = madden_player_dict["Run Block"]
            player["pass_block"] = madden_player_dict["Pass Block"]
            player["tackle"] = madden_player_dict["Tackle"]
            player["jumping"] = madden_player_dict["Jumping"]
            player["kick_return"] = madden_player_dict["Kick Return"]
            player["injury"] = madden_player_dict["Injury"]
            player["stamina"] = madden_player_dict["Stamina"]
            player["toughness"] = madden_player_dict["Toughness"]
            player["trucking"] = madden_player_dict["Trucking"]
            player["elusiveness"] = madden_player_dict["Elusiveness"]
            player["run_block_strength"] = madden_player_dict["Run Block Strength"]
            player["run_block_footwork"] = madden_player_dict["Run Block Footwork"]
            player["pass_block_strength"] = madden_player_dict["Pass Block Strength"]
            player["pass_block_footwork"] = madden_player_dict["Pass Block Footwork"]
            player["throw_accuracy_short"] = madden_player_dict["Throw Accuracy Short"]
            player["throw_accuracy_mid"] = madden_player_dict["Throw Accuracy Mid"]
            player["throw_accuracy_deep"] = madden_player_dict["Throw Accuracy Deep"]
            player["throw_on_the_run"] = madden_player_dict["Throw on the Run"]
            player["total_salary"] = madden_player_dict["Total Salary"]
            player["signing_bonus"] = madden_player_dict["Signing Bonus"]
            player["handedness"] = madden_player_dict["Handedness"]
            
            # Construct the next request, for the 'OverTheCap' contracts list page, and pass it the current player.
            # NOTE: The 'dont_filter=True' in the assignment below is CRITICAL, as omitting it will mean the spider 
            # only hits the OTC list once, due to it's default filtering rules preventing duplicates.
            otc_contracts_list_request = Request(
                settings.OTC_CONTRACTS_URL, 
                callback=self.find_contract_page, 
                dont_filter=True
            )
            otc_contracts_list_request.meta["player"] = player
            return otc_contracts_list_request
            
        else:
            # Skip this player.
            player = NFLPlayer()
            return player

    def find_contract_page(self, response):
        """ Scrapes the OverTheCap contracts list page to get the link to the player's contract page. """
        
        # Get the player object out of the meta data for the response.
        player = response.meta["player"]
        
        #logging.info("Inside find_contract_page for %s %s, %s %s.", 
        #             player["first_name"], player["last_name"], player["team"], player["position"])
        
        # Check last names for the presence of suffixes and remove them when found.
        last_name_minus_suffix = remove_suffix(player["last_name"])
        
        # Fill in the OTC_CONTRACT_LINK_TEMPLATE to get the pattern we will search for in the contracts page.
        # (The pattern helps when we need to try a first initial match, if the full first name match fails.)
        otc_anchor_text_regex = settings.OTC_ANCHOR_REGEX_TEMPLATE.replace("[FIRST_NAME]", player["first_name"])
        otc_anchor_text_regex = otc_anchor_text_regex.replace("[LAST_NAME]", last_name_minus_suffix)
        
        # Get the list of matches for this regex pattern.
        # WORKING!! This gives us a list of all <tr> tags containing the <td> tags which hold <a> tags where the 
        # text() matches the regex 
        name_match_trs_list = response.xpath(
            "//tr/td/a[re:match(text(), \"" + otc_anchor_text_regex + "\")]/../..", 
            namespaces={"re": "http://exslt.org/regular-expressions"}
        ).extract()
        
        logging.warning("%s %s: name_match_trs_list = %s", 
                        player["first_name"], player["last_name"], name_match_trs_list)
        
        # If we can't find text in an anchor tag that matches the full name, ...
        if not name_match_trs_list:
            
            logging.warning("OTC: Unable to find full first & last match for %s %s.", 
                            player["first_name"], player["last_name"])
            
            # ... then try matching the last name and the first initial. 
            # (E.g. Matthew Stafford is called Matt Stafford on OTC.)
            otc_anchor_text_regex = settings.OTC_ANCHOR_REGEX_TEMPLATE.replace(
                "[FIRST_NAME]", player["first_name"][0])
            otc_anchor_text_regex = otc_anchor_text_regex.replace("[LAST_NAME]", last_name_minus_suffix)
            
            # Get the list of matches for this regex pattern.
            name_match_trs_list = response.xpath(
                "//tr/td/a[re:match(text(), \"" + otc_anchor_text_regex + "\")]/../..", 
                namespaces={"re": "http://exslt.org/regular-expressions"}
            ).extract()
            
            if not name_match_trs_list:
                
                logging.error("Unable to find even partial name match on OTC for %s %s, %s %s.", 
                              player["first_name"], 
                              player["last_name"], 
                              player["team"], 
                              player["position"])
                logging.error("\t\tSkipping OTC player contract page.")
                
                # Return the player to the pipeline for writing to the output file.
                return player
                
        # In either case (full name or first initial only), we must have at least one element in our 
        # name_match_trs_list now. In fact, we will often have multiple matches, so we need to continue to try 
        # matching the other attributes until we either run out of matches, or find a likely match.
        
        for index, table_row in enumerate(name_match_trs_list):
            
            # EXAMPLE: name_match_trs_list = 
            # [
            # '<tr class="sortable" data-team="CAR" data-position="43DE">
            #     <td class="sortable">
            #         <a href="/player/charles-johnson/1150/">Charles Johnson</a>
            #     </td>
            #     <td class="sortable">43DE</td>
            #     <td class="sortable">
            #         <a class="team-link CAR" href="/salary-cap/carolina-panthers/">Panthers</a>
            #     </td>
            #     <td>$8,000,000</td>
            #     <td>$4,000,000</td>
            #     <td>$2,500,000</td>
            #     <td>$1,250,000</td>
            #     <td>31.3%</td>
            # </tr>', 
            # '<tr class="sortable" data-team="CAR" data-position="WR">
            #     <td class="sortable">
            #         <a href="/player/charles-johnson/2397/">Charles Johnson</a>
            #     </td>
            #     <td class="sortable">WR</td>
            #     <td class="sortable">
            #         <a class="team-link CAR" href="/salary-cap/carolina-panthers/">Panthers</a>
            #     </td>
            #     <td>$1,500,000</td>
            #     <td>$1,500,000</td>
            #     <td>$350,000</td>
            #     <td>$350,000</td>
            #     <td>23.3%</td>
            # </tr>'
            # ]
            
# CONTINUE HERE 2017_12_06
            
            # See if the positions (in the player object and on OTC) are similar enough that a match is likely.
            # On OTC, the position is found in the <td> following the <td> which contains the <a> tag.
            position_xpath = ("//a[contains(text(),\"" + 
                              player_name + 
                              "\")]/parent::*/following-sibling::*/text()")
            
            otc_position = response.xpath(position_xpath).extract()[0]
            
            logging.info("\tOTC partial name match position = %s", otc_position)
            
# TODO: Check for the various positions on OTC that are not in a format we use, like "43OLB", and 
# change change them to usable positions.
            
            if positions_are_similar(player["position"], otc_position):
                logging.warning("\tOTC: Using likely match for NFL.com's %s %s, %s %s;", 
                                player["first_name"], 
                                player["last_name"], 
                                player["team"], 
                                player["position"])
                logging.warning("\tOTC partial match name text: %s ;", player_name)
                logging.warning("\tOTC partial name match position: %s", otc_position)
                
                # The positions are similar enough, so build the contract page URL for this player from the XPath.
                player_link_xpath = "//a[contains(text(),\"" + player_name + "\")]/@href"
                player_contract_url = response.urljoin(response.xpath(player_link_xpath).extract()[0]) 
                # eg. "https://overthecap.com/player/matt-stafford/1060/"
                logging.info("\tOTC player_contract_url for %s %s, %s %s was:", 
                             player["first_name"], player["last_name"], player["team"], player["position"])
                logging.info("\t%s", player_contract_url)
                
                # Create the request object for this player's contract URL.
                player_contract_request = Request(player_contract_url, callback=self.parse_OTC_contract_page)
                # Pass along the player object.
                player_contract_request.meta["player"] = player
                # Return the request for the player's contract page.
                return player_contract_request
                
            # Otherwise, simply pass back the player object as is, without the contract and draft info.
            logging.error("\tOTC Unable to match %s %s, %s %s.", 
                          player["first_name"], player["last_name"], player["team"], player["position"])
            logging.error("\t\tSkipping OTC player contract page.")
            
            # Just return the player object.
            return player
        else:
            
            # We found at least one text (full name) that matches the pattern. Before we jump to the player contract 
            # page, we need to make sure we either have only one name match or we get the correct one of many.
            if len(name_match_trs_list) > 1:
                
                # Loop over the matches and get the associated position for each name.
                for index, name_string in enumerate(name_match_trs_list):
                    pass
                    
                    
            # Now use the string the regex matches as the value that the 
            # anchor tag's text must contain.
            player_link_text = name_match_trs_list[0]
            #logging.info("OTC full name match = %s", player_link_text)
            
            # Build the contract page URL for this player from the XPath.
            player_link_xpath = "//a[contains(text(),\"" + player_link_text + "\")]/@href"
            player_contract_url = response.urljoin(response.xpath(player_link_xpath).extract()[0])
            # eg. "https://overthecap.com/player/matt-stafford/1060/"
            logging.info("OTC player_contract_url for %s %s, %s %s was:", 
                         player["first_name"], player["last_name"], player["team"], player["position"])
            logging.info(player_contract_url)
            
            # Build the request object, including the player object in the meta.
            player_contract_request = Request(player_contract_url, callback=self.parse_OTC_contract_page)
            player_contract_request.meta["player"] = player
            
            # Pass along the next request for our spider to crawl.
            return player_contract_request
            
    def parse_OTC_contract_page(self, response):
        """ Scrapes the OTC page for a player to get details on his contract, years pro, and draft status. """
        # Get the player object out of the response's meta data.
        player = response.meta["player"]
        #logging.info("Inside parse_OTC_contract_page for %s %s.", player["first_name"], player["last_name"])
        
        # Now to grab the contract and draft into for this player.
        
        
        # Return our player object for writing to the output CSV file.
        return player

# ----------------------------------------------------- SECTION 3 -----------------------------------------------------
# ------------------------------------------------- Helper Functions --------------------------------------------------

def remove_suffix(name):
    """ Removes any typical suffix (" Jr.", " III", etc.) from a last name. """
    suffixes = [" jr", " jr.", " sr", " sr.", " ii", " iii", " iv", " v", " vi", " vii", " viii", " ix", " x"]
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
    # If the middle name part is "Van," "Vander," or "Jean," treat it as part of the last name.
    if (split_name_without_suffix[1].lower() == "van" or 
            split_name_without_suffix[1].lower() == "vander" or 
            split_name_without_suffix[1].lower() == "jean"):
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
    # If the middle name part is "Van," "Vander," or "Jean," treat it as part of the last name.
    if (split_name_without_suffix[1].lower() == "van" or 
            split_name_without_suffix[1].lower() == "vander" or 
            split_name_without_suffix[1].lower() == "jean"):
        return split_name_without_suffix[1] + " " + split_name_without_suffix[2]
    
    # In all other cases, treat the middle as part of the first name, and just return the third part.
    return split_name_without_suffix[2]

def positions_are_similar(nfl_position, madden_position):
    """
    This function is used in parse_NFL_profile_page, when the player's name on NFL.com was not an exact match with the 
    name in the "Latest Madden Ratings.csv" file. It compares the positions of the two player pages to see if they are 
    similar enough to be considered a match.
    """
    # If either position is QB and the other isn't, the answer is no.
    if nfl_position.upper() == "QB":
        return bool(madden_position.upper() == "QB")
    
    # If the NFL's position is RB, HB, FB, WR, or TE, madden_position can be: RB, HB, FB, WR, or TE.
    if nfl_position.upper() in ["RB", "HB", "FB", "WR", "TE"]:
        return bool(madden_position.upper() in ["RB", "HB", "FB", "WR", "TE"])
    
    # If the NFL's position is OL, T, OT, G, OG, LT, LG, C, RG, or RT, 
    # madden_position can be: OL, T, OT, G, OG, LS, LT, LG, C, RG, or RT.
    if nfl_position.upper() in ["OL", "T", "OT", "G", "OG", "LT", "LG", "C", "RG", "RT"]:
        return bool(madden_position.upper() in ["OL", "T", "OT", "G", "OG", "LS", "LT", "LG", "C", "RG", "RT"])
    
    # If the NFL's position is LS, 
    # madden_position can be: OL, T, OT, G, OG, LS, LT, LG, C, RG, RT, or TE.
    if nfl_position.upper() == "LS":
        return bool(madden_position.upper() in ["OL", "T", "OT", "G", "OG", "LS", "LT", "LG", "C", "RG", "RT", "TE"])
    
    # If the first position is DL, DE, LE, or RE, 
    # madden_position can be: DL, DE, LE, RE, DT, NT, LB, OLB, LOLB, ROLB, ILB, or MLB.
    if nfl_position.upper() in ["DL", "DE", "LE", "RE"]:
        return bool(madden_position.upper() in 
                    ["DL", "DE", "LE", "RE", "DT", "NT", "LB", "OLB", "LOLB", "ROLB", "ILB", "MLB"])
    
    # If the first position is DT or NT, madden_position can be: DL, DE, LE, RE, DT, or NT.
    if nfl_position.upper() in ["DT", "NT"]:
        return bool(madden_position.upper() in ["DL", "DE", "LE", "RE", "DT", "NT"])
    
    # If the first position is LB, OLB, LOLB, ROLB, ILB, or MLB, 
    # madden_position can be: DL, DE, LE, RE, LB, OLB, LOLB, ROLB, ILB, or MLB.
    if nfl_position.upper() in ["LB", "OLB", "LOLB", "ROLB", "ILB", "MLB"]:
        return bool(madden_position.upper() in ["DL", "DE", "LE", "RE", "LB", "OLB", "LOLB", "ROLB", "ILB", "MLB"])
    
    # If the first position is DB, CB, S, SAF, FS, or SS, madden_position can be: DB, CB, S, SAF, FS, or SS.
    if nfl_position.upper() in ["DB", "CB", "S", "SAF", "FS", "SS"]:
        return bool(madden_position.upper() in ["DB", "CB", "S", "SAF", "FS", "SS"])
    
    # If either position is K or P and the other isn't one of those, the answer is no.
    if nfl_position.upper() in ["K", "P"]:
        return bool(madden_position.upper() in ["K", "P"])
    
    logging.error("Unknown nfl_position passed to positions_are_similar:")
    logging.error("nfl_position.upper() = %s", nfl_position.upper())
    logging.error("madden_position.upper() = %s", madden_position.upper())
    return False

def choose_best_position(position1, position2):
    """
    This function takes in the two position strings for a player (found on NFL.com and in the latest Madden ratings) 
    and uses them in determining which Madden position to assign this player. If no determination can be made, but the 
    input positions were in general agreement, we assign "TBD" (to be determined). If the positions are not in 
    agreement, we assign "CONFLICT". Both "TBD" and "CONFLICT" will require manual replacing later.
    """
    # QB is easy.
    if position1.upper() == "QB":
        if position2.upper() == "QB":
            return "QB"
        return "CONFLICT"
    
    # If position1 is RB, try to go off of what we have in position2.
    if position1.upper() == "RB":
        if position2.upper() in ["RB", "WR", "TE"]:
            return "TBD"
        elif position2.upper() == "HB":
            return "HB"
        elif position2.upper() == "FB":
            return "FB"
        return "CONFLICT"
    
    # If position1 is HB, we are similar to WR and TE, and can be specific with RB, HB, and FB.
    if position1.upper() == "HB":
        if position2.upper() in ["WR", "TE"]:
            return "TBD"
        elif position2.upper() in ["RB", "HB"]:
            return "HB"
        # FB is special - assume it is correct even over HB.
        elif position2.upper() == "FB":
            return "FB"
        return "CONFLICT"
    
    # FB is special - assume it is correct even over HB; also similar enough to WR and TE.
    if position1.upper() == "FB":
        if position2.upper() in ["WR", "TE"]:
            return "TBD"
        if position2.upper() in ["RB", "HB", "FB"]:
            return "FB"
        return "CONFLICT"
    
    # If position1 is WR, we are similar to RB, HB, FB, and TE, and can be specific with WR.
    if position1.upper() == "WR":
        if position2.upper() in ["RB", "HB", "FB", "TE"]:
            return "TBD"
        elif position2.upper() == "WR":
            return "WR"
        return "CONFLICT"
    
    # If position1 is TE, we are similar to RB, HB, FB, and WR, and can be specific with TE.
    if position1.upper() == "TE":
        if position2.upper() in ["RB", "HB", "FB", "WR"]:
            return "TBD"
        elif position2.upper() == "TE":
            return "TE"
        return "CONFLICT"
    
    # If position1 is T, G, OT, OG, OL, or LS, try to go off of what we have in position2.
    if position1.upper() in ["T", "G", "OT", "OG", "OL", "LS"]:
        if position2.upper() in ["T", "G", "OT", "OG", "OL", "LS"]:
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
        elif position2.upper() == "TE":
            return "TE"
        return "CONFLICT"
    
    # If position1 is LT, just make sure position2 is some sort of generic OL or T.
    if position1.upper() == "LT":
        if position2.upper() in ["LT", "T", "OT", "OL"]:
            return "LT"
        # If position2 is a different specific OL position, we have a TBD.
        elif position2.upper() in ["G", "OG", "LS", "LG", "C", "RG", "RT"]:
            return "TBD"
        return "CONFLICT"
    
    # If position1 is LG, just make sure position2 is some sort of generic OL or G.
    if position1.upper() == "LG":
        if position2.upper() in ["LG", "G", "OG", "OL"]:
            return "LG"
        # If position2 is a different specific OL position, we have a TBD.
        elif position2.upper() in ["T", "OT", "LS", "LT", "C", "RG", "RT"]:
            return "TBD"
        return "CONFLICT"
    
    # If position1 is C, just make sure position2 is some sort of generic OL or C.
    if position1.upper() == "C":
        if position2.upper() in ["C", "G", "OG", "OL"]:
            return "C"
        # If position2 is a different specific OL position, we have a TBD.
        elif position2.upper() in ["T", "OT", "LS", "LT", "LG", "RG", "RT"]:
            return "TBD"
        return "CONFLICT"
    
    # If position1 is RG, just make sure position2 is some sort of generic OL or G.
    if position1.upper() == "RG":
        if position2.upper() in ["RG", "G", "OG", "OL"]:
            return "RG"
        # If position2 is a different specific OL position, we have a TBD.
        elif position2.upper() in ["T", "OT", "LS", "LT", "LG", "C", "RT"]:
            return "TBD"
        return "CONFLICT"
    
    # If position1 is RT, just make sure position2 is some sort of generic OL or T.
    if position1.upper() == "RT":
        if position2.upper() in ["RT", "T", "OT", "OL"]:
            return "RT"
        # If position2 is a different specific OL position, we have a TBD.
        elif position2.upper() in ["G", "OG", "LS", "LT", "LG", "C", "RG"]:
            return "TBD"
        return "CONFLICT"
    
    # If position1 is DL, try to go off of what we have in position2.
    if position1.upper() == "DL":
        if position2.upper() in ["DL", "DE", "LB", "OLB", "LOLB", "ROLB", "ILB", "MLB"]:
            return "TBD"
        elif position2.upper() == "LE":
            return "LE"
        elif position2.upper() == "RE":
            return "RE"
        elif position2.upper() in ["DT", "NT"]:
            return "DT"
        return "CONFLICT"
    
    # If position1 is DE, try to go off of what we have in position2.
    if position1.upper() == "DE":
        if position2.upper() in ["DL", "DE", "DT", "NT", "LB", "OLB", "LOLB", "ROLB", "ILB", "MLB"]:
            return "TBD"
        elif position2.upper() == "LE":
            return "LE"
        elif position2.upper() == "RE":
            return "RE"
        return "CONFLICT"
    
    # If position1 is LE, most others will be a TBD, except for DL, DE, or LE.
    if position1.upper() == "LE":
        if position2.upper() in ["RE", "DT", "NT", "LB", "OLB", "LOLB", "ROLB", "ILB", "MLB"]:
            return "TBD"
        elif position2.upper() in ["DL", "DE", "LE"]:
            return "LE"
        return "CONFLICT"
    
    # If position1 is RE, most others will be a TBD, except for DL, DE, or RE.
    if position1.upper() == "RE":
        if position2.upper() in ["LE", "DT", "NT", "LB", "OLB", "LOLB", "ROLB", "ILB", "MLB"]:
            return "TBD"
        elif position2.upper() in ["DL", "DE", "RE"]:
            return "RE"
        return "CONFLICT"
    
    # If position1 is DT or NT, we can match DT, NT, or the generic DL.
    if position1.upper() in ["DT", "NT"]:
        if position2.upper() in ["DE", "LE", "RE"]:
            return "TBD"
        elif position2.upper() in ["DL", "DT", "NT"]:
            return "DT"
        return "CONFLICT"
    
    # If position1 is LB, try to go off of position2.
    if position1.upper() == "LB":
        if position2.upper() in ["DL", "DE", "LE", "RE", "LB", "OLB"]:
            return "TBD"
        elif position2.upper() == "LOLB":
            return "LOLB"
        elif position2.upper() == "ROLB":
            return "ROLB"
        elif position2.upper() in ["ILB", "MLB"]:
            return "MLB"
        return "CONFLICT"
    
    # If position1 is OLB, try to go off of position2.
    if position1.upper() == "OLB":
        if position2.upper() in ["DL", "DE", "LE", "RE", "LB", "OLB", "ILB", "MLB"]:
            return "TBD"
        elif position2.upper() == "LOLB":
            return "LOLB"
        elif position2.upper() == "ROLB":
            return "ROLB"
        return "CONFLICT"
    
    # If position1 is LOLB, we can match on LB, OLB, or LOLB.
    if position1.upper() == "LOLB":
        if position2.upper() in ["DL", "DE", "LE", "RE", "ROLB", "ILB", "MLB"]:
            return "TBD"
        elif position2.upper() in ["LB", "OLB", "LOLB"]:
            return "LOLB"
        return "CONFLICT"
    
    # If position1 is ROLB, we can match on LB, OLB, or ROLB.
    if position1.upper() == "ROLB":
        if position2.upper() in ["DL", "DE", "LE", "RE", "LOLB", "ILB", "MLB"]:
            return "TBD"
        elif position2.upper() in ["LB", "OLB", "ROLB"]:
            return "ROLB"
        return "CONFLICT"
    
    # If position1 is ILB or MLB, we can match on LB, ILB, or MLB.
    if position1.upper() in ["ILB", "MLB"]:
        if position2.upper() in ["DL", "DE", "LE", "RE", "OLB", "LOLB", "ROLB"]:
            return "TBD"
        elif position2.upper() in ["LB", "ILB", "MLB"]:
            return "MLB"
        return "CONFLICT"
    
    # If position1 is DB, try to go off of what we have in position2.
    if position1.upper() == "DB":
        if position2.upper() in ["DB", "S", "SAF"]:
            return "TBD"
        elif position2.upper() == "CB":
            return "CB"
        elif position2.upper() == "FS":
            return "FS"
        elif position2.upper() == "SS":
            return "SS"
        return "CONFLICT"
    
    # If position1 is CB, we can only match DB or CB.
    if position1.upper() == "CB":
        if position2.upper() in ["S", "SAF", "FS", "SS"]:
            return "TBD"
        elif position2.upper() in ["DB", "CB"]:
            return "CB"
        return "CONFLICT"
    
    # If position1 is S or SAF, try to go off of what we have in position2.
    if position1.upper() in ["S", "SAF"]:
        if position2.upper() in ["DB", "CB", "S", "SAF"]:
            return "TBD"
        elif position2.upper() == "FS":
            return "FS"
        elif position2.upper() == "SS":
            return "SS"
        return "CONFLICT"
    
    # If position1 is FS, we can match DB, S, SAF, or FS.
    if position1.upper() == "FS":
        if position2.upper() in ["CB", "SS"]:
            return "TBD"
        elif position2.upper() in ["DB", "S", "SAF", "FS"]:
            return "FS"
        return "CONFLICT"
    
    # If position1 is SS, we can match DB, S, SAF, or SS.
    if position1.upper() == "SS":
        if position2.upper() in ["CB", "FS"]:
            return "TBD"
        elif position2.upper() in ["DB", "S", "SAF", "SS"]:
            return "SS"
        return "CONFLICT"
    
    # K is easy.
    if position1.upper() == "K":
        if position2.upper() == "K":
            return "K"
        elif position2.upper() == "P":
            return "TBD"
        return "CONFLICT"
    
    # P is easy.
    if position1.upper() == "P":
        if position2.upper() == "P":
            return "P"
        elif position2.upper() == "K":
            return "TBD"
        return "CONFLICT"
    
    logging.error("Unknown position1 passed to choose_best_position:")
    logging.error("position1.upper() = %s", position1.upper())
    logging.error("position2.upper() = %s", position2.upper())
    return "CONFLICT"


# ----------------------------------------------------- SECTION 4 -----------------------------------------------------
# -------------------------------------------------- Main Function ----------------------------------------------------

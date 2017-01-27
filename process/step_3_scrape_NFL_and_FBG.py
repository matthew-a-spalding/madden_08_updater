r""" 02_scrape_NFL_and_FBG.py
    
    This script crawls the entirety of the NFL team roster pages and the related FBGRatings.com player pages and 
    generates a CSV file named 'NFL and FBG.csv' containing the full list of current NFL players and their biographic 
    and salary data.
    
    See the documentation on running Scrapy from a script here: 
        http://doc.scrapy.org/en/latest/topics/practices.html#run-scrapy-from-a-script

"""

# ----------------------------------------------------- SECTION 1 -----------------------------------------------------
# ----------------------------------------- IMPORTS, SETTINGS, AND CONSTANTS ------------------------------------------
# 1 - Standard library imports
#import logging
#from twisted.internet import reactor

# 2 - Third-party imports
#from scrapy import signals
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
#from scrapy.utils.log import configure_logging

# 3 - Application-specific imports
#from scripted import settings
#import settings

# 4 - Global settings


# 5 - Global constants


# ----------------------------------------------------- SECTION 2 -----------------------------------------------------
# ------------------------------------------------ Class Declarations -------------------------------------------------


# ----------------------------------------------------- SECTION 3 -----------------------------------------------------
# ------------------------------------------------- Helper Functions --------------------------------------------------


# ----------------------------------------------------- SECTION 4 -----------------------------------------------------
# -------------------------------------------------- Main Function ----------------------------------------------------
if __name__ == "__main__":
    """ Initialize the spider and do the crawling. 
    
    NOTE: Running the scraper produces a CSV file that will still need to be modified, so it MUST BE CHECKED MANUALLY 
    afterwards for the following: 
        1) See if any players were given a position of TBD or CONFLICT. (There may be many TBD, but there shouldn't be 
            any CONFLICT. The TBDs mean that NFL.com and FBGRatings were in agreement, but neither was specific enough 
            for Madden - like just LB or RB.) 
        2) Some players may be missing their jersey numbers. If I can't find them myself, just choose something 
            reasonable. 
        3) Make sure each team has at least the required number of players at each position. The scripts might create 
            too many LEs and not enough REs, for example.
    
    """
    
    # Get the settings and initialize the crawler process.
    process = CrawlerProcess(get_project_settings())
    # Let's crawl!
    process.crawl('nfl_and_fbg')
    print('Starting our crawl...')
    process.start()
    # Once the reactor is done, we're done.
    print('Crawling stopped.')

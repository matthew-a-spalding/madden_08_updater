r""" step_3_scrape_NFL_rosters.py
    
    This script crawls the entirety of the NFL team roster pages and generates a CSV file named 'NFL rosters.csv',
    containing the full list of current NFL players and their latest Madden ratings as well as their biographic, in-
    game model, and contract data.
    
    For this process to run successfully, two other files must exist. The first is "process\inputs\step3\Latest 
    Madden Ratings.csv" and the second is a file matching the convention "docs\My Ratings\{0}\My {1} NFL Ratings - 
    FINAL.csv".format((int(datetime.now().year)))
    file should contain the full list of the latest ratings put out by EA Sports for Madden. It should have all of the 
    required columns as listed in the README file (process\step_1 README for madden_08_updater.txt). 
    
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
        1) Find the appropriate values for any fields that were set to 'TBD' or 'CONFLICT'. (There WILL be some.)
        2) Some players may be missing their jersey numbers. If I can't find them myself, just choose something 
            reasonable. 
        3) Make sure each team has at least the required number of players at each position. The scripts might create 
            too many LEs and not enough REs, for example.
    """
    
    # Get the settings and initialize the crawler PROCESS.
    PROCESS = CrawlerProcess(get_project_settings())
    # Let's crawl!
    PROCESS.crawl('nfl_rosters')
    print('Starting our crawl...')
    PROCESS.start()
    # Once the reactor is done, we're done.
    print('Crawling stopped.')

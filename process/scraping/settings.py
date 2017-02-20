# -*- coding: utf-8 -*-

# Scrapy settings for tutorial project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#     http://doc.scrapy.org/en/latest/topics/settings.html

BOT_NAME = "scripted_bot"
SPIDER_MODULES = ["scraping.spiders"]
NEWSPIDER_MODULE = "scraping.spiders"

LOG_LEVEL = "INFO"

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = "tutorial (+http://www.yourdomain.com)"
USER_AGENT = "Mozilla/5.0 (Windows; U; MSIE 10.0; Windows NT 9.0; en-US)"

# Per docs at http://doc.scrapy.org/en/latest/topics/item-pipeline.html#topics-item-pipeline
ITEM_PIPELINES = {
    "scraping.pipelines.PlayerPipeline": 100,
}

# Template used in the main_script to create the list of NFL roster urls.
NFL_ROSTER_LINK_TEMPLATE = "http://www.nfl.com/teams/[FULL_LOCATION][NICKNAME]/roster?team=[SHORT_LOCATION]"

# The complete list of NFL team locations, both full and short, and nicknames.
NFL_TEAMS = [{"[FULL_LOCATION]":"buffalo", "[SHORT_LOCATION]":"buf", "[NICKNAME]":"bills"},
#    {"[FULL_LOCATION]":"miami", "[SHORT_LOCATION]":"mia", "[NICKNAME]":"dolphins"},
#    {"[FULL_LOCATION]":"newengland", "[SHORT_LOCATION]":"ne", "[NICKNAME]":"patriots"},
#    {"[FULL_LOCATION]":"newyork", "[SHORT_LOCATION]":"nyj", "[NICKNAME]":"jets"},
#    {"[FULL_LOCATION]":"baltimore", "[SHORT_LOCATION]":"bal", "[NICKNAME]":"ravens"},
#    {"[FULL_LOCATION]":"cincinnati", "[SHORT_LOCATION]":"cin", "[NICKNAME]":"bengals"},
#    {"[FULL_LOCATION]":"cleveland", "[SHORT_LOCATION]":"cle", "[NICKNAME]":"browns"},
#    {"[FULL_LOCATION]":"pittsburgh", "[SHORT_LOCATION]":"pit", "[NICKNAME]":"steelers"},
#    {"[FULL_LOCATION]":"houston", "[SHORT_LOCATION]":"hou", "[NICKNAME]":"texans"},
#    {"[FULL_LOCATION]":"indianapolis", "[SHORT_LOCATION]":"ind", "[NICKNAME]":"colts"},
#    {"[FULL_LOCATION]":"jacksonville", "[SHORT_LOCATION]":"jac", "[NICKNAME]":"jaguars"},
#    {"[FULL_LOCATION]":"tennessee", "[SHORT_LOCATION]":"ten", "[NICKNAME]":"titans"},
#    {"[FULL_LOCATION]":"denver", "[SHORT_LOCATION]":"den", "[NICKNAME]":"broncos"},
#    {"[FULL_LOCATION]":"kansascity", "[SHORT_LOCATION]":"kc", "[NICKNAME]":"chiefs"},
#    {"[FULL_LOCATION]":"oakland", "[SHORT_LOCATION]":"oak", "[NICKNAME]":"raiders"},
#    {"[FULL_LOCATION]":"sandiego", "[SHORT_LOCATION]":"sd", "[NICKNAME]":"chargers"},
#    {"[FULL_LOCATION]":"dallas", "[SHORT_LOCATION]":"dal", "[NICKNAME]":"cowboys"},
#    {"[FULL_LOCATION]":"newyork", "[SHORT_LOCATION]":"nyg", "[NICKNAME]":"giants"},
#    {"[FULL_LOCATION]":"philadelphia", "[SHORT_LOCATION]":"phi", "[NICKNAME]":"eagles"},
#    {"[FULL_LOCATION]":"washigton", "[SHORT_LOCATION]":"was", "[NICKNAME]":"redskins"},
#    {"[FULL_LOCATION]":"chicago", "[SHORT_LOCATION]":"chi", "[NICKNAME]":"bears"},
#    {"[FULL_LOCATION]":"detroit", "[SHORT_LOCATION]":"det", "[NICKNAME]":"lions"},
#    {"[FULL_LOCATION]":"greenbay", "[SHORT_LOCATION]":"gb", "[NICKNAME]":"packers"},
#    {"[FULL_LOCATION]":"minnesota", "[SHORT_LOCATION]":"min", "[NICKNAME]":"vikings"},
#    {"[FULL_LOCATION]":"atlanta", "[SHORT_LOCATION]":"atl", "[NICKNAME]":"falcons"},
#    {"[FULL_LOCATION]":"carolina", "[SHORT_LOCATION]":"car", "[NICKNAME]":"panthers"},
#    {"[FULL_LOCATION]":"neworleans", "[SHORT_LOCATION]":"no", "[NICKNAME]":"saints"},
#    {"[FULL_LOCATION]":"tampabay", "[SHORT_LOCATION]":"tb", "[NICKNAME]":"buccaneers"},
#    {"[FULL_LOCATION]":"arizona", "[SHORT_LOCATION]":"ari", "[NICKNAME]":"cardinals"},
#    {"[FULL_LOCATION]":"st.louis", "[SHORT_LOCATION]":"stl", "[NICKNAME]":"rams"},
#    {"[FULL_LOCATION]":"sanfrancisco", "[SHORT_LOCATION]":"sf", "[NICKNAME]":"49ers"},
#    {"[FULL_LOCATION]":"seattle", "[SHORT_LOCATION]":"sea", "[NICKNAME]":"seahawks"},
]

# The RegEx to use to find the links to follow from the NFL roster pages to the player profile pages.
NFL_PROFILE_LINKS_REGEX = ".+/player/.+/profile$"

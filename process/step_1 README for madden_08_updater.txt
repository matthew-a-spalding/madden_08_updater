    This document explains how to use the files in this folder to update the working 'base' (already somewhat edited) 
Madden NFL '08 Roster file, entitled "base.ros", with the latest information from NFL.com, the most recent Madden NFL 
player ratings from EA, and my previous year's final player ratings file, entitled "My 20[XX] Player Attributes - 
FINAL 20[XX]_MM_DD.csv".


                                            Step 1: Reading this README
=======================================================================================================================
    Reading this document is the first step, as indicated by this file's name. The next step, as seen in the filename 
of another file in this folder, is to download and clean the latest Madden ratings from EA Sports. Step 3 is to run 
the script "step_3_scrape_NFL_rosters.py" from inside the virtual environment in \process\scraping, the process for 
which is detailed below. The fourth step is to edit and process the file output by Step 3, "My 20[XX] Player Attributes 
- Initial.csv", until it is in a finished state. The fifth and final step is to run "step_5_update_roster_file.py", 
which generates a roster file, "current.ros". Once validated, use that roster file to create a new franchise!

    The full instructions for each remaining step follow:


                            Step 2: Download and clean the latest Madden ratings from EA.
=======================================================================================================================
A. Get the most recent Madden NFL player ratings into a CSV file.
    
    1. These can usually be found online at sites like http://maddenratings.weebly.com or OperationSports at 
    https://forums.operationsports.com/forums/madden-nfl-football/. Put the original file in the folder 
    "docs\EA ratings\originals", and immediately export a copy of the original as a CSV file named "Madden [XX] Player 
    Ratings.csv" (where [XX] is the last two digits of the year) into the folder "docs\EA ratings\edited". 
    
    2. Flatten the "Madden [XX] Player Ratings.csv" player ratings file into one sheet (if it wasn't already), remove 
    any stat columns that we are not interested in using, and validate the data (check for missing fields, invalid 
    values like birthdates which aren't dates, etc.). 
    
    The columns to keep in the file "Madden [XX] Player Ratings.csv" / "Latest Madden Ratings.csv" (with fields 
    capitalized and punctuated exactly as shown - NOT lower_case underscore-connected fields) are:
        Team
        First Name
        Last Name
        Position
        Awareness
        Speed
        Acceleration
        Agility
        Strength
        Elusiveness
        Carrying
        Trucking
        Break Tackle*           May not be in the original file.
        Catching
        Jumping
        Throw Power
        Throw Accuracy Short
        Throw Accuracy Mid
        Throw Accuracy Deep
        Throw on the Run
        Playaction
        Pass Block
        Run Block
        Pass Block Power
        Pass Block Finesse
        Run Block Power
        Run Block Finesse
        Tackle
        Kick Power
        Kick Accuracy
        Kick Return
        Stamina
        Injury
        Toughness
        Handedness
        Jersey Number
        Height
        Weight
        Age
        Birthdate
        Years Pro
        College
        Total Salary
        Signing Bonus

    3. Once cleaned, copy "Madden [XX] Player Ratings.csv" into the folder "\process\inputs\step3" and rename it to 
    "Latest Madden Ratings.csv", overwriting any previous copy there.
    


                                Step 3: Scrape the current rosters from NFL.com.
=======================================================================================================================
A.  1. We need to update the file "Previous Player Attributes.csv," which sits alongside the file "Latest Madden 
    Ratings.csv," in the "\process\inputs\step3" folder, as it is required for the scraping to work. To do this:
        a) Delete any existing "Previous Player Attributes.csv" file (in "\process\inputs\step3").
        b) Copy the file "Current Player Attributes.csv" from "process\inputs\step5" (which should be the same file as 
        last year's "My 20[XX] Player Attributes - FINAL 20[XX_MM_DD].csv") and put it in the "\process\inputs\step3" 
        folder, renaming it to "Previous Player Attributes.csv".
    
    * NOTE! Looking at the new "Previous Player Attributes.csv" file may seem to indicate that we should also update 
    the years_pro column (adding 1 to each player's number of years in the league) to account for the new season, but 
    the code in "process\scraping\spiders\nfl_spider.py" already handles for this, adding one to the value from the 
    "years_pro" column in "Previous Player Attributes.csv" before comparing it with the NFL's 'years pro' field.
    
    2. Make sure that the LOG_LEVEL in "process\scraping\settings.py" is set to "INFO" to start with, as this will 
    give us the most information, which we will want to see on the first few runs of "step_3_scrape_NFL_rosters.py".

B.  Activate the venv in "process\scraping" so we can use Scrapy. To do this:
    1. Open a CMD window.
        CTRL-R -> cmd
    2. Change drive letters to the letter assigned to the USB thumb drive "Working Files": "E:" or "G:" or whatever:
        E:
    3. Change to the process folder:
        cd e:\Gaming\madden_08_updater\venv\
    3. Activate the virtual environment: 
        .\Scripts\activate.bat
    4. Go into the madden_08_updater\process directory.
        cd e:\Gaming\madden_08_updater\process

C.  Run the Scrapy script. THIS MUST BE RUN FROM THE "...madden_08_updater\process" DIRECTORY, OR SCRAPY WILL SAY THAT 
    IT CANNNOT FIND THE SPIDER "nfl_rosters". In the command prompt window, do:
    
    python step_3_scrape_NFL_rosters.py
    
    IF THERE ARE ERRORS FROM SCRAPY: Check the changelogs for Scrapy to see if anything has changed out from under me. 
    This happened the last time I tried to perform a fresh install of Scrapy - the class name in Scrapy's crawler.py 
    apparently had been changed from CrawlerPROCESS to CrawlerProcess, the casing of which Python cares about.
    
    If the format of the HTML on the NFL and OverTheCap sites has not changed, the step 3 script should have created a 
    file "My 20[XX] Player Attributes - Initial.csv" in "process\outputs\step3". If there is no file there, or if 
    Scrapy threw any error(s) in the CMD window, debug until the script correctly produces the file. (In case of an 
    error, it may simply be that the NFL has finally changed the layout of their website or the HTML within their 
    pages, or the Madden player attribute fields have changed again.) In order to get all the players that are 
    currently on actual NFL rosters, it will likely be necessary to iterate over the run of 
    "step_3_scrape_NFL_rosters.py" by altering code in "process\scraping\settings.py" to alter the LOG_LEVEL from the 
    initial value of "INFO" to "WARNING", and finally "ERROR" (or if absolutely necessary, DEBUG), while choosing 
    which new players not found in the "Latest Madden Ratings.csv" to add or skip. You might also want to limit the 
    number of teams which are included in early runs, to help with debugging/filtering. This is done by commenting/
    uncommenting lines in the NFL_TEAMS list in "process\scraping\settings.py".


                                Step 4: Process my ratings file until it is complete.
=======================================================================================================================
A.  Once the script for step 3 has created the file "My 20[XX] Player Attributes - Initial.csv," copy the file into 
    "docs\My Ratings\20[XX]" and make another copy as "My 20[XX] Player Attributes - In Progress 20[XX]_MM_DD.csv". 
    Manually edit (and save revision BAKs of) the file to:
    
    1. Make SURE to resolve any conflicts, meaning those fields whose values are shown as TBD or CONFLICT, and then 
    SORT THE CSV FILE by 1)team 2)position 3)jersey number. Only after making sure ALL players have a final position 
    (no 'CONFLICT' in the file) and it is sorted properly, then ...
    
    2. ...Run the add_missing_jersey_and_draft.py script to fill in any blanks for draft and jersey numbers:
        python add_missing_jersey_and_draft.py
    
    3. Run calculate_
    
    
    
    
    
    .py to add missing contract info:
        python add_missing_draft_and_contract_info.py

    4. Add other important missing/defaulted values, particularly for new players, like Face ID, Hair Style, etc.
    
    5. Sort by each field to make sure we get a range we expect, and that there are no empty or invalid values.
        * TO FIND MISSING FIELDS (BLANK CELLS IN EXCEL):
        - Select the entire range where there should be no blank cells.
        - Press F5 (fn-F5 on the Mac's keyboard). 
        - This brings up a "Go To" window. Here, click on the "Special..." button at the bottom.
        - Select the radio button for Blanks and click OK.
            It should show the first empty cell (if any) or say "No cells were found."
    
    6. Create a copy of the template file "Player Target Numbers by Position.xlsx" (from docs\Templates\) and put it 
    into the "docs\My Ratings\20[XX]" folder alongside the Player Attributes files. Working through that file, fill 
    out the roster according to the allotment numbers at each position by retiring, adding, and moving players from 
    one position to another similar position.
    
    
B.  Once the file is complete, save a final copy under "docs\My Ratings\20[XX]" as 
    "My 20[XX] Player Attributes - FINAL 20[XX]_MM_DD.csv". Also put a renamed copy of the file into 
    "process\inputs\step5" as "Current Player Attributes.csv" (overwriting the previous copy).


                                          Step 5: Update the roster file.
=======================================================================================================================

A.  1) In a command window, run the second script, "step_5_update_roster_file.py" as so: 
    
        E:\Gaming\madden_08_updater\process>python step_5_update_roster_file.py
    
    2) Move into the utilities folder and run the "dump_roster_to_csv" script so I can look at the generated roster: 
        
        E:\Gaming\madden_08_updater\process>cd utilities
        E:\Gaming\madden_08_updater\process\utilities>python dump_roster_to_csv.py
        
    (The output from this dumping will be in the folder "E:\Gaming\madden_08_updater\docs\Roster dumps\current.csv".) 
    
    The dumped file should look normal and usable in a real franchise. Inspect the CSV file to:
        a) Check all PROL and PRL2s to see that at least someone get one of each role. In particular, there should be 
            at least one: team_distraction (8), underachiever (4), project_player (7), team_mentor (5), 
            team_leader (6), etc. Well, yeah... basically, just check for all of them.
        b) Make any further refinements to the altered roster file through the MaddenAmp application. 
        
    3) After scanning the Excel dump for irregularities, take the output (the altered roster file "current.ros") and 
    test it in Madden NFL '08 to make sure it can be read and used in setting up a franchise mode. 

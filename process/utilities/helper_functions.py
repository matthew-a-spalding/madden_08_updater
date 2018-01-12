""" helper_functions.py

This is the only python sub-module used by the script "step_5_update_roster_file.py". It contains functions to perform 
any task that is repeated in the logic of that script's main function.

This file is broken up into the following sections:
1) Imports, Settings, and Constants
2) Local Variables
3) Main Function
"""

# --------------------------------------------------- SECTION 1 -------------------------------------------------------
# ---------------------------------------- IMPORTS, SETTINGS, AND CONSTANTS -------------------------------------------
# 1 - Standard library imports
import os, csv, math, ctypes

# 2 - Third-party imports

# 3 - Application-specific imports

# 4 - Global settings

# 5 - Global constants


# --------------------------------------------------- SECTION 2 -------------------------------------------------------
# --------------------------------------------- Class Declarations ----------------------------------------------------



# --------------------------------------------------- SECTION 3 -------------------------------------------------------
# ------------------------------------------------ Main Functions -----------------------------------------------------

def create_quarterback(player_dict, index):
    # For all of the following fields, we simply use 0.
    # TLHA, TRHA, PCPH, PLSH, PRSH, PLTH, PRTH, PUCL, TLEL, TREL, PTSL, PSTM, PFHO, PSXP, TLWR, TRWR, PMUS, PJTY, PSTY
    
    # PPTI will always get 1009, PLPL gets 100, PJER gets a 1, PCMT gets 999, PLHY gets -31, 
    
    # For attributes which have a column in the 'Latest Player Attributes.csv' file, use the value if it differs from 
    # the default value we put in that column. If not, we will use formulas to determine what value to use. 
    
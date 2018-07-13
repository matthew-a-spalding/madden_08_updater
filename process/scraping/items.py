r"""items.py
    
    This module is just the definition of the NFLPlayer item our spider captures.
"""
from scrapy.item import Item, Field

# pylint: disable=too-many-ancestors
class NFLPlayer(Item):
    """
        This is the class for encapsulating a player record and its fields.
    """
    acceleration = Field()
    age = Field()
    agility = Field()
    awareness = Field()
    birthdate = Field()
    break_tackle = Field()
    carrying = Field()
    catching = Field()
    college = Field()
    contract_length = Field()
    contract_years_left = Field()
    draft_pick = Field()
    draft_round = Field()
    elusiveness = Field()
    first_name = Field()
    handedness = Field()
    height = Field()
    injury = Field()
    jersey_number = Field()
    jumping = Field()
    kick_accuracy = Field()
    kick_power = Field()
    kick_return = Field()
    last_name = Field()
    pass_block = Field()
    pass_block_power = Field()
    pass_block_finesse = Field()
    playaction = Field()
    position = Field()
    run_block = Field()
    run_block_power = Field()
    run_block_finesse = Field()
    signing_bonus = Field()
    speed = Field()
    stamina = Field()
    strength = Field()
    tackle = Field()
    team = Field()
    throw_accuracy_deep = Field()
    throw_accuracy_mid = Field()
    throw_accuracy_short = Field()
    throw_on_the_run = Field()
    throw_power = Field()
    total_salary = Field()
    toughness = Field()
    trucking = Field()
    weight = Field()
    years_pro = Field()

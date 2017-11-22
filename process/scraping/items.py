"""
    This module is just the definition of the NFLPlayer item our spider captures.
"""
from scrapy.item import Item, Field

# pylint: disable=too-many-ancestors
class NFLPlayer(Item):
    """
        This is the class for encapsulating a player record and its fields.
    """
    team = Field()
    jersey_number = Field()
    first_name = Field()
    last_name = Field()
    position = Field()
    height = Field()
    weight = Field()
    age = Field()
    college = Field()
    years_pro = Field()
    speed = Field()
    acceleration = Field()
    strength = Field()
    agility = Field()
    awareness = Field()
    catching = Field()
    carrying = Field()
    throw_power = Field()
    throw_accuracy = Field()
    kick_power = Field()
    kick_accuracy = Field()
    run_block = Field()
    pass_block = Field()
    tackle = Field()
    jumping = Field()
    kick_return = Field()
    injury = Field()
    stamina = Field()
    toughness = Field()
    trucking = Field()
    elusiveness = Field()
    run_block_strength = Field()
    run_block_footwork = Field()
    pass_block_strength = Field()
    pass_block_footwork = Field()
    throw_accuracy_short = Field()
    throw_accuracy_mid = Field()
    throw_accuracy_deep = Field()
    throw_on_the_run = Field()
    total_salary = Field()
    signing_bonus = Field()
    handedness = Field()
#    draft_round = Field()
#    draft_position = Field()

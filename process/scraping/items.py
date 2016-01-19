from scrapy.item import Item, Field

class NFLPlayer(Item):
	team = Field()
	first_name = Field()
	last_name = Field()
	jersey_number = Field()
	position = Field()
	height = Field()
	weight = Field()
	age = Field()
	college = Field()
	experience = Field()
	draft_round = Field()
	draft_position = Field()
#	speed = Field()
#	strength = Field()
#	awareness = Field()
#	agility = Field()
#	acceleration = Field()
#	catching = Field()
#	carrying = Field()
#	jumping = Field()
#	break_tackle = Field()
#	tackling = Field()
#	throwing_power = Field()
#	throwing_accuracy_short = Field()
#	throwing_accuracy_medium = Field()
#	throwing_accuracy_deep = Field()
#	pass_blocking = Field()
#	run_blocking = Field()
#	kicking_power = Field()
#	kicking_accuracy = Field()
#	kick_returns = Field()
#	stamina = Field()
#	injury = Field()
#	toughness = Field()

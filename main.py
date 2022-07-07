# import pnwkit module; documentation: https://docs.pnwkit-py.mrvillage.dev/en/latest/index.html
import pnwkit
# import math module (for some calculations and functions, of course)
import math
import os
from dotenv import load_dotenv

load_dotenv()
# save my API key in a variable; will need to be set aside in a hidden file for use later for security purposes
api_key = os.getenv('API_KEY')
# create a QueryKit with my API key to create queries
kit = pnwkit.QueryKit(str(api_key))

# "Test" API call to get a bunch of information
general_query = kit.query(
    "nations", {
        "id": 244934,
        "first": 1
    }, """
	population
	soldiers
	continent
	defensive_wars{
		turns_left
	}
	offensive_wars{
		turns_left
	}
	cities{
		farm
		land
		coal_mine
		steel_mill
		powered
		infrastructure
		coal_power
	}
	massirr
	advanced_urban_planning
	urban_planning
	domestic_policy
	government_support_agency
	center_for_civil_engineering
	advanced_engineering_corps
	iron_works
	""")
# process the above nation query
general_result = general_query.get()

### FUNCTIONS ###


# function for calculating the daily food revenue of a nation
# production accurate within a few ones or tens, usage accurate within a few thousands?
def calc_food_rev(api_reult):
    # querying radiation information from GameInfo
    radiation_query = kit.query(
        "game_info", {}, """
		game_date
		radiation {
			africa
			antarctica
			asia
			australia
			europe
			global
			north_america
			south_america
		}
		""")
    # attempting to process above query
    radiation_result = radiation_query.get()
    # intialize the food_usage variable with the usage from population
    food_usage = api_reult.nations[0].population / 1000
    # if the nation is in any wars
    if (len(api_reult.nations[0].defensive_wars) > 0
            or len(api_reult.nations[0].offensive_wars) > 0):
        # add the usage from soldiers in wartime
        food_usage += api_reult.nations[0].soldiers / 500
    else:
        # add the usage from soldiers in peacetime
        food_usage += api_reult.nations[0].soldiers / 750
    # initialize the food_production variable to 0
    food_production = 0
    # iterate over all cities in the nation
    for city in api_reult.nations[0].cities:
        # initialize the city_production variable for that city to 0
        city_production = 0
        # if the nation has the Mass Irrigation national project
        if (api_reult.nations[0].massirr == True):
            # set the production to the number of farms multiplied by the land divided by 400 (effect of Mass Irrigation)
            city_production = city.farm * 12 * (city.land / 400)
        else:
            # set the production to the number of farms multiplied by the land divided by 500 (default production)
            city_production = city.farm * 12 * (city.land / 500)
        # if the nation has more than one farm
        if (city.farm > 1):
            # apply the production bonus
            city_production *= 1 + (city.farm - 1) * 0.0263157894737
        # add the current city's production to the nation's total production
        food_production += city_production
    # the continent's radiation index (need to check what continent the nation is on)
    continent_radiation = 1
    # the seasonal affect on food production (need to check what continent and season the nation is on)
    season_affect = 1
    # if they're on North America
    if (api_reult.nations[0].continent == "na"):
        continent_radiation = radiation_result.game_info.radiation.north_america
        # summer
        if (radiation_result.game_info.game_date.month > 5
                and radiation_result.game_info.game_date.month < 9):
            season_affect = 1.2
        # winter
        elif (radiation_result.game_info.game_date.month > 11
              or radiation_result.game_info.game_date.month < 3):
            season_affect = 0.8
    # if they're on South America
    elif (api_reult.nations[0].continent == "sa"):
        continent_radiation = radiation_result.game_info.radiation.south_america
        # winter
        if (radiation_result.game_info.game_date.month > 5
                and radiation_result.game_info.game_date.month < 9):
            season_affect = 0.8
        # summer
        elif (radiation_result.game_info.game_date.month > 11
              or radiation_result.game_info.game_date.month < 3):
            season_affect = 1.2
    # if they're on Europe
    elif (api_reult.nations[0].continent == "eu"):
        continent_radiation = radiation_result.game_info.radiation.europe
        # summer
        if (radiation_result.game_info.game_date.month > 5
                and radiation_result.game_info.game_date.month < 9):
            season_affect = 1.2
        # winter
        elif (radiation_result.game_info.game_date.month > 11
              or radiation_result.game_info.game_date.month < 3):
            season_affect = 0.8
    # if they're on Asia
    elif (api_reult.nations[0].continent == "as"):
        continent_radiation = radiation_result.game_info.radiation.asia
        # summer
        if (radiation_result.game_info.game_date.month > 5
                and radiation_result.game_info.game_date.month < 9):
            season_affect = 1.2
        # winter
        elif (radiation_result.game_info.game_date.month > 11
              or radiation_result.game_info.game_date.month < 3):
            season_affect = 0.8
    # if they're on Africa
    elif (api_reult.nations[0].continent == "af"):
        continent_radiation = radiation_result.game_info.radiation.africa
        # winter
        if (radiation_result.game_info.game_date.month > 5
                and radiation_result.game_info.game_date.month < 9):
            season_affect = 0.8
        # summer
        elif (radiation_result.game_info.game_date.month > 11
              or radiation_result.game_info.game_date.month < 3):
            season_affect = 1.2
    # if they're on Australia
    elif (api_reult.nations[0].continent == "au"):
        continent_radiation = radiation_result.game_info.radiation.australia
        # winter
        if (radiation_result.game_info.game_date.month > 5
                and radiation_result.game_info.game_date.month < 9):
            season_affect = 0.8
        # summer
        elif (radiation_result.game_info.game_date.month > 11
              or radiation_result.game_info.game_date.month < 3):
            season_affect = 1.2
    # if they're on Antarctica
    elif (api_reult.nations[0].continent == "an"):
        continent_radiation = radiation_result.game_info.radiation.antarctica
        # Antarctica is unaffected by season, but gets a permanent -50% food production
        food_production *= 0.5
    # calculate the radiation factor on food production
    radiationFactor = 1 - (
        (continent_radiation + radiation_result.game_info.radiation.global_) /
        1000)
    # apply the seasonal factor to the total production
    food_production *= season_affect
    # apply the radiation factor to the total production
    food_production *= radiationFactor
    # return the difference between the food_production and food_usage to determine net food revenue
    return round(food_production - food_usage, 2)


# function for calculating the cost of bringing a nation from their current city count to a goal
# completely accurate
def calc_city_cost(nation_call, goal_city):
    # intialize a temporary total cost to 0
    total_cost = 0
    # intialize a temporary cost to 0
    city_cost = 0
    for city_num in range(len(nation_call.nations[0].cities), goal_city):
        # calculate the cost of the next city
        city_cost = (50000 * pow(
            (city_num - 1), 3) + 150000 * city_num + 75000)
        # if the nation has Urban Planning project, apply it
        if (nation_call.nations[0].urban_planning == True):
            city_cost -= 50000000
        # if the nation has Advanced Urban Planning project, apply it
        if (nation_call.nations[0].advanced_urban_planning == True):
            city_cost -= 100000000
        # if the nation's domestic policy is currently Manifest Destiny, apply it
        if (nation_call.nations[0].domestic_policy ==
                pnwkit.data.DomesticPolicy(1)):
            # if the nation has Government Support Agency project, then couple its effects with Manifest Destiny
            if (nation_call.nations[0].government_support_agency == True):
                city_cost *= 0.925
            # otherwise, just apply Manifest Destiny
            else:
                city_cost *= 0.95
        # add the cost of the next city to the total cost
        total_cost += city_cost
    # finally, return the total city cost
    return total_cost


# function to calculate the cost of buying infra from a current amount to a goal amount
# accurate within a few tens or ones for multiples of 100, but within a few thousands for non-multiples of 100
def calc_infra_cost(nation_call, current_infra, goal_infra):
    infra_cost = calculate_infrastructure_value(current_infra, goal_infra)
    if (infra_cost > 0):
        if (nation_call.nations[0].center_for_civil_engineering == True
                and nation_call.nations[0].advanced_engineering_corps == True):
            if (nation_call.nations[0].domestic_policy
                    == pnwkit.data.DomesticPolicy(5) and
                    nation_call.nations[0].government_support_agency == True):
                infra_cost *= 0.825
            elif (nation_call.nations[0].domestic_policy ==
                  pnwkit.data.DomesticPolicy(5)):
                infra_cost *= 0.85
            else:
                infra_cost *= 0.9
        # if not, and if they have the Center for Civil Engineering project (lower one) with the policy supports, then apply them
        elif (nation_call.nations[0].center_for_civil_engineering == True):
            if (nation_call.nations[0].domestic_policy
                    == pnwkit.data.DomesticPolicy(5) and
                    nation_call.nations[0].government_support_agency == True):
                infra_cost *= 0.875
            elif (nation_call.nations[0].domestic_policy ==
                  pnwkit.data.DomesticPolicy(5)):
                infra_cost *= 0.9
            else:
                infra_cost *= 0.95
    return round(infra_cost, 2)


def calc_coal_rev(nation_call):
    coal_production = 0
    mill_usage = 0
    power_usage = 0
    for city in nation_call.nations[0].cities:
        city_coal = city.coal_mine * 3
        if (city.coal_mine > 1):
            city_coal *= 1 + ((city.coal_mine - 1) * 0.055555555555)
        coal_production += city_coal
        city_mill = city.steel_mill * 3
        if (city.steel_mill > 1):
            city_mill *= 1 + ((city.steel_mill - 1) * 0.125)
        if (nation_call.nations[0].iron_works == True):
            city_mill *= 1.36
        mill_usage += city_mill
        if (city.powered == True and city.coal_power > 0):
            temp_infra = city.infrastructure
            for i in range(1, city.coal_power):
                if (temp_infra >= 500):
                    temp_infra -= 500
                    power_usage += 6
                elif (temp_infra > 0):
                    math.ceil(temp_infra) / 100 * 1.2
                    temp_infra = 0
    return round(coal_production - mill_usage - power_usage, 2)


### The following code is taken directly from the open source Rift project ###
### (https://github.com/mrvillage/rift/blob/master/bot/src/funcs/tools.py) ###
def infrastructure_price(amount: float, /) -> float:
    return ((abs(amount - 10)**2.2) / 710) + 300


def calculate_infrastructure_value(start: float, end: float, /) -> float:
    value = 0
    start = round(start, 2)
    end = round(end, 2)
    difference = end - start
    if not difference:
        return 0
    if difference < 0:
        return 150 * difference
    if difference > 100 and difference % 100 == 0:
        chunk = round(infrastructure_price(start), 2) * 100
        return value + chunk + calculate_infrastructure_value(start + 100, end)
    if difference > 100 and difference % 100 != 0:
        chunk = round(infrastructure_price(start), 2) * (difference % 100)
        return (value + chunk +
                calculate_infrastructure_value(start + difference % 100, end))
    if difference <= 100:
        chunk = round(infrastructure_price(start), 2) * difference
        return value + chunk
    return value


### End of code from Rift ###

# test call to the calc_food_rev function with my nation id
print(calc_food_rev(general_result))

# test call to the calc_city_cost function with the generic API call at the beginning
print(calc_city_cost(general_result, 24))

# test call to the calc_infra_cost function with the generic API call at the beginning
print(calc_infra_cost(general_result, 2500, 2400))

# test call to the calc_coal_rev function with the generic API call at the beginning
print(calc_coal_rev(general_result))







test_query = kit.query(
    "alliances", {
        "id": 1,
        "first": 1
    }, """
	name
	""")
# process the above nation query
test_result = test_query.get()

try:
	print(test_result.alliances[0])
except:
	print("An error occurred")
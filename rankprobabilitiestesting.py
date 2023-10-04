import defs
import objs
from copy import deepcopy 

rank_config = {
    "starter": {"floor": 0, "ceiling": 0, "prob_multiplier": 0.5},
    "common": {"floor": 5, "ceiling": 0, "prob_multiplier": 1.0},
    "uncommon": {"floor": 15, "ceiling": 8, "prob_multiplier": 1.5},
    "rare": {"floor": 45, "ceiling": 25, "prob_multiplier": 2.0},
    "epic": {"floor": float("inf"), "ceiling": 50, "prob_multiplier": 3.0}}

starter_chassis = objs.Chassis("Rustbucket", "chassis", "starter", 10, [2,2,2,2,2], 200, 6, 15, 10, 40, 5)
starter_tires = objs.Part("Bycicle wheels", "wheels", "starter", 1, 20, 1, 5, 5, 0, 2)
starter_engine = objs.Part("Moped engine", "engine", "starter", 1, 10, 3, 20, 0, 20, 2)
starter_item = objs.Part("Repair Kit", "item_mount", "starter", 1, 15, 2, 10, 0, 15, 1)
starter_bumper = objs.Part("Plastic Bumper", "bumper", "starter", 1, 10, 2, 5, 0, 10, 1)

common_engine = objs.Part("4-Cylinder", "engine", "common", 2, 15, 5, 30, 0, 25, 3)
common_turret = objs.Part("Machine Gun", "turret", "common", 2, 20, 3, 15, 0, 20, 2)
common_bumper = objs.Part("Metal Bumper", "bumper", "common", 2, 18, 3, 12, 2, 8, 2)  

uncommon_bumper = objs.Part("Steel Bumper", "bumper", "uncommon", 2, 20, 4, 15, 5, 10, 3)
uncommon_tires = objs.Part("All-Terrain Tires", "wheels", "uncommon", 2, 22, 3, 15, 8, 0, 3)
uncommon_item = objs.Part("Armor Plating", "item_mount", "uncommon", 2, 20, 1, 5, 3, 10, 2)

rare_tires = objs.Part("Off-Road Tires", "wheels", "rare", 3, 25, 2, 10, 10, 0, 4)
rare_engine = objs.Part("Turbocharged V8", "engine", "rare", 3, 30, 4, 40, 5, 35, 5)
rare_chassis = objs.Chassis("Dune Buggy", "chassis", "rare", 12, [3,3,3,3,3], 250, 8, 18, 12, 50, 6)
rare_turret = objs.Part("Flamethrower", "turret", "rare", 3, 25, 2, 20, 0, 15, 3)

epic_chassis = objs.Chassis("Monster Truck", "chassis", "epic", 15, [4,4,4,4,4], 300, 10, 20, 15, 60, 8)
epic_engine = objs.Part("Electric Drive", "engine", "epic", 4, 40, 3, 50, 0, 45, 7)

inventory = {"engine":[starter_engine, rare_engine, common_engine, epic_engine],
               "wheels":[rare_tires, uncommon_tires, starter_tires], 
               "chassis":[starter_chassis, rare_chassis, epic_chassis],
               "bumper":[common_bumper, starter_bumper, uncommon_bumper],
               "item_mount":[starter_item, uncommon_item],
               "turret":[rare_turret, common_turret]}

def update_player_power(inventory):

        copied_inventory = deepcopy(inventory)
        # Assign value multiplier to each rarity
        rarity_multipliers = {
            "starter": 0.5,
            "common": 1.0,
            "uncommon": 1.5,
            "rare": 2.0,
            "epic": 3.0,
        }
        # Assign tech point multiplier
        tech_point_multiplier = 0.1
        # Assign chassis multiplier
        chassis_multiplier = 0.1
        # Get highest Tech Point chassis in player's inventory        
        highest_tech_point_chassis = max(copied_inventory["chassis"], key=lambda chassis: chassis.tech_points)
        # Get highest rarity chassis in player's inventory
        highest_rarity_chassis = max(copied_inventory["chassis"], key=lambda chassis: defs.rank_hierarchy.index(chassis.rank))
        # Get highest slot amount for each part type from all the chassis in player's inventory
        highest_slot_amounts = {}
        for chassis in copied_inventory["chassis"]:
            for part_type, slots in chassis.slots.items():
                highest_slot_amounts[part_type] = max(highest_slot_amounts.get(part_type, 0), slots)
        # Get highest rarity parts of each type up to amount of slots established by last step
        highest_rarity_parts = {}
        for part_type in highest_slot_amounts.keys():
            parts_of_type = copied_inventory[part_type]
            selected_parts = []
            while len(selected_parts) < highest_slot_amounts[part_type] and parts_of_type:
                highest_rarity_part = max(parts_of_type, key=lambda part: defs.rank_hierarchy.index(part.rank))
                selected_parts.append(highest_rarity_part)
                parts_of_type.remove(highest_rarity_part)
            highest_rarity_parts[part_type] = selected_parts
        # Calculate individual power levels of each of those parts, and sum it up
        total_power_level = 0
        for part_list in highest_rarity_parts.values():
            for part in part_list:
                part_power_level = (rarity_multipliers[part.rank] + tech_point_multiplier * part.tech_points)
                total_power_level += part_power_level
        # Calculate the power level of the highest rarity chassis with a higher weight
        highest_rarity_chassis_power = (rarity_multipliers[highest_rarity_chassis.rank] + tech_point_multiplier * highest_rarity_chassis.tech_points * chassis_multiplier)
        # Calculate the power level of the highest TP chassis with a higher weight
        highest_tech_point_chassis_power = (rarity_multipliers[highest_tech_point_chassis.rank] + tech_point_multiplier * highest_tech_point_chassis.tech_points * chassis_multiplier)
        # Add the power levels of the highest rarity and highest TP chassis with a higher weight
        total_power_level += highest_rarity_chassis_power + highest_tech_point_chassis_power

        return total_power_level

# Calculates probabilities for each rank
def rank_probabilities(power):    
    probabilities = {}
    rank_floor = ""
    rank_ceiling = ""
    #power_level = update_player_power(inventory)
    for rank in defs.rank_hierarchy:
        if power >= rank_config[rank]["floor"]:
            rank_floor = rank
        if power >= rank_config[rank]["ceiling"]:  
            rank_ceiling = rank
    print("Rank floor: ", rank_floor)
    print("Rank ceiling: ", rank_ceiling)
    in_threshold_ranks = [r for r in defs.rank_hierarchy if defs.rank_hierarchy.index(r) >= defs.rank_hierarchy.index(rank_floor) and defs.rank_hierarchy.index(r) <= defs.rank_hierarchy.index(rank_ceiling)]
    for rank in defs.rank_hierarchy:
        if rank in in_threshold_ranks:
            probabilities[rank] = round(80 / rank_config[rank]["prob_multiplier"])    
        elif defs.rank_hierarchy.index(rank) < defs.rank_hierarchy.index(rank_floor):
            probabilities[rank] = round(5 / rank_config[rank]["prob_multiplier"])    
        else:
            probabilities[rank] = round(15 / rank_config[rank]["prob_multiplier"])
    min_below_floor = min((value for rank, value in probabilities.items() if defs.rank_hierarchy.index(rank) < defs.rank_hierarchy.index(rank_floor)), default=None)
    if min_below_floor:
        for rank in defs.rank_hierarchy:
            if defs.rank_hierarchy.index(rank) < defs.rank_hierarchy.index(rank_floor):
                probabilities[rank] = min_below_floor
    return probabilities

# Tests

def test_update_player_power():

  power = update_player_power(inventory)

  print(power)

test_update_player_power()
power_level = 0
for i in range(21):
    print("\n")
    print("Power level: ", power_level)
    print(rank_probabilities(power_level))
    power_level += 5
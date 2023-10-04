import random
import defs
import mapgen
from copy import deepcopy

#-------------------------------------------------
#GAME LOGIC
#-------------------------------------------------

class Game():
    def __init__(self):
        self.current_node = None  # Initialize the current node as None
        self.inventory = defs.inventory
        self.power_level = self.update_player_power()
        self.rank_config = {
            "starter": {"floor": 0, "ceiling": 0, "prob_multiplier": 0.5},
            "common": {"floor": 5, "ceiling": 0, "prob_multiplier": 1.0},
            "uncommon": {"floor": 15, "ceiling": 8, "prob_multiplier": 1.5},
            "rare": {"floor": 45, "ceiling": 25, "prob_multiplier": 2.0},
            "epic": {"floor": float("inf"), "ceiling": 50, "prob_multiplier": 3.0}}
        self.rank_list = [r for r in self.rank_config.keys()]
        self.rank_odds = self.rank_probabilities()
        self.player_vehicle = defs.player_vehicle
        self.play()
    
    # Helper function to track player's power through their inventory to use as baseline for determining map generation difficulty and rewards
    def update_player_power(self):
        # Create deepcopy of inventory, so that it can be modified without affecting the actual inventory
        copied_inventory = deepcopy(self.inventory)
        tech_point_multiplier = 0.1
        chassis_multiplier = 0.1
        # Get highest Tech Point chassis in player's inventory        
        highest_tech_point_chassis = max(copied_inventory["chassis"], key=lambda chassis: chassis.tech_points)
        # Get highest rarity chassis in player's inventory
        highest_rarity_chassis = max(copied_inventory["chassis"], key=lambda chassis: self.rank_list.index(chassis.rank))
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
                highest_rarity_part = max(parts_of_type, key=lambda part: self.rank_list.index(part.rank))
                selected_parts.append(highest_rarity_part)
                parts_of_type.remove(highest_rarity_part)
            highest_rarity_parts[part_type] = selected_parts
        # Calculate individual power levels of each of those parts, and sum it up
        total_power_level = 0
        for part_list in highest_rarity_parts.values():
            for part in part_list:
                part_power_level = (self.rank_config[part.rank]["prob_multiplier"] + tech_point_multiplier * part.tech_points)
                total_power_level += part_power_level
        # Calculate the power level of the highest rarity chassis with a higher weight
        highest_rarity_chassis_power = (self.rank_config[highest_rarity_chassis.rank]["prob_multiplier"] + tech_point_multiplier * highest_rarity_chassis.tech_points * chassis_multiplier)
        # Calculate the power level of the highest TP chassis with a higher weight
        highest_tech_point_chassis_power = (self.rank_config[highest_tech_point_chassis.rank]["prob_multiplier"] + tech_point_multiplier * highest_tech_point_chassis.tech_points * chassis_multiplier)
        # Add the power levels of the highest rarity and highest TP chassis with a higher weight
        total_power_level += highest_rarity_chassis_power + highest_tech_point_chassis_power

        return total_power_level
        # FOR LATER: do the equivalent for mods

    # Helper function that updates rank probabilities based on player power level
    def rank_probabilities(self):    
        probabilities = {}
        rank_floor = ""
        rank_ceiling = ""
        # Cache for probability multipliers to avoid repeated lookups
        prob_multiplier_cache = {}
        # Loop through each rank to check floor and ceiling thresholds
        for rank in self.rank_list:
            # Cache multiplier for later use
            prob_multiplier = self.rank_config[rank]["prob_multiplier"]
            prob_multiplier_cache[rank] = prob_multiplier
            # Check if power level meets floor and ceiling thresholds
            if self.power_level >= self.rank_config[rank]["floor"]:
                rank_floor = rank
            if self.power_level >= self.rank_config[rank]["ceiling"]:
                rank_ceiling = rank
        # Get list of ranks between floor and ceiling and list of ranks below floor
        in_threshold_ranks = [r for r in self.rank_list if self.rank_list.index(r) >= self.rank_list.index(rank_floor) and self.rank_list.index(r) <= self.rank_list.index(rank_ceiling)]
        lower_than_threshold = [r for r in self.rank_list if self.rank_list.index(r) < self.rank_list.index(rank_floor)]
        # Loop through ranks again to calculate probabilities, ranks below treshold get lowest odds, ranks within thresholds get best odds, ranks above treshold get low odds
        for rank in self.rank_list:
            if rank in in_threshold_ranks:
                probabilities[rank] = round(80 / prob_multiplier_cache[rank])
            elif rank in lower_than_threshold:
                probabilities[rank] = round(5 / prob_multiplier_cache[rank])
            else:
                probabilities[rank] = round(15 / prob_multiplier_cache[rank])
        # All ranks below floor, if any, should have equal odds, set as the lowest of them
        min_below_floor = min((value for rank, value in probabilities.items() if rank in lower_than_threshold), default=None)
        for rank in self.rank_list:
            if rank in lower_than_threshold and min_below_floor:
                probabilities[rank] = min_below_floor
        return probabilities


    # Helper function to generate new maps
    def generate_new_map(self, min_width, max_width, min_height, max_height, min_density, max_density):
        new_map = mapgen.Map(random.randint(min_width, max_width), random.randint(min_height, max_height), round(random.uniform(min_density, max_density), 2))
        new_map.generate_map()
        new_map.assign_events()
        return new_map

    # Prompts the player on which lowest step node they want to start on the current map
    def choose_starting_node(self, map):
        first_node = defs.select_option_from_list(map.map[0], "Select your starting point:\n")
        self.current_node = first_node
        return first_node

    # Checks which type is associated with the current node, then either procedurally generates or choose the event from a list (for certain event types, should create a deepcopy of the event list and remove that entry, so it cannot be rolled again in the current map)
    def execute_event(self):
        if not self.current_node:
            return
        print(f"Entering node ({self.current_node.x}, {self.current_node.y}) - {self.current_node.type}")
        # Battle events are already random by nature, so no list will exist, just retrieve the map's general power rating to determine rank_floor and rank_ceiling
        if self.current_node.type == "battle":
            battle_events = []      # Placeholder just to remove linting
            event = random.choice(battle_events)
            event.execute()
        elif self.current_node.type == "choice":
            choice_events = []      # Placeholder just to remove linting
            event = random.choice(choice_events)
            event.execute()
        elif self.current_node.type == "garage":
            garage_events = []      # Placeholder just to remove linting
            event = random.choice(garage_events)
            event.execute()
        elif self.current_node.type == "boss":
            boss_events = []      # Placeholder just to remove linting
            event = random.choice(boss_events)
            event.execute()
        elif self.current_node.type == "treasure":
            treasure_events = []      # Placeholder just to remove linting
            event = random.choice(treasure_events)
            event.execute()
        elif self.current_node.type == "merchant":
            merchant_events = []      # Placeholder just to remove linting
            event = random.choice(merchant_events)
            event.execute()

    # Loops executing the current node, then checking if it has connections
    def move_to_next_node(self):
        while self.current_node:
            self.execute_event()
            # If so prompt for which to move on to, set the current node to that and restart the loop
            if self.current_node.connections_to:
                next_node = defs.select_option_from_list(self.current_node.connections_to, "Select your next area:\n")
                self.current_node = next_node
            # Otherwise set current_node to None to terminate the loop
            else:
                self.current_node = None
    
    # Basic game play loop
    def play(self):
        # Initialize player vehicle, with starter parts
        if not self.player_vehicle.parts:
            defs.player_init(self.player_vehicle)
        # Create a tutorial map
        tutorial_map = self.generate_new_map(1, 1, 5, 6, 1, 1)
        self.current_node = tutorial_map.map[0][0]
        self.move_to_next_node()
        # After tutorial is finished, begin the proper game loop until player is dead
        while self.player_vehicle.alive:
            map_list = [self.generate_new_map(4, 8, 10, 18, 0.2, 0.5) for i in range(3)]
            next_map = defs.select_option_from_list(map_list, "Select your next map:\n")
            self.choose_starting_node(next_map)
            self.move_to_next_node()
    

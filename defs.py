# This file fill hold all function definitions and game logic

import objs
from copy import deepcopy
import random

#-------------------------------------------------
#FUNCTION DEFINITIONS
#-------------------------------------------------

#Game loop logic
#-------------------------------------------------

# Basic option selection function
def select_option_from_list(options, prompt, tp_left = None):
    print(prompt)
    for index, option in enumerate(options):
        print(f"{index + 1}: {option}")

    while True:
        choice = input("Enter the index of the option you want to select (0 to skip): ")
        print("")
        try:
            index = int(choice) - 1
            if index == -1 and type(options[0]) != objs.Action:
                return None                                         # Skip this option
            elif 0 <= index < len(options) and tp_left is not None and hasattr(options[index], "tech_points"):
                tp_needed = options[index].tech_points
                if tp_needed > tp_left:
                    print("Not enough tech points available. Please try again.")
                    continue
                return options[index]
            elif 0 <= index < len(options):
                return options[index]
            else:
                print("Invalid index. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a valid index.")

# Turn start handling
def turn_start(vehicle):
    vehicle.regenerate_energy()
    vehicle.reduce_cooldowns()
    vehicle.update_action_availability()

# Player turn handling
def player_turn(player_vehicle, enemy_vehicle):

    turn_start(player_vehicle)
    
    # List action options
    available_actions = []                                          # Create a list to store available action
    for action in player_vehicle.actions:
        if action.available:
            available_actions.append(action)                        # Add available action to the list
    action_select_string = "Select from your available actions:"
    chosen_action = select_option_from_list(available_actions,action_select_string)
    if chosen_action is not None:                                   # Unnecessary if statement, but just so VS Code stops incorrectly linting it
        chosen_action.use(player_vehicle, enemy_vehicle)

# Enemy turn handling
def enemy_turn(player_vehicle, enemy_vehicle):
    
    turn_start(enemy_vehicle)

    available_actions = [action for action in enemy_vehicle.actions if action.available and action.name != "RAM!" and action.name != "Reload"]
    non_heal_actions = [action for action in available_actions if action.integrity_change <= 0]
    ram_dmg_calc = lambda vehicle, target: (vehicle.stats["weight"] ** 2) * (vehicle.stats["speed"] - target.stats["speed"]) if vehicle.stats["weight"] > 50 else vehicle.stats["weight"] * (vehicle.stats["speed"] - target.stats["speed"])

    ram_damage_target = ram_dmg_calc(enemy_vehicle, player_vehicle)
    ram_damage_vehicle = ram_dmg_calc(player_vehicle, enemy_vehicle)
    
    if len(available_actions) > 0:
        max_damage = max(action.damage for action in available_actions)
    else:
        max_damage = 0
    #Check if ramming would deal more damage than highest available damage dealing equipment and if there is enough integrity left
    if enemy_vehicle.stats["weight"] > player_vehicle.stats["weight"] and ram_damage_target > max_damage and enemy_vehicle.stats["integrity"] > ram_damage_vehicle:
        print(f"The opponent uses {objs.ram.name}\n")
        objs.ram.use(enemy_vehicle, player_vehicle)
    #Check for available actions including heals, if damaged
    elif len(available_actions) > 0 and enemy_vehicle.stats["integrity"] < enemy_vehicle.stats["max_integrity"]:
        action = random.choice(available_actions)
        print(f"The opponent uses {action.name}.\n")
        action.use(enemy_vehicle, player_vehicle)
    #Check for available actions including heals, if not damaged
    elif len(non_heal_actions) > 0 and enemy_vehicle.stats["integrity"] == enemy_vehicle.stats["max_integrity"]:
        action = random.choice(non_heal_actions)
        print(f"The opponent uses {action.name}.\n")
        action.use(enemy_vehicle, player_vehicle)
    #Reload if none available
    else:
        objs.reload.use(enemy_vehicle, player_vehicle)
        print("The opponent reloads all their equipment.\n")

def game_loop():
    # Create player vehicle
    player_vehicle = objs.Vehicle("Player Vehicle", "Player", None)

    # Edit player vehicle
    vehicle_edit(player_vehicle)

    # Create enemy vehicle (randomly for now)
    enemy_vehicle = create_enemy_vehicle("starter", "starter")

    player_parts = [part.name for part in player_vehicle.parts]
    enemy_parts = [part.name for part in enemy_vehicle.parts]
    print(f'Player vehicle: {player_parts}\nPlayer stats:{player_vehicle.stats}')
    print(f'Enemy vehicle: {enemy_parts}\nEnemy stats:{enemy_vehicle.stats}')

    turn = 1
    # Game loop
    while player_vehicle.alive and enemy_vehicle.alive:

        # Stalemate breaking, highest integrity percentage wins
        if turn >= 100:
            if enemy_vehicle.stats["integrity"] / enemy_vehicle.stats["max_integrity"] > player_vehicle.stats["integrity"] / player_vehicle.stats["max_integrity"]:
                print("Game Over! Your vehicle ran out of fuel.")
                break
            else:
                print("Congratulations! The enemy vehicle ran out of fuel.")
                break

        # Player's turn
        print(f"Turn: {turn}\n\n{player_vehicle.name} has {player_vehicle.stats['integrity']} integrity and {player_vehicle.stats['curr_energy']} energy left.\n{enemy_vehicle.name} has {enemy_vehicle.stats['integrity']} integrity and {enemy_vehicle.stats['curr_energy']} energy left.\n")
        player_turn(player_vehicle, enemy_vehicle)

        # Check if enemy vehicle is destroyed
        if not enemy_vehicle.alive:
            print("Congratulations! You destroyed the enemy vehicle.")
            break

        # Enemy's turn
        enemy_turn(player_vehicle, enemy_vehicle)

        # Check if player vehicle is destroyed
        if not player_vehicle.alive:
            print("Game Over! Your vehicle was destroyed by the enemy.")
            break

        turn += 1


#Vehicle build logic
#-------------------------------------------------

# Initialize player's inventory
inventory = {
    "chassis": [],
    "wheels": [],
    "engine": [],
    "bumper": [],
    "item_mount": [],
    "turret": [],
}

# Choose a part from part_list, given a determined type and rank
def select_part(type=None, rank=None):
    filtered_parts = []
    for part in objs.part_list:
        if (type is None or part.type == type) and (rank is None or part.rank == rank):
            filtered_parts.append(part)

    if not filtered_parts:
        print("No parts found.")
        return None

    print("Select a part:")
    for index, part in enumerate(filtered_parts):
        print(f"{index + 1}: {part.name} - Type: {part.type} - Rank: {part.rank}")
    select_string = ""
    new_part = select_option_from_list(filtered_parts, select_string)
    if new_part is not None:
        inventory[new_part.type].append(deepcopy(new_part))
    return None

# Edit player vehicle
def vehicle_edit(vehicle):
    chassis = inventory["chassis"]
    if not any(chassis) and vehicle.chassis.name == "Blank":                #Checks for starter status
        print("No chassis found in the inventory. Select a starter chassis to begin.")
        select_part(type="chassis", rank="starter")
        new_chassis  = chassis[0]
        for part_type, slots in new_chassis.slots.items():
            for i in range(slots):
                select_part(part_type, "starter")
        return vehicle_edit(vehicle)                                        #Restarts function so player can build their starter vehicle
    
    for part in vehicle.parts:                                              #Re-adds current build parts to inventory
        inventory[part.type].append(part)
    vehicle.parts = []                                                      #Resets parts and stats of current vehicle
    vehicle.reset_stats()
    
    string = "Select your next vehicle part.\n"
    vehicle_parts = []
    if len(chassis) == 1:
        vehicle_parts.append(chassis[0])
        chassis.remove(chassis[0])
    else:
        chassis_choice = select_option_from_list(chassis, string)
        vehicle_parts.append(chassis_choice)
        chassis.remove(chassis_choice)
    
    tp_left  = vehicle_parts[0].tech_points
    
    for part_type, slots in vehicle_parts[0].slots.items():
        for i in range(slots):
            print(f"Tech Points left: {tp_left}")
            part_choice = select_option_from_list(inventory[part_type], string, tp_left)
            if part_choice is not None:
                tp_left -= part_choice.tech_points
                vehicle_parts.append(part_choice)
                inventory[part_type].remove(part_choice)
    
    vehicle.parts = vehicle_parts
    vehicle.update_stats()
    return

# Enemy creation function, takes a minimum and maximum part rank as parameters 
def create_enemy_vehicle(rank_floor, rank_ceiling):
    rank_hierarchy = ["starter", "common", "uncommon", "rare", "epic"]
    rank_floor_index = rank_hierarchy.index(rank_floor)
    rank_ceiling_index = rank_hierarchy.index(rank_ceiling)
    usable_ranks = rank_hierarchy[rank_floor_index : rank_ceiling_index+1]

    # Select random chassis
    chassis_list = [part for part in objs.part_list if part.type == "chassis" and part.rank in usable_ranks]
    chassis = random.choice(chassis_list)
    enemy_vehicle = objs.Vehicle("Enemy Vehicle", "Enemy", [deepcopy(chassis)])

    # Add random parts to enemy vehicle within the specified rank range
    tech_points_used = 0
    for part_type, slots in chassis.slots.items():
        for _ in range(slots):
            parts = [part for part in objs.part_list if part.rank in usable_ranks and part.type == part_type and part.tech_points + tech_points_used <= chassis.tech_points]
            if parts:
                part = random.choice(parts)
                enemy_vehicle.add_part(deepcopy(part))
                tech_points_used += part.tech_points
    enemy_vehicle.reset_stats()
    enemy_vehicle.calculate_stats()
    return enemy_vehicle

#-------------------------------------------------
game_loop()
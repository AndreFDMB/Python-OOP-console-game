import random
import objs
import defs

def event_roll(eventlist):
    choice = random.choice(eventlist)
    eventlist.remove(choice)
    return choice

def battle(rankfloor, rankceiling):
    return f"Battle with ranks {rankfloor} to {rankceiling}"

def populate_path(pathlist):
    for step in pathlist:
        if pathlist.index(step) == 0:
            step.append(battle("nonboss1", "nonboss2"))
        elif pathlist.index(step) == len(pathlist) - 1:
            step.append(battle("boss1", "boss2"))
        else:
            nodes = range(random.randint(1, 4))
            for _ in nodes:
                event = event_roll(events_left)
                step.append(event)
    return pathlist

path = [[] for _ in range(random.randint(5, 8))]
events_left = [letter for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"]

#print("Before population:")
#print(path)

#populate_path(path)

#print("After population:")
#print(path)

def player_init():
    player_vhc = objs.Vehicle("Player Vehicle", "Player", None)
    defs.vehicle_edit(player_vhc)
    return player_vhc

def game_loop():
    # Create player vehicle
    player_vehicle = player_init()

    # Create enemy vehicle (randomly for now)
    #enemy_vehicle = defs.create_enemy_vehicle("starter", "starter")

    #player_parts = [part.name for part in player_vehicle.parts]
    #enemy_parts = [part.name for part in enemy_vehicle.parts]
    #print(f'Player vehicle: {player_parts}\nPlayer stats:{player_vehicle.stats}')
    #print(f'Enemy vehicle: {enemy_parts}\nEnemy stats:{enemy_vehicle.stats}')

    curr_path = populate_path(path)  # Generate a random path

    step_index = 0
    node_index = 0

    while True:
        step = curr_path[step_index]
        node = step[node_index]

        if isinstance(node, str):  # If it's a battle event
            print(f"Battle event: {node}")
            # Handle battle event here

        else:  # If it's a regular event
            event = node_roll(node)
            print(f"Event: {event}")
            # Handle regular event here

        node_index = select_node(step)  # Prompt the player to select the next node

        if node_index == -1:
            break  # Player chose to skip to the next step

        # Move to the next step or end the game if it's the last step
        if step_index + 1 < len(path):
            step_index += 1
        else:
            print("Congratulations! You reached the end of the path.")
            break

class Event:
    def __init__(self, name = "battle", string = "You run into an enemy, prepare for battle!", rank_floor = "starter", rank_ceiling = "starter", choices = None, effects = None):
        pass
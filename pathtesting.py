#Create Path list
#Create events list
#Randomly generate path length and nodes and assign events randomly from the events list (set up limiters to how many of each type can show)
#After each node resolves, prompt for next node
#After path is over, randomly generated 3 new paths based on player power level and prompt for next path

import random
import objs
import defs

class Event:
    def __init__(self, event_type, description):
        self.event_type = event_type
        self.description = description

    def execute(self, player, enemy, rank_floor = None, rank_ceiling = None, flavor_text = None, choice_dict = None):
        if self.event_type == 'battle':
            self.execute_battle(player, enemy, rank_floor, rank_ceiling)
        elif self.event_type == 'multiple_choice':
            self.execute_multiple_choice(flavor_text, choice_dict)
        elif self.event_type == 'treasure':
            self.execute_treasure()
        elif self.event_type == 'garage':
            self.execute_garage()
        elif self.event_type == 'stat_change':
            self.execute_stat_change()

    def execute_battle(self, player, enemy, rank_floor, rank_ceiling):
        # Logic for executing a battle event
        defs.create_enemy_vehicle(rank_floor, rank_ceiling)
        print("A battle event occurred!")
        turn = 1
        # Battle loop
        while player.alive and enemy.alive:

            # Stalemate breaking, highest integrity percentage wins
            if turn >= 100:
                if enemy.stats["integrity"] / enemy.stats["max_integrity"] > player.stats["integrity"] / player.stats["max_integrity"]:
                    print("Game Over! Your vehicle ran out of fuel.")
                    break
                else:
                    print("Congratulations! The enemy vehicle ran out of fuel.")
                    break

            # Player's turn
            print(f"Turn: {turn}\n\n{player.name} has {player.stats['integrity']} integrity and {player.stats['curr_energy']} energy left.\n{enemy.name} has {enemy.stats['integrity']} integrity and {enemy.stats['curr_energy']} energy left.\n")
            defs.player_turn(player, enemy)

            # Check if enemy vehicle is destroyed
            if not enemy.alive:
                print("Congratulations! You destroyed the enemy vehicle.")
                break

            # Enemy's turn
            defs.enemy_turn(player, enemy)

            # Check if player vehicle is destroyed
            if not player.alive:
                print("Game Over! Your vehicle was destroyed by the enemy.")
                break

            turn += 1

    def execute_multiple_choice(self, flavor_text, choice_dict):
        # Logic for executing a multiple choice event
        print("A multiple choice event occurred!\n")
        while True:
            print(f"{flavor_text}\n")
            for i, option in enumerate(choice_dict.keys()):
                print(f"{i}. {option}")
            choice = input("Enter the index of the option you want to select (0 to skip): ")
            print("")
            try:
                index = int(choice) - 1
                if 0 <= index < len(choice_dict):
                    return choice_dict[index][1]
                else:
                    print("Invalid index. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a valid index.")

    def execute_treasure(self):
        # Logic for executing a treasure event
        print("A treasure event occurred!")

    def execute_garage(self):
        # Logic for executing a garage event
        print("A garage event occurred!")
    
    def execute_stat_change(self):
        # Logic for executing a stat_change event
        print("A stat change event occurred!")


def generate_event(event_type):
    if event_type == 'battle':
        return Event(event_type, 'Battle Event')
    elif event_type == 'multiple_choice':
        return Event(event_type, 'Multiple Choice Event')
    elif event_type == 'treasure':
        return Event(event_type, 'Treasure Event')
    elif event_type == 'garage':
        return Event(event_type, 'Garage Event')
    elif event_type == 'stat_change':
        return Event(event_type, 'Stat Change Event')

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
events_left = []


# Example usage
event_types = ['battle', 'multiple_choice', 'treasure', 'garage', 'stat_change']

# Generate a random event
random_event_type = random.choice(event_types)
event = generate_event(random_event_type)

# Execute the event
event.execute()
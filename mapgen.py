import random
import objs
import defs
from copy import deepcopy
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Event parent class
class Event():
    def __init__(self, name, next = None):
        self.name = name
        self.next = next                        # Next event to be handled after the current is resolved, if any
    
    @property
    def player(self):
        return defs.player_vehicle
    
    # Event execution logic
    def execute(self):
        pass
    
    # Event resolve logic
    def resolve(self):
        self.execute()
        if self.next:
            self.next.execute()
        pass

# Subclass for regular battle events
class Battle(Event):
    def __init__(self, name, rank_odds_dict, next = None):
        super().__init__(name, next)
        self.part_rank_odds = rank_odds_dict
        self.enemy = self.create_enemy_vehicle()
    
    # Enemy creation function
    def create_enemy_vehicle(self):
        # Select random chassis
        chassis_rank = defs.dynamic_weighted_choice(self.part_rank_odds)
        chassis_list = [part for part in objs.part_list if part.type == "chassis" and part.rank == chassis_rank]
        chassis = random.choice(chassis_list)
        enemy_vehicle = objs.Vehicle("Enemy Vehicle", "Enemy", [deepcopy(chassis)])

        # Add random parts to enemy vehicle according to the current part rank probabilities
        tech_points_used = 0
        # Convert chassis.slots ordered dict into a list, that can be shuffled, before iterating, to avoid bias of only the first part types being filled first and last part types often no longer having any tech points
        slot_items = list(chassis.slots.items())
        random.shuffle(slot_items)
        for part_type, slots in slot_items:
            for _ in range(slots):
                part_rank = defs.dynamic_weighted_choice(self.part_rank_odds)
                parts = [part for part in objs.part_list if part.rank == part_rank and part.type == part_type and part.tech_points + tech_points_used <= chassis.tech_points]
                if parts:
                    part = random.choice(parts)
                    enemy_vehicle.add_part(deepcopy(part))
                    tech_points_used += part.tech_points
        enemy_vehicle.reset_stats()
        enemy_vehicle.calculate_stats()
        return enemy_vehicle

    def rewards(self):
        pass
    
    #execute
    def execute(self):
        defs.battle(self.player, self.enemy)
        self.rewards()

# Subclass for multiple choice events, the choices parameter will be a dictionary where keys are the choice flavor texts and the values are the associated consequences    
class Choice(Event):
    def __init__(self, name, flavor_text, choices, next = None):
        super().__init__(name, next)
        self.flavor_text = flavor_text          # The event's flavor text explaining what is happening and giving context
        self.choices = choices                  # The choices the player can make given the context, with associated effects

    def present_choice(self):
        choices = [key for key in self.choices.keys()]                          # Convert choices dictionary keys into list so it cna be fed into select_option_from_list function
        outcome = defs.select_option_from_list(choices, self.flavor_text)
        if type(self.choices[outcome] == Event):                                # Check if value of chosen key is another event object to set it as next
            self.next = self.choices[outcome]

# Subclass for vehicle editing
class Garage(Event):
    def __init__(self, name, next = None):
        super().__init__(name, next)

    # Logic for handling garage events
    def enter(self):
        print("You have entered the garage!")
        
        # Display current build
        print("Current vehicle build:")
        for part in self.player.parts:
            print(part.name)

        options = ["Edit vehicle", "Leave garage"]
        edit = defs.select_option_from_list(options, "What would you like to do?")
        
        if edit == "Edit vehicle":
            defs.vehicle_edit(self.player)
            print("Vehicle edited!")
        else:
            print("Leaving garage unchanged.")
    
    # Event execution logic
    def execute(self):
        self.enter()

# Subclass for special battles
class Boss(Event):
    def __init__(self, name,  faction, next = None):
        super().__init__(name, next)
        self.faction = faction

    def generate_boss(self, faction):
        # Get list of possible bosses
        boss_list = [] #placeholder for boss list        
        # Filter list by given faction
        faction_bosses = [boss for boss in boss_list if boss.faction == faction]
        # Randomly choose boss from filtered list
        self.boss_vehicle = random.choice(faction_bosses)

    def rewards(self):
        pass
    
    #execute
    def execute(self):
        defs.battle(self.player, self.boss_vehicle)
        self.rewards()

# Subclass for item rewards
class Treasure(Event):
    def __init__(self, name, rank_odds_dict, rank_floor = None, rank_ceiling = None, part_type = None, player_chooses = False, next = None):
        super().__init__(name, next)
        self.rank_odds_dict = rank_odds_dict    # Rank odds dictionary based on power level, to scale rewards
        self.rank_floor = rank_floor            # Determines minimum rank of parts randomly generated the treasure can roll
        self.rank_ceiling = rank_ceiling        # Determines maximum rank of parts randomly generated the treasure can roll
        self.part_type = part_type              # Determines if the reward is limited to only one part type
        self.player_chooses = player_chooses    # Determines if the reward can be chosen by the player or randomly rolled from a pool
    
    # Helper function to trim dict probabilities based on rank_floor or rank_ceiling
    def trim_ranks(self, dict):
        rank_indices = [r for r in dict.keys()]
        for key in dict.keys():
            if self.rank_floor and rank_indices.index(key) < rank_indices.index(self.rank_floor) or self.rank_ceiling and rank_indices.index(key) > rank_indices.index(self.rank_ceiling):
                dict.remove(key)
        return dict

    # Logic for players choosing to open or skip the treasure
    def open_choice(self):

        options = ["Open treasure", "Leave treasure"]
        
        choice = defs.select_option_from_list(options, "Do you want to open the treasure?")

        if choice == "Open treasure":

            possible_rewards = []

            # Filter parts by criteria
            for part in objs.part_list:
                if (self.part_type is None or part.type == self.part_type) and part.rank >= self.rank_floor and part.rank <= self.rank_ceiling:
                    possible_rewards.append(part)
            
            # Establish a trimmed rank odds dictionary based on rank floor and ceiling
            odds_dict = deepcopy(self.rank_odds_dict)
            if self.rank_floor or self.rank_ceiling:
                odds_dict = self.trim_ranks(odds_dict)

            if self.player_chooses:
                # Let player select from random subset
                subset = []
                for _ in range(3):
                    chosen_rank = defs.dynamic_weighted_choice(odds_dict)
                    rank_sublist = [part for part in possible_rewards if part.rank == chosen_rank]
                    chosen_reward = random.choice(rank_sublist)
                    while chosen_reward in subset:
                        chosen_reward = random.choice(rank_sublist)
                    subset.append(chosen_reward)
                reward = defs.select_option_from_list(subset, "Select your reward:")

            else:
                # Randomly choose reward
                chosen_rank = defs.dynamic_weighted_choice(odds_dict)
                rank_sublist = [part for part in possible_rewards if part.rank == chosen_rank]
                reward = random.choice(rank_sublist)

            # Give reward to player
            if reward:
                # Add deep copy to inventory
                defs.inventory[reward.type].append(deepcopy(reward)) 
                print(f"You received a {reward.name}!")

        else:
            print("Leaving treasure untouched.")
        
    def execute(self):
        self.open_choice()

# Subclass for vendor encounters
class Merchant(Event):
    def __init__(self, name, next):
        super().__init__(name, next)

#-------------------------------------------------

# Path node class, including a list for which other nodes it is connected to, and a type attribute
class Node():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.active = False
        self.connections_to = []
        self.connections_from = []
        self.connect_right = False
        self.connect_left = False
        self.type = ""                                  # String will be passed onto later function that randomly picks or generates an event of that type in the game loop when the player gets to this node
    
    def __repr__(self):
        return f"(""Area type and coordinates: {self.type}, {self.x}, {self.y})"

# Map class for creating, populating, connecting and defining path nodes
class Map():
    def __init__(self, map_width, map_height, density_min):
        self.map = []
        self.map_width = map_width
        self.map_height = map_height
        self.density_min = density_min
        self.density_max = round(density_min * 1.5, 2)
        self.event_odds = {
            "battle": 0.6,
            "choice": 1,
            "treasure": 0.1,
            "garage": 0.2,
            "merchant": 0.1
        }

    # Helper function for connecting two nodes both ways
    def connect_nodes(self, node1, node2):
        node1.connections_to.append(node2)
        node2.connections_from.append(node1)
        node2.active = True
    
    # Helper function for checking if type is same as in nodes with incoming connections
    def prevent_subsequent_special_events(self, node, potential_node_type):
        for connection in node.connections_from:
            if connection.type == potential_node_type:
                return False
        return True
    
    # Helper function for checking if a node rolls a special_event and there is already the same special event in an incoming connecting node, reroll until it doesn't
    def reroll_until_no_adjacent_special_node(self, node, special_event_list, curr_odds):
        while True:
            event_type = defs.dynamic_weighted_choice(curr_odds)
            if event_type in special_event_list:
                if self.prevent_subsequent_special_events(node, event_type):
                    break
            else:
                break
        return event_type

    # Helper function for adjusting odds of non-chosen special events
    def adjust_special_event_odds(self, chosen_event_type, special_event_list, curr_odds):
        for key in special_event_list:
            if key != chosen_event_type:
                curr_odds[key] *= 1.2  # Adjust as needed

    # Function for generating connections to the next step
    def generate_connections(self, node_list, next_step):
        next_index = self.map.index(next_step) + 1
        # Check if last step
        if next_index == len(self.map):
            return
        # Shuffle node order while preserving indices, to remove left to right bias during generation
        nodes = list(enumerate(node_list)) 
        random.shuffle(nodes)
        nodes = [n[1] for n in nodes]
        for node in nodes:
            # Only process the node if it has incoming connections or has been set to active randomly on the first step
            if not node.active:
                continue
            i = node.x
            random_density = round(random.uniform(self.density_min, self.density_max), 2)
            left = next_step[i-1] if i > 0 else None
            up = next_step[i]
            right = next_step[i+1] if i < len(next_step) - 1 else None

            # Loop until at least one connection is made
            while not node.connections_to:
                # Check if not left extremity, or if left adjacent node does not have a right connection
                if left and random.random() < random_density and not node_list[i - 1].connect_right:
                    self.connect_nodes(node, left)
                    node.connect_left = True  
                if right and random.random() < random_density and not node_list[i + 1].connect_left:
                    self.connect_nodes(node, right)
                    node.connect_right = True                       
                if random.random() < random_density:
                    self.connect_nodes(node, up)

    # Randomly assigns event types to each node in the created map
    def assign_events(self):
        special_events = ["treasure", "merchant", "garage"]
        current_odds = deepcopy(self.event_odds)
        for step in self.map:
            for node in step:
                # ignore iteration if node already has an assigned type (prevents reassigning boss node)
                if node.type:
                    continue
                event_type = self.reroll_until_no_adjacent_special_node(node, special_events, current_odds)
                node.type = event_type
                # If the chosen type was in special_events, reset their odds to base, to avoid overpopulating the map with these node types
                if event_type and event_type in special_events:
                    current_odds[event_type] = self.event_odds[event_type]
                # Increase odds of all special_events until they are rolled (excludes current node type if it rolled a special_events type)
                self.adjust_special_event_odds(event_type, special_events, current_odds)
                

    # Main function for generating a new map
    def generate_map(self):

        # Function for generating nodes in each step
        def generate_nodes(step_list, map_width_int):
            for x in range(map_width_int):
                step_list.append(Node(x, len(self.map) - 1))

        # Generate map with empty nodes
        for _ in range(self.map_height):
            self.map.append([])
            generate_nodes(self.map[-1], self.map_width)
        
        # Roll a random number between 2 and map_width, select that amount of nodes from the lowest index list, then generate connections to the next index list randomly, avoiding criss crossing
        first_node_amount = random.randint(2, self.map_width)
        first_nodes = random.sample(self.map[0], first_node_amount)
        for node in first_nodes:
            if node in self.map[0]:
                node.active = True
        # Create final boss step and node
        boss_node = Node(self.map_width // 2, len(self.map))
        boss_node.type = "boss"
        self.map.append([boss_node])
        # Generate all connections in map
        for i, step in enumerate(self.map):
            if i < len(self.map) - 2:
                self.generate_connections(self.map[i], self.map[i+1])
        # Connect boss node to all active nodes in previous step
        for node in self.map[-2]:
            if node.active:
                self.connect_nodes(node,self.map[-1][0])

        # Clean up nodes from the first step with no outgoing connections and the second step onwards with no incoming connections from map
        for i, step in enumerate(self.map):
            if i == 0:
                self.map[0] = [node for node in step if node.connections_to]
            else:
                step[:] = [node for node in step if node.connections_from]        

    def visualize_map(self):
        # Create a new figure for the visualization
        fig, ax = plt.subplots()

        # Define a dictionary to map event types to symbols or colors
        event_type_symbols = {
            "battle": "ro",   # Red circles for battles
            "choice": "bs",   # Blue squares for choices
            "treasure": "g^", # Green triangles for treasures
            "garage": "yp",   # Yellow pentagons for garages
            "merchant": "cv", # Cyan diamonds for merchants
            "boss": "ms"      # Magenta stars for Boss nodes
        }

        for _, step in enumerate(self.map):
            for node in step:
                # Use the appropriate symbol or color based on the node's event type
                symbol = event_type_symbols.get(node.type, "wo")  # Default to white circles for unknown types

                # Plot the node with the chosen symbol
                ax.plot(node.x, node.y, symbol, markersize=8, label=node.type)

                # Plot connections to other nodes (excluding Boss nodes)
                if node.type != "Boss":
                    for connected_node in node.connections_to:
                        ax.plot([node.x, connected_node.x], [node.y, connected_node.y], "b-")

        # Set axis limits to fit the entire plot within the figure (approximately 80% zoom out)
        x_min = -3  # Adjust as needed
        x_max = self.map_width + 3  # Adjust as needed
        y_min = -3  # Adjust as needed
        y_max = self.map_height + 3  # Adjust as needed
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)

        # Set axis limits and labels as needed
        ax.set_xlim(0, self.map_width)
        ax.set_ylim(0, self.map_height)
        ax.set_xlabel("X")
        ax.set_ylabel("Y")

        # Create custom legend elements for event types and densities
        legend_elements = [
            mpatches.Patch(color=symbol[0], label=event_type) for event_type, symbol in event_type_symbols.items()
        ]

        # Additional legend elements for map information
        map_info_elements = [
            mpatches.Patch(color="white", label=f"Map width: {self.map_width}"),
            mpatches.Patch(color="white", label=f"Map height: {self.map_height}"),
            mpatches.Patch(color="white", label=f"Map min density: {self.density_min}"),
            mpatches.Patch(color="white", label=f"Map max density: {self.density_max}")
        ]

        # Combine the legend elements
        legend_elements.extend(map_info_elements)

        # Add a legend to the plot
        ax.legend(handles=legend_elements, title="Event Types and Map Information")

        # Show the visualization
        plt.show()

#Map generation testing, uncomment to test
#maptest = Map(random.randint(4,8), random.randint(10,18), round(random.uniform(0.2, 0.6), 2))
#maptest.generate_map()
#maptest.assign_events()
#maptest.visualize_map()
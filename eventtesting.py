import random
import objs
import defs
from copy import deepcopy

# Event parent class
class Event():
    def __init__(self, name, next):
        self.name = name
        self.player = defs.player_vehicle
        self.next = next                        # Next event to be handled after the current is resolved, if any
    
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
    def __init__(self, name, rank_floor, rank_ceiling, effect, next = None):
        super().__init__(name, next)
        self.rank_floor = rank_floor            # Determines minimum rank of parts randomly generated enemy vehicle can roll
        self.rank_ceiling = rank_ceiling        # Determines maximum rank of parts randomly generated enemy vehicle can roll
        self.effect = effect                    # Special battle effects or buffs/debuffs
        self.enemy = self.create_enemy_vehicle()
    
    # Enemy creation function
    def create_enemy_vehicle(self):
        rank_hierarchy = ["starter", "common", "uncommon", "rare", "epic"]
        rank_floor_index = rank_hierarchy.index(self.rank_floor)
        rank_ceiling_index = rank_hierarchy.index(self.rank_ceiling)
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

    # Checks and applies temporary or local buffs/debuffs to the battle
    def check_effect(self):
        pass

    def rewards(self):
        pass
    
    #execute
    def execute(self):
        self.check_effect()
        defs.battle(self.player, self.enemy)
        self.rewards()
        self.resolve()

# SUbclass for multiple choice events, the choices parameter will be a dictionary where keys are the choice flavor texts and the values are the associated consequences    
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

class Garage(Event):
    def __init__(self, name, discount = None, next = None):
        super().__init__(name, next)
        self.discount = discount                # Special repairs discount on that garage

    # Logic for handling garage events
    def enter(self):
        pass

class Boss(Event):
    def __init__(self, name, effect,  next = None):
        super().__init__(name, next)
        self.effect = effect                    # Special battle effects or buffs/debuffs

class Treasure(Event):
    def __init__(self, name, rank_floor, rank_ceiling, effect, next):
        super().__init__(name, next)
        self.rank_floor = rank_floor            # Determines minimum rank of parts randomly generated the treasure can roll
        self.rank_ceiling = rank_ceiling        # Determines maximum rank of parts randomly generated the treasure can roll
        self.effect = effect                    # Special battle effects or buffs/debuffs
    
    # Logic for players choosing to open or skip the treasure
    def open_choice(self):
        pass

class Merchant(Event):
    def __init__(self, name, next):
        super().__init__(name, next)

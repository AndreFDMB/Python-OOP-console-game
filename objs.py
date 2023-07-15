# This file fill hold all class definitions and instances

from collections import namedtuple
from copy import deepcopy
import random

#-------------------------------------------------
#CLASS DEFINITIONS
#-------------------------------------------------

class Vehicle():
    def __init__(self, name, entity, chassis, parts, stats):
        self._name = name                                       # Vehicle name
        self._entity = entity                                   # Player or Enemy
        self._chassis = self.get_chassis_part()                 # Retrieves the chassis from the parts list for easy access
        self._parts = parts                                     # List of parts the build is comprised of
        self._stats = self.calculate_stats()                    # Dictionary of stats the vehicle has, like integrity, weight, speed, dodge chance, etc.
        self._stats["curr_energy"] = self._stats["energy_pool"] #Initialize current energy pool stat to be equal to vehicle's max energy pool after total stats are calculated
        self._alive = True                                      # Vehicle alive state
        self._actions = [deepcopy(part.action) for part in parts] if parts else []
        self._actions.append(reload)
        self._actions.append(ram)

#Decorators
#-------------------------------------------------

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def entity(self):
        return self._entity

    @entity.setter
    def entity(self, value):
        self._entity = value

    @property
    def parts(self):
        return self._parts

    @parts.setter
    def parts(self, value):
        self._parts = value
        self._stats = self.calculate_stats()

    @property
    def stats(self):
        return self._stats

    @stats.setter
    def stats(self, value):
        self._stats = value

    @property
    def alive(self):
        return self._alive

    @alive.setter
    def alive(self, value):
        self._alive = value

    @property
    def actions(self):
        return self._actions

    @actions.setter
    def actions(self, value):
        self._actions = value

    @property
    def chassis(self):
        return self._chassis

    @chassis.setter
    def chassis(self, value):
        self._chassis = value

#-------------------------------------------------

    def get_chassis_part(self):                     # Retrieve chassis
        for part in self.parts:
            if part.type.lower() == "chassis":
                return part
        return blank_chassis

    def calculate_stats(self):                      # Sums up each stat from the part dictionaries present in the vehicle's parts list
        total_stats = {}
        for part in self.parts:
            for key, value in part.stats.items():
                total_stats[key] = total_stats.get(key, 0) + value
        return total_stats

    def reset_stats(self):                           # Reset stats to 0
        for stat in self.stats.keys():
            stat = 0

    def update_stats(self):                          # Update vehicle stats
        for stat, value in self.stats:
            for part in self.parts:
                part_value = getattr(part, stat, 0)
                value += part_value
            getattr(self, f'set_{stat}')(value)
    
    def regenerate_energy(self):                    # Execute energy regen, checking for ceiling
        curr = self._stats["curr_energy"]
        regen = self._stats["energy_regen"]
        max = self._stats["max_energy"]
        if curr + regen <= max:
            curr += regen
        else:
            curr = max

    def reduce_cooldowns(self):                     # Execute cooldown reduction for every action
        for action in self.actions:
            if action.curr_cooldown > 0 and action.cooldown > 0:
                action.curr_cooldown(action.curr_cooldown - 1) 

    def update_action_availability(self):
        curr = self._stats["curr_energy"]
        regen = self._stats["energy_regen"]
        for action in self.actions:
            if curr + regen < action.energy_cost and action.energy_cost > 0:
                action.available(False)
            if action.curr_cooldown > 0:
                action.available(False)
            if action.curr_uses <= 0:
                action.available(False)

    def dodged(self):                               # Checks for dodge chance
        if random.random() * 100 < self.stats["dodge"]:
            return True
        return False

    def take_damage(self, damage):                   # Damage the vehicle
        integrity = self.stats["integrity"]
        integrity -= damage
        print(f"The {self.name} takes {damage} integrity damage!\n")
        if integrity <= 0:
            integrity = 0
            self.alive = False
        self.stats["integrity"] = integrity

    def add_part(self, part):                        # Add a part to the build
        if isinstance(part, Chassis):
            print("Cannot add chassis as a separate part. Use the Chassis instance while creating the vehicle.")
            return

        chassis = self.get_chassis_part()
        if chassis is None:
            print("No chassis found. Cannot add part without a chassis.")
            return

        # Check if the part is compatible with the chassis slots
        if part.type.lower() not in self.chassis.slots._fields:
            print(f"The part type '{part.type}' is not compatible with the chassis slots.")
            return

        # Check if there are part slots left for the part's type
        available_slots = getattr(self.chassis.slots, part.type.lower())
        if available_slots <= 0:
            print(f"No available slots for the part type '{part.type}' in the chassis.")
            return
        
        # Check if the part exceeds the chassis tech point allowance
        tech_point_allowance = self.chassis.tech_points
        tech_points_needed = part.tech_points
        if tech_point_allowance < tech_points_needed:
            print("Exceeds tech point allowance for the chassis.")
            return

        # Add the part to the build
        self.parts.append(deepcopy(part))
        self._chassis = self.get_chassis_part()
        self.stats = self.calculate_stats()

    def remove_part(self, part):                     # Remove a part from the build
        self.parts.remove(part)
        self.stats = self.calculate_stats()

    def clear_parts(self):                           # Clear all parts from the build and reset stats
        self.parts = []
        self.reset_stats()

class Part():
    def __init__(self, name, type, rank, tech_points, integrity, weight, speed=0, dodge=0, energy_pool=0, energy_regen=0, action=None):
        self._name = name                            # Part name
        self._type = type                            # Part type
        self._rank = rank                            # Part rank (starter, common, uncommon etc.)
        self._tech_points = tech_points              # Part's tech point value, always positive for chassis and usually negative otherwise
        self._max_integrity = integrity              # Part integrity max
        self._curr_integrity = integrity             # Part current integrity, starts at max
        self._weight = weight                        # Part weight
        self._speed = speed                          # Part speed
        self._dodge = dodge                          # Part dodge
        self._energy_pool = energy_pool              # Part energy pool
        self._energy_regen = energy_regen            # Part energy regen
        self._action = action                        # Associated action, if any
        self._stats = {                              # Dictionary of part stats
            "integrity": self.max_integrity,
            "weight": self.weight,
            "speed": self.speed,
            "dodge": self.dodge,
            "energy_pool": self.energy_pool,
            "energy_regen": self.energy_regen
        }
        part_list.append(self)

#Decorators
#-------------------------------------------------

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        self._type = value

    @property
    def rank(self):
        return self._rank

    @rank.setter
    def rank(self, value):
        self._rank = value
    
    @property
    def tech_points(self):
        return self._tech_points

    @tech_points.setter
    def tech_points(self, value):
        self._tech_points = value

    @property
    def max_integrity(self):
        return self._max_integrity

    @max_integrity.setter
    def max_integrity(self, value):
        self._max_integrity = value

    @property
    def curr_integrity(self):
        return self._curr_integrity

    @curr_integrity.setter
    def curr_integrity(self, value):
        self._curr_integrity = value

    @property
    def weight(self):
        return self._weight

    @weight.setter
    def weight(self, value):
        self._weight = value

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, value):
        self._speed = value

    @property
    def dodge(self):
        return self._dodge

    @dodge.setter
    def dodge(self, value):
        self._dodge = value

    @property
    def energy_pool(self):
        return self._energy_pool

    @energy_pool.setter
    def energy_pool(self, value):
        self._energy_pool = value

    @property
    def energy_regen(self):
        return self._energy_regen

    @energy_regen.setter
    def energy_regen(self, value):
        self._energy_regen = value

    @property
    def action(self):
        return self._action

    @action.setter
    def action(self, value):
        self._action = value

    @property
    def stats(self):
        return self._stats

    @stats.setter
    def stats(self, value):
        self._stats = value

#-------------------------------------------------

# Define a namedtuple class for the slots
Slots = namedtuple('Slots', ['wheels', 'engine', 'bumper', 'item_mount', 'turret'])

class Chassis(Part):
    def __init__(self, name, type, rank, tech_points, slots, integrity, weight, speed=0, dodge=0, energy_pool=0, energy_regen=0, action=None):
        super().__init__(name, type, rank, tech_points, integrity, weight, speed, dodge, energy_pool, energy_regen, action)
        self._slots = Slots(*slots)

#Decorators
#-------------------------------------------------

    @property
    def slots(self):
        return self._slots
    
    @slots.setter
    def slots(self, value):
        self._slots = value

#-------------------------------------------------

class Action():
    def __init__(self, name, integrity_change=0, damage=0, cooldown=0, uses=0, energy_cost=0):
        self._name = name                            # Action name
        self._integrity_change = integrity_change    # Action change to integrity, positive or negative
        self._damage = damage                        # Action damage
        self._cooldown = cooldown                    # Action cooldown per use
        self._curr_cooldown = 0                      # Action current cooldown, starts off cooldown
        self._max_uses = uses                        # Action maximum uses before reload
        self._curr_uses = uses                       # Action current uses left
        self._energy_cost = energy_cost              # Action energy cost per use
        self._available = True                       # Action availability state

#Decorators
#-------------------------------------------------

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def integrity_change(self):
        return self._integrity_change

    @integrity_change.setter
    def integrity_change(self, value):
        self._integrity_change = value

    @property
    def damage(self):
        return self._damage

    @damage.setter
    def damage(self, value):
        self._damage = value

    @property
    def cooldown(self):
        return self._cooldown

    @cooldown.setter
    def cooldown(self, value):
        self._cooldown = value

    @property
    def curr_cooldown(self):
        return self._curr_cooldown

    @curr_cooldown.setter
    def curr_cooldown(self, value):
        self._curr_cooldown = value

    @property
    def max_uses(self):
        return self._max_uses

    @max_uses.setter
    def max_uses(self, value):
        self._max_uses = value

    @property
    def curr_uses(self):
        return self._curr_uses

    @curr_uses.setter
    def curr_uses(self, value):
        self._curr_uses = value

    @property
    def energy_cost(self):
        return self._energy_cost

    @energy_cost.setter
    def energy_cost(self, value):
        self._energy_cost = value

    @property
    def available(self):
        return self._available

    @available.setter
    def available(self, value):
        self._available = value

#-------------------------------------------------

    def use(self, vehicle, target):                 #Uses the action, changing associated vehicle's stats accordingly
        if self.name == "Reload":                   #Handling special reload action
            for part in vehicle.parts:
                if part.max_uses > 0 and part.curr_uses < part.max_uses:
                    part.curr_uses(part.curr_uses + 1)
            return
        
        if self.name == "RAM!":                     #Handling special ram action calculation
            vhcweight = vehicle.stats["weight"]
            vhcspeed = vehicle.stats["speed"]
            tgtweight = target.stats["weight"]
            tgtspeed = target.stats["speed"]
            ram_damage_target = lambda: (vhcweight ** 2) * (vhcspeed - tgtspeed) if vhcweight > 50 else vhcweight * (vhcspeed - tgtspeed)
            ram_damage_vehicle = lambda: (tgtweight ** 2) * (tgtspeed - vhcspeed) if tgtweight > 50 else tgtweight * (tgtspeed - vhcspeed)
            self.integrity_change = -ram_damage_vehicle()
            self.damage = -ram_damage_target()
            return

        if self.integrity_change > 0:
            vehicle.stats["integrity"] += self.integrity_change
        if self.integrity_change < 0:
            vehicle.take_damage(self.integrity_change)
        vehicle.stats["curr_energy"] -= self.energy_cost
        self.curr_cooldown = self.cooldown
        if self.max_uses > 0:
            self.curr_uses -= 1
        if self.damage > 0:
            if target.dodged():                     #Checks for dodge before applying damage
                print(f"The {target.name} dodged the {self.name}!\n")
            else:
                target.take_damage(self.damage)

#-------------------------------------------------
#OBJECT INSTANCES
#-------------------------------------------------

#Actions
#-------------------------------------------------

ram = Action("RAM!", 1, 1)
reload = Action("Reload")

fire_smg = Action("Fire SMG", 0, 30, 0, 3)
fire_flamethrower = Action("Use Flamethrower", 0, 50, 3)
fire_laser = Action("Fire Laser", 0, 25, energy_cost=30)

medkit = Action("Medkit heal", 60, 0, 5)

trt_harpoon = Action("Fire Harpoon", 0, 60, 4)
trt_catapult = Action("Fire Catapult", 0, 75, 3)

#Chassis - slots format = ['wheels', 'engine', 'bumper', 'item_mount', 'turret']
#-------------------------------------------------

part_list = []

blank_chassis = Chassis("Blank", "chassis", 0, 0, [0, 0, 0, 0, 0], 0, 0)

tuktuk = Chassis("Tuk-Tuk", "chassis", "starter", 7, [1, 1, 0, 2, 0], 200, 6, 15, 10, 40, 5)
lada = Chassis("Lada", "chassis", "starter", 8, [1, 1, 1, 3, 1], 250, 15, 10, 8, 80, 8)
tractor = Chassis("Tractor", "chassis", "starter", 9, [2, 1, 1, 2, 1], 300, 40, 5, 2, 100, 10)

#Parts
#-------------------------------------------------

#Wheels
bicycle = Part("Bycicle wheels", "wheels", "starter", 1, 20, 1, 5, 5, 0, 2)
tractorwh = Part("Tractor wheels", "wheels", "starter", 2, 120, 10, -10, -5, 20, 2)

#Engine
mopedeng = Part("Moped engine", "engine", "starter", 1, 10, 3, 20, 0, 20, 2)
steameng = Part("Steam engine", "engine", "starter", 2, 80, 10, 30, 2, 50, 5)

#Bumper
spikes = Part("Spikes", "bumper", "starter", 1, 20, 2)
tractorshovel = Part("Tractor shovel", "bumper", "starter", 2, 100, 8, -2, -2)

#Item
smg = Part("SMG", "item", "starter", 1, 10, 2, action=fire_smg)
flamethrower = Part("Flamethrower", "item", "starter", 2, 20, 5, -2, -2, action=fire_flamethrower)
laser = Part("Laser", "item", "starter", 1, 5, 5, 0, 0, 20, -4, fire_laser)
medkit = Part("Medkit", "item", "starter", 2, 0, 6, -2, -2, 0, -2, medkit)

#Turret
harpoon = Part("Harpoon", "turret", "starter", 2, 50, 5, action=trt_harpoon)
catapult = Part("Catapult", "turret", "starter", 3, 100, 10, -4, -4, action=trt_catapult)
plas_spoiler = Part("Plastic Spoiler", "turret", "starter", 1, 25, 2, 5, 4)
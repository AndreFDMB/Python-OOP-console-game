# This file will hold all class definitions and instances

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from collections import OrderedDict
from copy import deepcopy
import random

#-------------------------------------------------
#CLASS DEFINITIONS
#-------------------------------------------------

@dataclass
class Action:
    name: str
    integrity_change: int = 0
    damage: int = 0
    cooldown: int = 0
    max_uses: int = 0
    energy_cost: int = 0
    available: bool = True
    curr_cooldown: int = 0
    
    def __post_init__(self):
        self.curr_uses = self.max_uses

    def use(self, vehicle, target):                 #Uses the action, changing associated vehicle's stats accordingly
        if self.name == "Reload":                   #Handling special reload action
            for action in vehicle.actions:
                if action.max_uses > 0 and action.curr_uses < action.max_uses:
                    action.curr_uses  += 1
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
            vehicle.heal(self.integrity_change)
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

@dataclass
class Part:
    name: str
    type: str
    rank: str
    tech_points: int
    max_integrity: int
    weight: int
    speed: int = 0
    dodge: int = 0
    energy_pool: int = 0
    energy_regen: int = 0
    action: Optional[Action] = None
    curr_integrity: int = field(init=False)
    stats: Dict[str, int] = field(default_factory=dict)  

    def __post_init__(self):
        self.curr_integrity = self.max_integrity
        self.stats = {
            "integrity": self.max_integrity,
            "weight": self.weight,
            "speed": self.speed,
            "dodge": self.dodge,
            "energy_pool": self.energy_pool,
            "energy_regen": self.energy_regen,
        }

    def __repr__(self):
        return f"{self.name}\nRank: {self.rank}\nTech Point cost: {self.tech_points}\nStats as Integrity | weight | speed | dodge | energy pool | energy regen | action\n{self.max_integrity} | {self.weight} | {self.speed} | {self.dodge}% | {self.energy_pool} | {self.energy_regen} | {self.action}\n"

class Chassis(Part):
    def __init__(self, name, type, rank, tech_points, slots, integrity, weight, speed=0, dodge=0, energy_pool=0, energy_regen=0, action=None):
        super().__init__(name, type, rank, tech_points, integrity, weight, speed, dodge, energy_pool, energy_regen, action)
        slot_names = ("wheels", "engine", "bumper", "item_mount", "turret")
        self.slots = OrderedDict(zip(slot_names, slots))

    def __repr__(self):
        return f"{self.name}\nRank: {self.rank}\nTech Points: {self.tech_points}\nSlots: {self.slots['wheels']} wheels, {self.slots['engine']} engine, {self.slots['bumper']} bumper, {self.slots['item_mount']} item mount, {self.slots['turret']} turret\n Stats as Integrity | weight | speed | dodge | energy pool | energy regen | action\n{self.max_integrity} | {self.weight} | {self.speed} | {self.dodge}% | {self.energy_pool} | {self.energy_regen} | {self.action}\n"

@dataclass
class Vehicle:
    name: str                                       # Vehicle name
    entity: str                                     # Player or Enemy
    parts: List[Part]                               # List of parts the build is comprised of

    def __post_init__(self):
        self.chassis = self.get_chassis_part()      # Retrieves the chassis from the parts list for easy access
        self.stats = self.calculate_stats()         # Dictionary of stats the vehicle has, like integrity, weight, speed, dodge chance, etc. as a sum from all the equipped parts including chassis
        self.alive = True                           # Vehicle alive state

    @property                                       # Creates copies of actions, to avoid similar actions sharing things like cooldown, uses etc.
    def actions(self):
        if not hasattr(self, "_action_copies"):
            self._action_copies = [deepcopy(part.action) for part in self.parts if part.action is not None]
            self._action_copies.append(deepcopy(reload))
            self._action_copies.append(deepcopy(ram))
        return self._action_copies

    @actions.setter
    def actions(self, value):
        self._actions = value

    def get_chassis_part(self):                     # Retrieve chassis
        for part in self.parts:
            if isinstance(part, Chassis):
                return part
        return blank_chassis

    def calculate_stats(self):                      # Calculate's vehicles total stats based on all equipped parts
        total_stats = {}
        for part in self.parts:
            for key, value in part.stats.items():
                total_stats[key] = total_stats.get(key, 0) + value
        total_stats["curr_energy"] = total_stats.get("energy_pool", 0)
        total_stats["max_integrity"] = total_stats.get("integrity", 0)
        for stat, value in total_stats.items():
            total_stats[stat] = max(value, 0)

        self._stats = total_stats
        return total_stats

    def reset_stats(self):                           # Reset stats to 0
        for stat in self.stats.keys():
            self.stats[stat] = 0

    def update_stats(self):                          # Update vehicle stats
        for stat, value in self.stats.items():
            for part in self.parts:
                part_value = getattr(part, stat, 0)
                self.stats[stat] = value + part_value
                self.stats["curr_energy"] = self.stats.get("energy_pool", 0)
                self.stats["max_integrity"] = self.stats.get("integrity", 0)
            if self.stats[stat] < 0:
                self.stats[stat] = 0
    
    def regenerate_energy(self):                    # Execute energy regen, checking for ceiling
        curr = self.stats["curr_energy"]
        regen = self.stats["energy_regen"]
        max = self.stats["energy_pool"]
        if curr + regen <= max:
            curr += regen
        else:
            curr = max
        self._stats["curr_energy"] = curr

    def reduce_cooldowns(self):                     # Execute cooldown reduction for every action
        for action in self.actions:
            if action.curr_cooldown > 0 and action.cooldown > 0:
                action.curr_cooldown -= 1

    def update_action_availability(self):           # Checks which actions are available and updates their status
        curr = self._stats["curr_energy"]
        for action in self.actions:
            if action.energy_cost > 0:
                if curr < action.energy_cost:
                    action.available = False
                else:
                    action.available = True
            if action.max_uses > 0:
                if action.curr_uses < 1:
                    action.available = False
                else:
                    action.available = True
            if action.cooldown > 0:
                if action.curr_cooldown > 0:
                    action.available = False
                else:
                    action.available = True

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

    def heal(self, amount):                         # Heals damage to the vehicle, with max integrity ceiling check
        max_integrity = self.stats["max_integrity"]
        current_integrity = self.stats["integrity"]
        new_integrity = min(current_integrity + amount, max_integrity)
        healed_amount = new_integrity - current_integrity
        print(f"The {self.name} is healed for {healed_amount} integrity.\n")
        self.stats["integrity"] = new_integrity

    def add_part(self, part):                        # Add a part to the build
        if isinstance(part, Chassis):
            print("Cannot add chassis as a separate part. Use the Chassis instance while creating the vehicle.")
            return

        # Check if the part is compatible with the chassis slots
        if part.type.lower() not in self.chassis.slots.keys():
            print(f"The part type '{part.type}' is not compatible with the chassis slots.")
            return

        # Check if there are part slots left for the part's type
        available_slots = self.chassis.slots[part.type]
        for buildpart in self.parts:
            if buildpart.type == part.type:
                available_slots -= 1
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

#Chassis - slots format = ["wheels", "engine", "bumper", "item_mount", "turret"]
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
smg = Part("SMG", "item_mount", "starter", 1, 10, 2, action=fire_smg)
flamethrower = Part("Flamethrower", "item_mount", "starter", 2, 20, 5, -2, -2, action=fire_flamethrower)
laser = Part("Laser", "item_mount", "starter", 1, 5, 5, 0, 0, 20, -4, fire_laser)
medkit = Part("Medkit", "item_mount", "starter", 2, 0, 6, -2, -2, 0, -2, medkit)

#Turret
harpoon = Part("Harpoon", "turret", "starter", 2, 50, 5, action=trt_harpoon)
catapult = Part("Catapult", "turret", "starter", 3, 100, 10, -4, -4, action=trt_catapult)
plas_spoiler = Part("Plastic Spoiler", "turret", "starter", 1, 25, 2, 5, 4)
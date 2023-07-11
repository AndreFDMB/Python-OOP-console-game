#-------------------------------------------------
#This file contain all the class and function definitions
#-------------------------------------------------

import random
from vars import *

#The base chassis class for vehicles, as well as all its relevant properties.
class Chassis():
    def __init__(self, name, slots, speed, weight, integrity, dodge, energy_pool, regen_rate, starter = False):
        self.name = name
        self.slots = slots
        self.speed = speed
        self.weight = weight
        self.integrity = integrity
        self.dodge = dodge
        self.energy_pool = energy_pool
        self.curr_energy = energy_pool
        self.regen_rate = regen_rate
        self.alive = True
        self.equipment = []
        self.starter = starter

    def __repr__(self):
        return "The {name} has:\n{integrity} integrity points\n{dodge}% chance to dodge\nSpeed is {speed}km/h\nweight is {weight} tons\n{currEnergy} energy left\n{regen} energy regenerated per turn".format(name = self.name, integrity = self.integrity, dodge = self.dodge, speed = self.speed, weight = self.weight, currEnergy = self.curr_energy, regen = self.regen_rate)
        
    #Check for dodge before applying damage
    def dodgeCheck(self):
        if random.random() * 100 < self.dodge:
            return True
        return False

    #Damage calculations, using the given action's damage value as parameter
    def takeDamage(self, damage):
        curr_integrity = self.integrity
        curr_integrity -= damage
        if curr_integrity <= 0:
            curr_integrity = 0
            self.alive = False
            print("The {name} has been destroyed!".format(name = self.name))
    
    #The default Ram action available to all vehicles
    def ram(self, enemy_speed):
        #If chassis is heavy, use higher ram multiplier, to make up for slower speed
        if self.weight > 50:
            self.ram = (self.weight ** 2) * (self.speed - enemy_speed)
        else:
            self.ram = self.weight * (self.speed - enemy_speed)

    #This shows how much energy is recovered to the pool per turn
    def energyRegen(self):
        if self.curr_energy < self.energy_pool:
            #Prevent energy pool overflow
            if self.curr_energy + self.regen_rate > self.energy_pool:
                self.curr_energy = self.energy_pool
            else:
                self.curr_energy += self.regen_rate
    
    #Adds increases or decreases from equipment. buffs or debuffs to the vehicle dynamically when passed a source object and shared stat value
    def updateAttribute(self, stat, source, duration = None):
        setattr(self, stat, getattr(self, stat) + getattr(source, stat))

#The base equipment class for mounting on vehicle equipment slots, as well as their type and properties.
class Equipment():
    def __init__(self, name, action, type, weight, heal = None, uses = -1, cooldown = 0, integrity = 0, energy_cost = 0, damage = 0, starter = False):
        self.name = name
        self.action = action
        self.type = type
        self.weight = weight
        self.heal = heal
        self.uses = uses
        self.uses_left = uses
        self.cooldown = cooldown
        self.curr_cooldown = 0
        self.integrity = integrity
        self.energy_cost = energy_cost
        self.damage = damage
        self.available = True
        self.starter = starter

    def __repr__(self):
        return "This {name} is an equipment of type {type}\nIt weights {weight} tons\nHas a healing power of {heal}\nHas {uses} uses left\nIncreases integrity by {integrity}\nHas an energy cost per use of {energy_cost}\nIt has a cooldown of {cooldown} turns per use and is currently cooling down for {curr_cooldown} turns".format(name = self.name, type = self.type, weight = self.weight, heal = self.heal, uses = self.uses, integrity = self.integrity, energy_cost = self.energy_cost, cooldown = self.cooldown, curr_cooldown = self.curr_cooldown)     
    
    def use(self, curr_energy):
        if self.available:
            #Process energy requirement
            if curr_energy >= self.energy_cost:
                #Process cooldown
                if self.cooldown > 0:
                    self.curr_cooldown = self.cooldown
                    self.available = False
                #Process ammo
                if self.uses != -1:
                    self.uses_left -= 1
                    if self.uses_left == 0:
                        self.available = False
            integrity_change = 0
            #Process health costs or bonuses from action use
            if self.heal is not None:
                integrity_change += self.heal
            #Returns value to change on self integrity, damage to enemy and energy cost even if 0
            return integrity_change, self.damage, self.energy_cost
    
    #Reduces cooldown every turn for weapons with cooldown above 0
    def reduceCooldown(self):
        if self.curr_cooldown != 0:
            self.curr_cooldown -= 1
        #Make self available if cooldown reaches 0
        if self.curr_cooldown == 0:
            self.available = True

    #The default Reload action available to all equipments with uses
    def reload(self):
        if self.uses_left < self.uses:
            self.uses_left += 1
            #Make self available if not on cooldown
            if self.curr_cooldown == 0:
                self.available = True

#-------------------------------------------------
#Game logic function definitions
#-------------------------------------------------

#Ram action
def ram(self, target):
    ram_damage = self.ram(target.speed)
    target_damage = target.ram(self.speed)
    if not target.dodgeCheck():
        self.takeDamage(target_damage)
        target.takeDamage(ram_damage)
        print("The {self} rams the {target}, dealing {damage} damage to its integrity and taking {selfdamage} damage!".format(self = self.name, target = target.name, damage = ram_damage, selfdamage = target_damage))
    else:
        print("The {target} dodged the ram attack!".format(target = target.name))

#Use equipment
def use(vehicle, target, eqpt):
    integrity_change, damage, energy_cost = eqpt.use(vehicle.curr_energy)
    vehicle.curr_energy -= energy_cost
    vehicle.integrity += integrity_change
    if damage > 0:
        if not target.dodgeCheck():
            target.takeDamage(damage)
        else:
            print("The {target} dodged the attack!".format(target = target.name))

#Player turn events
def player_turn(player_vehicle, enemy_vehicle):
    #Regen energy
    player_vehicle.energy_regen()
    #Lower cooldowns
    for equipment in player_vehicle.equipment:
        equipment.reduceCooldown()
    
    while True:
        # List action options
        print("Player's turn:")
        print("1. Ram")
        print("2. Reload")
        available_equipment = []  # Create a list to store available equipment
        for i, equipment in enumerate(player_vehicle.equipment):
            if equipment.available:
                available_equipment.append(equipment)  # Add available equipment to the list
                print(f"{len(available_equipment) + 2}. Use {equipment.action}")

        # Prompt for selection
        action = input("Select an action: ")

        # Execute selection
        if action == "1":
            ram(player_vehicle, enemy_vehicle)
            break  # Break out of the loop after valid action
        elif action == "2":
            for equipment in player_vehicle.equipment:
                equipment.reload()
            print("You reload all your equipment.")
            break  # Break out of the loop after valid action
        else:
            action_index = int(action) - 3
            if action_index >= 0 and action_index < len(available_equipment):
                equipment = available_equipment[action_index]
                # Use the selected equipment
                use(player_vehicle, enemy_vehicle, equipment)
                break  # Break out of the loop after valid action
            else:
                print("Invalid action! Please try again.\n")

def enemy_turn(player_vehicle, enemy_vehicle):
    #Regen energy
    enemy_vehicle.energy_regen()
    #Lower cooldowns
    for equipment in enemy_vehicle.equipment:
        equipment.reduceCooldown()

    available_equipment = []  # Create a list to store available equipment
    for equipment in enemy_vehicle.equipment:
        if equipment.available:
            available_equipment.append(equipment)
    
    #Check for ramming priority
    if enemy_vehicle.weight > player_vehicle.weight:
        #Check if ramming would deal more damage then highest available damage dealing equipment and if there is enough integrity left
        ram_damage = enemy_vehicle.ram(player_vehicle.speed)
        max_weapon_damage = max(equipment.damage for equipment in available_equipment)
        if ram_damage > max_weapon_damage and enemy_vehicle.integrity > enemy_vehicle.ram(player_vehicle.speed):
            ram(enemy_vehicle, player_vehicle)
    #Check for available equipment
    elif len(available_equipment) > 0:
        action = random.choice(available_equipment)
        use(enemy_vehicle, player_vehicle, action)
    #Reload if none available
    else:
        for equipment in enemy_vehicle.equipment:
            equipment.reload()
        print("The opponent reloads all their equipment.")

#Player starter chassis choice
def choose_starter_item(lst):
    item_type = 0
    if type(lst[0]) == Chassis:
        item_type = 1
    if item_type == 1:
        print("Choose a chassis:")
    else: 
        print("Choose an equipment:")
    #Create a list of starter chassis
    starters = [chassis for chassis in lst if chassis.starter]
    
    #Print list of selections
    for i, chassis in enumerate(starters):
        print("{index}. {chassis}".format(index=i+1, chassis=chassis))
    
    #Input for selection
    if item_type == 1:    
        item_index = int(input("Select a chassis: ")) - 1
    else:
        item_index = int(input("Select an equipment: ")) - 1
    if item_index >= 0 and item_index < len(starters):
        return starters[item_index]
    else:
        print("Invalid selection.")
        return choose_starter_item(lst)

def start_game():
    # Select a chassis
    chassis = choose_starter_item(chassislist)

    # Choose weapons for each slot in the chassis
    for i in range(chassis.slots):
        equipment = choose_starter_item(equipmentlist)
        chassis.weapons.append(equipment)

    # Create enemy chassis
    enemy_chassis = random.choice(chassislist)  # Select a random chassis from the vehicles list

    # Choose weapons for each slot in the enemy's chassis
    for i in range(enemy_chassis.slots):
        equipment = random.choice(equipmentlist)  
        # Select a random weapon from the weapons list
        enemy_chassis.weapons.append(equipment)  

    current_turn = 1
    # Start the game loop
    while True:
        print("Turn "+ str(current_turn))
        print(chassis)
        print(enemy_chassis)
        print("")

        player_turn(chassis, enemy_chassis)
        if not enemy_chassis.alive:
            print("You win!")
            break

        enemy_turn(chassis, enemy_chassis)
        if not chassis.alive:
            print("You lose!")
            break

        current_turn += 1
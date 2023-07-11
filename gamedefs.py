#-------------------------------------------------
#Contains all the class and function definitions
#-------------------------------------------------

import random
import copy

#-------------------------------------------------
#CLASS DEFINITIONS
#-------------------------------------------------

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
        return "The {name} has:\n{integrity} integrity points\n{dodge}% chance to dodge\nSpeed is {speed}km/h\nweight is {weight} tons\n{currEnergy} energy left out of {totalEnergy}\n{regen} energy regenerated per turn\n".format(
            name = self.name, 
            integrity = self.integrity, 
            dodge = self.dodge, 
            speed = self.speed, 
            weight = self.weight, 
            currEnergy = self.curr_energy,
            totalEnergy = self.energy_pool, 
            regen = self.regen_rate)
        
    #Check for dodge before applying damage
    def dodgeCheck(self):
        if random.random() * 100 < self.dodge:
            return True
        return False

    #Damage calculations, using the given action's damage value as parameter
    def takeDamage(self, damage):
        self.integrity -= damage
        if self.integrity <= 0:
            self.integrity = 0
            self.alive = False
            print("The {name} has been destroyed!".format(name = self.name))
    
    #The default Ram action available to all vehicles
    def ram(self, enemy_speed):
        #If chassis is heavy, use higher ram multiplier, to make up for slower speed
        if self.weight > 50:
            return (self.weight ** 2) * (self.speed - enemy_speed)
        else:
            return self.weight * (self.speed - enemy_speed)

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
    
    #Flags equipment as unavailable if insufficient energy, or on cooldown, or without ammo
    def updateEquipmentAvailability(self):
        for equipment in self.equipment:
            if equipment.energy_cost > self.curr_energy + self.regen_rate:
                equipment.available = False
            if equipment.curr_cooldown > 0:
                equipment.available = False
            if equipment.uses > 0 and equipment.uses_left == 0:
                equipment.available = False

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
        return "This {name} is an equipment of type {type}\nIt weights {weight} tons\nHas a healing power of {heal}\nHas {uses} uses left\nIncreases integrity by {integrity}\nHas an energy cost per use of {energy_cost}\nIt has a cooldown of {cooldown} turns per use and is currently cooling down for {curr_cooldown} turns".format(
            name = self.name, 
            type = self.type, 
            weight = self.weight, 
            heal = self.heal, 
            uses = self.uses, 
            integrity = self.integrity, 
            energy_cost = self.energy_cost, 
            cooldown = self.cooldown, 
            curr_cooldown = self.curr_cooldown)     
    
    def use(self, vehicle):
        #Process cooldown
        if self.cooldown > 0:
            self.curr_cooldown = self.cooldown
        #Process ammo
        if self.uses_left > 0:
            self.uses_left -= 1
        #Process health costs or bonuses from action use
        integrity_change = 0
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
#CLASS INSTANCES
#-------------------------------------------------

#-------------------------------------------------
#Chassis section
#-------------------------------------------------
moped = Chassis("Moped", 2, 50, 2, 150, 30, 50, 5, True)
lada = Chassis("Lada", 4, 60, 10, 250, 10, 60, 10, True)
tractor = Chassis("Tractor", 3, 30, 50, 300, 5, 100, 10, True)

chassislist = [moped,lada,tractor]

#-------------------------------------------------
#Equipment section
#-------------------------------------------------
smg = Equipment("SMG", "Fire SMG", "weapon", 1, uses=3, integrity=25, damage=25, starter=True)
laser = Equipment("Laser", "Fire Laser", "weapon", 3, integrity=30, damage=20, energy_cost=25,starter=True)
flamethrower = Equipment("Flamethrower", "Fire Flamethrower", "weapon", 10, integrity=50, damage=30, cooldown=4, starter=True)

equipmentlist = [smg, laser, flamethrower]

#-------------------------------------------------
#Game logic function definitions
#-------------------------------------------------

#Ram action
def ram(vehicle, target):
    ram_damage = vehicle.ram(target.speed)
    target_damage = target.ram(vehicle.speed)
    if not target.dodgeCheck():
        vehicle.takeDamage(target_damage)
        target.takeDamage(ram_damage)
        print("The {vehicle} rams the {target}, dealing {damage} damage to its integrity and taking {selfdamage} damage!".format(vehicle = vehicle.name, target = target.name, damage = ram_damage, selfdamage = target_damage))
    else:
        print("The {target} dodged the ram attack!".format(target = target.name))

#Use equipment
def use(vehicle, target, eqpt):
    integrity_change, damage, energy_cost = eqpt.use(vehicle)
    vehicle.curr_energy -= energy_cost
    vehicle.integrity += integrity_change
    if damage > 0:
        if not target.dodgeCheck():
            target.takeDamage(damage)
            print("{action} deals {damage} damage to the enemy's integrity! They now have {integrityleft} integrity left.".format(
                action = eqpt.action, 
                damage = damage, 
                integrityleft = target.integrity))
        else:
            print("The {target} dodged the attack!".format(target = target.name))
    vehicle.updateEquipmentAvailability()

#Player turn events
def player_turn(player_vehicle, enemy_vehicle):
    #Regen energy
    player_vehicle.energyRegen()
    #Lower cooldowns
    for equipment in player_vehicle.equipment:
        equipment.reduceCooldown()
    player_vehicle.updateEquipmentAvailability()
    
    while True:
        # List action options
        print("Player's turn:")
        print("1. Ram")
        print("2. Reload")
        available_equipment = []  # Create a list to store available equipment
        for i, equipment in enumerate(player_vehicle.equipment):
            if equipment.available == True:
                available_equipment.append(equipment)  # Add available equipment to the list
                print(f"{len(available_equipment) + 2}. {equipment.action}")

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
        elif action.isdigit() and 2 < int(action) < 2 + len(available_equipment) + 1:
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
    enemy_vehicle.energyRegen()
    #Lower cooldowns
    for equipment in enemy_vehicle.equipment:
        equipment.reduceCooldown()
    enemy_vehicle.updateEquipmentAvailability()

    available_equipment = []  # Create a list to store available equipment
    for equipment in enemy_vehicle.equipment:
        if equipment.available:
            available_equipment.append(equipment)
    
    #Check for ramming priority
    if enemy_vehicle.weight > player_vehicle.weight:
        #Check if ramming would deal more damage then highest available damage dealing equipment and if there is enough integrity left
        ram_damage = enemy_vehicle.ram(player_vehicle.speed)
        max_damage = max(equipment.damage for equipment in available_equipment)
        if ram_damage > max_damage and enemy_vehicle.integrity > enemy_vehicle.ram(player_vehicle.speed):
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
    enemy_vehicle.updateEquipmentAvailability()

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
        chassis.equipment.append(equipment)
        chassis.updateAttribute("integrity", equipment)
        chassis.updateAttribute("weight", equipment)

    # Create enemy chassis
    enemy_chassis = copy.deepcopy(random.choice(chassislist))  # Select a random chassis from the vehicles list
    enemy_chassis.equipment = []

    # Choose weapons for each slot in the enemy's chassis
    for i in range(enemy_chassis.slots):
        equipment = random.choice(equipmentlist)
        enemy_equipment = copy.deepcopy(equipment)
        enemy_chassis.equipment.append(enemy_equipment)
        enemy_chassis.updateAttribute("integrity", enemy_equipment)
        enemy_chassis.updateAttribute("weight", enemy_equipment)
        
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

start_game()
#-------------------------------------------------
#This file contain all the class and function definitions
#-------------------------------------------------

import random

#The base chassis class for vehicles, as well as all its relevant properties.
class Chassis():
    def __init__(self, name, slots, speed, weight, integrity, dodge, energy_pool, regen_rate):
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
    def updateAttribute(self, stat, source):
        setattr(self, stat, getattr(self, stat) + getattr(source, stat))

#The base equipment class for mounting on vehicle equipment slots, as well as their type and properties.
class Equipment():
    def __init__(self, name, action, type, weight, heal = None, uses = -1, cooldown = 0, integrity = 0, energy_cost = 0, damage = 0):
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
        self.damage = 0
        self.available = True

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
            #Returns value to change on self integrity and damage to enemy, even if 0
            return integrity_change, self.damage
    
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

def player_turn():
    pass

def enemy_turn():
    pass

def start_game():
    pass

def choose_chassis():
    pass

def choose_weapon():
    pass
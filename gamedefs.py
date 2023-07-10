#-------------------------------------------------
#This file contain all the class and function definitions
#-------------------------------------------------

#The base chassis class for vehicles, as well as all its relevant properties.
class Chassis():
    def __init__(self, name, slots, speed, weight, integrity, energy_pool, regen_rate):
        self.name = name
        self.slots = slots
        self.speed = speed
        self.weight = weight
        self.integrity = integrity
        self.energy_pool = energy_pool
        self.regen_rate = regen_rate
        self.alive = True

    def __repr__(self):
        return "placeholderstring"
        
    #Check for dodge before applying damage
    def dodgeCheck(self):
        pass

    #Damage calculations, using the given action's damage value as parameter
    def takeDamage(self, damage):
        pass

    #The default Ram action available to all vehicles
    def ram(self):
        pass

    #The default Reload aciton available to all vehicles
    def reload(self):
        pass

    #This shows how much energy is recovered to the pool per turn
    def energyRegen(self):
        pass

#The base equipment class for mounting on vehicle equipment slots, as well as their type and properties.
class Equipment():
    def __init__(self, name, type, weight, heal = 0, uses = -1, integrity = 0, energy_cost = 0):
        pass

    def __repr__(self):
        return "placeholderstring"     
    
    def use(self):
        pass

    def reduceCooldown(self):
        pass

#The weapon equipment subclass.
class Weapon(Equipment):
    pass

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
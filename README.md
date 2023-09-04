# Python-OOP-console-game

*This project will be a simple turn based battle game, run initially on the terminal, to showcase OOP programming in Python, as well as version control and in the near future database generation and maintenance. (Further down the line, it may have actual UI and graphics added.)*

The basic premise is simple: players build their own vehicles out of a selection of available chassis, each with different stats, equipment mounts and so on, and then assign equipment to the equipmentn slots, each equipment piece enabling an action that the player may take on their turn, whether attacking the opponent, buffing themselves, or healing, among others.
Players start by choosing their starter chassis and weapon from a limited selection, and then battle randomly generated enemies in turn based combat, picking actions according to their vehicle build and availability in order to defeat their foes and obtain more parts to make better builds.

**To run a starter battle vertical slice, simply run the defs.py file.**

**TO-DO:**
-enhance gameloop with paths and varying events and rewards
    -make special event classes
        -parent event class
            -base execution logic
            -check for running another event after current event is resolved
            -choose next node
        -battle event
            -create enemy
            -apply special temporary effects, if any
            -battle logic
            -battle rewards
        -multiple choice event
            -base execution logic
            -multiple choices with varying efefcts, including gaining/losing currency, or leading to different event types
        -garage event
            -offer repairs (possibly with discount)
            -ability to edit build
        -boss event
            -boss based on player build overall tech rank
            -boss reward
        -treasure event
            -choice between treasure or skipping
            -picking treasure may lead to other events, such as battles
        -merchant event
            -merchant provides parts or temporary buffs
    -path system
        -create path lists based on player overall tech score and give player choice on which to pick (except for the very first "tutorial" path)
        -populate with randomly generated nodes with existing events
    -integrate into game loop logic
        -apply event system to path generation and path generation to base game loop
-expand chassis and equipment selection (through a SQLite database and object instance creator script)
-currency system (fuel and scrap)
-part mod system
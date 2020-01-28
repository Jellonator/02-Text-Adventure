#!/usr/bin/env python3
import sys, os
# Check to make sure we are running the correct version of Python
assert sys.version_info >= (3,7), "This script requires at least Python 3.7"

import character
import json
import gameutil
import gameenemy
import gameitem

# The game and item description files (in the same folder as this script)
FILE_LEVEL = 'level.json'
FILE_ITEMS = 'items.json'
FILE_CLASSES = "classes.json"
FILE_ENEMIES = "enemies.json"

# Load the contents of the files into the game and items dictionaries. You can largely ignore this
# Sorry it's messy, I'm trying to account for any potential craziness with the file location
def load_json(name: str):
    try:
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        with open(os.path.join(__location__, name)) as json_file: 
            return json.load(json_file)
    except:
        print("There was a problem reading either the game or item file.")
        os._exit(1)

class GameData:
    def __init__(self, leveldata, itemdata, player, enemydefs):
        self.level = leveldata
        self.items = itemdata
        self.player = player
        self.enemydefs = enemydefs
        self.room = ""
        self.lastroom = ""
        self.finished = False
        self.actions = {
            "help": GameAction(action_help, "You're already using this, dummy!"),
            "stat": GameAction(action_stat, "Gives information on your current stats."),
            "quit": GameAction(action_quit, "Quit the game."),
            "move": GameAction(action_move, "Move to another room."),
            "inventory": GameAction(action_inventory, "List inventory items."),
            "attack": GameAction(action_attack, "Attack an enemy")
        }
        self.explored = {}
        self.cleared_combats = {}
        self.encounter = []

class GameAction:
    def __init__(self, func, helptext):
        self.func = func
        self.help = helptext

def action_help(gamedata, args):
    if len(args) == 0:
        print("Available actions:", ", ".join(gamedata.actions.keys()))
        print("Type 'help action' for information about the given action.")
    elif len(args) == 1:
        name = args[0]
        if name in gamedata.actions:
            print(gamedata.actions[name].help)
    else:
        print("Too many arguments to 'help'.")

def action_stat(gamedata, args):
    if len(args) == 0:
        print(gamedata.player.format_string())
        print("Type 'stat statname' for more information about the given stat.")
    elif len(args) == 1:
        name = args[0]
        if name in ["str", "strength"]:
            print("Strength, your physical power and health.")
            print("If you run out, you die from your injuries.")
            print("STR:", gamedata.player.strength.format_string())
        elif name in ["dex", "dexterity"]:
            print("Dexterity, your agility and stealthiness.")
            print("If you run out, you cease to move again.")
            print("DEX:", gamedata.player.dexterity.format_string())
        elif name in ["wis", "wisdom"]:
            print("Wisdom, your mental acuity and intelligence.")
            print("If you run out, you lose the will to keep going.")
            print("WIS:", gamedata.player.wisdom.format_string())
        elif name in ["soul"]:
            print("Soul, your mortal connection.")
            print("If you run out, you succumb to the darkness and your soul is lost forever.")
            print("SOUL:", gamedata.player.soul.format_string())
        else:
            print("Unknown stat '{}'".format(name))
    else:
        print("Too many arguments to 'stat'.")

def action_quit(gamedata, args):
    if len(args) == 0:
        gamedata.finished = True
    else:
        print("Too many arguments to 'help'.")

def action_move(gamedata, args):
    if len(args) == 0:
        print("Need at least one argument to 'move'.")
    elif len(args) == 1:
        if len(gamedata.encounter) > 0:
            print("You're engaged in combat, unable to move!")
            return
        name = args[0]
        exitdata = gamedata.level[gamedata.room]["exits"]
        try:
            index = int(name) - 1
            if index in range(len(exitdata)):
                enter_location(gamedata, exitdata[index]["target"])
                return
        except ValueError:
            for data in exitdata:
                if data["exit"].lower() == name:
                    enter_location(gamedata, data["target"])
                    return
        print("Invalid exit '{}'".format(name))
    else:
        print("Too many arguments to 'move'.")

def action_inventory(gamedata, args):
    if len(args) == 0:
        numitems = len(gamedata.player.inventory)
        if numitems == 0:
            print("You don't have anything in your inventory.")
        else:
            if numitems == 1:
                print("You have 1 item in your inventory:")
            else:
                print("You have {} items in your inventory:".format(numitems))
            for item in gamedata.player.inventory:
                print("\t{}".format(item.name))
    else:
        print("Too many arguments to 'inventory'")

def action_attack(gamedata, args):
    if len(args) == 0:
        if len(gamedata.encounter) == 0:
            print("No enemies to attack.")
            return
        attacks = gamedata.player.get_attacks()
        attack = gameutil.choose_from_list(attacks, True, "Choose an attack")
        if attack == None:
            return
        attack.use(gamedata, {})
    else:
        print("Too many arguments to 'attack'")

def enter_location(gamedata, location):
    if location == gamedata.room:
        print("You tried to move there, but you were already there all along!\nFunny how nature do that.")
        return
    if location in gamedata.level:
        gamedata.explored[location] = True
        gamedata.lastroom = gamedata.room
        gamedata.room = location
        roomdata = gamedata.level[location]
        if "name" in roomdata:
            print("You enter the '{}'.".format(roomdata["name"]))
        else:
            print("You enter the room.")
        if "desc-post-combat" in roomdata and location in gamedata.cleared_combats:
            print(roomdata["desc-post-combat"])
        if "desc" in roomdata:
            print(roomdata["desc"])
        else:
            print("There is nothing noteworthy about this room.")
        if "encounter" in roomdata and location not in gamedata.cleared_combats:
            for enemyname in roomdata["encounter"]:
                if enemyname in gamedata.enemydefs:
                    enemy = gameenemy.GameEnemy(enemyname, gamedata.enemydefs[enemyname])
                    gamedata.encounter.append(enemy)
                else:
                    print("Unknown enemy '{}'".format(enemyname))
            if len(gamedata.encounter) > 0:
                print("You were ambushed by {}!".format(gameutil.gen_ambush_text(gamedata.encounter)))
    else:
        print("Unrecognized location '{}'".format(location))

def render(gamedata):
    print(gamedata.player.format_string())
    roomdata = gamedata.level[gamedata.room]
    if len(gamedata.encounter) == 0:
        if "exits" in roomdata and len(roomdata["exits"]) > 0:
            exitdefs = roomdata["exits"]
            exitnum = len(exitdefs)
            if exitnum == 1:
                print("There is 1 exit:")
            else:
                print("There are {} exits:".format(exitnum))
            for i, exitdata in enumerate(exitdefs):
                exitinfo = "???"
                exitname = exitdata["exit"]
                exittarget = exitdata["target"]
                if exittarget in gamedata.explored and exittarget in gamedata.level:
                    exitinfo = gamedata.level[exittarget]["name"]
                print("    {}. {}:\t{}".format(i, exitname, exitinfo))
            print("Enter 'move location' to move to another location")
        else:
            print("There doesn't appear to be anywhere to go...")
    else:
        print("Type 'attack' to attack an enemy")

def update(gamedata):
    i = 0
    prevlen = len(gamedata.encounter)
    while i < len(gamedata.encounter):
        enemy = gamedata.encounter[i]
        if enemy.is_dead():
            gamedata.encounter.pop(i)
            print("You killed the {}!".format(enemy.name))
        else:
            i += 1
    if len(gamedata.encounter) == 0 and prevlen > 0:
        print("You defeated all of the enemies!")
        input("Press enter to continue...")

def game_loop(gamedata):
    while not gamedata.finished:
        render(gamedata)
        userinput = input("> ").lower().strip()
        userargs = userinput.split()
        if len(userargs) > 0:
            action = userargs[0]
            args = userargs[1:]
            if action in gamedata.actions:
                gamedata.actions[action].func(gamedata, args)
            else:
                print("Unknown action '{}'".format(action))
        update(gamedata)

# The main function for the game
def main():
    level = load_json(FILE_LEVEL)
    items = load_json(FILE_ITEMS)
    classdefs = load_json(FILE_CLASSES)
    enemydefs = load_json(FILE_ENEMIES)
    
    player = character.generate_character(classdefs, items)
    gamedata = GameData(level, items, player, enemydefs)
    print("Type 'help' for information.")
    enter_location(gamedata, "WHOUS")
    game_loop(gamedata)

# run the main function
if __name__ == '__main__':
	main()
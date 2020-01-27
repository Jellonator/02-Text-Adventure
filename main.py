#!/usr/bin/env python3
import sys, os
# Check to make sure we are running the correct version of Python
assert sys.version_info >= (3,7), "This script requires at least Python 3.7"

import character
import json

# The game and item description files (in the same folder as this script)
FILE_LEVEL = 'zork.json'
FILE_ITEMS = 'items.json'
FILE_CLASSES = "classes.json"

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
    def __init__(self, leveldata, itemdata, player, startroom):
        self.level = leveldata
        self.items = itemdata
        self.player = player
        self.room = startroom
        self.finished = False
        self.actions = {
            "help": GameAction(action_help, "You're already using this, dummy!"),
            "stat": GameAction(action_stat, "Gives information on your current stats."),
            "quit": GameAction(action_quit, "Quit the game.")
        }

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
            print("Unknown stat name.")
    else:
        print("Too many arguments to 'stat'.")

def action_quit(gamedata, args):
    if len(args) == 0:
        gamedata.finished = True
    else:
        print("Too many arguments to 'help'.")

def game_loop(gamedata):
    print("Type 'help' for information.")
    while not gamedata.finished:
        userinput = input("> ").lower().strip()
        userargs = userinput.split()
        if len(userargs) > 0:
            action = userargs[0]
            args = userargs[1:]
            if action in gamedata.actions:
                gamedata.actions[action].func(gamedata, args)

# The main function for the game
def main():
    current = 'WHOUS' # The starting location

    level = load_json(FILE_LEVEL)
    items = load_json(FILE_ITEMS)
    classdefs = load_json(FILE_CLASSES)
    
    player = character.generate_character(classdefs)
    print(player.format_string())
    gamedata = GameData(level, items, player, current)
    game_loop(gamedata)

# run the main function
if __name__ == '__main__':
	main()
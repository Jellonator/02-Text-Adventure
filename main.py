#!/usr/bin/env python3
import sys, os, json
# Check to make sure we are running the correct version of Python
assert sys.version_info >= (3,7), "This script requires at least Python 3.7"

import character

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

# The main function for the game
def main():
    current = 'WHOUS'  # The starting location
    end_game = ['END']  # Any of the end-game locations

    level = load_json(FILE_LEVEL)
    items = load_json(FILE_ITEMS)
    classdefs = load_json(FILE_CLASSES)
    
    player = character.Character()
    classlist = [name for name in classdefs]
    classlist.sort()
    for i, classname in enumerate(classlist):
        print("{}. {}".format(i + 1, classname))
    index = -1
    numclasses = len(classlist)
    while not index in range(numclasses):
        try:
            index = int(input("What is your class? [1-{}]: ".format(numclasses))) - 1
            if not index in range(numclasses):
                print("Input is not a valid index.")
        except TypeError:
            print("Input is not a valid integer.")
    chosen_class_name = classlist[index]
    chosen_class_data = classdefs[chosen_class_name]
    if "stats" in chosen_class_data:
        class_stats = chosen_class_data["stats"]
        if "STR" in class_stats:
            player.strength.reset(class_stats["STR"])
        if "DEX" in class_stats:
            player.dexterity.reset(class_stats["DEX"])
        if "WIS" in class_stats:
            player.wisdom.reset(class_stats["WIS"])
        if "SOUL" in class_stats:
            player.soul.reset(class_stats["SOUL"])
    print(player.format_string())

# run the main function
if __name__ == '__main__':
	main()
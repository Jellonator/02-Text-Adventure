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
INTERACT_COMMANDS = ["look", "search", "take", "open"]

def load_json(name: str):
    """
    Load the contents of the files into the game and items dictionaries. You can largely ignore this
    Sorry it's messy, I'm trying to account for any potential craziness with the file location
    """
    try:
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        with open(os.path.join(__location__, name)) as json_file: 
            return json.load(json_file)
    except:
        print("There was a problem reading either the game or item file.")
        os._exit(1)

def preprocess_level_items(roomname, room):
    """
    Preprocesses a room's data so that all of its defined items can be interacted with.
    """
    if not "items" in room:
        return
    items = room["items"]
    if not "interact" in room:
        room["interact"] = {}
    interact = room["interact"]
    for itemname, itemdef in items.items():
        if itemname in interact:
            continue
        # Unique, but a level could check if a specific item was taken anyways
        flag = "@{}_{}".format(roomname, itemname)
        itemkey = itemdef.get("item")
        data = {
            "take": {
                "type": "if",
                "flag": flag,
                "default": True,
                "true": [
                    {
                        "type": "give",
                        "item": itemkey
                    }, {
                        "type": "setflag",
                        "flag": flag,
                        "value": False
                    }
                ],
                "false": "You already took the {}.".format(itemname)
            },
            "look": {
                "type": "if",
                "flag": flag,
                "default": True,
                "true": itemdef.get("look", "There is a {}.".format(itemname)),
                "false": "You already took the {}.".format(itemname)
            }
        }
        interact[itemname] = data


class GameData:
    """
    A class that contains the entire game's state.

    Attributes
    ----------

    level: dict[str -> dict]
        A dictionary of level data where keys are level names and values are
        level definitions.
    items: dict[str -> dict]
        A dictionary of item data where keys are item names and values are item
        definitions.
    enemydefs: dict[str -> dict]
        A dictionary of enemy data where keys are enemy names and values are
        enemy definitions.
    player: Character
        The player state of the game.
    room: str
        The room that the player is currently in.
    lastroom: str
        The room that the player was in previously.
    finished: bool
        Set to true to end the game.
    actions: dict[str -> PlayerAction]
        A dictionary of actions that the player can take; keys are action names
        and values are action definition
    """
    def __init__(self, leveldata, itemdata, player, enemydefs):
        self.level = leveldata
        for roomname, room in self.level.items():
            preprocess_level_items(roomname, room)
        self.items = itemdata
        self.player = player
        self.enemydefs = enemydefs
        self.room = ""
        self.lastroom = ""
        self.finished = False
        self.actions = {
            "help": PlayerAction(action_help, "You're already using this, dummy!"),
            "stats": PlayerAction(action_stat, "Gives information on your current stats."),
            "quit": PlayerAction(action_quit, "Quit the game."),
            "move": PlayerAction(action_move, "Move to another room."),
            "inventory": PlayerAction(action_inventory, "List inventory items."),
            "use": PlayerAction(action_use, "Use an item"),
            "attack": PlayerAction(action_attack, "Attack an enemy")
        }
        self.flags = {}
        self.explored = {}
        self.cleared_combats = {}
        self.encounter = []
    def remove_dead_enemies(self):
        """
        Removes enemies whose health is zero from the encounter.
        """
        i = 0
        prevlen = len(self.encounter)
        while i < len(self.encounter):
            enemy = self.encounter[i]
            if enemy.is_dead():
                self.encounter.pop(i)
                print("You killed the {}!".format(gameutil.FMT_ENEMY.format(enemy.name)))
            else:
                i += 1
        if len(self.encounter) == 0 and prevlen > 0:
            self.cleared_combats[self.room] = True
            print("You defeated all of the enemies!")
            input("Press enter to continue...")

class PlayerAction:
    """
    An action that the player can make

    Attributes
    ----------

    func: function(gamedata: Gamedata, args: list[str])
        A function to call to make this action.
    help: str
        Help text for this action.
    """
    def __init__(self, func, helptext):
        self.func = func
        self.help = helptext

def action_help(gamedata, args):
    """
    The 'help' action
    """
    if len(args) == 0:
        print(gameutil.FMT_IMPORTANT.format("Available actions: " + ", ".join(gamedata.actions.keys())))
        print(gameutil.FMT_IMPORTANT.format("Type 'help action' for information about the given action."))
    elif len(args) == 1:
        name = args[0]
        if name in gamedata.actions:
            print(gamedata.actions[name].help)
    else:
        print(gameutil.FMT_IMPORTANT.format("Too many arguments to 'help'."))

def action_stat(gamedata, args):
    """
    The 'stat' action. Gives information about the player's stats.
    """
    if len(args) == 0:
        print(gameutil.FMT_STAT.format("STR") + ":", gamedata.player.strength.format_string())
        print("\tStrength, your physical power and health.")
        print("\tIf you run out, you die from your injuries.")
        print(gameutil.FMT_STAT.format("DEX") + ":", gamedata.player.dexterity.format_string())
        print("\tDexterity, your agility and stealthiness.")
        print("\tIf you run out, you cease to move again.")
        print(gameutil.FMT_STAT.format("WIS") + ":", gamedata.player.wisdom.format_string())
        print("\tWisdom, your mental acuity and intelligence.")
        print("\tIf you run out, you lose the will to keep going.")
        print(gameutil.FMT_STAT.format("SOUL") + ":", gamedata.player.soul.format_string())
        print("\tSoul, your mortal connection.")
        print("\tIf you run out, you succumb to the darkness and your soul is lost forever.")
    else:
        print("Too many arguments to 'stat'.")

def action_quit(gamedata, args):
    """
    The 'quit' action. Quits the game.
    """
    if len(args) == 0:
        gamedata.finished = True
    else:
        print("Too many arguments to 'quit'.")

def action_move(gamedata, args):
    """
    The 'move' action. Moves the player to another location.
    """
    if len(args) == 0:
        print("Needs one argument to 'move'.")
    elif len(args) == 1:
        if len(gamedata.encounter) > 0:
            print("You're engaged in combat, unable to move!")
            return
        name = args[0]
        exitdata = gamedata.level[gamedata.room]["exits"]
        try:
            index = int(name) - 1
            if index in range(len(exitdata)):
                try_enter_location(gamedata, exitdata[index])
                return
        except ValueError:
            for data in exitdata:
                if data["exit"].lower() == name:
                    try_enter_location(gamedata, data)
                    return
        print("Invalid exit '{}'".format(name))
    else:
        print("Too many arguments to 'move'.")

def action_use(gamedata, args):
    """
    The 'use' action. Uses an item.
    """
    if len(args) == 0:
        attacks = gamedata.player.get_use_actions()
        if len(attacks) == 0:
            print("You have no items which can be used.")
            return
        attack = gameutil.choose_from_list(attacks, True, "Choose an item to use")
        if attack == None:
            return
        if attack.use(gamedata) != False:
            do_enemy_turn(gamedata)
    else:
        print("Too many arguments to 'use'")

def action_inventory(gamedata, args):
    """
    The 'inventory' action. Lists the items in the player's inventory.
    """
    if len(args) == 0:
        inventory = [item for item in gamedata.player.inventory if not item.unlisted]
        numitems = len(inventory)
        if numitems == 0:
            print("You don't have anything in your inventory.")
        else:
            if numitems == 1:
                print("You have 1 item in your inventory:")
            else:
                print("You have {} items in your inventory:".format(numitems))
            for item in inventory:
                print("\t{} - {}".format(gameutil.FMT_OPTION.format(item.name), item.desc))
    else:
        print("Too many arguments to 'inventory'")

def action_attack(gamedata, args):
    """
    The 'attack' action. Attacks an enemy (if available)
    """
    if len(args) == 0:
        if len(gamedata.encounter) == 0:
            print("No enemies to attack.")
            return
        attacks = gamedata.player.get_attacks()
        attack = gameutil.choose_from_list(attacks, True, "Choose an attack", None, gameutil.FMT_NONE)
        if attack == None:
            return
        if attack.use(gamedata) != False:
            do_enemy_turn(gamedata)
    else:
        print("Too many arguments to 'attack'")

def do_enemy_turn(gamedata):
    """
    Performs the enemies' turn.
    """
    gamedata.remove_dead_enemies()
    for enemy in gamedata.encounter:
        if not gamedata.player.is_dead():
            enemy.do_turn(gamedata)
    gamedata.player.do_turn(gamedata)

def try_enter_location(gamedata, exitdata):
    location = exitdata["target"]
    if "flag" in exitdata:
        required_value = exitdata.get("flag-test", True)
        flag = exitdata.get("flag")
        if gamedata.flags.get(flag, exitdata.get("flag-default")) == required_value:
            enter_location(gamedata, location)
        else:
            execute_level_action(gamedata, exitdata.get("fail-text", "For some reason, you weren't able to leave."))
    else:
        enter_location(gamedata, location)


def enter_location(gamedata, location):
    """
    Enters a new location.

    Parameters
    ----------
    location: str
        The new location to enter.
    """
    if location == gamedata.room:
        print("You tried to move there, but you were already there all along!\nWacky how nature do that.")
        return
    if location in gamedata.level:
        gamedata.explored[location] = True
        gamedata.lastroom = gamedata.room
        gamedata.room = location
        roomdata = gamedata.level[location]
        if "desc-post-combat" in roomdata and location in gamedata.cleared_combats:
            print(gameutil.FMT_IMPORTANT.format(roomdata["desc-post-combat"]))
        if "desc" in roomdata:
            execute_level_action(gamedata, roomdata["desc"])
        else:
            print(gameutil.FMT_IMPORTANT.format("There is nothing noteworthy about this room."))
        if "encounter" in roomdata and location not in gamedata.cleared_combats:
            for enemyname in roomdata["encounter"]:
                if enemyname in gamedata.enemydefs:
                    enemy = gameenemy.GameEnemy(enemyname, gamedata.enemydefs[enemyname])
                    gamedata.encounter.append(enemy)
                else:
                    print("Unknown enemy '{}'".format(enemyname))
            if len(gamedata.encounter) > 0:
                fmt_text = gameutil.gen_ambush_text(gamedata.encounter)
                print("You were ambushed by {}!".format(fmt_text))
    else:
        print(gameutil.FMT_IMPORTANT.format("Unrecognized location '{}'".format(location)))

def render(gamedata):
    """
    Prints useful information to the player.
    """
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
                revealed = exitdata.get("revealed", False)
                if (exittarget in gamedata.explored or revealed) and exittarget in gamedata.level:
                    exitinfo = gamedata.level[exittarget]["name"]
                print("    {}. {}:\t{}".format(i, gameutil.FMT_OPTION.format(exitname), exitinfo))
            print("Enter 'move location' to move to another location")
        else:
            print("There doesn't appear to be anywhere to go...")
        print("Use 'search', 'look', 'take', or 'open' to interact with objects.")
    else:
        print("Use 'attack', 'use', or 'look' to interact during combat.")

def update(gamedata):
    """
    Update the game.
    """
    gamedata.remove_dead_enemies()
    if gamedata.player.is_dead():
        reason = gamedata.player.get_cause_of_death()
        if reason == "str":
            print(gameutil.FMT_IMPORTANT.format("You perish from your physical injuries."))
            print(gameutil.FMT_IMPORTANT.format("Congratulations, your death wasn't slow and painful!"))
        elif reason == "dex":
            print(gameutil.FMT_IMPORTANT.format("You fall to the ground and are unable to get back up."))
            if len(gamedata.encounter) > 0:
                print(gameutil.FMT_IMPORTANT.format("Unable to defend yourself any longer, your enemies finish you off."))
                print(gameutil.FMT_IMPORTANT.format("Congratulations, you died with honor!"))
            else:
                print(gameutil.FMT_IMPORTANT.format("You lay in place in agony, and eventually die of dehydration."))
                print(gameutil.FMT_IMPORTANT.format("Congratulations, your body decomposed peacefully!"))
        elif reason == "wis":
            if len(gamedata.encounter) > 0:
                print(gameutil.FMT_IMPORTANT.format("You lose the will to defend yourself, and you stare blankly as your enemies finish you off."))
                print(gameutil.FMT_IMPORTANT.format("Congratulations, you... uh, at least you tried?"))
            else:
                print(gameutil.FMT_IMPORTANT.format("You lose the will to continue onward, and you run back home."))
                print(gameutil.FMT_IMPORTANT.format("Congratulations, you lived!"))
        elif reason == "soul":
            print(gameutil.FMT_IMPORTANT.format("You succumb to the darkness. You slowly feel your soul start to slip away,\n"+\
                "and another one takes its place."))
            print(gameutil.FMT_IMPORTANT.format("Congratulations, your body is still technically alive!"))
        input("Press enter to continue...")
        gamedata.finished = True

def execute_level_action(gamedata, action):
    """
    Execute the given action.

    Parameters
    ----------
    action: str, list, or dict
        The action to perform. The result depends on the type of the action.
        dict: Perform a game action, e.g. setting flags, conditionals, etc.
            "setflag": Set a flag.
            "if": Conditional
            "has": Conditional, but to check if the player has an item.
            "give": Give the player an item
            "print": Print text
            "remove": Remove an item
        list: Run each item of the list as an action sequentially.
        str: Print out the string.
    """
    if isinstance(action, list):
        for item in action:
            execute_level_action(gamedata, item)
    elif isinstance(action, str):
        print(gameutil.FMT_IMPORTANT.format(action))
    elif isinstance(action, dict):
        atype = action.get("type")
        # Oh no what have I done
        if atype == "print":
            print(gameutil.FMT_IMPORTANT.format(action.get("text")))
        elif atype == "setflag":
            gamedata.flags[action.get("flag")] = action.get("value")
        elif atype == "if":
            flagname = action.get("flag")
            value = None
            if flagname in gamedata.flags:
                value = gamedata.flags[flagname]
            else:
                value = action.get("default")
            testvalue = action.get("value", None)
            if (testvalue == None and value) or value == testvalue:
                if "true" in action:
                    execute_level_action(gamedata, action.get("true"))
            else:
                if "false" in action:
                    execute_level_action(gamedata, action.get("false"))
        elif atype == "has":
            itemname = action.get("item")
            if gamedata.player.has_item(itemname):
                if "true" in action:
                    execute_level_action(gamedata, action.get("true"))
            else:
                if "false" in action:
                    execute_level_action(gamedata, action.get("false"))
        elif atype == "give":
            itemname = action.get("item")
            item = gameitem.GameItem(itemname, gamedata.items[itemname])
            gamedata.player.inventory.append(item)
            print(gameutil.FMT_IMPORTANT.format("You got the {}".format(item.name)))
        elif atype == "remove":
            itemname = action.get("item")
            removeall = action.get("remove-all", False)
            i = 0
            while i < len(gamedata.player.inventory):
                item = gamedata.player.inventory[i]
                if item.fullname == itemname:
                    gamedata.player.inventory.pop(i)
                    if not removeall:
                        break
                else:
                    i = i + 1
        else:
            print("Unknown level action '{}'".format(atype))
    else:
        print("Not a valid level action type")

def interact_with(gamedata, action, directobject):
    """
    Interact with the given object with the given action.

    Parameters
    ----------

    action: str
        The method of interaction, e.g. look, search, and take.
    directobject: str
        The name of the object that is being interacted with.
    """
    fmt_verb = action
    if action == "look":
        fmt_verb += " at"
    roomdata = gamedata.level[gamedata.room].get("interact", {})
    if directobject in roomdata:
        objectdata = roomdata[directobject]
        if action in objectdata:
            data = objectdata[action]
            execute_level_action(gamedata, data)
        else:
            print(gameutil.FMT_IMPORTANT.format("Can't {} the {}".format(fmt_verb, directobject)))
    else:
        print(gameutil.FMT_IMPORTANT.format("There is no {} to {}".format(directobject, fmt_verb)))

def interact(gamedata, action, args):
    """
    Interact with the environment

    Parameters
    ----------
    action: str
        The action to perform
    args: list[str]
        The arguments to the action
    """
    if len(gamedata.encounter) > 0 and action != "look":
        print(gameutil.FMT_IMPORTANT.format("You can't do that while you're fighting."))
    elif len(args) == 0:
        if action == "look":
            if len(gamedata.encounter) > 0:
                print("You see {}".format(gameutil.gen_ambush_text(gamedata.encounter)))
            else:
                roomdata = gamedata.level[gamedata.room]
                execute_level_action(gamedata, roomdata.get("look", "There's not much to look at."))
        else:
            print(gameutil.FMT_IMPORTANT.format("Not enough arguments to '{}'".format(action)))
    elif len(args) == 1:
        directobject = args[0]
        if len(gamedata.encounter) > 0 and action == "look":
            did_find = False
            for enemy in gamedata.encounter:
                if enemy.shortname.lower() == directobject or enemy.name.lower() == directobject:
                    print(gameutil.FMT_IMPORTANT.format(enemy.look))
                    did_find = True
                    break
            if not did_find:
                print(gameutil.FMT_IMPORTANT.format("There is no {} to look at".format(directobject)))
        else:
            interact_with(gamedata, action, directobject)
    else:
        print(gameutil.FMT_IMPORTANT.format("Too many arguments to '{}'".format(action)))

def game_loop(gamedata):
    """
    Basic game loop
    """
    while not gamedata.finished:
        render(gamedata)
        userinput = input("> ").lower().strip()
        userargs = userinput.split()
        if len(userargs) > 0:
            action = userargs[0]
            args = userargs[1:]
            if action in gamedata.actions:
                gamedata.actions[action].func(gamedata, args)
            elif action in INTERACT_COMMANDS:
                interact(gamedata, action, args)
            else:
                print(gameutil.FMT_IMPORTANT.format("Unknown action '{}'".format(action)))
        update(gamedata)

# The main function for the game
def main():
    """
    Initialize game
    """
    level = load_json(FILE_LEVEL)
    items = load_json(FILE_ITEMS)
    classdefs = load_json(FILE_CLASSES)
    enemydefs = load_json(FILE_ENEMIES)
    
    player = character.generate_character(classdefs, items)
    gamedata = GameData(level, items, player, enemydefs)
    print(gameutil.FMT_IMPORTANT.format("Type 'help' for information."))
    enter_location(gamedata, "WHOUS")
    game_loop(gamedata)

# run the main function
if __name__ == '__main__':
	main()
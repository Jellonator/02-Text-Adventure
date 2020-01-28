import gameitem
import gameutil

class Character:
    def __init__(self):
        self.strength = gameutil.CharacterStat(3)
        self.dexterity = gameutil.CharacterStat(3)
        self.wisdom = gameutil.CharacterStat(3)
        self.soul = gameutil.CharacterStat(3)
        self.inventory = []
        self.basicattack = gameitem.GameActionAttack("punch", None, {
            "name": "Unarmed attack",
            "target": "single",
            "stat": "STR",
            "bonus": 0
        })
    def format_string(self):
        return "STR " + self.strength.format_string() + " " \
            "DEX " + self.dexterity.format_string() + " " \
            "WIS " + self.wisdom.format_string() + " " \
            "SOUL " + self.soul.format_string() + " "
    def get_carrying_capacity(self):
        return max(self.strength.value + self.dexterity.value, 4)
    def get_attacks(self):
        ls = [self.basicattack]
        for item in self.inventory:
            for attack in item.attacks.values():
                ls.append(attack)
        return ls
    def get_stat(self, name, cancancelchoose=False):
        if name == "str":
            return self.strength
        elif name == "dex":
            return self.dexterity
        elif name == "wis":
            return self.wisdom
        elif name == "soul":
            return self.soul
        elif name == "none":
            return None
        elif name == "choose":
            stats = ["STR", "DEX", "WIS", "SOUL"]
            value = gameutil.choose_from_list(stats)
            if value == None:
                return None
            return self.get_stat(value.lower(), cancancelchoose)
        else:
            print("Unknown stat name '{}'".format(name))
            return None

def generate_character(classdefs, itemdefs):
    player = Character()
    classlist = [name for name in classdefs]
    classlist.sort()
    for i, classname in enumerate(classlist):
        print("{}. {}:\t{}".format(i + 1, classname, classdefs[classname]["description"]))
    index = -1
    numclasses = len(classlist)
    while not index in range(numclasses):
        try:
            index = int(input("What is your class? [1-{}]: ".format(numclasses)).lower().strip()) - 1
            if not index in range(numclasses):
                print("Input is not a valid index.")
        except ValueError:
            print("Input is not a valid integer.")
    chosen_class_name = classlist[index]
    chosen_class_data = classdefs[chosen_class_name]
    if "stat_max" in chosen_class_data:
        class_stats = chosen_class_data["stat_max"]
        if "STR" in class_stats:
            player.strength.reset(class_stats["STR"])
        if "DEX" in class_stats:
            player.dexterity.reset(class_stats["DEX"])
        if "WIS" in class_stats:
            player.wisdom.reset(class_stats["WIS"])
        if "SOUL" in class_stats:
            player.soul.reset(class_stats["SOUL"])
    if "stat_value" in chosen_class_data:
        class_values = chosen_class_data["stat_value"]
        if "STR" in class_values:
            player.strength.setvalue(class_values["STR"])
        if "DEX" in class_values:
            player.dexterity.setvalue(class_values["DEX"])
        if "WIS" in class_values:
            player.wisdom.setvalue(class_values["WIS"])
        if "SOUL" in class_values:
            player.soul.setvalue(class_values["SOUL"])
    if "items" in chosen_class_data:
        for item in chosen_class_data["items"]:
            player.inventory.append(gameitem.GameItem(item, itemdefs[item]))
    return player
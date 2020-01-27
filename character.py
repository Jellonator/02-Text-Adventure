MAX_STAT_VALUE = 10

class CharacterStat:
    def __init__(self, maxvalue):
        if maxvalue < 1:
            maxvalue = 1
        if maxvalue > MAX_STAT_VALUE:
            maxvalue = MAX_STAT_VALUE
        self.maxvalue = maxvalue
        self.value = maxvalue
    def reset(self, maxvalue):
        if maxvalue < 1:
            maxvalue = 1
        if maxvalue > MAX_STAT_VALUE:
            maxvalue = MAX_STAT_VALUE
        self.maxvalue = maxvalue
        self.value = maxvalue
    def setvalue(self, newvalue):
        self.value = newvalue
        if self.value > self.maxvalue:
            self.value = self.maxvalue
        if self.value < 0:
            self.value = 0
    def add(self, amount):
        self.setvalue(self.value + amount)
    def subtract(self, amount):
        self.setvalue(self.value - amount)
    def is_empty(self):
        return self.value == 0
    def upgrade(self, amount):
        if self.maxvalue + amount < 1:
            amount = 1 - self.maxvalue
        if self.maxvalue + amount > MAX_STAT_VALUE:
            amount = MAX_STAT_VALUE - amount
        self.maxvalue += amount
        self.value += amount
    def get_ratio(self):
        return self.value / self.maxvalue
    def format_string(self):
        return "|" + "+" * self.value + "." * (self.maxvalue - self.value) + "|" + " " * (MAX_STAT_VALUE - self.maxvalue)

class Character:
    def __init__(self):
        self.strength = CharacterStat(3)
        self.dexterity = CharacterStat(3)
        self.wisdom = CharacterStat(3)
        self.soul = CharacterStat(3)
    def format_string(self):
        return "STR " + self.strength.format_string() + " " \
            "DEX " + self.dexterity.format_string() + " " \
            "WIS " + self.wisdom.format_string() + " " \
            "SOUL " + self.soul.format_string() + " "

def generate_character(classdefs):
    player = Character()
    classlist = [name for name in classdefs]
    classlist.sort()
    for i, classname in enumerate(classlist):
        print("{}. {}:\t{}".format(i + 1, classname, classdefs[classname]["description"]))
    index = -1
    numclasses = len(classlist)
    while not index in range(numclasses):
        try:
            index = int(input("What is your class? [1-{}]: ".format(numclasses))) - 1
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
    return player
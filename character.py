import gameitem
import gameutil

class Character:
    """
    The player.

    Attributes
    ----------
    strength: CharacterStat
        The strength stat
    dexterity: CharacterStat
        The dexterity stat
    wisdom: CharacterStat
        The wisdom stat
    soul: CharacterStat
        The soul stat
    inventory: list[GameItem]
        The player's inventory
    """
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
        self.basicavoid = gameitem.GameActionDefend("dodge", None, {
            "name": "Dodge",
            "stat": "DEX",
            "bonus": 0,
            "resist": "physical"
        })
        self.basicresist = gameitem.GameActionDefend("resist", None, {
            "name": "Resist",
            "stat": "WIS",
            "bonus": 0,
            "resist": "mental"
        })
        self.basicpray = gameitem.GameActionDefend("pray", None, {
            "name": "Pray",
            "stat": "SOUL",
            "bonus": 0,
            "resist": "mental"
        })
    def format_string(self):
        """
        Format the player's information
        """
        return gameutil.FMT_STAT.format("STR ") + self.strength.format_string() + " " \
            + gameutil.FMT_STAT.format("DEX ") + self.dexterity.format_string() + " " \
            + gameutil.FMT_STAT.format("WIS ") + self.wisdom.format_string() + " " \
            + gameutil.FMT_STAT.format("SOUL ") + self.soul.format_string() + " "
    def get_carrying_capacity(self):
        """
        Get the player's carrying capacity. Unused.
        """
        return max(self.strength.value + self.dexterity.value, 4)
    def get_attacks(self):
        """
        Get a list of attacks that the player can perform.
        """
        ls = [self.basicattack]
        for item in self.inventory:
            for attack in item.attacks.values():
                ls.append(attack)
        return ls
    def get_defense_roll(self, dtype):
        """
        Get the player's defense roll, returns an integer as the number of dice
        that should be rolled.

        Parameters
        ----------
        dtype: str
            The damage type
        """
        available_reactions = []
        for item in self.inventory:
            for reaction in item.reactions.values():
                if reaction.does_resist(dtype):
                    available_reactions.append(reaction)
        if self.basicavoid.does_resist(dtype):
            available_reactions.append(self.basicavoid)
        if self.basicresist.does_resist(dtype):
            available_reactions.append(self.basicresist)
        if len(available_reactions) == 0:
            return 0
        reaction = gameutil.choose_from_list(available_reactions, False, "Choose a reaction")
        return reaction.get_defense(self)
    def get_use_actions(self):
        """
        Get the player's use actions.
        """
        ls = []
        for item in self.inventory:
            for attack in item.actions.values():
                ls.append(attack)
        return ls
    def get_stat(self, name, cancancelchoose=False, chooseprompt="Choose a stat to use"):
        """
        Get a player's stat.

        Parameter
        ---------
        name: str
            The name of the stat.
        cancancelchoose: bool = False
            If the stat is "choose", then the player may cancel choosing a stat.
            If True, then this function may return None.
        chooseprompt: str
            If the stat is "choose", then this is the promp that the player
            will see when selecting a stat.
        """
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
            value = gameutil.choose_from_list(stats, cancancelchoose, chooseprompt, None, gameutil.FMT_STAT)
            if value == None:
                return None
            return self.get_stat(value.lower(), cancancelchoose)
        else:
            print("Unknown stat name '{}'".format(name))
            return None
    def has_item(self, itemname):
        """
        Returns True if the player has the given item.

        itemname: str
            The name of the item.
        """
        for item in self.inventory:
            if item.fullname == itemname:
                return True
        return False
    def is_dead(self):
        """
        Returns true if player is kill
        """
        return self.strength.value == 0 or self.dexterity.value == 0 or\
            self.wisdom.value == 0 or self.soul.value == 0
    def get_cause_of_death(self):
        """
        Get an autopsy report
        """
        if self.strength.value == 0:
            return "str"
        elif self.dexterity.value == 0:
            return "dex"
        elif self.wisdom.value == 0:
            return "wis"
        elif self.soul.value == 0:
            return "soul"
        else:
            return None

def generate_character(classdefs, itemdefs):
    """
    Create a new character.

    Parameters
    ----------
    classdefs: dict[str -> dict]
        Class definitions.
    itemdefs: dict[str -> dict]
        Item definitions
    """
    player = Character()
    classlist = [name for name in classdefs]
    classlist.sort()
    classdescs = [classdefs[name]["description"] for name in classlist]
    chosen_class_name = gameutil.choose_from_list(classlist, False, "What is your class?", classdescs)
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
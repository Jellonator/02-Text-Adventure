import random

MAX_STAT_VALUE = 10

_FMT_MAGENTA = '\033[95m'
_FMT_BLUE = '\033[94m'
_FMT_GREEN = '\033[92m'
_FMT_YELLOW = '\033[93m'
_FMT_RED = '\033[91m'
_FMT_BRIGHT = '\033[97m'
_FMT_BOLD = '\033[1m'
_FMT_UNDERLINE = '\033[4m'
_FMT_END = '\033[0m'

FMT_ENEMY = _FMT_MAGENTA + _FMT_BOLD + "{}" + _FMT_END
FMT_STAT = _FMT_BLUE + _FMT_BOLD + "{}" + _FMT_END
FMT_GOOD = _FMT_GREEN + _FMT_BOLD + "{}" + _FMT_END
FMT_BAD = _FMT_RED + _FMT_BOLD + "{}" + _FMT_END
FMT_IMPORTANT = _FMT_BOLD + "{}" + _FMT_END
FMT_OPTION = _FMT_YELLOW + "{}" + _FMT_END
FMT_NONE = "{}"

class CharacterStat:
    """
    A character stat.

    Attributes
    ----------
    maxvalue: int
        The maximum value for this stat.
    value: int
        The actual value of this stat. The value is always restricted to the
        range [0, maxvalue].
    """
    def __init__(self, maxvalue):
        if maxvalue < 1:
            maxvalue = 1
        if maxvalue > MAX_STAT_VALUE:
            maxvalue = MAX_STAT_VALUE
        self.maxvalue = maxvalue
        self.value = maxvalue
    def reset(self, maxvalue):
        """
        Reset this stat.

        Parameters
        ----------
        maxvalue: int
            The new maximum value to use.
        """
        if maxvalue < 1:
            maxvalue = 1
        if maxvalue > MAX_STAT_VALUE:
            maxvalue = MAX_STAT_VALUE
        self.maxvalue = maxvalue
        self.value = maxvalue
    def setvalue(self, newvalue):
        """
        Set the value of this stat.

        Parameters
        ----------
        newvalue: int
            The new value to use.
        """
        self.value = newvalue
        if self.value > self.maxvalue:
            self.value = self.maxvalue
        if self.value < 0:
            self.value = 0
    def add(self, amount):
        """
        Add the given amount to this stat's value.
        Equivalent to stat.setvalue(stat.value + amount)

        Parameters
        ----------
        amount: int
            The amount to add.
        """
        self.setvalue(self.value + amount)
    def subtract(self, amount):
        """
        Subtract the given amount from this stat's value.
        Equivalent to stat.setvalue(stat.value - amount)

        Parameters
        ----------
        amount: int
            The amount to subtract.
        """
        self.setvalue(self.value - amount)
    def is_empty(self):
        """
        Returns true if this stat's value is 0.
        """
        return self.value == 0
    def upgrade(self, amount):
        """
        Increase this stat's value and maximum value by 'amount'.
        """
        if self.maxvalue + amount < 1:
            amount = 1 - self.maxvalue
        if self.maxvalue + amount > MAX_STAT_VALUE:
            amount = MAX_STAT_VALUE - amount
        self.maxvalue += amount
        self.value += amount
    def format_string(self):
        """
        Format this stat into a human-readable string
        """
        fmt_stat = FMT_GOOD.format("+" * self.value)
        fmt_missing = FMT_BAD.format("." * (self.maxvalue - self.value))
        return "|" + fmt_stat + fmt_missing + "|" + " " * (MAX_STAT_VALUE - self.maxvalue)

class EnemyHealth:
    """
    An enemy's health.

    Attributes
    ----------
    maxvalue: int
        The maximum value for this enemy's health.
    value: int
        The actual health value. The value is always restricted to the
        range [0, maxvalue].
    """
    def __init__(self, maxvalue):
        if maxvalue < 1:
            maxvalue = 1
        self.maxvalue = maxvalue
        self.value = maxvalue
    def setvalue(self, newvalue):
        """
        Set the health value.

        Parameters
        ----------
        newvalue: int
            The new value to use.
        """
        self.value = newvalue
        if self.value > self.maxvalue:
            self.value = self.maxvalue
        if self.value < 0:
            self.value = 0
    def add(self, amount):
        """
        Add the given amount of health.
        Equivalent to health.setvalue(health.value + amount)

        Parameters
        ----------
        amount: int
            The amount to add.
        """
        self.setvalue(self.value + amount)
    def subtract(self, amount):
        """
        Subtract the given amount of health.
        Equivalent to health.setvalue(health.value + amount)

        Parameters
        ----------
        amount: int
            The amount to add.
        """
        self.setvalue(self.value - amount)
    def is_empty(self):
        """
        Returns true if there is no more health left.
        """
        return self.value == 0

def join_list_pretty(ls):
    """
    Join a list in a human readable way.
    An empty list returns the empty string.
    A list with a single element returns the only element of the list converted to a string.
    A list with two elements returns a string in the format "x and y".
    A list with three or more elements returns a string in the format "x, y, and z"

    Parameters
    ----------
    ls: list
        The list to join
    """
    if len(ls) == 0:
        return ""
    elif len(ls) == 1:
        return str(ls[0])
    elif len(ls) == 2:
        return str(ls[0]) + " and " + str(ls[1])
    else:
        return ", ".join((str(x) for x in ls[:-1])) + ", and " + str(ls[-1])

def gen_ambush_text(encounter):
    """
    Turn a list of enemies into a human-readable string.
    If there are multiple enemies of the same type, then their names are combined;
    e.g. if there are two enemies named "Spider", then they become "2 Spiders".

    Parameters
    ----------
    encounter: list[GameEnemy]
        The list of enemies.
    """
    ls = [(x.name, x.nameplural) for x in encounter]
    ls.sort()
    ls2 = []
    num = 0
    name = ""
    for value in ls:
        if value[0] == name:
            num += 1
        else:
            if num == 1:
                ls2.append("a " + FMT_ENEMY.format(value[0]))
            elif num > 1:
                ls2.append("{} {}".format(num, FMT_ENEMY.format(value[1])))
            name = value[0]
            num = 1
    if num == 1:
        ls2.append("a " + FMT_ENEMY.format(value[0]))
    elif num > 1:
        ls2.append("{} {}".format(num, FMT_ENEMY.format(value[1])))
    return join_list_pretty(ls2)

def choose_from_list(ls, cancancel, prompt, descriptions=None, fmt=FMT_OPTION):
    """
    Ask the player to choose an option from a list of options.

    Parameters
    ----------
    ls: list
        A list of items to choose from. All options must be convertable to a
        string, or define the __str__ function.
    cancancel: bool
        If true, then the player can instead enter "cancel" to cancel their
        selection. In this case, this function may return None.
    prompt: str
        The prompt to give the player.
    """
    if cancancel:
        prompt = prompt + " [or 'cancel' to cancel]"
    prompt = prompt + ": "
    maxlen = max((len(str(x)) for x in ls))
    for i, name in enumerate(ls):
        desc = ""
        if descriptions != None and i < len(descriptions):
            desc = str(descriptions[i])
        namestr = str(name)
        spacelen = maxlen + 1 - len(namestr)
        namestr = fmt.format(namestr)
        print("    {}. {}{}    {}".format(FMT_IMPORTANT.format(i + 1), namestr, " " * spacelen, desc))
    index = -1
    while not index in range(len(ls)):
        try:
            ivalue = input(prompt).lower().strip()
            if ivalue == "cancel" and cancancel:
                return None
            index = int(ivalue) - 1
            if index not in range(len(ls)):
                print("Input is not valid.")
        except ValueError:
            print("Input is not valid.")
    return ls[index]

def roll_dice(num, sides):
    """
    Roll dice with the given number of sides.

    Parameters
    ----------
    num: int
        The number of dice to roll.
    sides:
        The number of sides each dice has.
    """
    return [random.randint(1, sides) for _ in range(num)]
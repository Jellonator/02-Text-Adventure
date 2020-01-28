import random

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

class EnemyHealth:
    def __init__(self, maxvalue):
        if maxvalue < 1:
            maxvalue = 1
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
    def get_ratio(self):
        return self.value / self.maxvalue

def join_list_pretty(ls):
    if len(ls) == 0:
        return ""
    elif len(ls) == 1:
        return str(ls[0])
    elif len(ls) == 2:
        return str(ls[0]) + " and " + str(ls[1])
    else:
        return ", ".join((str(x) for x in ls[:-1])) + ", and " + str(ls[-1])

def gen_ambush_text(encounter):
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
                ls2.append("a " + value[0])
            elif num > 1:
                ls2.append("{} {}".format(num, value[1]))
            name = value[0]
            num = 1
    if num == 1:
        ls2.append("a " + value[0])
    elif num > 1:
        ls2.append("{} {}".format(num, value[1]))
    return join_list_pretty(ls2)

def choose_from_list(ls, cancancel, prompt):
    if cancancel:
        prompt = prompt + " [or 'cancel' to cancel]"
    prompt = prompt + ": "
    for i, name in enumerate(ls):
        print("{}. {}".format(i + 1, str(name)))
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
    return [random.randint(1, sides) for _ in range(num)]
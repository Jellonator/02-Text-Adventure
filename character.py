MAX_STAT_VALUE = 10

class CharacterStat:
    def __init__(self, maxvalue: int):
        if maxvalue < 1:
            maxvalue = 1
        if maxvalue > MAX_STAT_VALUE:
            maxvalue = MAX_STAT_VALUE
        self.maxvalue = maxvalue
        self.value = maxvalue
    def reset(self, maxvalue: int):
        if maxvalue < 1:
            maxvalue = 1
        if maxvalue > MAX_STAT_VALUE:
            maxvalue = MAX_STAT_VALUE
        self.maxvalue = maxvalue
        self.value = maxvalue
    def add(self, amount: int):
        self.value = self.value + amount
        if self.value > self.maxvalue:
            self.value = self.maxvalue
        if self.value < 0:
            self.value = 0
    def subtract(self, amount: int):
        self.add(-amount)
    def is_empty(self) -> bool:
        return self.value == 0
    def upgrade(self, amount: int):
        if self.maxvalue + amount < 1:
            amount = 1 - self.maxvalue
        if self.maxvalue + amount > MAX_STAT_VALUE:
            amount = MAX_STAT_VALUE - amount
        self.maxvalue += amount
        self.value += amount
    def get_ratio(self) -> float:
        return self.value / self.maxvalue
    def format_string(self) -> str:
        return "|" + "+" * self.value + "-" * (self.maxvalue - self.value) + "|" + " " * (MAX_STAT_VALUE - self.maxvalue)

class Character:
    def __init__(self):
        self.strength = CharacterStat(3)
        self.dexterity = CharacterStat(3)
        self.wisdom = CharacterStat(3)
        self.soul = CharacterStat(3)
    def format_string(self) -> str:
        return "STR " + self.strength.format_string() + " " \
            "DEX " + self.dexterity.format_string() + " " \
            "WIS " + self.wisdom.format_string() + " " \
            "SOUL " + self.soul.format_string() + " "
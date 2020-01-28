import gameutil

def choose_enemy(gamedata):
    return gameutil.choose_from_list(gamedata.encounter, True, "Choose an enemy to attack")

ATTACK_MISS = 0
ATTACK_HIT = 1
ATTACK_CANCEL = 2

def try_attack_enemy(gamedata, target, stat, stat_negate, attack_bonus):
    player_stat = gamedata.player.get_stat(stat, False)
    dice_stat = None
    player_stat_value = 0
    if player_stat != None:
        if stat_negate:
            player_stat_value = player_stat.maxvalue - player_stat.value + 1
        else:
            player_stat_value = player_stat.value
        dice_stat = gameutil.roll_dice(player_stat_value, 6)
    else:
        dice_stat = []
    if attack_bonus == 0:
        input("Rolling {}d6 to attack...".format(player_stat_value))
    else:
        input("Rolling {}d6 + {}d6...".format(player_stat_value, attack_bonus))
    dice_bonus = gameutil.roll_dice(attack_bonus, 6)
    fmt_stat = ' '.join((str(x) for x in dice_stat))
    roll_total = sum(dice_stat) + sum(dice_bonus)
    if attack_bonus == 0:
        print("You rolled: [{} {}] = {}".format(stat.upper(), fmt_stat, roll_total))
    else:
        fmt_bonus = ' '.join((str(x) for x in dice_bonus))
        print("You rolled: [{} {}] [+ {}] = {}".format(stat.upper(), fmt_stat, fmt_bonus, roll_total))
    input("The {} is rolling {}d6 for defense...".format(target.name, target.defense))
    target_dice = target.get_defense_roll()
    target_roll_total = sum(target_dice)
    fmt_target = ' '.join((str(x) for x in target_dice))
    print("The {} rolled [{}] = {}".format(target.name, fmt_target, target_roll_total))
    if roll_total >= target_roll_total:
        return ATTACK_HIT
    else:
        return ATTACK_MISS

class GameAction:
    def __init__(self, attackname, parentitem, attackdef):
        self.name = attackdef.get("name", attackname)
        self.parentitem = parentitem
    def format_info(self):
        return ""
    def __str__(self):
        info = self.format_info().strip()
        if info != "":
            info = "[{}]".format(info)
        if self.parentitem != None:
            return "{} ({}) {}".format(self.name, self.parentitem.name, info)
        else:
            return "{} {}".format(self.name, info)

class GameActionAttack(GameAction):
    def __init__(self, attackname, parentitem, attackdef):
        super().__init__(attackname, parentitem, attackdef)
        self.target = attackdef.get("target", "single")
        self.stat = attackdef.get("stat", "none").lower()
        self.stat_negate = attackdef.get("stat-negate", False)
        self.bonus = attackdef.get("bonus", 0)
        self.damage = attackdef.get("damage", 1)
    def format_info(self):
        c = ""
        if self.stat_negate:
            c = "-"
        if self.stat == "none":
            return "+" + str(self.bonus)
        elif self.bonus == 0:
            return c + self.stat.upper()
        else:
            return c + self.stat.upper() + "+" + str(self.bonus)
    def use(self, gamedata, shared):
        target = shared.get("target")
        if target == None:
            target = choose_enemy(gamedata)
            if target == None:
                return False
            shared["target"] = target
        print("Attacking {}".format(target.name))
        status = try_attack_enemy(gamedata, target, self.stat, self.stat_negate, self.bonus)
        if status == ATTACK_HIT:
            print("You hit the {} for {} damage!".format(target.name, self.damage))
            target.health.subtract(self.damage)
        elif status == ATTACK_MISS:
            print("You missed the {}.".format(target.name))
        else:
            return False
        return True

class GameItem:
    def __init__(self, itemname, itemdef):
        self.name = itemdef.get("name", itemname)
        self.weight = itemdef.get("weight", 0)
        self.max_durability = itemdef.get("durability", 1)
        self.durability = self.max_durability
        self.actions = {}
        self.attacks = {}
        self.reactions = {}
        if "attacks" in itemdef:
            for attackname, attackdef in itemdef["attacks"].items():
                # print(attackname, attackdef)
                if attackdef.get("type") == "attack":
                    self.attacks[attackname] = GameActionAttack(attackname, self, attackdef)
                else:
                    print("Unrecognized attack type '{}'".format(attackdef.get("type")))
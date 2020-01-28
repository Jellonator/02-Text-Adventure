import gameutil

def choose_enemy(gamedata):
    return gameutil.choose_from_list(gamedata.encounter, True, "Choose an enemy to attack")
    # for i, enemy in enumerate(gamedata.enemies):
    #     print("{}. {}".format(i + 1, enemy.name))
    # index = -1
    # while not index in range(len(gamedata.enemies)):
    #     try:
    #         ivalue = input("Choose an enemy to attack [or 'cancel' to cancel]: ").lower().strip()
    #         if ivalue == "cancel":
    #             return None
    #         index = int(ivalue) - 1
    #         if index not in range(len(gamedata.enemies)):
    #             print("Enemy index is not in range.")
    #     except ValueError:
    #         print("Invalid integer.")
    # return gamedata.enemies[index]

class GameActionAttack:
    def __init__(self, attackname, parentitem, attackdef):
        self.name = attackdef.get("name", attackname)
        self.target = attackdef.get("target", "single")
        self.stat = attackdef.get("stat", "none").lower()
        self.bonus = attackdef.get("bonus", 0)
        self.parentitem = parentitem
    def format_info(self):
        if self.stat == "none":
            return "+" + str(self.bonus)
        elif self.bonus == 0:
            return self.stat.upper()
        else:
            return self.stat.upper() + "+" + str(self.bonus)
    def use(self, gamedata, shared):
        target = shared.get("target")
        if target == None:
            target = choose_enemy(gamedata)
            if target == None:
                return False
            shared["target"] = target
        print("Attacking {}".format(target.name))
        player_stat = gamedata.player.get_stat(self.stat, False)
        dice_stat = None
        player_stat_value = 0
        if player_stat != None:
            player_stat_value = player_stat.value
            dice_stat = gameutil.roll_dice(player_stat.value, 6)
        else:
            dice_stat = []
        if self.bonus == 0:
            input("Rolling {}d6 to attack...".format(player_stat_value))
        else:
            input("Rolling {}d6 + {}d6...".format(player_stat_value, self.bonus))
        dice_bonus = gameutil.roll_dice(self.bonus, 6)
        fmt_stat = ' '.join((str(x) for x in dice_stat))
        roll_total = sum(dice_stat) + sum(dice_bonus)
        if self.bonus == 0:
            print("You rolled: [{} {}] = {}".format(self.stat.upper(), fmt_stat, roll_total))
        else:
            fmt_bonus = ' '.join((str(x) for x in dice_bonus))
            print("You rolled: [{} {}] [+ {}] = {}".format(self.stat.upper(), fmt_stat, fmt_bonus, roll_total))
        input("The {} is rolling {}d6 for defense...".format(target.name, target.defense))
        target_dice = target.get_defense_roll()
        target_roll_total = sum(target_dice)
        fmt_target = ' '.join((str(x) for x in target_dice))
        print("The {} rolled [{}] = {}".format(target.name, fmt_target, target_roll_total))
        if roll_total >= target_roll_total:
            print("You hit the {} for 1 damage!".format(target.name))
            target.health.subtract(1)
        else:
            print("You missed the {}.".format(target.name))
        return True
    def __str__(self):
        if self.parentitem != None:
            return "{} ({}) [{}]".format(self.name, self.parentitem.name, self.format_info())
        else:
            return "{} [{}]".format(self.name, self.format_info())

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
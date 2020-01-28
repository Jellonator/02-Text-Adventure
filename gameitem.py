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
        self.stat = attackdef.get("stat", "NONE")
        self.bonus = attackdef.get("bonus", 0)
        self.parentitem = parentitem
    def format_info(self):
        if self.stat == "NONE":
            return "+" + str(self.bonus)
        elif self.bonus == 0:
            return self.stat
        else:
            return self.stat + "+" + str(self.bonus)
    def use(self, gamedata, shared):
        target = shared.get("target")
        if target == None:
            target = choose_enemy(gamedata)
            if target == None:
                return False
            shared["target"] = target
        print("Attacking {}".format(target.name))
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
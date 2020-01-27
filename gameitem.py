class GameActionAttack:
    def __init__(self, attackname, attackdef):
        self.name = attackdef.get("name", attackname)
        self.target = attackdef.get("target", "single")
        self.stat = attackdef.get("stat", "NONE")
        self.bonus = attackdef.get("bonus", 0)
    def format_info(self):
        return "[]"

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
                    self.attacks[attackname] = GameActionAttack(attackname, attackdef)
                else:
                    print("Unrecognized attack type '{}'".format(attackdef.get("type")))
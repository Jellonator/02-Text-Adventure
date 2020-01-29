import gameutil
import random

class EnemyAttack:
    def __init__(self, attackname, attackdef):
        self.description = attackdef.get("desc", "It attacks you")
        self.description_hit = attackdef.get("desc-hit", "It hits you")
        self.description_miss = attackdef.get("desc-miss", "It missed you")
        self.damage = attackdef.get("damage", 1)
        self.stat = attackdef.get("stat", "none").lower()
        self.roll = attackdef.get("roll", 1)
        self.damage_type = attackdef.get("damage-type", "physical")
        if self.damage_type not in ["physical", "mental"]:
            print("WARNING: damage type '{}' not recognized.".format(self.damage_type))
            self.damage_type = "physical"
    def use(self, player, enemy):
        print(self.description)
        input("The {} is rolling {}d6 to attack...".format(enemy.name, self.roll))
        dice_attack = enemy.get_attack_roll(self.roll)
        dice_attack_total = sum(dice_attack)
        dice_attack_fmt = ' '.join((str(x) for x in dice_attack))
        print("The {} rolled [{}] = {}".format(enemy.name, dice_attack_fmt, dice_attack_total))
        player_roll = player.get_defense_roll(self.damage_type)
        input("Rolling {}d6 for to defend...".format(player_roll))
        dice_player = gameutil.roll_dice(player_roll, 6)
        dice_player_total = sum(dice_player)
        dice_player_fmt = ' '.join((str(x) for x in dice_player))
        print("You rolled [{}] = {}".format(dice_player_fmt, dice_player_total))
        if dice_attack_total > dice_player_total:
            print(self.description_hit)
            print("You took {} {} damage!".format(self.damage, self.stat.upper()))
            stat = player.get_stat(self.stat)
            stat.subtract(self.damage)
        else:
            print(self.description_miss)

class GameEnemy:
    def __init__(self, enemyname, enemydata):
        self.name = enemydata.get("name", enemyname)
        self.nameplural = enemydata.get("plural", self.name + "s")
        self.health = gameutil.EnemyHealth(enemydata.get("health", 1))
        self.description = enemydata.get("desc", "")
        self.defense = enemydata.get("defense", 1)
        self.attacks = []
        if "actions" in enemydata:
            for actionname, actiondata in enemydata["actions"].items():
                atype = actiondata.get("type")
                if atype == "attack":
                    self.attacks.append(EnemyAttack(actionname, actiondata))
                else:
                    print("Unknown enemy attack type '{}'".format(atype))
        # -1 is no curse.
        # Player's attack sets curses to 1. This way, curse doesn't get removed
        # for the player's next attack. Curse is also decremented *before* the
        # enemy's attack so that their attack is only cursed for 1 turn.
        self.curse = -1
    def get_defense_value(self):
        defense = self.defense
        if self.curse >= 0 and defense > 1:
            defense -= 1
        return defense
    def get_defense_roll(self):
        return gameutil.roll_dice(self.get_defense_value(), 6)
    def get_attack_roll(self, roll):
        if self.curse >= 0 and roll > 1:
            roll -= 1
        return gameutil.roll_dice(roll, 6)
    def is_dead(self):
        return self.health.value == 0
    def do_turn(self, gamedata):
        self.curse = self.curse - 1
        if len(self.attacks) == 0:
            print("The {} can't do anything.".format(self.name))
        else:
            atk = random.choice(self.attacks)
            atk.use(gamedata.player, self)
    def __str__(self):
        ret = self.name
        if self.health.value != self.health.maxvalue:
            ret += " [-{}]".format(self.health.maxvalue - self.health.value)
        if self.curse > 0:
            ret += " [curse {}]".format(self.curse)
        return ret
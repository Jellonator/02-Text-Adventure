import gameutil
import random

class EnemyAction:
    """
    Enemy Action
    """
    def __init__(self, attackname, attackdef):
        self.next_action = attackdef.get("next-action")
        if self.next_action != None:
            self.next_action = parse_enemy_action("anonymous-action", self.next_action)
    def use(self, player, enemy):
        """
        Use the enemy's attack

        Parameters
        ----------
        player: Character
            The player to attack
        enemy: GameEnemy
            The enemy that is attacking
        """
        self._game_use(player, enemy)
        enemy.next_action = self.next_action
    def _game_use(self, player, enemy):
        """
        Do not call directly!
        """
        print("Nothing to do!")

class EnemyAttack(EnemyAction):
    """
    Enemy attack
    """
    def __init__(self, attackname, attackdef):
        super().__init__(attackname, attackdef)
        self.description = attackdef.get("desc", "It attacks you")
        self.description_hit = attackdef.get("desc-hit", "It hits you")
        self.description_miss = attackdef.get("desc-miss", "It missed you")
        self.damage = attackdef.get("damage", 1)
        self.stats = attackdef.get("stat", [])
        if isinstance(self.stats, str):
            self.stats = [self.stats]
        for i in range(len(self.stats)):
            self.stats[i] = self.stats[i].lower()
        self.roll = attackdef.get("roll", 1)
        self.damage_type = attackdef.get("damage-type", "physical")
        if self.damage_type not in ["physical", "mental"]:
            print("WARNING: damage type '{}' not recognized.".format(self.damage_type))
            self.damage_type = "physical"
    def _game_use(self, player, enemy):
        print(self.description)
        input("The {} is rolling {}d6 to attack...".format(enemy.name, self.roll))
        dice_attack = enemy.get_attack_roll(self.roll)
        dice_attack_total = sum(dice_attack)
        dice_attack_fmt = gameutil.FMT_BAD.format(' '.join((str(x) for x in dice_attack)))
        dice_attack_total_fmt = gameutil.FMT_BAD.format(dice_attack_total)
        print("The {} rolled [{}] = {}".format(enemy.name, dice_attack_fmt, dice_attack_total_fmt))
        player_roll = player.get_defense_roll(self.damage_type)
        input("Rolling {}d6 for to defend...".format(player_roll))
        dice_player = gameutil.roll_dice(player_roll, 6)
        dice_player_total = sum(dice_player)
        dice_player_fmt = gameutil.FMT_GOOD.format(' '.join((str(x) for x in dice_player)))
        dice_player_total_fmt = gameutil.FMT_GOOD.format(dice_player_total)
        print("You rolled [{}] = {}".format(dice_player_fmt, dice_player_total_fmt))
        if dice_attack_total > dice_player_total:
            print(self.description_hit)
            fmt_damage = ["{} {}".format(gameutil.FMT_BAD.format(self.damage),
                gameutil.FMT_STAT.format(stat.upper())) for stat in self.stats]
            print("You took {} damage!".format(gameutil.join_list_pretty(fmt_damage)))
            for stat in self.stats:
                playerstat = player.get_stat(stat)
                playerstat.subtract(self.damage)
        else:
            print(self.description_miss)

class EnemyActionWait(EnemyAction):
    """
    Enemy wait
    """
    def __init__(self, attackname, attackdef):
        super().__init__(attackname, attackdef)
        self.description = attackdef.get("desc", "It attacks you")
    def _game_use(self, player, enemy):
        print(self.description)

def parse_enemy_action(actionname, actiondata):
    atype = actiondata.get("type")
    if atype == "attack":
        return EnemyAttack(actionname, actiondata)
    elif atype == "wait":
        return EnemyActionWait(actionname, actiondata)
    else:
        print("Unknown enemy attack type '{}'".format(atype))
        return None

class GameEnemy:
    """
    Game enemy
    """
    def __init__(self, enemyname, enemydata):
        self.shortname = enemyname
        self.name = enemydata.get("name", enemyname)
        self.look = enemydata.get("look", "It's a {}".format(self.name))
        self.nameplural = enemydata.get("plural", self.name + "s")
        self.health = gameutil.EnemyHealth(enemydata.get("health", 1))
        self.description = enemydata.get("desc", "")
        self.defense = enemydata.get("defense", 1)
        self.attacks = []
        self.next_action = None
        if "actions" in enemydata:
            for actionname, actiondata in enemydata["actions"].items():
                action = parse_enemy_action(actionname, actiondata)
                if action != None:
                    self.attacks.append(action)
        # -1 is no curse.
        # Player's attack sets curses to 1. This way, curse doesn't get removed
        # for the player's next attack. Curse is also decremented *before* the
        # enemy's attack so that their attack is only cursed for 1 turn.
        self.curse = -1
    def get_defense_value(self):
        """
        Get this enemy's defense value
        """
        defense = self.defense
        if self.curse >= 0 and defense > 1:
            defense -= 1
        return defense
    def get_defense_roll(self):
        """
        Roll defense

        Returns a list[int] of dice values
        """
        return gameutil.roll_dice(self.get_defense_value(), 6)
    def get_attack_roll(self, roll):
        """
        Roll attack

        Returns a list[int] of dice values.
        """
        if self.curse >= 0 and roll > 1:
            roll -= 1
        return gameutil.roll_dice(roll, 6)
    def is_dead(self):
        """
        Returns true if the enemy is dead
        """
        return self.health.value == 0
    def do_turn(self, gamedata):
        """
        Perform this enemy's turn
        """
        self.curse = self.curse - 1
        if len(self.attacks) == 0:
            print("The {} can't do anything.".format(self.name))
        else:
            if self.next_action != None:
                a = self.next_action
                self.next_action = None
                a.use(gamedata.player, self)
            elif len(self.attacks) > 0:
                atk = random.choice(self.attacks)
                atk.use(gamedata.player, self)
            else:
                print("Does nothing")
    def fmt_name(self):
        return gameutil.FMT_ENEMY.format(self.name)
    def __str__(self):
        ret = gameutil.FMT_ENEMY.format(self.name)
        if self.health.value != self.health.maxvalue:
            ret += " [-{}]".format(self.health.maxvalue - self.health.value)
        if self.curse > 0:
            ret += " [curse {}]".format(self.curse)
        return ret
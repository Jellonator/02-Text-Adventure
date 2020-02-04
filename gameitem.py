import gameutil
import random

def choose_enemy(gamedata):
    """
    Choose an enemy to attack
    """
    return gameutil.choose_from_list(gamedata.encounter, True,
        "Choose an enemy to attack", None, gameutil.FMT_NONE)

ATTACK_MISS = 0
ATTACK_HIT = 1
ATTACK_CANCEL = 2

def try_attack_enemy(gamedata, target, stat, stat_negate, attack_bonus):
    """
    Try to attack an enemy; returns ATTACK_HIT on success, ATTACK_MISS on
    failure, and ATTACK_CANCEL if the attack was cancelled. Actually doing
    damage to the enemy is the responsibility of the callee.

    Parameters
    ----------
    target: GameEnemy
        The enemy to attack.
    stat: str
        The player stat to use for attacking.
    stat_negate: bool
        If true, the stat is negated to (stat.maxvalue - stat.value + 1).
    attack_bonus: int
        The attack bonus.
    """
    player_stat = gamedata.player.get_stat(stat, False)
    dice_stat = None
    player_stat_value = 0
    if player_stat != None:
        if stat_negate:
            player_stat_value = player_stat.maxvalue - player_stat.value + 1
        else:
            player_stat_value = player_stat.value
        dice_stat = gameutil.roll_dice(player_stat_value + attack_bonus, 6)
    else:
        dice_stat = gameutil.roll_dice(attack_bonus, 6)
    if attack_bonus == 0:
        input("Rolling {}d6 to attack...".format(player_stat_value))
    else:
        input("Rolling {}d6 + {}d6...".format(player_stat_value, attack_bonus))
    fmt_stat = gameutil.FMT_GOOD.format(' '.join((str(x) for x in dice_stat)))
    roll_total = sum(dice_stat)
    fmt_roll_total = gameutil.FMT_GOOD.format(roll_total)
    print("You rolled: [{}] = {}".format(fmt_stat, fmt_roll_total))
    input("The {} is rolling {}d6 for defense...".format(target.name, target.get_defense_value()))
    target_dice = target.get_defense_roll()
    target_roll_total = sum(target_dice)
    fmt_target = gameutil.FMT_BAD.format(' '.join((str(x) for x in target_dice)))
    fmt_target_roll_total = gameutil.FMT_BAD.format(target_roll_total)
    print("The {} rolled [{}] = {}".format(target.name, fmt_target, fmt_target_roll_total))
    if roll_total >= target_roll_total:
        return ATTACK_HIT
    else:
        return ATTACK_MISS

class GameAction:
    """
    A game action. Can be a use item, attack, defend, etc.
    """
    def __init__(self, attackname, parentitem, attackdef):
        self.name = attackdef.get("name", attackname)
        self.info = attackdef.get("info")
        self.single_use = attackdef.get("single-use", False)
        self.parentitem = parentitem
    def format_info(self):
        """
        Format the action's information
        """
        return ""
    def get_defense(self, player):
        """
        Get the defense roll.

        Parameters
        ----------
        player: Character
            The player
        """
        return 1
    def does_resist(self, typename):
        """
        Returns true if this action can be used to resist the given damage type.

        Parameters
        ----------
        typename: str
            The damage type to resist.
        """
        return False
    def use(self, gamedata):
        """
        Use this item.
        """
        self._game_use(gamedata, {})
        if self.single_use:
            gamedata.player.inventory.remove(self.parentitem)
    def _game_use(self, gamedata, shared):
        """
        Please don't use this method directly.
        """
        print("Nothing to do.")
    def __str__(self):
        info = self.format_info().strip()
        if info != "":
            info = "[{}]".format(info)
        if self.info != None:
            info += " - " + self.info
        fmtname = gameutil.FMT_OPTION.format(self.name)
        if self.parentitem != None:
            return "{} ({}) {}".format(fmtname, gameutil.FMT_OPTION.format(self.parentitem.name), info)
        else:
            return "{} {}".format(fmtname, info)

class GameActionAttack(GameAction):
    """
    Attack action
    """
    def __init__(self, attackname, parentitem, attackdef):
        super().__init__(attackname, parentitem, attackdef)
        self.target = attackdef.get("target", "single")
        self.random_count = attackdef.get("random-count", 1)
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
            return gameutil.FMT_STAT.format(c + self.stat.upper())
        else:
            return gameutil.FMT_STAT.format(c + self.stat.upper()) + "+" + str(self.bonus)
    def _attack(self, gamedata, target):
        print("Attacking {}".format(target.name))
        status = try_attack_enemy(gamedata, target, self.stat, self.stat_negate, self.bonus)
        if status == ATTACK_HIT:
            print("You hit the {} for {} damage!".format(target.name, gameutil.FMT_GOOD.format(self.damage)))
            target.health.subtract(self.damage)
        elif status == ATTACK_MISS:
            print("You missed the {}.".format(target.name))
        else:
            return False
        return True
    def _game_use(self, gamedata, shared):
        if self.target == "single":
            # Theoretically could be used so that a single attack could hit twice
            target = shared.get("target")
            if target == None:
                target = choose_enemy(gamedata)
                if target == None:
                    return False
                shared["target"] = target
            self._attack(gamedata, target)
        elif self.target == "all":
            for enemy in gamedata.encounter:
                self._attack(gamedata, enemy)
        elif self.target == "random":
            for _i in range(self.random_count):
                if len(gamedata.encounter) > 0:
                    enemy = random.choice(gamedata.encounter)
                    self._attack(gamedata, enemy)
                    gamedata.remove_dead_enemies()
                else:
                    break
        else:
            print("Unknown target value '{}'".format(self.target))

class GameActionCurse(GameAction):
    """
    Curse action
    """
    def __init__(self, attackname, parentitem, attackdef):
        super().__init__(attackname, parentitem, attackdef)
        self.target = attackdef.get("target", "single")
        self.stat = attackdef.get("stat", "none").lower()
        self.stat_negate = attackdef.get("stat-negate", False)
        self.bonus = attackdef.get("bonus", 0)
        self.amount = attackdef.get("amount", 1)
    def format_info(self):
        c = ""
        if self.stat_negate:
            c = "-"
        if self.stat == "none":
            return "+" + str(self.bonus)
        elif self.bonus == 0:
            return gameutil.FMT_STAT.format(c + self.stat.upper())
        else:
            return gameutil.FMT_STAT.format(c + self.stat.upper()) + "+" + str(self.bonus)
    def _game_use(self, gamedata, shared):
        # Theoretically could be used so that a single attack could hit twice
        target = shared.get("target")
        if target == None:
            target = choose_enemy(gamedata)
            if target == None:
                return False
            shared["target"] = target
        print("Cursing {}".format(target.name))
        status = try_attack_enemy(gamedata, target, self.stat, self.stat_negate, self.bonus)
        if status == ATTACK_HIT:
            plural = ""
            if self.amount > 1:
                plural = "s"
            print("You cursed the {} for {} turn{}!".format(target.name, self.amount, plural))
            target.curse = max(target.curse, self.amount)
        elif status == ATTACK_MISS:
            print("You missed the {}.".format(target.name))
        else:
            return False
        return True

class GameActionDefend(GameAction):
    """
    Defend action
    """
    def __init__(self, attackname, parentitem, attackdef):
        super().__init__(attackname, parentitem, attackdef)
        self.stat = attackdef.get("stat", "none").lower()
        self.stat_negate = attackdef.get("stat-negate", False)
        self.bonus = attackdef.get("bonus", 0)
        self.resist = attackdef.get("resist", "all")
        if self.resist not in ["all", "physical", "mental"]:
            print("Unknown resist type '{}'".format(self.resist))
            self.resist = "all"
    def format_info(self):
        c = ""
        if self.stat_negate:
            c = "-"
        if self.stat == "none":
            return "+" + str(self.bonus)
        elif self.bonus == 0:
            return gameutil.FMT_STAT.format(c + self.stat.upper())
        else:
            return gameutil.FMT_STAT.format(c + self.stat.upper()) + "+" + str(self.bonus)
    def get_defense(self, player):
        stat = player.get_stat(self.stat)
        value = 0
        if stat != None:
            if self.stat_negate:
                value = stat.maxvalue - stat.value + 1
            else:
                value = stat.value
        return value + self.bonus
    def does_resist(self, typename):
        return self.resist == "all" or self.resist == typename

class GameActionHeal(GameAction):
    """
    Heal action
    """
    def __init__(self, attackname, parentitem, attackdef):
        super().__init__(attackname, parentitem, attackdef)
        self.stat = attackdef.get("stat", "none").lower()
        self.amount = attackdef.get("amount", 1)
    def format_info(self):
        return "+{}".format(gameutil.FMT_GOOD.format(self.amount))
    def _game_use(self, gamedata, shared):
        stat = gamedata.player.get_stat(self.stat, True, "Choose a stat to heal")
        if stat != None:
            stat.add(self.amount)
            return True
        return False

class GameActionBarricade(GameAction):
    """
    Barricade action
    """
    def __init__(self, attackname, parentitem, attackdef):
        super().__init__(attackname, parentitem, attackdef)
        self.amount = attackdef.get("amount", 1)
    def format_info(self):
        return "+{}".format(gameutil.FMT_GOOD.format(self.amount))
    def _game_use(self, gamedata, shared):
        gamedata.player.barricade = max(gamedata.player.barricade, self.amount)
        return True

def generate_abilities(actions, item, itemlist):
    for attackname, attackdef in itemlist.items():
        # print(attackname, attackdef)
        atype = attackdef.get("type")
        if atype == "attack":
            actions[attackname] = GameActionAttack(attackname, item, attackdef)
        elif atype == "curse":
            actions[attackname] = GameActionCurse(attackname, item, attackdef)
        elif atype == "block":
            actions[attackname] = GameActionDefend(attackname, item, attackdef)
        elif atype == "heal":
            actions[attackname] = GameActionHeal(attackname, item, attackdef)
        elif atype == "barricade":
            actions[attackname] = GameActionBarricade(attackname, item, attackdef)
        else:
            print("Unrecognized attack type '{}'".format(atype))

class GameItem:
    """
    A game item
    """
    def __init__(self, itemname, itemdef):
        self.fullname = itemname
        self.name = itemdef.get("name", itemname)
        self.weight = itemdef.get("weight", 0)
        self.max_durability = itemdef.get("durability", 1)
        self.desc = itemdef.get("desc", "")
        self.durability = self.max_durability
        self.unlisted = itemdef.get("unlisted", False)
        self.actions = {}
        self.attacks = {}
        self.reactions = {}
        if "attacks" in itemdef:
            generate_abilities(self.attacks, self, itemdef["attacks"])
        if "actions" in itemdef:
            generate_abilities(self.actions, self, itemdef["actions"])
        if "reactions" in itemdef:
            generate_abilities(self.reactions, self, itemdef["reactions"])
import gameutil

class GameEnemy:
    def __init__(self, enemyname, enemydata):
        self.name = enemydata.get("name", enemyname)
        self.nameplural = enemydata.get("plural", self.name + "s")
        self.health = gameutil.EnemyHealth(enemydata.get("health", 1))
        self.description = enemydata.get("desc", "")
        self.defense = enemydata.get("defense", 1)
    def get_defense_roll(self):
        return gameutil.roll_dice(self.defense, 6)
    def is_dead(self):
        return self.health.value == 0
    def __str__(self):
        if self.health.value == self.health.maxvalue:
            return self.name
        else:
            return self.name + " [-{}]".format(self.health.maxvalue - self.health.value)
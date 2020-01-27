import gameutil

class GameEnemy:
    def __init__(self, enemyname, enemydata):
        self.name = enemydata.get("name", enemyname)
        self.nameplural = enemydata.get("plural", self.name + "s")
        self.health = gameutil.CharacterStat(enemydata.get("health", 1))
        self.description = enemydata.get("desc", "")
    def is_dead(self):
        return self.health.value == 0
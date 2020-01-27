class GameItem:
    def __init__(self, itemname, itemdef):
        self.name = itemdef.get("name", itemname)
        self.weight = itemdef.get("weight", 0)
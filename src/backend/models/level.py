from math import ceil

class Level:
    def __init__(self):
        self.level = 0
        self.xp = 0
        self.current_level = 0
        self.needed_xp = 0

    def add_xp(self, xp: int):
        self.xp += xp
        self.update_level()

    def remove_xp(self, xp: int):
        self.xp = max(0, self.xp - xp)
    
    def update_level(self):
        if self.xp >= self.needed_xp:
            # TODO: Check for double level up
            self.level += 1
            self.needed_xp = ceil((self.needed_xp*1.25)/100)*100 # Round to next 100

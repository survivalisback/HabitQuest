
class Level:
    def __init__(self, level: int = 0, experience_points: int = 0):
        self.level = level
        self.experience_points = experience_points

    def calculate_level(self) -> int:
        # Simple leveling system: every 100 XP increases the level by 1
        self.level = self.experience_points // 100
        return self.level
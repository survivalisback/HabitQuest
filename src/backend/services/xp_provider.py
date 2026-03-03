from models.habit import Habit

class XpProvider:
    def __init__(self):
        pass

    def calculate_xp(self, habit: Habit) -> int:
        base_xp = habit.difficulty * 10
        frequency_multiplier = {
            "daily": 1.0,
            "weekly": 1.5,
            "monthly": 2.0
        }.get(habit.frequency, 1.0)
        
        return int(base_xp * frequency_multiplier)
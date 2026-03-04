from models.habit import Habit
from level_policy import Level

class StaticXpProvider:
    def __init__(self, level: Level):
        self.level = level

    def calculate_xp(self, habit: Habit) -> int:
        base_xp = habit.difficulty * 10
        frequency_multiplier = {
            "once": 1.0,
            "daily": 1.0,
            "weekly": 1.5,
            "monthly": 2.0
        }.get(habit.frequency, 1.0)
        
        return int(base_xp * frequency_multiplier)

    def grant_xp(self, habit: Habit):
        xp = self.calculate_xp(habit)
        self.level.add_xp(xp)

class DynamicXpProvider:
    def __init__(self, level: Level):
        self.level = level

    def calculate_xp(self, habit: Habit) -> int:
        # Placeholder for dynamic XP calculation logic
        # This could involve calling an AI service to evaluate the habit's attributes and history
        return 0  # Return a default value for now
    
    def grant_xp(self, habit: Habit):
        xp = self.calculate_xp(habit)
        self.level.add_xp(xp)
from datetime import datetime
from typing import Annotated

class Habit:
    id: Annotated[int, "Auto-incremented primary key - Is created by the database and should not be edited manually"]
    name: str
    description: str
    frequency: Annotated[str, "e.g. 'daily', 'weekly', 'monthly'"]
    difficulty: Annotated[str, "1-5"]
    xp_reward: int
    streak: int
    longest_streak: int
    last_completed: datetime
    created_at: datetime
    updated_at: datetime

    def __init__(self, name, description, frequency, difficulty):
        self.name = name
        self.description = description
        self.frequency = frequency
        self.difficulty = difficulty
    
    def check_duplicate(self, other_habit: 'Habit') -> bool:
        return self.name == other_habit.name and self.description == other_habit.description and self.frequency == other_habit.frequency
    
    def is_valid(self) -> bool:
        if not self.name or not self.description or not self.frequency:
            return False
        if self.difficulty:
            if self.difficulty < 1 or self.difficulty > 5:
                return False
        return True
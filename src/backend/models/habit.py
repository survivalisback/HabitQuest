from datetime import datetime

class Habit:
    id: int
    name: str
    description: str
    frequency: str
    difficulty: str
    xp_reward: int
    streak: int
    longest_streak: int
    last_completed: str
    created_at: datetime
    updated_at: datetime

    def __init__(self, name, description, frequency, difficulty):
        self.name = name
        self.description = description
        self.frequency = frequency
        self.difficulty = difficulty
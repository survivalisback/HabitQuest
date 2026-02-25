from repository.habitRepository import HabitRepository
from models.habit import Habit
from datetime import datetime

# Business/Gamification Logic
class Service:
    habit_repository: HabitRepository

    def __init__(self):
        self.habit_repository = HabitRepository()

    def create_habit(self, name: str, description: str, frequency: str, difficulty: int):
        habit = Habit(name, description, frequency, difficulty)
        habit.xp_reward = self.calculate_xp_reward(habit)
        habit.updated_at = habit.created_at = datetime.now()
        self.habit_repository.create_habit(habit)

    # TODO: Calculate xp reward based on llm
    def calculate_xp_reward(self, habit: Habit) -> int:
        return habit.difficulty * 10
from repository.habitRepository import HabitRepository
from models.habit import Habit
from datetime import datetime

# Business/Gamification Logic
class Service:
    def __init__(self, repository: HabitRepository):
        self.habit_repository = repository

    def create_habit(self, name: str, description: str, frequency: str, difficulty: int):
        habit = Habit(name, description, frequency, difficulty)
        habit.xp_reward = self.calculate_xp_reward(habit)
        habit.updated_at = habit.created_at = datetime.now()
        self.habit_repository.create_habit(habit)

    def edit_habit(self, habit_id: int, name: str, description: str, frequency: str, difficulty: int):
        habit = Habit(name, description, frequency, difficulty)
        habit.xp_reward = self.calculate_xp_reward(habit)
        habit.updated_at = datetime.now()
        self.habit_repository.update_habit(habit_id, habit)

    def delete_habit(self, habit_id: int):
        self.habit_repository.delete_habit(habit_id)
    
    def toggle_task_completion(self, habit_id: int):
        self.habit_repository.toggle_task_completion(habit_id)

    # TODO: Calculate xp reward based on llm
    def calculate_xp_reward(self, habit: Habit) -> int:
        return habit.difficulty * 10
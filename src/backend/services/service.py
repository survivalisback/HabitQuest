from repository.habitRepository import HabitRepository
from models.habit import Habit
from datetime import datetime
from services.xp_provider import StaticXpProvider

# Business/Gamification Logic
class Service:
    def __init__(self, repository: HabitRepository, xp_provider: StaticXpProvider):
        self.habit_repository = repository
        self.xp_provider = xp_provider

    def create_habit(self, name: str, description: str, frequency: str, difficulty: int):
        habit = Habit(name, description, frequency, difficulty)
        habit.xp_reward = self.xp_provider.calculate_xp(habit)
        habit.updated_at = habit.created_at = datetime.now()
        self.habit_repository.create_habit(habit)

    def edit_habit(self, habit_id: int, name: str, description: str, frequency: str, difficulty: int):
        habit = Habit(name, description, frequency, difficulty)
        existing_habit = self.habit_repository.get_habit_by_id(habit_id)
        if existing_habit is not None and getattr(existing_habit, "xp_reward", None) is not None:
            habit.xp_reward = existing_habit.xp_reward
        else:
            habit.xp_reward = self.xp_provider.calculate_xp(habit)
        habit.updated_at = datetime.now()
        self.habit_repository.update_habit(habit_id, habit)

    def delete_habit(self, habit_id: int):
        self.habit_repository.delete_habit(habit_id)
    
    def toggle_habit_completion(self, habit_id: int):
        is_completed = self.habit_repository.toggle_habit_completion(habit_id)
        completed_habit = self.habit_repository.get_habit_by_id(habit_id)
        if completed_habit is not None:
            if is_completed:
                self.xp_provider.grant_xp(completed_habit)
            else:
                self.xp_provider.revoke_xp(completed_habit)
        return is_completed

from repository.habitRepository import HabitRepository
from models.habit import Habit
from models.user import User
from datetime import datetime
from services.xp_provider import StaticXpProvider

# Business/Gamification Logic
class Service:
    def __init__(self, repository: HabitRepository, xp_provider: StaticXpProvider):
        self.habit_repository = repository
        self.xp_provider = xp_provider

    def login_user(self, user_id: int, username: str | None = None):
        self.habit_repository.connection.ensure_user(User(user_id=user_id, username=username))

    def create_habit(self, user_id: int, name: str, description: str, frequency: str, difficulty: int):
        habit = Habit(name, description, frequency, difficulty, user_id)
        habit.xp_reward = self.xp_provider.calculate_xp(habit)
        habit.updated_at = habit.created_at = datetime.now()
        self.habit_repository.create_habit(habit, user_id)

    def edit_habit(self, user_id: int, habit_id: int, name: str, description: str, frequency: str, difficulty: int):
        habit = Habit(name, description, frequency, difficulty, user_id)
        existing_habit = self.habit_repository.get_habit_by_id(habit_id, user_id)
        if existing_habit is not None and getattr(existing_habit, "xp_reward", None) is not None:
            habit.xp_reward = existing_habit.xp_reward
        else:
            habit.xp_reward = self.xp_provider.calculate_xp(habit)
        habit.updated_at = datetime.now()
        self.habit_repository.update_habit(habit_id, habit, user_id)

    def delete_habit(self, user_id: int, habit_id: int):
        self.habit_repository.delete_habit(habit_id, user_id)
    
    def toggle_habit_completion(self, user_id: int, habit_id: int):
        is_completed = self.habit_repository.toggle_habit_completion(habit_id, user_id)
        completed_habit = self.habit_repository.get_habit_by_id(habit_id, user_id)
        if completed_habit is not None:
            if is_completed:
                self.xp_provider.grant_xp(completed_habit)
            else:
                self.xp_provider.revoke_xp(completed_habit)
        return is_completed

    def get_habits(self, user_id: int):
        return self.habit_repository.get_habits_for_user(user_id)

from repository.habitRepository import HabitRepository
from models.habit import Habit
from models.user import User
from models.level import get_level_info
from datetime import datetime
from services.auth import JwtConfig, generate_jwt, hash_password, verify_jwt, verify_password
from config import settings


# Business/Gamification Logic
class Service:
    def __init__(self, repository: HabitRepository, xp_provider, streak_service=None):
        self.habit_repository = repository
        self.xp_provider = xp_provider
        self.streak_service = streak_service
        self.jwt_config = JwtConfig(
            secret=settings.jwt_secret,
            issuer=settings.jwt_issuer,
            expires_in_seconds=settings.jwt_expires_in_seconds,
        )

    @property
    def db(self):
        return self.habit_repository.connection

    def register_user(self, username: str, password: str) -> dict[str, str | int]:
        normalized = (username or "").strip()
        if not normalized:
            raise ValueError("Username is required.")
        if not password:
            raise ValueError("Password is required.")

        existing_id = self.db.get_user_id_by_username(normalized)
        if existing_id is not None:
            raise ValueError("Username already exists.")

        user_id = self.db.get_next_user_id()
        password_hash = hash_password(password)
        self.db.ensure_user(
            User(user_id=user_id, username=normalized, password=password_hash)
        )
        self.db.set_user_password_hash(user_id, password_hash)
        self.db.ensure_user_progress(user_id)
        token = generate_jwt(user_id, self.jwt_config)
        return {"user_id": user_id, "username": normalized, "token": token}

    def login_user(self, username: str, password: str) -> dict[str, str | int]:
        normalized = (username or "").strip()
        if not normalized or not password:
            raise ValueError("Username and password are required.")

        user_id = self.db.get_user_id_by_username(normalized)
        if user_id is None:
            raise ValueError("Invalid username or password.")

        stored_hash = self.db.get_user_password_hash(user_id)
        if stored_hash is None or not verify_password(password, stored_hash):
            raise ValueError("Invalid username or password.")

        token = generate_jwt(user_id, self.jwt_config)
        return {"user_id": user_id, "username": normalized, "token": token}

    def get_user_id_from_token(self, token: str) -> int:
        raw = (token or "").strip()
        if raw.lower().startswith("bearer "):
            raw = raw.split(" ", 1)[1].strip()
        user_id = verify_jwt(raw, self.jwt_config)
        if user_id is None:
            raise ValueError("Invalid or expired token.")
        return user_id

    def create_habit(self, user_id: int, name: str, description: str, frequency: str):
        if frequency == "once":
            raise ValueError("One-time habits should use the /trackOneTime endpoint.")
        habit = Habit(name, description, frequency, 3, user_id)
        evaluation = self.xp_provider.evaluate_habit(habit)
        habit.difficulty = evaluation["difficulty"]
        habit.xp_reward = evaluation["xp"]
        habit.updated_at = habit.created_at = datetime.now()
        self.habit_repository.create_habit(habit, user_id)

    def edit_habit(self, user_id: int, habit_id: int, name: str, description: str, frequency: str):
        habit = Habit(name, description, frequency, 3, user_id)
        evaluation = self.xp_provider.evaluate_habit(habit)
        habit.difficulty = evaluation["difficulty"]
        habit.xp_reward = evaluation["xp"]
        habit.updated_at = datetime.now()
        self.habit_repository.update_habit(habit_id, habit, user_id)

    def delete_habit(self, user_id: int, habit_id: int):
        habit = self.habit_repository.get_habit_by_id(habit_id, user_id)
        if habit is not None:
            is_completed = self.db.get_current_period_completion(habit_id, habit.frequency)
            if is_completed:
                self.xp_provider.revoke_xp(habit, self.db, user_id)
        self.db.delete_habit_completions(habit_id)
        self.habit_repository.delete_habit(habit_id, user_id)

    def toggle_habit_completion(self, user_id: int, habit_id: int) -> dict:
        is_completed = self.habit_repository.toggle_habit_completion(habit_id, user_id)
        completed_habit = self.habit_repository.get_habit_by_id(habit_id, user_id)

        xp_reward = 0
        streak = 0
        streak_bonus_xp = 0

        if completed_habit is not None:
            if is_completed:
                xp_reward = self.xp_provider.grant_xp(completed_habit, self.db, user_id)
                if self.streak_service:
                    streak = self.streak_service.calculate_streak(habit_id, completed_habit.frequency)
                    streak_bonus_xp = self.streak_service.calculate_streak_bonus_xp(xp_reward, streak)
                    if streak_bonus_xp > 0:
                        self.db.update_user_xp(user_id, streak_bonus_xp)
            else:
                xp_reward = self.xp_provider.revoke_xp(completed_habit, self.db, user_id)

        progress = self.db.get_user_progress(user_id)
        level_info = get_level_info(progress["total_xp"])

        return {
            "habit_id": habit_id,
            "completed": is_completed,
            "xp_reward": xp_reward,
            "streak": streak,
            "streak_bonus_xp": streak_bonus_xp,
            "level_info": level_info,
        }

    def get_habits(self, user_id: int):
        return self.habit_repository.get_habits_for_user(user_id)

    def get_profile(self, user_id: int) -> dict:
        progress = self.db.get_user_progress(user_id)
        level_info = get_level_info(progress["total_xp"])
        return {
            "total_xp": progress["total_xp"],
            "total_completions": progress["total_completions"],
            "level_info": level_info,
        }

    def track_one_time(self, user_id: int, name: str, description: str) -> dict:
        habit = Habit(name, description, "once", 3, user_id)
        evaluation = self.xp_provider.evaluate_habit(habit)
        habit.difficulty = evaluation["difficulty"]
        xp = evaluation["xp"]
        self.db.update_user_xp(user_id, xp)
        self.db.increment_completions(user_id, 1)
        progress = self.db.get_user_progress(user_id)
        level_info = get_level_info(progress["total_xp"])
        return {
            "name": name,
            "xp_reward": xp,
            "level_info": level_info,
        }

    def get_habit_streaks(self, user_id: int) -> dict[int, int]:
        if not self.streak_service:
            return {}
        data = self.db.get_all_habit_streaks(user_id)
        completions = data["completions"]
        frequencies = data["frequencies"]
        result = {}
        for habit_id in completions:
            freq = frequencies.get(habit_id, "daily")
            streak = self.streak_service.calculate_streak(habit_id, freq)
            result[habit_id] = streak
        return result

from repository.habitRepository import HabitRepository
from models.habit import Habit
from models.user import User
from datetime import datetime
from services.xp_provider import StaticXpProvider
from services.auth import JwtConfig, generate_jwt, hash_password, verify_jwt, verify_password
from config import settings

# Business/Gamification Logic
class Service:
    def __init__(self, repository: HabitRepository, xp_provider: StaticXpProvider):
        self.habit_repository = repository
        self.xp_provider = xp_provider
        self.jwt_config = JwtConfig(
            secret=settings.jwt_secret,
            issuer=settings.jwt_issuer,
            expires_in_seconds=settings.jwt_expires_in_seconds,
        )

    def register_user(self, username: str, password: str) -> dict[str, str | int]:
        normalized = (username or "").strip()
        if not normalized:
            raise ValueError("Username is required.")
        if not password:
            raise ValueError("Password is required.")

        existing_id = self.habit_repository.connection.get_user_id_by_username(normalized)
        if existing_id is not None:
            raise ValueError("Username already exists.")

        user_id = self.habit_repository.connection.get_next_user_id()
        password_hash = hash_password(password)
        self.habit_repository.connection.ensure_user(
            User(user_id=user_id, username=normalized, password=password_hash)
        )
        self.habit_repository.connection.set_user_password_hash(user_id, password_hash)
        token = generate_jwt(user_id, self.jwt_config)
        return {"user_id": user_id, "username": normalized, "token": token}

    def login_user(self, username: str, password: str) -> dict[str, str | int]:
        normalized = (username or "").strip()
        if not normalized or not password:
            raise ValueError("Username and password are required.")

        user_id = self.habit_repository.connection.get_user_id_by_username(normalized)
        if user_id is None:
            raise ValueError("Invalid username or password.")

        stored_hash = self.habit_repository.connection.get_user_password_hash(user_id)
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

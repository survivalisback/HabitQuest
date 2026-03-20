from repository.db_connector import DBConnector
from models.user import User


class UserRepository:
    def __init__(self, db: DBConnector):
        self.connection = db

    def create_user(self, user: User) -> None:
        self.connection.ensure_user(user)
        self.connection.set_user_password_hash(user.user_id, user.password)
        self.connection.ensure_user_progress(user.user_id)

    def get_user_id_by_username(self, username: str) -> int | None:
        return self.connection.get_user_id_by_username(username)

    def get_next_user_id(self) -> int:
        return self.connection.get_next_user_id()

    def get_password_hash(self, user_id: int) -> str | None:
        return self.connection.get_user_password_hash(user_id)

    def get_progress(self, user_id: int) -> dict:
        return self.connection.get_user_progress(user_id)

    def update_xp(self, user_id: int, xp_delta: int) -> None:
        self.connection.update_user_xp(user_id, xp_delta)

    def increment_completions(self, user_id: int, delta: int) -> None:
        self.connection.increment_completions(user_id, delta)

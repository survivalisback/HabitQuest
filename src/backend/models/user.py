from typing import Annotated


class User:
    user_id: Annotated[int, "Unique user identifier"]
    username: str
    password: str

    def __init__(self, user_id: int, username: str | None = None, password: str | None = None):
        self.user_id = user_id
        self.username = username or f"user-{user_id}"
        self.password = password or ""

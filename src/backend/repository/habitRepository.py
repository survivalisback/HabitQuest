import logging

from repository.db_connector import DBConnector
from models.habit import Habit


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class HabitRepository:
    def __init__(self, db: DBConnector):
        self.connection = db
        self.habits = []

    def create_habit(self, habit: Habit, user_id: int):
        self.update_habits(user_id)
        if any(existing_habit.check_duplicate(habit) for existing_habit in self.habits):
            logger.warning("Duplicate habit detected. Habit not added.")
            raise ValueError("Habit already exists.")
        if not habit.is_valid():
            logger.warning("Invalid habit data. Habit not added.")
            raise ValueError("Invalid habit data.")
        try:
            self.connection.add_habit(habit)
        except Exception as e:
            logger.error(f"Error adding habit to database: {e}")
            raise

    def update_habit(self, habit_id: int, habit: Habit, user_id: int):
        self.connection.update_habit(habit_id, habit, user_id)

    def delete_habit(self, habit_id: int, user_id: int):
        self.connection.delete_habit(habit_id, user_id)

    def toggle_habit_completion(self, habit_id: int, user_id: int) -> bool:
        return self.connection.toggle_habit_completion(habit_id, user_id)

    def update_habits(self, user_id: int):
        self.habits = self.connection.get_habits(user_id)

    def get_habit_id(self, habit: Habit, user_id: int) -> int:
        self.update_habits(user_id)
        for existing_habit in self.habits:
            if existing_habit.check_duplicate(habit):
                return existing_habit.id
        return -1
    
    def get_habit_by_id(self, habit_id: int, user_id: int) -> Habit:
        return self.connection.get_habit_by_id(habit_id, user_id)

    def get_habits_for_user(self, user_id: int) -> list[Habit]:
        return self.connection.get_habits(user_id)

    def get_current_period_completion(self, habit_id: int, frequency: str) -> bool:
        return self.connection.get_current_period_completion(habit_id, frequency)

    def delete_completions(self, habit_id: int) -> None:
        self.connection.delete_habit_completions(habit_id)

    def get_all_streaks(self, user_id: int) -> dict:
        return self.connection.get_all_habit_streaks(user_id)

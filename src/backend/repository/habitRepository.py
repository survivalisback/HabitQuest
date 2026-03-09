import logging

from repository.db_connector import DBConnector
from models.habit import Habit


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class HabitRepository:
    def __init__(self, db: DBConnector):
        self.connection = db
        self.habits = []

    def create_habit(self, habit: Habit):
        self.update_habits()
        if any(existing_habit.check_duplicate(habit) for existing_habit in self.habits):
            logger.warning("Duplicate habit detected. Habit not added.")
            return
        if not habit.is_valid():
            logger.warning("Invalid habit data. Habit not added.")
            return
        try:
            self.connection.add_habit(habit)
        except Exception as e:
            logger.error(f"Error adding habit to database: {e}")

    def update_habit(self, habit_id: int, habit: Habit):
        self.connection.update_habit(habit_id, habit)

    def delete_habit(self, habit_id: int):
        self.connection.delete_habit(habit_id)

    def toggle_habit_completion(self, habit_id: int) -> bool:
        return self.connection.toggle_habit_completion(habit_id)

    def update_habits(self):
        self.habits = self.connection.get_habits()

    def get_habit_id(self, habit: Habit) -> int:
        self.update_habits()
        for existing_habit in self.habits:
            if existing_habit.check_duplicate(habit):
                return existing_habit.id
        return -1
    
    def get_habit_by_id(self, habit_id: int) -> Habit:
        return self.connection.get_habit_by_id(habit_id)

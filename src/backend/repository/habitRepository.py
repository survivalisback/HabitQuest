from backend.repository.db_connector import DBConnector
from models.habit import Habit

class HabitRepository:

    connection: DBConnector
    habits: list

    def __init__(self):
        self.connection = DBConnector()
        self.habits = []

    def create_habit(self, habit: Habit):
        self.update_habits()
        if any(existing_habit.check_duplicate(habit) for existing_habit in self.habits):
            print("Duplicate habit detected. Habit not added.")
            return
        try:
            self.connection.add_habit(habit)
        except Exception as e:
            print(f"Error adding habit to database: {e}")

    def get_habits(self):
        self.update_habits()
        return self.habits

    def update_habit(self, habit_id: int, habit: Habit):
        self.connection.update_habit(habit_id, habit)

    def delete_habit(self, habit_id: int):
        pass

    def update_habits(self):
        self.habits = self.connection.get_habits()

    def get_habit_id(self, habit: Habit) -> int:
        self.update_habits()
        for existing_habit in self.habits:
            if existing_habit.check_duplicate(habit):
                return existing_habit.id
        return -1
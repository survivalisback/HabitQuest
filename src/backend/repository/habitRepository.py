from backend.repository.db_connector import DBConnector
from models.habit import Habit

class HabitRepository:

    connection: DBConnector
    habits: list

    def __init__(self):
        self.connection = DBConnector()
        self.habits = []

    def create_habit(self, habit: Habit):
        try:
            self.connection.add_habit(habit)
            # TODO: Check if habit is a duplicate
        except Exception as e:
            print(f"Error adding habit to database: {e}")

    def get_habits(self):
        self.update_habits()
        return self.habits

    def update_habit(self, habit_id: int, habit: Habit):
        pass

    def delete_habit(self, habit_id: int):
        pass

    def update_habits(self):
        self.habits = self.connection.get_habits()
from backend.repository.db_connector import DBConnector

class HabitRepository:

    connection: DBConnector
    habits: list

    def __init__(self):
        self.connection = DBConnector()
        self.habits = []

    def create_habit(self, habit):
        pass

    def get_habits(self):
        pass

    def update_habit(self, habit_id, habit):
        pass

    def delete_habit(self, habit_id):
        pass
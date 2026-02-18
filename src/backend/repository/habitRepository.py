from dbconnector import DBConnector

class HabitRepository:

    dbConnector: DBConnector
    habits: list

    def __init__(self, db):
        self.dbConnector = db

    def create_habit(self, habit):
        pass

    def get_habits(self):
        pass

    def update_habit(self, habit_id, habit):
        pass

    def delete_habit(self, habit_id):
        pass
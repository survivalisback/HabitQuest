import sqlite3
from models.habit import Habit

class DBConnector:
    def __init__(self):
        self.connection = sqlite3.connect("./db/habitquest.db")
        self.cursor = self.connection.cursor()

    def getHabits(self) -> list:
        self.cursor.execute("SELECT * FROM Habit")
        return self.cursor.fetchall()

    def addHabit(self, habit: Habit) -> None:
        self.cursor.execute("""
        INSERT INTO Habit (name, description, frequency, difficulty, xp_reward)
        VALUES (?, ?, ?, ?, ?)
        """, (habit.name, habit.description, habit.frequency, habit.difficulty, habit.xp_reward))
        self.connection.commit()

    def removeHabit(self, habit: Habit) -> None:
        self.cursor.execute("DELETE FROM Habit WHERE id = ?", (habit.id,))
        self.connection.commit()

    def editHabit(self, habit: Habit) -> None:
        self.cursor.execute("""
        UPDATE Habit
        SET name = ?, description = ?, frequency = ?, difficulty = ?, xp_reward = ?
        WHERE id = ?
        """, (habit.name, habit.description, habit.frequency, habit.difficulty, habit.xp_reward, habit.id))
        self.connection.commit()

    def createBaseFile(self) -> None:
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS "Habit" (
	    "id" INTEGER NOT NULL UNIQUE,
	    "name" TEXT NOT NULL,
        "description" TEXT,
        "frequency" TEXT,
        "difficulty" INTEGER NOT NULL,
        "xp_reward" INTEGER NOT NULL,
        PRIMARY KEY("id")
       );
        """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS "HabitCompleted" (
	    "id" INTEGER NOT NULL UNIQUE,
        "habitID" INTEGER NOT NULL,
        "time" TIMESTAMP NOT NULL,
        PRIMARY KEY("id"),
        FOREIGN KEY ("habitID") REFERENCES "Habit"("id")
        ON UPDATE NO ACTION ON DELETE NO ACTION
        );
        """)
        self.connection.commit()

    def close(self) -> None:
        self.connection.close()
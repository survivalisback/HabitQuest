import sqlite3, logging
from models import habit
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DBConnector:
    def __init__(self):
        settings.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(str(settings.database_path))
        self.cursor = self.connection.cursor()

    def get_habits(self) -> list:
        self.cursor.execute("SELECT * FROM Habit")
        return self.cursor.fetchall()

    def add_habit(self, habit: habit.Habit) -> None:
        self.cursor.execute("""
        INSERT INTO Habit (name, description, frequency, difficulty, xp_reward)
        VALUES (?, ?, ?, ?, ?)
        """, (habit.name, habit.description, habit.frequency, habit.difficulty, habit.xp_reward))
        self.connection.commit()

    def delete_habit(self, habit: habit.Habit) -> None:
        self.cursor.execute("DELETE FROM Habit WHERE id = ?", (habit.id,))
        self.connection.commit()

    def update_habit(self, habit_id: int, habit: habit.Habit) -> None:
        self.cursor.execute("""
        UPDATE Habit
        SET name = ?, description = ?, frequency = ?, difficulty = ?, xp_reward = ?
        WHERE id = ?
        """, (habit.name, habit.description, habit.frequency, habit.difficulty, habit.xp_reward, habit_id))
        self.connection.commit()

    # TODO: Add toggle logic. Keep in mind, that a completed habit gets its own entry in the HabitCompleted table. Therefore, if the task is toggled twice, the entry in the HabitCompleted table should be deleted.
    def toggle_task_completion(self, habit_id: int) -> None:
        pass

    def create_base_file(self) -> None:
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

db = DBConnector()
print(db.get_habits())

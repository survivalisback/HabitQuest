import sqlite3, logging
from datetime import datetime, timedelta
from models.habit import Habit
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

    def add_habit(self, habit: Habit) -> None:
        self.cursor.execute("""
        INSERT INTO Habit (name, description, frequency, difficulty, xp_reward)
        VALUES (?, ?, ?, ?, ?)
        """, (habit.name, habit.description, habit.frequency, habit.difficulty, habit.xp_reward))
        self.connection.commit()

    def delete_habit(self, habit_id: int) -> None:
        self.cursor.execute("DELETE FROM Habit WHERE habit_id = ?", (habit_id))
        self.connection.commit()

    def update_habit(self, habit_id: int, habit: Habit) -> None:
        self.cursor.execute("""
        UPDATE Habit
        SET name = ?, description = ?, frequency = ?, difficulty = ?, xp_reward = ?
        WHERE habit_id = ?
        """, (habit.name, habit.description, habit.frequency, habit.difficulty, habit.xp_reward, habit_id))
        self.connection.commit()

    # TODO: Add toggle logic. Keep in mind, that a completed habit gets its own entry in the HabitCompleted table. Therefore, if the task is toggled twice, the entry in the HabitCompleted table should be deleted.
    def toggle_habit_completion(self, habit_id: int) -> bool:
        self.cursor.execute(
            "SELECT frequency FROM Habit WHERE habit_id = ?",
            (habit_id,)
        )
        row = self.cursor.fetchone()
        if row is None:
            raise ValueError(f"Habit with id {habit_id} not found.")

        period_start = self._resolve_period_start(row[0])
        now_iso = datetime.now().isoformat(timespec="seconds")

        self.cursor.execute(
            """
            SELECT completed
            FROM HabitCompleted
            WHERE habitID = ? AND period_start = ?
            """,
            (habit_id, period_start)
        )
        completion_row = self.cursor.fetchone()

        if completion_row is None:
            self.cursor.execute(
                """
                INSERT INTO HabitCompleted (habitID, period_start, completed, completed_at)
                VALUES (?, ?, 1, ?)
                """,
                (habit_id, period_start, now_iso)
            )
            self.connection.commit()
            return True

        new_completed = 0 if bool(completion_row[0]) else 1
        self.cursor.execute(
            """
            UPDATE HabitCompleted
            SET completed = ?, completed_at = ?
            WHERE habitID = ? AND period_start = ?
            """,
            (new_completed, now_iso, habit_id, period_start)
        )
        self.connection.commit()
        return bool(new_completed)

    def get_habit_by_id(self, habit_id: int) -> Habit | None:
        self.cursor.execute(
            """
            SELECT name, description, frequency, difficulty, xp_reward, habit_id
            FROM Habit
            WHERE habit_id = ?
            """,
            (habit_id,)
        )
        row = self.cursor.fetchone()
        if row is None:
            return None

        db_habit = Habit(row[0], row[1], row[2], row[3])
        db_habit.xp_reward = row[4]
        db_habit.id = row[5]
        return db_habit

    def _resolve_period_start(self, frequency: str) -> str:
        now = datetime.now().date()
        normalized = (frequency or "").lower()

        if normalized == "weekly":
            return (now - timedelta(days=now.weekday())).isoformat()
        if normalized == "monthly":
            return now.replace(day=1).isoformat()
        if normalized == "once":
            return "1970-01-01"
        return now.isoformat()

    def create_base_file(self) -> None:
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS "Habit" (
        "habit_id" INTEGER NOT NULL UNIQUE,
        "user_id" INTEGER NOT NULL,
        "name" TEXT NOT NULL,
        "description" TEXT,
        "frequency" TEXT NOT NULL,
        "difficulty" INTEGER NOT NULL,
        "xp_reward" INTEGER NOT NULL,
        PRIMARY KEY("habit_id")
        );
        """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS "HabitCompleted" (
        "habit_completed_id" INTEGER NOT NULL UNIQUE,
        "habitID" INTEGER NOT NULL,
        "period_start" DATE NOT NULL,
        "completed" BOOLEAN NOT NULL,
        "completed_at" TIMESTAMP NOT NULL,
        PRIMARY KEY("habit_completed_id"),
        FOREIGN KEY ("habitID") REFERENCES "Habit"("habit_id")
        ON UPDATE NO ACTION ON DELETE NO ACTION
        );
        """)
        self.cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS "idx_habit_completed_unique_period"
        ON HabitCompleted ("habitID", "period_start");
        """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS "User" (
        "userid" INTEGER NOT NULL UNIQUE,
        "username" TEXT,
        PRIMARY KEY("userid"),
        FOREIGN KEY ("userid") REFERENCES "UserLogin"("userid")
        ON UPDATE NO ACTION ON DELETE NO ACTION,
        FOREIGN KEY ("userid") REFERENCES "Habit"("user_id")
        ON UPDATE NO ACTION ON DELETE NO ACTION
        );
        """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS "UserLogin" (
        "userid" INTEGER NOT NULL UNIQUE,
        "password" TEXT NOT NULL,
        PRIMARY KEY("userid")
        );
        """)
        self.connection.commit()

    def close(self) -> None:
        self.connection.close()

if __name__ == "__main__":
    db = DBConnector()
    db.create_base_file()
    db.close()

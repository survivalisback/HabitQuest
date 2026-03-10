import sqlite3, logging
from datetime import datetime, timedelta
from models.habit import Habit
from models.user import User
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DBConnector:
    def __init__(self):
        settings.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(str(settings.database_path))
        self.cursor = self.connection.cursor()
        self.create_base_file()
        self._ensure_habit_user_column()

    def get_habits(self, user_id: int) -> list[Habit]:
        self.cursor.execute(
            """
            SELECT habit_id, user_id, name, description, frequency, difficulty, xp_reward
            FROM Habit
            WHERE user_id = ?
            ORDER BY habit_id
            """,
            (user_id,)
        )
        rows = self.cursor.fetchall()
        habits = []
        for row in rows:
            habit = Habit(row[2], row[3], row[4], row[5], row[1])
            habit.id = row[0]
            habit.xp_reward = row[6]
            habits.append(habit)
        return habits

    def add_habit(self, habit: Habit) -> None:
        self.cursor.execute("""
        INSERT INTO Habit (user_id, name, description, frequency, difficulty, xp_reward)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (habit.user_id, habit.name, habit.description, habit.frequency, habit.difficulty, habit.xp_reward))
        self.connection.commit()

    def delete_habit(self, habit_id: int, user_id: int) -> None:
        self.cursor.execute("DELETE FROM Habit WHERE habit_id = ? AND user_id = ?", (habit_id, user_id))
        self.connection.commit()

    def update_habit(self, habit_id: int, habit: Habit, user_id: int) -> None:
        self.cursor.execute("""
        UPDATE Habit
        SET name = ?, description = ?, frequency = ?, difficulty = ?, xp_reward = ?
        WHERE habit_id = ? AND user_id = ?
        """, (habit.name, habit.description, habit.frequency, habit.difficulty, habit.xp_reward, habit_id, user_id))
        self.connection.commit()

    # TODO: Add toggle logic. Keep in mind, that a completed habit gets its own entry in the HabitCompleted table. Therefore, if the task is toggled twice, the entry in the HabitCompleted table should be deleted.
    def toggle_habit_completion(self, habit_id: int, user_id: int) -> bool:
        self.cursor.execute(
            "SELECT frequency FROM Habit WHERE habit_id = ? AND user_id = ?",
            (habit_id, user_id)
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

    def get_habit_by_id(self, habit_id: int, user_id: int) -> Habit | None:
        self.cursor.execute(
            """
            SELECT name, description, frequency, difficulty, xp_reward, habit_id, user_id
            FROM Habit
            WHERE habit_id = ? AND user_id = ?
            """,
            (habit_id, user_id)
        )
        row = self.cursor.fetchone()
        if row is None:
            return None

        db_habit = Habit(row[0], row[1], row[2], row[3], row[6])
        db_habit.xp_reward = row[4]
        db_habit.id = row[5]
        return db_habit

    def ensure_user(self, user: User) -> None:
        self.cursor.execute(
            """
            INSERT OR IGNORE INTO UserLogin (userid, password)
            VALUES (?, ?)
            """,
            (user.user_id, user.password)
        )
        self.cursor.execute(
            """
            INSERT OR IGNORE INTO User (userid, username)
            VALUES (?, ?)
            """,
            (user.user_id, user.username)
        )
        self.connection.commit()

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

    def _ensure_habit_user_column(self) -> None:
        self.cursor.execute("PRAGMA table_info(Habit)")
        columns = {row[1] for row in self.cursor.fetchall()}
        if "user_id" not in columns:
            self.cursor.execute('ALTER TABLE Habit ADD COLUMN "user_id" INTEGER NOT NULL DEFAULT 1')
            self.connection.commit()

    def close(self) -> None:
        self.connection.close()

if __name__ == "__main__":
    db = DBConnector()
    db.create_base_file()
    db.close()

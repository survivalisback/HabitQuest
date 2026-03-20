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
        self.connection = sqlite3.connect(str(settings.database_path), check_same_thread=False)
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.cursor = self.connection.cursor()
        self._ensure_schema()

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

    def get_current_period_completion(self, habit_id: int, frequency: str) -> bool:
        period_start = self._resolve_period_start(frequency)
        self.cursor.execute(
            "SELECT completed FROM HabitCompleted WHERE habitID = ? AND period_start = ?",
            (habit_id, period_start),
        )
        row = self.cursor.fetchone()
        return row is not None and bool(row[0])

    def delete_habit_completions(self, habit_id: int) -> None:
        self.cursor.execute("DELETE FROM HabitCompleted WHERE habitID = ?", (habit_id,))
        self.connection.commit()

    def cleanup_expired_completions(self) -> int:
        """Remove stale completion records (completed=0) for past periods."""
        today = datetime.now().date().isoformat()
        self.cursor.execute(
            "DELETE FROM HabitCompleted WHERE completed = 0 AND period_start < ?",
            (today,),
        )
        deleted = self.cursor.rowcount
        self.connection.commit()
        return deleted

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

    def get_user_id_by_username(self, username: str) -> int | None:
        self.cursor.execute(
            """
            SELECT userid
            FROM User
            WHERE username = ?
            """,
            (username,)
        )
        row = self.cursor.fetchone()
        if row is None:
            return None
        return int(row[0])

    def get_next_user_id(self) -> int:
        self.cursor.execute(
            """
            SELECT COALESCE(MAX(userid), 0) + 1
            FROM User
            """
        )
        row = self.cursor.fetchone()
        return int(row[0]) if row is not None else 1

    def get_user_password_hash(self, user_id: int) -> str | None:
        self.cursor.execute(
            """
            SELECT password
            FROM UserLogin
            WHERE userid = ?
            """,
            (user_id,)
        )
        row = self.cursor.fetchone()
        if row is None:
            return None
        return row[0]

    def set_user_password_hash(self, user_id: int, password_hash: str) -> None:
        self.cursor.execute(
            """
            INSERT INTO UserLogin (userid, password)
            VALUES (?, ?)
            ON CONFLICT(userid) DO UPDATE SET password = excluded.password
            """,
            (user_id, password_hash)
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

    def get_completion_history(self, habit_id: int, limit: int = 60) -> list[dict]:
        self.cursor.execute(
            """
            SELECT period_start, completed_at
            FROM HabitCompleted
            WHERE habitID = ? AND completed = 1
            ORDER BY period_start DESC
            LIMIT ?
            """,
            (habit_id, limit),
        )
        return [
            {"period_start": row[0], "completed_at": row[1]}
            for row in self.cursor.fetchall()
        ]

    def get_all_habit_streaks(self, user_id: int) -> dict[int, dict]:
        self.cursor.execute(
            """
            SELECT h.habit_id, h.frequency, hc.period_start
            FROM Habit h
            JOIN HabitCompleted hc ON hc.habitID = h.habit_id AND hc.completed = 1
            WHERE h.user_id = ?
            ORDER BY h.habit_id, hc.period_start DESC
            """,
            (user_id,),
        )
        from collections import defaultdict
        habit_completions: dict[int, list[dict]] = defaultdict(list)
        habit_freqs: dict[int, str] = {}
        for row in self.cursor.fetchall():
            habit_id_val, freq, period = row
            habit_freqs[habit_id_val] = freq
            habit_completions[habit_id_val].append({"period_start": period})

        return {"completions": habit_completions, "frequencies": habit_freqs}

    def get_user_progress(self, user_id: int) -> dict:
        self.cursor.execute(
            "SELECT total_xp, total_completions FROM UserProgress WHERE user_id = ?",
            (user_id,),
        )
        row = self.cursor.fetchone()
        if row is None:
            return {"total_xp": 0, "total_completions": 0}
        return {"total_xp": row[0], "total_completions": row[1]}

    def update_user_xp(self, user_id: int, xp_delta: int) -> None:
        self.ensure_user_progress(user_id)
        self.cursor.execute(
            "UPDATE UserProgress SET total_xp = MAX(0, total_xp + ?) WHERE user_id = ?",
            (xp_delta, user_id),
        )
        self.connection.commit()

    def increment_completions(self, user_id: int, delta: int) -> None:
        self.ensure_user_progress(user_id)
        self.cursor.execute(
            "UPDATE UserProgress SET total_completions = MAX(0, total_completions + ?) WHERE user_id = ?",
            (delta, user_id),
        )
        self.connection.commit()

    def ensure_user_progress(self, user_id: int) -> None:
        self.cursor.execute(
            "INSERT OR IGNORE INTO UserProgress (user_id, total_xp, total_completions) VALUES (?, 0, 0)",
            (user_id,),
        )
        self.connection.commit()

    def create_base_file(self) -> None:
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS "UserLogin" (
        "userid" INTEGER NOT NULL UNIQUE,
        "password" TEXT NOT NULL,
        PRIMARY KEY("userid")
        );
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
        CREATE TABLE IF NOT EXISTS "Habit" (
        "habit_id" INTEGER NOT NULL UNIQUE,
        "user_id" INTEGER NOT NULL,
        "name" TEXT NOT NULL,
        "description" TEXT,
        "frequency" TEXT NOT NULL,
        "difficulty" INTEGER NOT NULL,
        "xp_reward" INTEGER NOT NULL,
        PRIMARY KEY("habit_id"),
        FOREIGN KEY ("user_id") REFERENCES "User"("userid")
        ON UPDATE NO ACTION ON DELETE CASCADE
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
        ON UPDATE NO ACTION ON DELETE CASCADE
        );
        """)
        self.cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS "idx_habit_completed_unique_period"
        ON HabitCompleted ("habitID", "period_start");
        """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS "UserProgress" (
        "user_id" INTEGER PRIMARY KEY,
        "total_xp" INTEGER NOT NULL DEFAULT 0,
        "total_completions" INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY ("user_id") REFERENCES "User"("userid")
        ON UPDATE NO ACTION ON DELETE CASCADE
        );
        """)
        self.connection.commit()

    def _ensure_schema(self) -> None:
        self._migrate_legacy_habit_table()
        self._migrate_legacy_habit_completed_table()
        self.create_base_file()
        self._ensure_habit_user_column()

    def _table_exists(self, name: str) -> bool:
        self.cursor.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
            (name,)
        )
        return self.cursor.fetchone() is not None

    def _table_columns(self, name: str) -> set[str]:
        self.cursor.execute(f"PRAGMA table_info({name})")
        return {row[1] for row in self.cursor.fetchall()}

    def _migrate_legacy_habit_table(self) -> None:
        if not self._table_exists("Habit"):
            return

        columns = self._table_columns("Habit")
        if "habit_id" in columns:
            return

        if "id" not in columns:
            return

        legacy_name = f'Habit_legacy_{datetime.now().strftime("%Y%m%d%H%M%S")}'
        logger.warning("Legacy Habit schema detected. Migrating to habit_id; backing up to %s.", legacy_name)
        legacy_columns = columns
        try:
            self.cursor.execute(f'ALTER TABLE "Habit" RENAME TO "{legacy_name}"')
        except sqlite3.OperationalError:
            logger.info("Legacy Habit table already migrated by another connection.")
            return
        self.create_base_file()
        user_id_expr = "user_id" if "user_id" in legacy_columns else "1"
        self.cursor.execute(
            f"""
            INSERT INTO Habit (habit_id, user_id, name, description, frequency, difficulty, xp_reward)
            SELECT id, {user_id_expr}, name, description, frequency, difficulty, xp_reward
            FROM "{legacy_name}"
            """
        )
        self.connection.commit()

    def _migrate_legacy_habit_completed_table(self) -> None:
        if not self._table_exists("HabitCompleted"):
            return

        columns = self._table_columns("HabitCompleted")
        expected = {"habit_completed_id", "habitID", "period_start", "completed", "completed_at"}
        if expected.issubset(columns):
            return

        legacy_name = f'HabitCompleted_legacy_{datetime.now().strftime("%Y%m%d%H%M%S")}'
        logger.warning(
            "Legacy HabitCompleted schema detected. Recreating table; backing up to %s.",
            legacy_name,
        )
        try:
            self.cursor.execute(f'ALTER TABLE "HabitCompleted" RENAME TO "{legacy_name}"')
        except sqlite3.OperationalError:
            logger.info("Legacy HabitCompleted table already migrated by another connection.")
            return
        self.create_base_file()

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

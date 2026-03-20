from models.habit import Habit


DEFAULT_DIFFICULTY = 3


class StaticXpProvider:
    def __init__(self):
        pass

    def calculate_difficulty(self, habit: Habit) -> int:
        return DEFAULT_DIFFICULTY

    def calculate_xp(self, habit: Habit) -> int:
        base_xp = habit.difficulty * 10
        frequency_multiplier = {
            "once": 1.0,
            "daily": 1.0,
            "weekly": 1.5,
            "monthly": 2.0,
        }.get(habit.frequency, 1.0)

        return int(base_xp * frequency_multiplier)

    def evaluate_habit(self, habit: Habit) -> dict:
        difficulty = self.calculate_difficulty(habit)
        habit.difficulty = difficulty
        xp = self.calculate_xp(habit)
        return {"difficulty": difficulty, "xp": xp, "reasoning": "Static defaults"}

    def _resolve_habit_xp(self, habit: Habit) -> int:
        stored_xp = getattr(habit, "xp_reward", None)
        if isinstance(stored_xp, (int, float)):
            return int(stored_xp)
        return self.calculate_xp(habit)

    def grant_xp(self, habit: Habit, db_connector, user_id: int) -> int:
        xp = self._resolve_habit_xp(habit)
        db_connector.update_user_xp(user_id, xp)
        db_connector.increment_completions(user_id, 1)
        return xp

    def revoke_xp(self, habit: Habit, db_connector, user_id: int) -> int:
        xp = self._resolve_habit_xp(habit)
        db_connector.update_user_xp(user_id, -xp)
        db_connector.increment_completions(user_id, -1)
        return xp


class DynamicXpProvider:
    def __init__(self, ai_client, static_fallback: StaticXpProvider):
        self.ai_client = ai_client
        self.static_fallback = static_fallback

    def evaluate_habit(self, habit: Habit) -> dict:
        result = self.ai_client.evaluate_habit(
            name=habit.name,
            description=getattr(habit, "description", ""),
            frequency=habit.frequency,
        )
        if result is not None:
            return result
        return self.static_fallback.evaluate_habit(habit)

    def calculate_xp(self, habit: Habit) -> int:
        static_xp = self.static_fallback.calculate_xp(habit)
        result = self.ai_client.evaluate_habit_xp(
            name=habit.name,
            description=getattr(habit, "description", ""),
            frequency=habit.frequency,
            difficulty=habit.difficulty,
            static_xp=static_xp,
        )
        if result is not None:
            return result
        return static_xp

    def _resolve_habit_xp(self, habit: Habit) -> int:
        stored_xp = getattr(habit, "xp_reward", None)
        if isinstance(stored_xp, (int, float)):
            return int(stored_xp)
        return self.calculate_xp(habit)

    def grant_xp(self, habit: Habit, db_connector, user_id: int) -> int:
        xp = self._resolve_habit_xp(habit)
        db_connector.update_user_xp(user_id, xp)
        db_connector.increment_completions(user_id, 1)
        return xp

    def revoke_xp(self, habit: Habit, db_connector, user_id: int) -> int:
        xp = self._resolve_habit_xp(habit)
        db_connector.update_user_xp(user_id, -xp)
        db_connector.increment_completions(user_id, -1)
        return xp

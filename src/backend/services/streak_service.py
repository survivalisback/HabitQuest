from datetime import date, timedelta


STREAK_BONUS_THRESHOLDS = {
    3: 0.10,
    7: 0.25,
    14: 0.50,
    30: 1.00,
}


class StreakService:
    def __init__(self, db_connector):
        self.db = db_connector

    def calculate_streak(self, habit_id: int, frequency: str) -> int:
        completions = self.db.get_completion_history(habit_id, limit=60)
        if not completions:
            return 0

        today = date.today()
        streak = 0

        if frequency == "daily":
            expected = today
            for row in completions:
                period = date.fromisoformat(row["period_start"])
                if period == expected:
                    streak += 1
                    expected -= timedelta(days=1)
                elif period < expected:
                    break
        elif frequency == "weekly":
            current_monday = today - timedelta(days=today.weekday())
            expected = current_monday
            for row in completions:
                period = date.fromisoformat(row["period_start"])
                if period == expected:
                    streak += 1
                    expected -= timedelta(weeks=1)
                elif period < expected:
                    break
        elif frequency == "monthly":
            expected_year = today.year
            expected_month = today.month
            for row in completions:
                period = date.fromisoformat(row["period_start"])
                if period.year == expected_year and period.month == expected_month:
                    streak += 1
                    expected_month -= 1
                    if expected_month < 1:
                        expected_month = 12
                        expected_year -= 1
                elif (period.year < expected_year or
                      (period.year == expected_year and period.month < expected_month)):
                    break
        else:
            return 0

        return streak

    @staticmethod
    def get_streak_bonus_multiplier(streak: int) -> float:
        multiplier = 0.0
        for threshold, mult in sorted(STREAK_BONUS_THRESHOLDS.items()):
            if streak >= threshold:
                multiplier = mult
            else:
                break
        return multiplier

    @staticmethod
    def calculate_streak_bonus_xp(base_xp: int, streak: int) -> int:
        multiplier = StreakService.get_streak_bonus_multiplier(streak)
        return int(base_xp * multiplier)

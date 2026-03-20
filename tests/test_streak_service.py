import pytest
from unittest.mock import MagicMock, patch
from datetime import date, timedelta
from services.streak_service import StreakService


def _make_service(completions):
    db = MagicMock()
    db.get_completion_history.return_value = completions
    return StreakService(db)


def _rows(*dates):
    return [{"period_start": d.isoformat()} for d in dates]


class TestDailyStreak:
    @patch("services.streak_service.date")
    def test_no_completions(self, mock_date):
        mock_date.today.return_value = date(2026, 3, 20)
        mock_date.fromisoformat = date.fromisoformat
        svc = _make_service([])
        assert svc.calculate_streak(1, "daily") == 0

    @patch("services.streak_service.date")
    def test_today_only(self, mock_date):
        mock_date.today.return_value = date(2026, 3, 20)
        mock_date.fromisoformat = date.fromisoformat
        svc = _make_service(_rows(date(2026, 3, 20)))
        assert svc.calculate_streak(1, "daily") == 1

    @patch("services.streak_service.date")
    def test_three_consecutive(self, mock_date):
        mock_date.today.return_value = date(2026, 3, 20)
        mock_date.fromisoformat = date.fromisoformat
        svc = _make_service(_rows(
            date(2026, 3, 20), date(2026, 3, 19), date(2026, 3, 18)
        ))
        assert svc.calculate_streak(1, "daily") == 3

    @patch("services.streak_service.date")
    def test_gap_breaks_streak(self, mock_date):
        mock_date.today.return_value = date(2026, 3, 20)
        mock_date.fromisoformat = date.fromisoformat
        svc = _make_service(_rows(
            date(2026, 3, 20), date(2026, 3, 18)
        ))
        assert svc.calculate_streak(1, "daily") == 1

    @patch("services.streak_service.date")
    def test_missing_today(self, mock_date):
        mock_date.today.return_value = date(2026, 3, 20)
        mock_date.fromisoformat = date.fromisoformat
        svc = _make_service(_rows(date(2026, 3, 19), date(2026, 3, 18)))
        assert svc.calculate_streak(1, "daily") == 0


class TestWeeklyStreak:
    @patch("services.streak_service.date")
    def test_current_week(self, mock_date):
        # 2026-03-20 is a Friday, Monday is 2026-03-16
        mock_date.today.return_value = date(2026, 3, 20)
        mock_date.fromisoformat = date.fromisoformat
        svc = _make_service(_rows(date(2026, 3, 16)))
        assert svc.calculate_streak(1, "weekly") == 1

    @patch("services.streak_service.date")
    def test_two_consecutive_weeks(self, mock_date):
        mock_date.today.return_value = date(2026, 3, 20)
        mock_date.fromisoformat = date.fromisoformat
        svc = _make_service(_rows(date(2026, 3, 16), date(2026, 3, 9)))
        assert svc.calculate_streak(1, "weekly") == 2

    @patch("services.streak_service.date")
    def test_gap_breaks_weekly(self, mock_date):
        mock_date.today.return_value = date(2026, 3, 20)
        mock_date.fromisoformat = date.fromisoformat
        svc = _make_service(_rows(date(2026, 3, 16), date(2026, 3, 2)))
        assert svc.calculate_streak(1, "weekly") == 1


class TestMonthlyStreak:
    @patch("services.streak_service.date")
    def test_current_month(self, mock_date):
        mock_date.today.return_value = date(2026, 3, 20)
        mock_date.fromisoformat = date.fromisoformat
        svc = _make_service(_rows(date(2026, 3, 1)))
        assert svc.calculate_streak(1, "monthly") == 1

    @patch("services.streak_service.date")
    def test_three_consecutive_months(self, mock_date):
        mock_date.today.return_value = date(2026, 3, 20)
        mock_date.fromisoformat = date.fromisoformat
        svc = _make_service(_rows(
            date(2026, 3, 1), date(2026, 2, 1), date(2026, 1, 1)
        ))
        assert svc.calculate_streak(1, "monthly") == 3

    @patch("services.streak_service.date")
    def test_year_boundary(self, mock_date):
        mock_date.today.return_value = date(2026, 1, 15)
        mock_date.fromisoformat = date.fromisoformat
        svc = _make_service(_rows(date(2026, 1, 1), date(2025, 12, 1)))
        assert svc.calculate_streak(1, "monthly") == 2

    @patch("services.streak_service.date")
    def test_gap_breaks_monthly(self, mock_date):
        mock_date.today.return_value = date(2026, 3, 20)
        mock_date.fromisoformat = date.fromisoformat
        svc = _make_service(_rows(date(2026, 3, 1), date(2025, 12, 1)))
        assert svc.calculate_streak(1, "monthly") == 1


class TestUnknownFrequency:
    @patch("services.streak_service.date")
    def test_unknown_returns_zero(self, mock_date):
        mock_date.today.return_value = date(2026, 3, 20)
        mock_date.fromisoformat = date.fromisoformat
        svc = _make_service(_rows(date(2026, 3, 20)))
        assert svc.calculate_streak(1, "once") == 0


class TestGetStreakBonusMultiplier:
    @pytest.mark.parametrize("streak,expected", [
        (0, 0.0),
        (2, 0.0),
        (3, 0.10),
        (6, 0.10),
        (7, 0.25),
        (13, 0.25),
        (14, 0.50),
        (29, 0.50),
        (30, 1.00),
        (100, 1.00),
    ])
    def test_multiplier(self, streak, expected):
        assert StreakService.get_streak_bonus_multiplier(streak) == expected


class TestCalculateStreakBonusXp:
    def test_zero_streak(self):
        assert StreakService.calculate_streak_bonus_xp(30, 0) == 0

    def test_streak_3(self):
        assert StreakService.calculate_streak_bonus_xp(30, 3) == 3

    def test_streak_7(self):
        assert StreakService.calculate_streak_bonus_xp(40, 7) == 10

    def test_zero_base_xp(self):
        assert StreakService.calculate_streak_bonus_xp(0, 30) == 0

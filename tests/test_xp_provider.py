import pytest
from unittest.mock import MagicMock
from models.habit import Habit
from services.xp_provider import StaticXpProvider, DynamicXpProvider, _resolve_habit_xp


def _make_habit(difficulty=3, frequency="daily"):
    h = Habit("Test", "desc", frequency, difficulty, 1)
    return h


class TestStaticXpProviderCalculateXp:
    def setup_method(self):
        self.provider = StaticXpProvider()

    def test_daily_diff3(self):
        assert self.provider.calculate_xp(_make_habit(3, "daily")) == 30

    def test_weekly_diff3(self):
        assert self.provider.calculate_xp(_make_habit(3, "weekly")) == 45

    def test_monthly_diff3(self):
        assert self.provider.calculate_xp(_make_habit(3, "monthly")) == 60

    def test_once_diff3(self):
        assert self.provider.calculate_xp(_make_habit(3, "once")) == 30

    def test_daily_diff1(self):
        assert self.provider.calculate_xp(_make_habit(1, "daily")) == 10

    def test_monthly_diff5(self):
        assert self.provider.calculate_xp(_make_habit(5, "monthly")) == 100

    def test_unknown_frequency_defaults(self):
        assert self.provider.calculate_xp(_make_habit(3, "yearly")) == 30


class TestStaticXpProviderEvaluateHabit:
    def test_evaluate_returns_dict(self):
        provider = StaticXpProvider()
        h = _make_habit()
        result = provider.evaluate_habit(h)
        assert result["difficulty"] == 3
        assert "xp" in result
        assert result["reasoning"] == "Static defaults"


class TestResolveXp:
    def setup_method(self):
        self.provider = StaticXpProvider()

    def test_uses_stored_xp_int(self):
        h = _make_habit(3, "daily")
        h.xp_reward = 99
        assert self.provider.resolve_xp(h) == 99

    def test_uses_stored_xp_float(self):
        h = _make_habit(3, "daily")
        h.xp_reward = 50.0
        assert self.provider.resolve_xp(h) == 50

    def test_falls_back_when_none(self):
        h = _make_habit(3, "daily")
        h.xp_reward = None
        assert self.provider.resolve_xp(h) == 30

    def test_falls_back_when_missing(self):
        h = Habit("Test", "desc", "daily", 3, 1)
        if hasattr(h, "xp_reward"):
            delattr(h, "xp_reward")
        # getattr returns None for missing attr → calculate
        assert self.provider.resolve_xp(h) == 30


class TestDynamicXpProvider:
    def test_ai_returns_result(self):
        ai = MagicMock()
        ai.evaluate_habit.return_value = {"difficulty": 4, "xp": 55, "reasoning": "AI says"}
        provider = DynamicXpProvider(ai, StaticXpProvider())
        h = _make_habit()
        result = provider.evaluate_habit(h)
        assert result["difficulty"] == 4
        assert result["xp"] == 55

    def test_ai_returns_none_falls_back(self):
        ai = MagicMock()
        ai.evaluate_habit.return_value = None
        provider = DynamicXpProvider(ai, StaticXpProvider())
        h = _make_habit()
        result = provider.evaluate_habit(h)
        assert result["difficulty"] == 3
        assert result["reasoning"] == "Static defaults"

    def test_resolve_xp_uses_stored(self):
        ai = MagicMock()
        provider = DynamicXpProvider(ai, StaticXpProvider())
        h = _make_habit(3, "daily")
        h.xp_reward = 77
        assert provider.resolve_xp(h) == 77
        ai.evaluate_habit_xp.assert_not_called()

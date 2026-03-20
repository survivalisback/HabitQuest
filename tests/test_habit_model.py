import pytest
from models.habit import Habit


class TestCheckDuplicate:
    def test_exact_duplicate(self):
        a = Habit("Run", "Go running", "daily", 3, 1)
        b = Habit("Run", "Go running", "daily", 3, 1)
        assert a.check_duplicate(b) is True

    def test_different_name(self):
        a = Habit("Run", "Go running", "daily", 3, 1)
        b = Habit("Walk", "Go running", "daily", 3, 1)
        assert a.check_duplicate(b) is False

    def test_different_description(self):
        a = Habit("Run", "Go running", "daily", 3, 1)
        b = Habit("Run", "Go walking", "daily", 3, 1)
        assert a.check_duplicate(b) is False

    def test_different_frequency(self):
        a = Habit("Run", "Go running", "daily", 3, 1)
        b = Habit("Run", "Go running", "weekly", 3, 1)
        assert a.check_duplicate(b) is False

    def test_different_difficulty_still_duplicate(self):
        a = Habit("Run", "Go running", "daily", 3, 1)
        b = Habit("Run", "Go running", "daily", 5, 1)
        assert a.check_duplicate(b) is True

    def test_different_user_id_still_duplicate(self):
        a = Habit("Run", "Go running", "daily", 3, 1)
        b = Habit("Run", "Go running", "daily", 3, 99)
        assert a.check_duplicate(b) is True


class TestIsValid:
    def test_valid_habit(self):
        h = Habit("Run", "Go running", "daily", 3, 1)
        assert h.is_valid() is True

    def test_none_difficulty_is_valid(self):
        h = Habit("Run", "Go running", "daily", None, 1)
        assert h.is_valid() is True

    def test_empty_name(self):
        h = Habit("", "Go running", "daily", 3, 1)
        assert h.is_valid() is False

    def test_none_name(self):
        h = Habit(None, "Go running", "daily", 3, 1)
        assert h.is_valid() is False

    def test_empty_frequency(self):
        h = Habit("Run", "Go running", "", 3, 1)
        assert h.is_valid() is False

    def test_none_frequency(self):
        h = Habit("Run", "Go running", None, 3, 1)
        assert h.is_valid() is False

    def test_difficulty_zero(self):
        h = Habit("Run", "Go running", "daily", 0, 1)
        assert h.is_valid() is False

    def test_difficulty_six(self):
        h = Habit("Run", "Go running", "daily", 6, 1)
        assert h.is_valid() is False

    def test_difficulty_negative(self):
        h = Habit("Run", "Go running", "daily", -1, 1)
        assert h.is_valid() is False

    def test_difficulty_1_boundary(self):
        h = Habit("Run", "Go running", "daily", 1, 1)
        assert h.is_valid() is True

    def test_difficulty_5_boundary(self):
        h = Habit("Run", "Go running", "daily", 5, 1)
        assert h.is_valid() is True

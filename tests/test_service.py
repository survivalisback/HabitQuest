import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from services.service import Service
from services.auth import JwtConfig, generate_jwt, verify_jwt


def _mock_settings():
    s = MagicMock()
    s.jwt_secret = "test-secret"
    s.jwt_issuer = "test-issuer"
    s.jwt_expires_in_seconds = 3600
    return s


def _make_service(streak_service=None):
    with patch("services.service.settings", _mock_settings()):
        svc = Service(
            habit_repository=MagicMock(),
            user_repository=MagicMock(),
            xp_provider=MagicMock(),
            streak_service=streak_service,
        )
    return svc


class TestRegisterUser:
    def test_success(self):
        svc = _make_service()
        svc.user_repository.get_user_id_by_username.return_value = None
        svc.user_repository.get_next_user_id.return_value = 42
        result = svc.register_user("alice", "pass123")
        assert result["user_id"] == 42
        assert result["username"] == "alice"
        assert "token" in result
        svc.user_repository.create_user.assert_called_once()

    def test_empty_username(self):
        svc = _make_service()
        with pytest.raises(ValueError, match="Username"):
            svc.register_user("", "pass")

    def test_whitespace_username(self):
        svc = _make_service()
        with pytest.raises(ValueError, match="Username"):
            svc.register_user("   ", "pass")

    def test_no_password(self):
        svc = _make_service()
        with pytest.raises(ValueError, match="Password"):
            svc.register_user("alice", "")

    def test_duplicate_username(self):
        svc = _make_service()
        svc.user_repository.get_user_id_by_username.return_value = 1
        with pytest.raises(ValueError, match="already exists"):
            svc.register_user("alice", "pass")

    def test_strips_whitespace(self):
        svc = _make_service()
        svc.user_repository.get_user_id_by_username.return_value = None
        svc.user_repository.get_next_user_id.return_value = 1
        result = svc.register_user("  alice  ", "pass")
        assert result["username"] == "alice"


class TestLoginUser:
    def test_success(self):
        svc = _make_service()
        svc.user_repository.get_user_id_by_username.return_value = 5
        from services.auth import hash_password
        svc.user_repository.get_password_hash.return_value = hash_password("pass")
        result = svc.login_user("alice", "pass")
        assert result["user_id"] == 5
        assert "token" in result

    def test_unknown_user(self):
        svc = _make_service()
        svc.user_repository.get_user_id_by_username.return_value = None
        with pytest.raises(ValueError, match="Invalid"):
            svc.login_user("ghost", "pass")

    def test_wrong_password(self):
        svc = _make_service()
        svc.user_repository.get_user_id_by_username.return_value = 5
        from services.auth import hash_password
        svc.user_repository.get_password_hash.return_value = hash_password("correct")
        with pytest.raises(ValueError, match="Invalid"):
            svc.login_user("alice", "wrong")

    def test_empty_credentials(self):
        svc = _make_service()
        with pytest.raises(ValueError):
            svc.login_user("", "")


class TestGetUserIdFromToken:
    def test_valid_token(self):
        svc = _make_service()
        token = generate_jwt(7, svc.jwt_config)
        assert svc.get_user_id_from_token(token) == 7

    def test_bearer_prefix(self):
        svc = _make_service()
        token = generate_jwt(7, svc.jwt_config)
        assert svc.get_user_id_from_token(f"Bearer {token}") == 7

    def test_invalid_token(self):
        svc = _make_service()
        with pytest.raises(ValueError, match="Invalid"):
            svc.get_user_id_from_token("bad-token")

    def test_empty_token(self):
        svc = _make_service()
        with pytest.raises(ValueError, match="Invalid"):
            svc.get_user_id_from_token("")


class TestCreateHabit:
    def test_creates_habit(self):
        svc = _make_service()
        svc.xp_provider.evaluate_habit.return_value = {"difficulty": 3, "xp": 30, "reasoning": "ok"}
        svc.create_habit(1, "Run", "Go running", "daily")
        svc.habit_repository.create_habit.assert_called_once()

    def test_rejects_once_frequency(self):
        svc = _make_service()
        with pytest.raises(ValueError, match="(?i)one-time"):
            svc.create_habit(1, "Run", "Go running", "once")


class TestToggleHabitCompletion:
    def test_completing_awards_xp(self):
        svc = _make_service()
        svc.habit_repository.toggle_habit_completion.return_value = True
        habit = MagicMock()
        habit.frequency = "daily"
        svc.habit_repository.get_habit_by_id.return_value = habit
        svc.xp_provider.resolve_xp.return_value = 30
        svc.user_repository.get_progress.return_value = {"total_xp": 30, "total_completions": 1}
        result = svc.toggle_habit_completion(1, 10)
        assert result["completed"] is True
        assert result["xp_reward"] == 30
        svc.user_repository.update_xp.assert_called_with(1, 30)
        svc.user_repository.increment_completions.assert_called_with(1, 1)

    def test_uncompleting_reverts_xp(self):
        svc = _make_service()
        svc.habit_repository.toggle_habit_completion.return_value = False
        habit = MagicMock()
        habit.frequency = "daily"
        svc.habit_repository.get_habit_by_id.return_value = habit
        svc.xp_provider.resolve_xp.return_value = 30
        svc.user_repository.get_progress.return_value = {"total_xp": 0, "total_completions": 0}
        result = svc.toggle_habit_completion(1, 10)
        assert result["completed"] is False
        svc.user_repository.update_xp.assert_called_with(1, -30)
        svc.user_repository.increment_completions.assert_called_with(1, -1)

    def test_with_streak_bonus(self):
        streak_svc = MagicMock()
        streak_svc.calculate_streak.return_value = 7
        streak_svc.calculate_streak_bonus_xp.return_value = 10
        svc = _make_service(streak_service=streak_svc)
        svc.habit_repository.toggle_habit_completion.return_value = True
        habit = MagicMock()
        habit.frequency = "daily"
        svc.habit_repository.get_habit_by_id.return_value = habit
        svc.xp_provider.resolve_xp.return_value = 40
        svc.user_repository.get_progress.return_value = {"total_xp": 50, "total_completions": 1}
        result = svc.toggle_habit_completion(1, 10)
        assert result["streak"] == 7
        assert result["streak_bonus_xp"] == 10
        # update_xp called twice: once for base, once for bonus
        calls = svc.user_repository.update_xp.call_args_list
        assert calls[0].args == (1, 40)
        assert calls[1].args == (1, 10)

    def test_without_streak_service(self):
        svc = _make_service(streak_service=None)
        svc.habit_repository.toggle_habit_completion.return_value = True
        habit = MagicMock()
        habit.frequency = "daily"
        svc.habit_repository.get_habit_by_id.return_value = habit
        svc.xp_provider.resolve_xp.return_value = 30
        svc.user_repository.get_progress.return_value = {"total_xp": 30, "total_completions": 1}
        result = svc.toggle_habit_completion(1, 10)
        assert result["streak"] == 0
        assert result["streak_bonus_xp"] == 0


class TestDeleteHabit:
    def test_completed_habit_reverts_xp(self):
        svc = _make_service()
        habit = MagicMock()
        habit.frequency = "daily"
        svc.habit_repository.get_habit_by_id.return_value = habit
        svc.habit_repository.get_current_period_completion.return_value = True
        svc.xp_provider.resolve_xp.return_value = 30
        svc.delete_habit(1, 10)
        svc.user_repository.update_xp.assert_called_with(1, -30)
        svc.user_repository.increment_completions.assert_called_with(1, -1)

    def test_not_completed_no_xp_change(self):
        svc = _make_service()
        habit = MagicMock()
        habit.frequency = "daily"
        svc.habit_repository.get_habit_by_id.return_value = habit
        svc.habit_repository.get_current_period_completion.return_value = False
        svc.delete_habit(1, 10)
        svc.user_repository.update_xp.assert_not_called()

    def test_always_deletes(self):
        svc = _make_service()
        svc.habit_repository.get_habit_by_id.return_value = None
        svc.delete_habit(1, 10)
        svc.habit_repository.delete_completions.assert_called_with(10)
        svc.habit_repository.delete_habit.assert_called_with(10, 1)


class TestTrackOneTime:
    def test_awards_xp(self):
        svc = _make_service()
        svc.xp_provider.evaluate_habit.return_value = {"difficulty": 3, "xp": 30, "reasoning": "ok"}
        svc.user_repository.get_progress.return_value = {"total_xp": 30, "total_completions": 1}
        result = svc.track_one_time(1, "Clean desk", "Tidy up")
        assert result["name"] == "Clean desk"
        assert result["xp_reward"] == 30
        assert "level_info" in result
        svc.user_repository.update_xp.assert_called_with(1, 30)
        svc.user_repository.increment_completions.assert_called_with(1, 1)


class TestGetProfile:
    def test_returns_structure(self):
        svc = _make_service()
        svc.user_repository.get_progress.return_value = {"total_xp": 150, "total_completions": 5}
        result = svc.get_profile(1)
        assert result["total_xp"] == 150
        assert result["total_completions"] == 5
        assert "level_info" in result


class TestGetHabitStreaks:
    def test_returns_streaks(self):
        streak_svc = MagicMock()
        streak_svc.calculate_streak.return_value = 3
        svc = _make_service(streak_service=streak_svc)
        svc.habit_repository.get_all_streaks.return_value = {
            "completions": {10: True, 20: True},
            "frequencies": {10: "daily", 20: "weekly"},
        }
        result = svc.get_habit_streaks(1)
        assert result[10] == 3
        assert result[20] == 3

    def test_no_streak_service(self):
        svc = _make_service(streak_service=None)
        assert svc.get_habit_streaks(1) == {}

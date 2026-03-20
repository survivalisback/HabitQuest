import os

os.environ["ANTHROPIC_API_KEY"] = "test-key"

import pytest
from models.habit import Habit
from services.auth import JwtConfig


@pytest.fixture
def sample_habit():
    h = Habit("Push-ups", "Do 20 push-ups", "daily", 3, 1)
    h.xp_reward = 30
    return h


@pytest.fixture
def weekly_habit():
    h = Habit("Grocery shopping", "Buy groceries", "weekly", 3, 1)
    h.xp_reward = 45
    return h


@pytest.fixture
def monthly_habit():
    h = Habit("Budget review", "Review monthly budget", "monthly", 3, 1)
    h.xp_reward = 60
    return h


@pytest.fixture
def jwt_config():
    return JwtConfig(secret="test-secret", issuer="test-issuer", expires_in_seconds=3600)

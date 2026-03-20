from math import ceil
from models.level import get_level_info, _resolve_title


def _xp_for_level(target_level: int) -> int:
    """Calculate total XP needed to reach exact start of target_level."""
    total = 0
    needed = 100
    for _ in range(1, target_level):
        total += needed
        needed = ceil((needed * 1.25) / 100) * 100
    return total


# --- get_level_info ---

class TestGetLevelInfo:
    def test_zero_xp(self):
        info = get_level_info(0)
        assert info["level"] == 1
        assert info["xp_in_level"] == 0
        assert info["xp_needed"] == 100
        assert info["title"] == "Beginner"

    def test_mid_level_1(self):
        info = get_level_info(50)
        assert info["level"] == 1
        assert info["xp_in_level"] == 50

    def test_just_below_level_up(self):
        info = get_level_info(99)
        assert info["level"] == 1
        assert info["xp_in_level"] == 99

    def test_exact_level_2(self):
        info = get_level_info(100)
        assert info["level"] == 2
        assert info["xp_in_level"] == 0
        assert info["xp_needed"] == 200

    def test_exact_level_3(self):
        info = get_level_info(300)
        assert info["level"] == 3
        assert info["xp_in_level"] == 0
        assert info["title"] == "Apprentice"

    def test_level_5_specialist(self):
        xp = _xp_for_level(5)
        info = get_level_info(xp)
        assert info["level"] == 5
        assert info["title"] == "Specialist"

    def test_level_10_master(self):
        xp = _xp_for_level(10)
        info = get_level_info(xp)
        assert info["level"] == 10
        assert info["title"] == "Master"

    def test_large_xp(self):
        info = get_level_info(100000)
        assert info["level"] > 10
        assert set(info.keys()) == {"level", "title", "xp_in_level", "xp_needed", "total_xp"}

    def test_total_xp_echoed(self):
        info = get_level_info(42)
        assert info["total_xp"] == 42

    def test_return_keys(self):
        info = get_level_info(0)
        assert set(info.keys()) == {"level", "title", "xp_in_level", "xp_needed", "total_xp"}


# --- _resolve_title ---

class TestResolveTitle:
    def test_level_1(self):
        assert _resolve_title(1) == "Beginner"

    def test_level_2(self):
        assert _resolve_title(2) == "Beginner"

    def test_level_3(self):
        assert _resolve_title(3) == "Apprentice"

    def test_level_5(self):
        assert _resolve_title(5) == "Specialist"

    def test_level_7(self):
        assert _resolve_title(7) == "Expert"

    def test_level_10(self):
        assert _resolve_title(10) == "Master"

    def test_level_12(self):
        assert _resolve_title(12) == "Master"

    def test_level_15(self):
        assert _resolve_title(15) == "Grandmaster"

    def test_level_20(self):
        assert _resolve_title(20) == "Legend"

    def test_level_30(self):
        assert _resolve_title(30) == "Mythic"

    def test_level_99(self):
        assert _resolve_title(99) == "Mythic"

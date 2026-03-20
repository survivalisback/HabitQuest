from math import ceil


MILESTONE_TITLES = {
    1: "Beginner",
    3: "Apprentice",
    5: "Specialist",
    7: "Expert",
    10: "Master",
    15: "Grandmaster",
    20: "Legend",
    30: "Mythic",
}

# Base XP required for level 1 -> 2
_BASE_XP = 100


def get_level_info(total_xp: int) -> dict:
    """Reconstruct level from total XP by iterating the 1.25x formula from level 0."""
    level = 1
    xp_consumed = 0
    needed = _BASE_XP

    while total_xp >= xp_consumed + needed:
        xp_consumed += needed
        level += 1
        needed = ceil((needed * 1.25) / 100) * 100

    xp_in_level = total_xp - xp_consumed
    title = _resolve_title(level)

    return {
        "level": level,
        "title": title,
        "xp_in_level": xp_in_level,
        "xp_needed": needed,
        "total_xp": total_xp,
    }


def _resolve_title(level: int) -> str:
    """Return the title of the highest milestone <= current level."""
    best = "Beginner"
    for milestone, title in sorted(MILESTONE_TITLES.items()):
        if milestone <= level:
            best = title
        else:
            break
    return best


class Level:
    def __init__(self):
        self.level = 0
        self.xp = 0
        self.current_level = 0
        self.needed_xp = 0

    def add_xp(self, xp: int):
        self.xp += xp
        self.update_level()

    def remove_xp(self, xp: int):
        self.xp = max(0, self.xp - xp)

    def update_level(self):
        if self.xp >= self.needed_xp:
            # TODO: Check for double level up
            self.level += 1
            self.needed_xp = ceil((self.needed_xp * 1.25) / 100) * 100  # Round to next 100

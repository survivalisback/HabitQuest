from repository.habitRepository import HabitRepository

# Business/Gamification Logic
class Service:
    habit_repository: HabitRepository

    def __init__(self):
        self.habit_repository = HabitRepository()
# HabitQuest

A gamified habit tracking application that combines daily habit management with RPG-style progression mechanics. Built with FastAPI and vanilla JavaScript.

## Features

- **Habit Tracking** — Create and manage habits with daily, weekly, monthly, or one-time frequencies
- **XP & Leveling** — Earn experience points for completing habits and level up through 13 milestone titles (Beginner to Mythic)
- **Streaks** — Build streaks for consistent habit completion with bonus XP multipliers (up to 100% at 30-day streaks)
- **AI-Powered XP** — Optionally use Claude AI to dynamically evaluate habit difficulty and assign XP rewards
- **User Profiles** — View total XP, completions, current level, and title

## Tech Stack

| Layer    | Technology                          |
|----------|-------------------------------------|
| Backend  | Python 3.13+, FastAPI, Uvicorn      |
| Frontend | HTML, CSS, vanilla JavaScript        |
| Database | SQLite                               |
| Auth     | JWT (python-jose), bcrypt            |
| AI       | Anthropic Claude API (optional)      |
| Package Manager | uv                           |

## Project Structure

```
HabitQuest/
├── src/
│   ├── backend/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── config.py            # Settings & environment config
│   │   ├── dependencies.py      # Dependency injection
│   │   ├── api/                 # Route handlers
│   │   ├── models/              # Domain models (Habit, User, Level)
│   │   ├── repository/          # Database access layer
│   │   └── services/            # Business logic & auth
│   └── frontend/
│       ├── index.html
│       ├── app.js
│       └── style.css
├── db/                          # SQLite database
├── tests/                       # Pytest test suite
├── docs/                        # Project documentation
└── uml/                         # UML diagrams
```

## Getting Started

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager

### Installation

```bash
git clone <repository-url>
cd HabitQuest
uv sync
```

### Configuration

Create or edit `src/backend/.env`:

```env
AI_XP_ENABLED=false
ANTHROPIC_API_KEY=your-api-key-here
```

Set `AI_XP_ENABLED=true` and provide a valid API key to enable AI-powered XP evaluation.

### Running

Start the backend server:

```bash
cd src/backend
python -m uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`. Open `src/frontend/index.html` in a browser to use the application.

## API Endpoints

| Method | Endpoint                | Description                     |
|--------|-------------------------|---------------------------------|
| POST   | `/register`             | Register a new user             |
| POST   | `/login`                | Login and receive JWT token     |
| GET    | `/habits`               | List user habits with streaks   |
| POST   | `/createTask`           | Create a new habit              |
| PUT    | `/editTask`             | Edit an existing habit          |
| DELETE | `/deleteTask`           | Delete a habit                  |
| POST   | `/toggleTaskCompletion` | Toggle completion for a period  |
| POST   | `/trackOneTime`         | Track a one-time accomplishment |
| GET    | `/profile`              | Get user XP, level, and title   |
| POST   | `/ai/preview-xp`       | Preview AI-calculated XP        |

## Testing

```bash
pytest
```

Tests cover authentication, habit models, level progression, business logic, streaks, and XP calculation.

## Gamification Details

### XP Calculation

- **Static mode:** `difficulty × 10 × frequency_multiplier` (daily 1x, weekly 1.5x, monthly 2x)
- **Dynamic mode (AI):** Claude evaluates the habit description and assigns XP based on realistic difficulty

### Streak Bonuses

| Streak | Bonus |
|--------|-------|
| 3      | +10%  |
| 7      | +25%  |
| 14     | +50%  |
| 30     | +100% |

### Level Progression

Levels use exponential scaling (1.25x per level, base 100 XP). Each level milestone unlocks a new title, from **Beginner** through **Legend** to **Mythic**.

## Contributing & Commit History

A significant portion of this project was developed through pair programming sessions. As a result, the git commit history does not always accurately reflect individual contributions — commits may have been authored by one person while the code was written collaboratively.
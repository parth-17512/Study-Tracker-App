# StudyTrack

**Build a Better You**

StudyTrack is a personal desktop application for tracking study time, managing goals, and visualizing study history. Built with a focus on reliability, offline-first data, and an architecture ready for future ML/AI integrations.

## Features

- Study Stopwatch and Countdown Timer
- Goal tracking (Daily, Weekly, Monthly)
- Study Streaks
- GitHub-style Activity Heatmap
- Analytics and historical sessions
- Configurable settings

## Setup and Installation

### Requirements

- Python 3.12+
- PySide6
- SQLAlchemy

### Development Setup

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Run the application: `python main.py`

## Architecture

StudyTrack uses a clean layered architecture separating the UI from business logic and database persistence:

```
UI -> Services -> Repositories -> Database (SQLite)
```

For full details on architecture, database schema, and future ML/AI roadmap, refer to the `docs/PROJECT_SPEC.md` and `docs/AGENT_INSTRUCTIONS.md`.

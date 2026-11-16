# StudyTrack

### Turn study intentions into consistent progress.

StudyTrack is a desktop study and productivity companion for people who want to build better learning habits. It brings focused study sessions, personal notes, a full-day time map, progress analytics, and optional AI assistance together in one place—so learners can spend less effort piecing together their routine and more time making meaningful progress.

> **The idea behind the project:** studying is not just about counting hours. It is about building consistency, understanding how you use your time, and making your next study session easier to start.

## Who StudyTrack is for

- **Students** preparing for exams, managing coursework, or trying to make a regular study routine stick.
- **Self-directed learners** exploring new topics and keeping their learning resources organized.
- **Professionals** tracking time spent on upskilling and reviewing their progress over time.
- **Anyone building a focus habit** who wants a private, practical way to understand where their time goes.

## Why use StudyTrack?

Many productivity tools record a timer or store notes, but leave learners to connect the dots themselves. StudyTrack connects the everyday parts of a learning routine: plan and time a session, capture useful notes, review the day, and use your own history to decide what to improve next.

It is designed to make progress visible without turning learning into a competition. Your sessions and notes stay on your computer by default, while optional hosted AI features are controlled through Settings.

## What you can do

### Focus and record study sessions

- Run a stopwatch or a countdown timer for focused work.
- Pause and resume a session, then save it with a topic and optional notes.
- Recover an active timer after closing and reopening the app.
- Review, search, edit, and manage saved study sessions.

### Map your whole day

- Use the **Time Stamp** view to see a selected day as a complete 24-hour timeline.
- See completed study sessions alongside manually entered rest and other activities.
- Add, edit, or remove non-study activities and notes.
- Review time spent studying, resting, on other activities, and time still uncategorized.
- Identify gaps in the day. Unallocated time means it has not been categorized; it does not necessarily mean you were inactive.

### Organize learning notes

- Keep notes and folders in a hierarchical library.
- Write and preview Markdown, with automatic saving as you edit.
- Search notes, mark favorites, and revisit recent materials.
- Optionally use AI to polish and format a note before applying the suggested changes.

### Understand your progress

- Review study totals, session history, average session length, and time by subject.
- Compare recent study periods and inspect trends across days and weeks.
- Explore daily activity in the calendar and study heatmap.
- Track daily goal progress and study streaks. A day qualifies toward a streak when completed study time reaches at least half the configured daily goal.
- Earn XP for completed focus sessions and see your level progress.

### Take your data with you

- Export session records as CSV or JSON.
- Export a feature-engineered CSV dataset for your own machine-learning experiments.

## AI and machine-learning features

AI and ML are designed as practical extensions of your study history—not as claims that the app predicts outcomes or replaces your judgment.

### AI Study Coach

- Ask questions about your study activity and learning routine.
- The coach can use selected, read-only app tools to retrieve study statistics, streaks, subject breakdowns, and note content.
- Note retrieval uses **retrieval-augmented generation (RAG)**: notes are split into chunks, indexed in a local ChromaDB collection, and relevant passages can be retrieved to ground a response.
- Chat history is stored locally so you can return to earlier conversations.
- Generate AI-written study insights from analytics data, and optionally format notes with AI.
- Configure Gemini or a hosted API that supports the OpenAI-compatible chat-completions format. Choose provider priority and fallback behavior in Settings.

### ML-ready study dataset

StudyTrack includes a data-preparation pipeline that exports completed sessions with useful temporal and historical features, including:

- Target session duration
- Local start hour, day of week, and weekend indicator
- Study time and session count in the preceding seven days
- Approximate streak at the start of each session

Rolling-context features are calculated from sessions strictly before the session being described, making the export a useful starting point for personal analysis and model experiments. The app prepares and exports the dataset; model training and predictions are left to your chosen ML workflow.

## Privacy and AI controls

- StudyTrack stores its SQLite database, settings, chat history, and local note index on your computer.
- The app does not require an account or cloud sync for its core timer, notes, timeline, and analytics features.
- Hosted AI providers are optional. Cloud context must be explicitly enabled in Settings before the app uses configured hosted providers.
- When enabled, relevant prompts and context may be sent to the provider you configured. Review that provider's privacy policy, data handling, pricing, and usage limits before use.
- If hosted AI is not configured or permitted, core local features remain available.

## Technology

- **Python 3.12+**
- **PySide6** desktop interface
- **SQLite and SQLAlchemy** for local persistence
- **ChromaDB** for local semantic note retrieval
- **Gemini and OpenAI-compatible APIs** for optional hosted AI
- **pytest** for automated tests
- **PyInstaller** for Windows executable packaging

## Get started

### Requirements

- Python 3.12 or newer
- Windows is the primary packaged target. Building the standalone `.exe` requires Windows.

### Run from source

```powershell
git clone https://github.com/parth-17512/Study-Tracker-App.git
cd Study-Tracker-App
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

AI is optional. To use hosted AI features, open **Settings → AI Study Coach & LLM Providers**, configure a provider, and explicitly enable cloud context consent. Compatible hosted APIs must support the OpenAI-compatible `POST /chat/completions` format.

### Run tests

```powershell
pytest
```

### Build the Windows executable

```powershell
python build.py
```

The build script creates a single-file executable at `dist/StudyTrack.exe` and an onedir build at `dist/StudyTrack/StudyTrack.exe`. The local note index uses ChromaDB's default ONNX embedding backend; its initialization is deferred until the note-index service is needed.

## Data location

On Windows, StudyTrack keeps persistent application data under:

```text
%APPDATA%\StudyTrack\
```

This includes the SQLite database and local application data, separate from the temporary files used by a packaged executable.

## Project structure

```text
app/
  ai/          Coach agent, tools, and provider integrations
  database/    SQLite models, database setup, and migrations
  ml/          Feature extraction and dataset export
  services/    Study, notes, timeline, analytics, and data services
  timer/       Timer engine and recoverable timer state
  ui/          PySide6 pages, components, and widgets
tests/         Automated test suite
ml_experiments/ ML dataset notes and experiment starting point
```

## Project objective

StudyTrack was created to make focused learning easier to sustain and easier to understand. By bringing time tracking, daily planning, note-taking, analytics, and optional AI into one private-first desktop app, it helps learners turn small, repeatable study sessions into a routine—and gives them the context to keep improving that routine.

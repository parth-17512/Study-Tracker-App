# StudyTrack — Coding Agent Instructions

## Role

You are the primary coding agent responsible for building **StudyTrack**, a polished desktop study-tracking application.

You must treat `PROJECT_SPEC.md` as the product specification and this file as the engineering execution contract.

The goal is not merely to make a demo. Build a reliable, maintainable, portfolio-quality application that can later support analytics, machine learning, and AI-agent capabilities.

---

# 1. Read Before Coding

Before changing or creating code:

1. Read `PROJECT_SPEC.md` completely.
2. Read this `AGENT_INSTRUCTIONS.md` completely.
3. Inspect the existing repository structure.
4. Inspect all existing source code before modifying it.
5. Inspect `reference/UI_REFERENCE.png` if it exists.
6. Check the current Git status and existing commits.
7. Determine which project phase is currently complete.
8. Implement only the next incomplete phase unless the user explicitly asks for a different scope.

Do not assume the repository is empty or that previous code is disposable.

---

# 2. Product Identity

Application name:

**StudyTrack**

Tagline:

**Build a Better You**

StudyTrack is a desktop application for recording, analyzing, and improving study habits.

The core product should help a student:

- Start study sessions.
- Track exact study duration.
- Use stopwatch and countdown timers.
- Set daily/weekly/monthly goals.
- Track streaks.
- Visualize study activity with a GitHub-style heatmap.
- Analyze study behavior.
- Search and review previous sessions.
- Export study data.
- Eventually use machine learning and AI agents for personalized insights.

The application should feel like a real modern productivity product, not a classroom prototype.

---

# 3. Technology Stack

Use the following stack unless there is a strong technical reason not to.

## Core

- Python 3.12+
- PySide6
- SQLite
- Python's built-in `sqlite3` where appropriate
- SQLAlchemy
- Pydantic where useful

## Visualization

Use one of:

- PyQtGraph
- Matplotlib

Prefer PyQtGraph when interactive desktop charts are useful.

## Testing

- pytest

## Packaging

- PyInstaller

## Development

- Git
- GitHub
- VS Code compatible project structure

Do not introduce unnecessary frameworks or services.

The application should work locally and offline for its core functionality.

---

# 4. Architecture Rules

Use a layered architecture:

```text
UI
 ↓
Services
 ↓
Repositories
 ↓
Database
```

Timer infrastructure should remain separated:

```text
UI
 ↓
Timer Service
 ↓
Timer Engine
```

Analytics should consume service/repository interfaces rather than directly manipulating UI state.

Future ML and AI components must also consume clean service interfaces rather than accessing the database directly.

Suggested structure:

```text
StudyTrack/
│
├── app/
│   ├── ui/
│   │   ├── windows/
│   │   ├── pages/
│   │   ├── widgets/
│   │   └── components/
│   │
│   ├── services/
│   │   ├── timer_service.py
│   │   ├── session_service.py
│   │   ├── goal_service.py
│   │   ├── streak_service.py
│   │   ├── analytics_service.py
│   │   └── notification_service.py
│   │
│   ├── models/
│   │   ├── study_session.py
│   │   ├── subject.py
│   │   ├── goal.py
│   │   └── setting.py
│   │
│   ├── repositories/
│   │   ├── session_repository.py
│   │   ├── subject_repository.py
│   │   ├── goal_repository.py
│   │   └── settings_repository.py
│   │
│   ├── database/
│   │   ├── database.py
│   │   ├── models.py
│   │   └── migrations/
│   │
│   ├── timer/
│   │   ├── timer_engine.py
│   │   └── timer_state.py
│   │
│   ├── analytics/
│   │   ├── daily.py
│   │   ├── weekly.py
│   │   ├── monthly.py
│   │   ├── subjects.py
│   │   └── streaks.py
│   │
│   ├── notifications/
│   │   └── notification_manager.py
│   │
│   ├── ml/
│   │   └── __init__.py
│   │
│   ├── agents/
│   │   └── __init__.py
│   │
│   └── config/
│       └── settings.py
│
├── tests/
├── data/
├── scripts/
├── reference/
│   └── UI_REFERENCE.png
├── docs/
├── main.py
├── pyproject.toml
├── requirements.txt
├── README.md
└── .gitignore
```

The exact structure may evolve, but architectural responsibilities must remain clear.

---

# 5. Core Engineering Principles

Follow these principles throughout the project.

## 5.1 Reliability First

Correctness is more important than speed of implementation.

A timer that visually looks correct but records incorrect durations is unacceptable.

A dashboard that looks beautiful but shows incorrect statistics is unacceptable.

A database operation that can silently lose data is unacceptable.

---

## 5.2 Single Source of Truth

Do not duplicate important derived data unnecessarily.

For example:

- Total study time should be derived from study sessions.
- Daily goal progress should be derived from sessions.
- Streaks should be derived from session history.
- Heatmap values should be derived from study sessions.

Avoid storing redundant totals unless there is a documented performance reason.

---

## 5.3 Separation of Responsibilities

UI code should not contain business logic.

Repositories should not contain UI code.

The timer engine should not directly manipulate database records.

Analytics should not manipulate widgets.

The database layer should not know about PySide6.

---

## 5.4 Small, Testable Components

Prefer small functions and classes with clear responsibilities.

Avoid huge files containing unrelated logic.

Avoid "god classes".

---

## 5.5 No Silent Failures

Never use:

```python
except:
    pass
```

Do not silently swallow errors.

Unexpected errors should be logged.

User-facing errors should provide useful information.

---

## 5.6 Preserve Existing Functionality

Before changing existing code:

- Understand it.
- Identify dependencies.
- Avoid unnecessary rewrites.
- Preserve working behavior.
- Run tests before and after significant changes.

Do not replace working architecture simply because you prefer another style.

---

# 6. UI / UX Requirements

The UI should follow the visual language of the provided reference image.

The reference is a visual inspiration, not a requirement to copy crypto/finance-specific concepts.

Use:

- Modern dark dashboard
- Deep navy/black background
- Purple/violet primary accent
- Blue secondary accent
- Green success states
- Orange/yellow warning states
- Light text
- Muted secondary text
- Rounded cards
- Thin borders
- Subtle shadows
- Subtle gradients where appropriate
- Modern typography
- Clean icons
- Good spacing
- Strong visual hierarchy

Target resolution:

- Minimum: 1280×720
- Preferred: 1440×900

The UI should remain usable at smaller reasonable desktop sizes.

Avoid:

- Excessive visual clutter
- Giant unnecessary text
- Inconsistent spacing
- Random colors
- Excessive animations
- Unnecessary gradients
- Poor contrast
- UI elements that look like placeholders

Use reusable components for cards, buttons, inputs, charts, navigation, dialogs, etc.

---

# 7. Main Dashboard

The dashboard should eventually contain:

## Top Metrics

Four major metric cards:

1. Today's Study
2. Current Streak
3. Total Study Time
4. Weekly Goal

## Main Sections

- Study Timer
- Today's Sessions
- Study Goals

## Lower Sections

- Study Activity
- Subject Distribution
- Quick Stats
- Recent Sessions

The dashboard should present meaningful information at a glance.

---

# 8. Timer Requirements

The timer is one of the most important components.

Support:

- Stopwatch mode
- Countdown mode

Controls should include appropriate combinations of:

- Start
- Pause
- Resume
- Stop
- Cancel
- Reset

Quick presets:

- 25 minutes
- 50 minutes
- 1 hour
- 2 hours
- Custom duration

---

# 9. Timer State Machine

Use explicit timer states:

```text
IDLE
RUNNING
PAUSED
COMPLETED
CANCELLED
```

Define valid transitions.

Do not allow arbitrary state mutations.

Example:

```text
IDLE → RUNNING
RUNNING → PAUSED
PAUSED → RUNNING
RUNNING → COMPLETED
RUNNING → CANCELLED
PAUSED → CANCELLED
COMPLETED → IDLE
CANCELLED → IDLE
```

The exact implementation can evolve, but state transitions must be deterministic and tested.

---

# 10. Critical Timer Implementation Rule

Do NOT implement countdown timing by simply decrementing an integer every second.

Bad approach:

```python
remaining -= 1
```

This becomes inaccurate because:

- UI updates can be delayed.
- The operating system can sleep.
- The application can freeze.
- The machine can experience load.
- The window can be minimized.
- The process can be interrupted.

Instead, use timestamps.

For example:

```text
start_time
target_end_time
current_time
```

Then calculate:

```text
remaining = target_end_time - current_time
```

For stopwatch mode:

```text
elapsed = current_time - start_time
```

The UI timer should be a display mechanism, not the authoritative source of elapsed time.

---

# 11. Timer Persistence

The application should be able to recover from an application restart.

Persist enough state to determine whether an active timer exists.

When the application starts:

- Detect an active timer.
- Determine whether it should still be running.
- If appropriate, allow the user to resume it.
- Allow the user to discard it.
- Do not silently create duplicate sessions.

Test scenarios involving:

- Restarting the application.
- System sleep.
- Long UI delays.
- Pausing.
- Resuming.
- Countdown completion.
- Cancellation.
- Reset.
- Clock changes where practical.

---

# 12. Study Session Model

A study session should support fields such as:

```text
id
start_time
end_time
duration_seconds
subject_id
topic
notes
session_type
status
created_at
updated_at
```

Session types:

```text
stopwatch
countdown
```

Statuses:

```text
completed
cancelled
interrupted
```

Do not count cancelled or invalid sessions as completed study time unless the product specification explicitly defines otherwise.

---

# 13. Subjects

Support subjects such as:

- Machine Learning
- Python
- Deep Learning
- DSA
- System Design
- Generative AI

Users should be able to manage subjects.

Subject statistics should eventually include:

- Total study time
- Session count
- Average session duration
- Last studied date

---

# 14. Goals

Support:

- Daily goals
- Weekly goals
- Monthly goals

Initial example defaults:

```text
Daily: 6 hours
Weekly: 35 hours
Monthly: 150 hours
```

These are defaults, not hardcoded limitations.

Goal progress must be derived from actual study sessions.

Do not maintain independent progress counters that can become inconsistent with the session database.

---

# 15. Streaks

Default streak threshold:

```text
30 minutes per day
```

A day qualifies when the total valid completed study time reaches the configured threshold.

Multiple sessions on the same day must be combined.

Track:

- Current streak
- Longest streak
- Total study days

Do not count future dates as completed study days.

The streak threshold should eventually be configurable.

---

# 16. GitHub-Style Activity Heatmap

Implement a yearly study activity heatmap.

Each day should have an activity level based on study duration.

Suggested levels:

```text
0 minutes
1–30 minutes
31–60 minutes
61–180 minutes
180+ minutes
```

Requirements:

- Year selector
- Hover tooltip
- Daily study duration
- Click-to-day details where practical
- Visually similar to GitHub's contribution heatmap
- Do not copy GitHub branding

Heatmap data must come from study sessions.

---

# 17. Calendar

Implement a monthly calendar view.

Show:

- Study activity
- Goal indicators
- Study duration
- Relevant session information

Selecting a date should allow the user to inspect that day's study details.

---

# 18. Analytics

Support:

- Daily analytics
- Weekly analytics
- Monthly analytics
- Subject analytics

Useful metrics include:

- Total study time
- Session count
- Average session duration
- Goal completion
- Most productive day
- Subject distribution
- Study consistency
- Recent trends

Charts must use real application data.

Never create fake values merely to make the dashboard look complete.

---

# 19. Search and Filtering

Eventually support search across:

- Sessions
- Subjects
- Topics
- Notes

Suggested shortcut:

```text
Ctrl + K
```

Filtering should be responsive and predictable.

---

# 20. Notifications and Alarm

Countdown completion should trigger an appropriate alarm/notification.

Support configurable:

- Notifications
- Alarm sound
- Timer behavior

The exact implementation can evolve based on platform limitations.

---

# 21. Settings

Eventually include settings for:

- Default timer mode
- Default timer duration
- Streak threshold
- Notifications
- Alarm
- Theme
- Data export
- Data import
- Data clearing
- Other relevant application preferences

Destructive operations must require confirmation.

---

# 22. Database

Use SQLite for the initial application.

Use SQLAlchemy to provide a maintainable database abstraction.

Core tables:

```text
subjects
study_sessions
goals
settings
```

Potential future tables may be added as the product evolves.

Use:

- Foreign keys
- Appropriate indexes
- Transactions
- Constraints
- Sensible timestamps
- Clear naming

Database schema changes should have a migration/future-schema strategy.

Do not casually modify schemas in ways that destroy existing user data.

---

# 23. Data Export

The user should eventually be able to export study data.

Support:

- CSV
- JSON

Exported data should be clean enough to later load into pandas.

This is important because the future ML layer will rely on real historical study data.

---

# 24. Testing

Use pytest.

Write tests for:

- Timer state transitions
- Stopwatch duration
- Countdown duration
- Pause/resume
- Cancellation
- Session creation
- Session completion
- Goal calculation
- Streak calculation
- Heatmap aggregation
- Analytics
- Edge cases
- Database operations

Whenever a bug is discovered:

1. Identify the root cause.
2. Fix the underlying issue.
3. Add a regression test.
4. Run the relevant test.
5. Run the full test suite.

Do not simply patch the visible symptom.

---

# 25. Logging

Implement useful application logging.

Log important events such as:

- Application startup
- Database initialization
- Timer start
- Timer pause
- Timer resume
- Timer completion
- Timer cancellation
- Session save
- Session cancellation
- Database errors
- Unexpected application errors

Do not log sensitive information unnecessarily.

---

# 26. Error Handling

Use explicit error handling.

Errors should be:

- Logged.
- Understandable to developers.
- Appropriately communicated to users.

Do not hide unexpected failures.

Avoid broad exception handling unless there is a specific reason.

---

# 27. Performance

Keep the application responsive.

Avoid:

- Blocking the UI thread with long operations.
- Recalculating expensive analytics unnecessarily.
- Loading huge datasets into the UI when unnecessary.
- Unnecessary database queries.

If a task becomes expensive, consider:

- Caching
- Background workers
- Query optimization
- Incremental calculation

Do not prematurely optimize simple code.

---

# 28. Security and Data Safety

The application is primarily local-first.

Nevertheless:

- Validate user inputs.
- Avoid unsafe SQL construction.
- Use parameterized queries/ORM operations.
- Do not hardcode secrets.
- Do not commit API keys.
- Keep `.env` files out of Git where applicable.
- Confirm destructive database actions.

---

# 29. Documentation

Keep documentation synchronized with implementation.

Relevant documentation may include:

```text
docs/
├── PROJECT_SPEC.md
├── ARCHITECTURE.md
├── DATABASE.md
├── UI_DESIGN.md
└── ROADMAP.md
```

If architecture or database decisions change materially, update the corresponding documentation.

Do not allow documentation to describe features that do not actually exist.

---

# 30. Git Discipline

Use logical Git commits.

Prefer commits such as:

```text
feat: implement timer engine
feat: add study session persistence
feat: add daily goals
fix: correct streak calculation
test: add timer edge-case coverage
refactor: separate analytics service
docs: update database architecture
```

Do not create meaningless commits for every tiny edit.

Do not commit:

- Secrets
- API keys
- Local virtual environments
- Build artifacts
- Temporary files
- User database files unless explicitly intended

---

# 31. Development Phases

Build the project incrementally in this order.

## Phase 0 — Project Planning and Setup

Establish:

- Repository
- Python environment
- Dependencies
- Project structure
- Git
- Documentation
- Configuration
- Basic startup

Acceptance:

- Project starts.
- Structure is clean.
- Dependencies are reproducible.
- Documentation exists.

---

## Phase 1 — Application Foundation

Implement:

- PySide6 application shell
- Main window
- Navigation
- Theme
- Base layout
- Reusable UI components
- Initial dashboard shell

Acceptance:

- Application launches reliably.
- Navigation works.
- UI establishes the StudyTrack visual identity.

---

## Phase 2 — Timer Engine

Implement:

- Timer state machine
- Stopwatch
- Countdown
- Pause/resume
- Cancellation
- Reset
- Timestamp-based timing
- Timer persistence/recovery foundation

Acceptance:

- Timer behavior is deterministic.
- Timing remains correct despite UI delays and system sleep where testable.
- Tests exist.

---

## Phase 3 — Study Sessions

Implement:

- Study session model
- Database persistence
- Session repository
- Session service
- Subject association
- Session history

Acceptance:

- Completed sessions are stored correctly.
- Invalid/cancelled sessions are handled correctly.
- Restart does not corrupt data.

---

## Phase 4 — Goals

Implement:

- Daily goals
- Weekly goals
- Monthly goals
- Progress calculations
- Goal UI

Acceptance:

- Goal progress is derived from actual sessions.
- Multiple sessions aggregate correctly.

---

## Phase 5 — Streaks

Implement:

- Current streak
- Longest streak
- Total study days
- Configurable threshold foundation

Acceptance:

- Streak calculations work across multiple sessions and date boundaries.
- Future dates are excluded.

---

## Phase 6 — Activity Heatmap

Implement:

- Yearly heatmap
- Activity levels
- Tooltips
- Year selection
- Daily detail interaction where practical

Acceptance:

- Heatmap values match actual study sessions.

---

## Phase 7 — Calendar

Implement:

- Monthly calendar
- Study indicators
- Goal indicators
- Date details

---

## Phase 8 — Analytics

Implement:

- Daily
- Weekly
- Monthly
- Subject analytics
- Charts
- Summary statistics

---

## Phase 9 — Search and Filtering

Implement:

- Session search
- Subject filtering
- Topic search
- Notes search
- Ctrl+K interface

---

## Phase 10 — Notifications and Alarm

Implement:

- Countdown completion notification
- Alarm
- Configuration

---

## Phase 11 — Settings and Data Management

Implement:

- Preferences
- Theme settings
- Timer defaults
- Streak threshold
- Export/import
- Data clearing with confirmation

---

## Phase 12 — Reliability and Testing

Strengthen:

- Unit tests
- Integration tests
- Error handling
- Logging
- Edge cases
- Database reliability
- Timer reliability

Do not consider the application production-ready until this phase is substantially complete.

---

## Phase 13 — Packaging

Implement:

- PyInstaller build
- Windows executable
- Clean distribution structure
- Startup testing

Acceptance:

- A user can run the packaged application without installing the development environment.

---

# 32. Future Machine Learning Foundation

Do not rush into ML.

The application must first collect reliable real-world data.

Eventually support ML tasks such as:

- Productivity prediction
- Study duration prediction
- Goal completion prediction
- Productive-time analysis
- Consistency analysis

Potential features:

```text
hour_of_day
day_of_week
subject
recent_study_time
recent_session_count
current_streak
goal_progress
average_session_duration
study_days_recently
```

Do not train fake models using fabricated data simply to demonstrate ML.

Use actual accumulated user data when enough data exists.

The ML layer should be isolated from the core application.

---

# 33. Future AI Agent Foundation

Eventually create a Study Coach agent.

Potential tools:

```text
get_today_stats
get_week_stats
get_month_stats
get_subject_stats
get_goal_progress
get_streak
get_recent_sessions
```

Future capabilities:

- Natural-language study questions
- Personalized study plans
- Progress explanations
- Trend explanations
- Study recommendations
- Goal assistance

The agent must interact through service/tool interfaces.

Do NOT allow the agent to directly manipulate the database.

---

# 34. Core Product Progression

Follow this product progression:

```text
Reliable Timer
      ↓
Reliable Study Data
      ↓
Analytics
      ↓
Machine Learning
      ↓
AI Agents
```

Do not reverse this order.

The quality of future ML/AI depends on the quality of the underlying study data.

---

# 35. Phase Execution Protocol

For every phase:

## Step 1 — Understand

Read the relevant part of `PROJECT_SPEC.md`.

Inspect the existing implementation.

Determine dependencies and possible side effects.

## Step 2 — Plan

Before writing significant code, determine:

- Files to create
- Files to modify
- Database changes
- UI changes
- Tests required
- Potential edge cases

Keep the plan proportional to the phase.

## Step 3 — Implement

Implement only the current phase.

Do not start future features unless they are required for the current phase's architecture.

## Step 4 — Test

Run:

- Relevant unit tests
- Integration tests where applicable
- Full test suite

Fix failures before considering the phase complete.

## Step 5 — Run the Application

Launch the application and verify the actual UI and behavior.

Do not rely only on static code inspection.

## Step 6 — Verify Acceptance Criteria

Compare implementation against the acceptance criteria in `PROJECT_SPEC.md`.

Do not mark a phase complete merely because the code compiles.

## Step 7 — Fix

Fix:

- Bugs
- UI issues
- Database issues
- Incorrect calculations
- Edge cases
- Regressions

## Step 8 — Update Documentation

Update relevant docs when necessary.

## Step 9 — Git Commit

Create a logical Git commit after the phase is stable.

## Step 10 — Report

Provide a concise phase completion report.

---

# 36. Phase Completion Report

After each phase, report:

```text
PHASE: <number and name>

STATUS:
Complete / Blocked

IMPLEMENTED:
- ...

FILES CREATED:
- ...

FILES MODIFIED:
- ...

DATABASE:
- ...

UI:
- ...

TESTS:
- ...

VALIDATION:
- Application launched: Yes/No
- Relevant tests passed: Yes/No
- Full test suite passed: Yes/No

KNOWN ISSUES:
- ...

GIT COMMIT:
- ...

NEXT PHASE:
- ...
```

Do not claim something passed unless it was actually tested.

---

# 37. Scope Control

Do not introduce scope creep.

If the current phase is:

```text
Phase 2 — Timer Engine
```

do not suddenly implement:

- ML
- AI agent
- Advanced analytics
- Cloud synchronization
- Authentication
- Mobile application
- Unrequested integrations

unless the current phase explicitly requires the architectural foundation for them.

---

# 38. Product Decisions

You may make reasonable engineering decisions about:

- Class names
- Function names
- File organization
- Internal implementation details
- Small UI details
- Test organization

For major product decisions that change requirements, stop and ask for approval rather than silently changing the specification.

Examples:

- Removing a core feature
- Changing the meaning of a streak
- Changing goal calculation
- Changing session semantics
- Adding cloud synchronization
- Introducing an external paid service

---

# 39. Bug-Fixing Protocol

When a bug occurs:

1. Reproduce it.
2. Identify the root cause.
3. Explain the cause internally.
4. Fix the underlying implementation.
5. Add a regression test.
6. Run the relevant tests.
7. Run the full suite.
8. Re-test the application.

Never repeatedly patch symptoms without understanding the underlying cause.

---

# 40. Quality Standard

The final application should be:

- Reliable
- Maintainable
- Testable
- Visually polished
- Responsive
- Local-first
- Data-safe
- Modular
- Well documented
- Suitable for a portfolio
- Architected for future ML/AI expansion

The goal is to build something that can be shown as a serious software engineering + AI/ML portfolio project.

---

# 41. Important Constraints

Never:

- Skip reading the specification.
- Implement every phase at once.
- Destroy existing working code unnecessarily.
- Use fake analytics data in the finished product.
- Store redundant derived values without reason.
- Use a naive decrementing timer as the authoritative clock.
- Put business logic directly into UI widgets.
- Let future AI agents directly manipulate the database.
- Ignore failing tests.
- Hide exceptions with `except: pass`.
- Commit secrets.
- Claim success without validation.

Always:

- Inspect before modifying.
- Work phase by phase.
- Test continuously.
- Preserve data.
- Keep architecture clean.
- Keep documentation synchronized.
- Verify the actual application.
- Add regression tests for bugs.
- Prefer correctness over speed.

---

# 42. Starting Instruction

When this instruction file is first provided to you, begin with the following workflow:

1. Locate `PROJECT_SPEC.md`.
2. Read it completely.
3. Read `AGENT_INSTRUCTIONS.md`.
4. Inspect the repository.
5. Inspect `reference/UI_REFERENCE.png` if available.
6. Inspect Git status/history.
7. Determine the current implementation state.
8. Identify the next incomplete phase.
9. Implement ONLY that phase.
10. Run the relevant tests.
11. Run the full test suite.
12. Launch and inspect the application.
13. Fix any issues found.
14. Update documentation if required.
15. Create a logical Git commit.
16. Produce the phase completion report.
17. Stop and wait before starting the next phase unless the user explicitly instructs you to continue.

The most important rule is:

> **Build StudyTrack incrementally, one verified phase at a time. Do not sacrifice reliability, architecture, or data correctness for speed.**

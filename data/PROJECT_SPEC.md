# StudyTrack --- Project Specification

**Version:** 1.0\
**Project type:** Personal desktop productivity application\
**Primary platform:** Windows\
**Primary goal:** Reliable study-time tracking with a polished dashboard
and a clean foundation for future ML and AI-agent features.

------------------------------------------------------------------------

# 1. Product Overview

StudyTrack is a personal desktop application for tracking study time.

The application should combine:

-   Study stopwatch
-   Countdown timer
-   Session recording
-   Daily/weekly/monthly goals
-   Streak tracking
-   GitHub-style study activity heatmap
-   Study history
-   Calendar
-   Subject tracking
-   Analytics
-   Desktop notifications
-   Alarm
-   Data export

The application must work offline for all core features.

The architecture must leave clear extension points for future:

-   Machine Learning
-   Generative AI
-   AI agents
-   Personalized recommendations
-   Productivity prediction
-   Study planning

The first version must not depend on AI or ML.

------------------------------------------------------------------------

# 2. Product Principles

The project should follow these principles:

1.  Reliability before complexity.
2.  Accurate study-time calculation.
3.  Local-first data storage.
4.  Clean separation of concerns.
5.  Reusable UI components.
6.  Testable business logic.
7.  Easy future extension.
8.  No unnecessary dependencies.
9.  No telemetry.
10. No cloud dependency for core functionality.

------------------------------------------------------------------------

# 3. Technology Stack

Use:

  Component         Technology
  ----------------- --------------------------------------------------
  Language          Python 3.12+
  Desktop UI        PySide6
  Database          SQLite
  Database ORM      SQLAlchemy
  Validation        Pydantic where useful
  Charts            PyQtGraph or suitable PySide6-compatible library
  Testing           pytest
  Packaging         PyInstaller
  Version control   Git

Do not use React, Node.js, Docker, a web server, or a cloud database for
the core desktop application.

Python's built-in SQLite support should be used through SQLAlchemy.

------------------------------------------------------------------------

# 4. UI / UX Design Direction

A provided UI reference image is the primary visual inspiration.

The visual style should be:

-   Premium
-   Modern
-   Dark
-   Minimal
-   Data-rich
-   Professional
-   Focused

The reference uses a modern dark analytics dashboard. Recreate its
visual language for StudyTrack.

Do not copy cryptocurrency concepts, labels, assets, or business logic
from the reference.

## Visual characteristics

Use:

-   Dark navy/black background
-   Purple/violet primary accent
-   Blue secondary accent
-   Green success indicators
-   Orange/yellow warning indicators
-   White primary text
-   Muted gray secondary text
-   Rounded cards
-   Thin borders
-   Subtle shadows
-   Subtle gradients
-   Clean typography
-   Modern icons
-   Consistent spacing
-   Progress bars
-   Circular progress indicators
-   Charts
-   Heatmaps
-   Tables

Avoid:

-   Excessive glow
-   Excessive animations
-   Clutter
-   Tiny unreadable text
-   Unnecessary decorative elements

Minimum supported window size:

**1280 × 720**

The layout should adapt gracefully to larger screens.

------------------------------------------------------------------------

# 5. Application Branding

Application name:

**StudyTrack**

Subtitle:

**Build a Better You**

Suggested icon concept:

-   Open book
-   Study timer
-   Small progress indicator

The icon should be simple and modern.

------------------------------------------------------------------------

# 6. Application Navigation

Use a persistent left sidebar.

Navigation:

-   Dashboard
-   Timer
-   Sessions
-   Goals
-   Analytics
-   Calendar
-   Subjects
-   Settings

The active navigation item should have a clear highlighted state.

Use a single main application window with stacked pages/views.

------------------------------------------------------------------------

# 7. Top Bar

The top bar should contain:

-   Search
-   Keyboard shortcut indicator
-   Theme toggle
-   Notifications
-   Profile/settings area

Search shortcut:

**Ctrl + K**

The top bar should remain visually consistent across main pages.

------------------------------------------------------------------------

# 8. Dashboard

The Dashboard is the primary screen.

Heading:

**Dashboard**

Subtitle:

**"Discipline today, a better tomorrow."**

Display the current date.

## Top metric cards

Create four metric cards.

### Card 1 --- Today's Study

Example:

**4h 20m**

**of 6h goal**

Progress:

**72%**

Use a horizontal progress bar.

### Card 2 --- Current Streak

Example:

**12 days**

Secondary:

**Longest: 27 days**

Use a flame icon.

### Card 3 --- Total Study Time

Example:

**245h 30m**

Secondary:

**Across 89 study days**

### Card 4 --- Weekly Goal

Example:

**28h / 35h**

Progress:

**80%**

All values must be dynamically calculated.

Never hard-code example values into production logic.

------------------------------------------------------------------------

# 9. Dashboard Main Layout

Below the metric cards, use three major cards.

## Left --- Study Timer

Large timer interface.

## Center --- Today's Sessions

List today's sessions.

## Right --- Study Goals

Daily/weekly/monthly goal progress.

Below these:

-   Study Activity
-   Subject Distribution
-   Quick Stats

Finally:

-   Recent Sessions table

------------------------------------------------------------------------

# 10. Timer

The timer must support two modes.

## Stopwatch

Starts from:

`00:00:00`

Controls:

-   Start
-   Pause
-   Resume
-   Stop
-   Reset

The stopwatch measures an open-ended study session.

## Countdown

User chooses:

-   Hours
-   Minutes
-   Seconds

Example:

`01:00:00`

Controls:

-   Start
-   Pause
-   Resume
-   Cancel

When the timer reaches zero:

1.  Play alarm.
2.  Show desktop notification.
3.  Mark session completed.
4.  Save session.
5.  Update dashboard.
6.  Update goal progress.
7.  Update streak.
8.  Update heatmap.
9.  Update analytics.

------------------------------------------------------------------------

# 11. Timer Accuracy

This is a critical requirement.

Do not implement countdown by simply subtracting one second repeatedly.

Instead store timestamps.

For a countdown:

-   start_time
-   target_end_time

Calculate:

`remaining_time = target_end_time - current_time`

This prevents timer drift.

The timer must remain accurate if:

-   UI rendering is delayed
-   the application temporarily freezes
-   the computer is under load

------------------------------------------------------------------------

# 12. Timer State Machine

Use explicit timer states:

-   IDLE
-   RUNNING
-   PAUSED
-   COMPLETED
-   CANCELLED

Valid transitions:

`IDLE -> RUNNING`

`RUNNING -> PAUSED`

`PAUSED -> RUNNING`

`RUNNING -> COMPLETED`

`RUNNING -> CANCELLED`

`PAUSED -> CANCELLED`

Prevent invalid state transitions.

The timer engine should be independent of the UI.

------------------------------------------------------------------------

# 13. Timer Persistence and Recovery

If the application closes while a timer is active:

1.  Persist enough information to restore it.
2.  On application startup detect an unfinished timer.
3.  Show:

**"Resume previous session?"**

Options:

-   Resume
-   Discard

Do not silently lose study time.

Handle:

-   Application crash
-   Normal close
-   Computer sleep
-   Application restart

------------------------------------------------------------------------

# 14. Quick Timer Presets

Provide:

-   25 min
-   50 min
-   1 hour
-   2 hours

Also provide:

**Custom Duration**

The default countdown should be 25 minutes.

------------------------------------------------------------------------

# 15. Session Recording

Every study session should be represented by a database record.

Fields:

-   id
-   start_time
-   end_time
-   duration_seconds
-   subject_id
-   topic
-   notes
-   session_type
-   status
-   created_at
-   updated_at

Session types:

-   stopwatch
-   countdown

Statuses:

-   completed
-   cancelled
-   interrupted

Store duration internally in seconds.

Display duration as:

-   `HH:MM:SS`
-   or human-readable format such as `1h 25m`

------------------------------------------------------------------------

# 16. Session Creation

Before starting a session, optionally allow:

-   Subject
-   Topic
-   Notes

Example:

Subject:

Machine Learning

Topic:

Logistic Regression

Notes:

Andrew Ng Week 3

These fields should be optional.

The user must be able to start a timer without filling them in.

------------------------------------------------------------------------

# 17. Session Completion

When a session completes:

1.  Calculate actual duration.
2.  Validate timestamps.
3.  Save the session atomically.
4.  Trigger alarm.
5.  Trigger notification.
6.  Recalculate daily total.
7.  Recalculate goals.
8.  Recalculate streak.
9.  Refresh dashboard.
10. Refresh heatmap.
11. Refresh analytics.

Avoid duplicate completion records.

------------------------------------------------------------------------

# 18. Today's Sessions

Dashboard should show today's sessions.

Example:

``` text
Machine Learning
09:00 AM - 10:30 AM
1h 30m

Python
11:00 AM - 12:00 PM
1h

Deep Learning
02:15 PM - 03:45 PM
1h 30m

System Design
04:00 PM - 04:50 PM
50m
```

Buttons:

-   Start New Session
-   View All

Use compact cards/list rows.

------------------------------------------------------------------------

# 19. Goals

Support:

-   Daily goals
-   Weekly goals
-   Monthly goals

Default values:

Daily:

**6 hours**

Weekly:

**35 hours**

Monthly:

**150 hours**

These values must be configurable.

------------------------------------------------------------------------

# 20. Goal Calculation

Goal progress must be calculated from actual study sessions.

Example:

Daily goal:

`6h`

Sessions:

`2h + 1h + 1h 30m`

Total:

`4h 30m`

Progress:

`75%`

Do not manually increment a separate total that can become inconsistent
with the database.

------------------------------------------------------------------------

# 21. Goal UI

Create goal cards.

Daily:

``` text
4h 20m / 6h
72%
```

Weekly:

``` text
28h / 35h
80%
```

Monthly:

``` text
84h / 150h
56%
```

Use:

-   Circular progress
-   Horizontal progress
-   Percentage
-   Remaining time

Provide:

**Manage Goals**

Goal management should support:

-   Create
-   Edit
-   Delete
-   Activate/deactivate

------------------------------------------------------------------------

# 22. Streak System

Track:

-   Current streak
-   Longest streak
-   Total study days

Default minimum daily study time:

**30 minutes**

A day counts as a study day if:

`total study duration >= minimum daily threshold`

Example:

-   Monday: 1h → study day
-   Tuesday: 2h → study day
-   Wednesday: 10m → not a study day
-   Thursday: 1h → study day

Multiple sessions on the same date should be combined.

Do not count future dates.

Use consistent local calendar-day boundaries.

------------------------------------------------------------------------

# 23. GitHub-Style Study Activity Heatmap

Create a GitHub-contribution-style activity grid.

Each cell represents one calendar day.

Color intensity represents total study duration.

Default levels:

  Study Time    Level
  ------------- -------
  0 min         0
  1--30 min     1
  31--60 min    2
  61--180 min   3
  180+ min      4

Show:

-   Days of week
-   Months
-   Year selector

Example:

`2026`

Allow previous years where data exists.

------------------------------------------------------------------------

# 24. Heatmap Interaction

Hovering over a day should show:

``` text
September 16, 2026

Study:
4h 20m

Sessions:
3
```

Clicking a day should open that day's study information.

Display:

-   Total study time
-   Number of sessions
-   Subjects
-   Individual sessions
-   Goal progress

Heatmap data must come from the database.

------------------------------------------------------------------------

# 25. Calendar

Create a monthly calendar view.

Each day should indicate:

-   Study completed
-   No study
-   Goal completed
-   Goal incomplete

Clicking a date should show:

-   Total study time
-   Sessions
-   Goal progress
-   Subjects studied
-   Session details

Allow month/year navigation.

------------------------------------------------------------------------

# 26. Sessions Page

Create a full session history.

Columns:

-   Date
-   Start
-   End
-   Duration
-   Subject
-   Topic
-   Type
-   Status

Features:

-   Search
-   Filter
-   Sort
-   Edit
-   Delete

Filters:

-   Date
-   Subject
-   Topic
-   Session type
-   Status

Sorting:

-   Date
-   Duration
-   Subject

Deleting should require confirmation.

------------------------------------------------------------------------

# 27. Subjects

Create a Subjects page.

Allow creating and managing subjects.

Example:

-   Machine Learning
-   Python
-   Deep Learning
-   Data Structures
-   System Design
-   Generative AI

For each subject show:

-   Total study time
-   Number of sessions
-   Average session duration
-   Last studied date

Allow subject-specific analytics.

Subjects should be stored in their own table.

------------------------------------------------------------------------

# 28. Analytics

Create an Analytics page.

Sections:

-   Daily
-   Weekly
-   Monthly
-   Subjects

## Daily analytics

Show:

-   Total study time
-   Number of sessions
-   Average session duration
-   Goal completion percentage

## Weekly analytics

Show:

-   Total study time
-   Average daily study time
-   Study days
-   Goal completion

Create a 7-day bar/line chart.

## Monthly analytics

Show:

-   Total study time
-   Total sessions
-   Average daily study
-   Longest session
-   Study days
-   Goal completion

## Subject analytics

Create a donut/pie chart showing study distribution.

Example:

``` text
Machine Learning 42%
Python           25%
Deep Learning    18%
System Design    10%
Other             5%
```

These values must be calculated dynamically.

------------------------------------------------------------------------

# 29. Quick Stats

Dashboard should show:

-   Average Session
-   Most Productive Day
-   Goal Completion
-   Total Sessions

Example:

``` text
Average Session
1h 12m

Most Productive Day
Wednesday
5h 40m

Goal Completion
4 / 7 days

Total Sessions
18
```

All values must be calculated from real data.

------------------------------------------------------------------------

# 30. Search

The top search bar should search across:

-   Sessions
-   Subjects
-   Topics
-   Notes

Example:

Searching:

`Logistic Regression`

should find relevant sessions through:

-   Subject
-   Topic
-   Notes

Keyboard shortcut:

**Ctrl + K**

Use debouncing where useful.

------------------------------------------------------------------------

# 31. Notifications

Implement desktop notifications.

When the timer finishes:

Title:

**Study session completed**

Message:

**1 hour of study recorded.**

Allow:

-   Notifications ON/OFF
-   Alarm ON/OFF
-   Alarm sound
-   Custom alarm sound if practical

Keep notification logic isolated in NotificationService.

------------------------------------------------------------------------

# 32. Settings

Settings should contain:

## General

-   Default countdown duration
-   Minimum daily study duration
-   Auto-save session
-   Confirm before cancelling

## Notifications

-   Enable notifications

## Alarm

-   Enable alarm
-   Alarm sound
-   Volume if supported

## Appearance

-   Dark mode
-   Light mode

Default:

**Dark mode**

## Data

-   Database location
-   Export data
-   Import/restore data
-   Clear all data

Destructive actions require confirmation.

------------------------------------------------------------------------

# 33. Data Export

Support:

-   CSV
-   JSON

Export study history.

Exported data must be easy to load with:

-   pandas
-   Jupyter Notebook
-   scikit-learn

The export format should contain useful fields such as:

-   Date
-   Start time
-   End time
-   Duration
-   Subject
-   Topic
-   Notes
-   Session type
-   Status

------------------------------------------------------------------------

# 34. Database

Use:

**SQLite + SQLAlchemy**

Recommended tables:

## subjects

-   id
-   name
-   description
-   created_at
-   updated_at
-   is_active

## study_sessions

-   id
-   start_time
-   end_time
-   duration_seconds
-   subject_id
-   topic
-   notes
-   session_type
-   status
-   created_at
-   updated_at

## goals

-   id
-   goal_type
-   target_seconds
-   start_date
-   end_date
-   is_active
-   created_at
-   updated_at

## settings

-   key
-   value
-   updated_at

Optional future tables:

-   daily_statistics
-   session_tags
-   tags
-   ai_recommendations
-   ml_predictions
-   agent_tasks

Do not add future tables unless they are actually needed.

------------------------------------------------------------------------

# 35. Database Rules

Use database transactions for important operations.

Use foreign keys.

Use indexes for frequently queried fields such as:

-   start_time
-   subject_id
-   status

Avoid duplicated derived values unless there is a clear performance
reason.

Use migrations or a migration-friendly schema strategy so future
database changes do not require deleting user data.

------------------------------------------------------------------------

# 36. Project Architecture

Use a layered architecture.

Recommended structure:

``` text
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
│
├── data/
│
├── scripts/
│
├── reference/
│   └── UI_REFERENCE.png
│
├── docs/
│
├── main.py
├── pyproject.toml
├── requirements.txt
├── README.md
└── .gitignore
```

------------------------------------------------------------------------

# 37. Separation of Concerns

The UI must not contain database logic.

The UI must not directly execute SQL.

The UI should not contain complex business calculations.

The timer should not directly manipulate database tables.

Use:

``` text
UI
 ↓
Services
 ↓
Repositories
 ↓
Database
```

Example:

``` text
Dashboard
 ↓
AnalyticsService
 ↓
SessionRepository
 ↓
SQLite
```

Timer:

``` text
Timer UI
 ↓
TimerService
 ↓
SessionService
 ↓
SessionRepository
 ↓
SQLite
```

------------------------------------------------------------------------

# 38. Reusable UI Components

Create reusable components such as:

-   MetricCard
-   ProgressCard
-   TimerWidget
-   SessionCard
-   GoalCard
-   ActivityHeatmap
-   StatCard
-   ChartCard
-   DataTable
-   NavigationSidebar
-   TopBar
-   Dialog
-   Toast/Notification

Avoid duplicating UI code.

------------------------------------------------------------------------

# 39. Error Handling

Never silently ignore exceptions.

Do not use:

``` python
try:
    ...
except:
    pass
```

Instead:

-   Catch expected exceptions.
-   Log unexpected exceptions.
-   Show useful user-facing messages.
-   Protect database integrity.
-   Never silently lose study sessions.

------------------------------------------------------------------------

# 40. Logging

Implement application logging.

Log important events:

-   Application startup
-   Database initialization
-   Timer start
-   Timer pause
-   Timer resume
-   Timer completion
-   Session saved
-   Session cancellation
-   Database errors
-   Application errors

Do not log unnecessary private information.

------------------------------------------------------------------------

# 41. Performance

The application should start quickly.

Do not block the UI thread with:

-   Large database queries
-   Large calculations
-   File operations
-   Expensive chart rendering

Use background workers where appropriate.

The timer must never freeze the UI.

------------------------------------------------------------------------

# 42. Accessibility and UX

Use:

-   Clear hierarchy
-   Readable fonts
-   Good contrast
-   Tooltips
-   Keyboard shortcuts
-   Visible focus states
-   Clear button labels
-   Consistent interaction patterns

Important actions should provide visible feedback.

------------------------------------------------------------------------

# 43. First Launch

On first launch:

1.  Create database automatically.
2.  Show setup screen.

Display:

**Welcome to StudyTrack**

Fields:

Daily study goal:

`6 hours`

Minimum study required for streak:

`30 minutes`

Button:

**Start Tracking**

Then open Dashboard.

------------------------------------------------------------------------

# 44. Default Configuration

Default daily goal:

**6 hours**

Default weekly goal:

**35 hours**

Default monthly goal:

**150 hours**

Default streak threshold:

**30 minutes**

Default countdown:

**25 minutes**

Default theme:

**Dark**

Notifications:

**Enabled**

Alarm:

**Enabled**

All defaults must be configurable.

------------------------------------------------------------------------

# 45. Privacy

This is a personal offline application.

Do not:

-   Collect telemetry
-   Track user behavior externally
-   Upload study history
-   Add advertising
-   Require cloud accounts

Future AI APIs must be opt-in.

------------------------------------------------------------------------

# 46. Future ML Architecture

Create an empty:

``` text
app/ml/
```

Do not implement ML in the initial release.

The ML layer must be independent of UI implementation.

Potential future models:

-   ProductivityPredictor
-   StudyDurationPredictor
-   GoalCompletionPredictor
-   ProductiveTimeAnalyzer
-   StudyConsistencyPredictor

Potential features:

-   hour_of_day
-   day_of_week
-   subject
-   session_duration
-   previous_day_study_time
-   previous_week_study_time
-   recent_session_count
-   current_streak
-   goal_progress

Potential predictions:

-   expected_session_duration
-   productivity_score
-   goal_completion_probability

Never train fake models using random data.

First collect real user study data.

------------------------------------------------------------------------

# 47. Future AI Agent Architecture

Create an empty:

``` text
app/agents/
```

Do not implement the AI agent initially.

Future agent:

**StudyCoachAgent**

Potential tools:

``` text
get_today_stats()
get_week_stats()
get_month_stats()
get_subject_stats()
get_goal_progress()
get_streak()
get_recent_sessions()
```

Potential future questions:

-   "How much did I study today?"
-   "What subject did I study most this month?"
-   "When am I most productive?"
-   "Create a study plan for tomorrow."
-   "Why has my study time decreased?"
-   "How many hours have I studied this week?"

The agent must interact through application services.

It must not directly manipulate database tables.

------------------------------------------------------------------------

# 48. Future AI/ML Data Flow

Current system:

``` text
                 Desktop UI
                     │
                     ▼
                 Services
                     │
                     ▼
                Repositories
                     │
                     ▼
                  SQLite
```

Future:

``` text
                   ML
                    │
                    ▼
                 Services
                    │
                    ▼
              Repositories
                    │
                    ▼
                 SQLite
```

and:

``` text
                AI Agent
                    │
                    ▼
                  Tools
                    │
                    ▼
                 Services
                    │
                    ▼
              Repositories
                    │
                    ▼
                 SQLite
```

This keeps future AI/ML code separate from the core application.

------------------------------------------------------------------------

# 49. ML Dataset Preparation

The application should eventually make it easy to generate a structured
dataset.

Potential dataset columns:

``` text
date
day_of_week
hour_of_day
subject
topic
session_type
duration_seconds
previous_day_minutes
previous_week_minutes
sessions_today
current_streak
daily_goal_seconds
daily_goal_progress
goal_completed
```

Only derive these features when enough real data exists.

Do not introduce leakage into ML training.

For example, do not use future information to predict past behavior.

------------------------------------------------------------------------

# 50. Future AI Study Coach

A future AI Study Coach could:

1.  Analyze historical study data.
2.  Answer natural-language questions.
3.  Create study plans.
4.  Recommend study times.
5.  Analyze goal progress.
6.  Identify patterns.
7.  Explain productivity trends.

Example:

``` text
User:
I have 3 hours today. What should I study?

AI:
Based on your active goals and recent study history:

09:00 - 10:15
Machine Learning

10:15 - 10:30
Break

10:30 - 11:30
Python

11:30 - 12:00
Revision
```

This is a future feature, not part of the initial MVP.

------------------------------------------------------------------------

# 51. Testing Strategy

Use pytest.

Test business logic independently from the UI.

## Timer tests

Test:

-   Start
-   Pause
-   Resume
-   Stop
-   Cancel
-   Completion
-   Countdown accuracy
-   State transitions
-   Restart recovery

## Session tests

Test:

-   Creation
-   Saving
-   Updating
-   Deleting
-   Duration calculation
-   Completed sessions
-   Cancelled sessions

## Goal tests

Test:

-   Daily goal
-   Weekly goal
-   Monthly goal
-   Progress percentage
-   Overachievement

## Streak tests

Test:

-   One study day
-   Consecutive days
-   Missing day
-   Multiple sessions on one day
-   Minimum threshold
-   Current streak
-   Longest streak
-   Future dates

## Analytics tests

Test:

-   Daily totals
-   Weekly totals
-   Monthly totals
-   Subject totals
-   Average session
-   Goal completion

------------------------------------------------------------------------

# 52. Timer Edge Cases

Explicitly test:

-   Application closes during timer
-   Application restarts during timer
-   Computer sleeps
-   Computer wakes
-   UI delay
-   Pause/resume
-   Cancelled session
-   Zero duration
-   Very long duration
-   Multiple sessions
-   Duplicate completion
-   System clock changes

The timer should never create negative duration.

------------------------------------------------------------------------

# 53. Data Integrity

Study data is the most important application data.

Requirements:

-   Atomic database writes
-   Foreign-key integrity
-   Valid timestamps
-   Non-negative duration
-   No duplicate completion records
-   Safe deletion
-   Recovery after application restart
-   Database backup/export capability

------------------------------------------------------------------------

# 54. Packaging

The final application must be buildable into a Windows executable using
PyInstaller.

The user should not need Python installed to run the packaged
executable.

Provide build documentation.

Example command:

``` bash
pyinstaller --windowed ...
```

The exact command should match the project's actual entry point and
assets.

Make sure packaged resources such as:

-   icons
-   sounds
-   styles
-   database initialization assets

are correctly included.

------------------------------------------------------------------------

# 55. Documentation

README.md must contain:

-   Project overview
-   Features
-   Screenshots
-   Technology stack
-   Installation
-   Running locally
-   Testing
-   Architecture
-   Database structure
-   Packaging
-   Data export
-   Future ML roadmap
-   Future AI-agent roadmap

Also document important architectural decisions.

------------------------------------------------------------------------

# 56. Development Phases

The project MUST be developed incrementally.

Do not attempt to build every feature simultaneously.

------------------------------------------------------------------------

## PHASE 0 --- Project Planning and Setup

### Objective

Prepare a clean development environment.

### Tasks

-   Create Git repository.
-   Create project structure.
-   Create virtual environment.
-   Configure Python 3.12+.
-   Add pyproject.toml.
-   Add dependencies.
-   Add .gitignore.
-   Add README.
-   Add PROJECT_SPEC.md.
-   Add UI reference image.
-   Configure logging.
-   Create basic application entry point.

### Acceptance Criteria

-   Project runs.
-   Main window opens.
-   Repository is clean.
-   Dependencies install successfully.

------------------------------------------------------------------------

# PHASE 1 --- Application Foundation

### Objective

Create the base desktop application and visual system.

### Tasks

-   Create PySide6 main window.
-   Create sidebar.
-   Create top bar.
-   Create navigation system.
-   Create dark theme.
-   Create typography system.
-   Create spacing system.
-   Create reusable cards.
-   Create reusable buttons.
-   Create basic dashboard layout.
-   Create SQLite database initialization.
-   Create SQLAlchemy setup.
-   Create initial database models.
-   Create repository base structure.
-   Create service base structure.

### Acceptance Criteria

-   Application opens.
-   Dashboard is visible.
-   Sidebar navigation works.
-   Dark theme matches the visual reference.
-   Database initializes automatically.
-   No database code exists inside UI widgets.

------------------------------------------------------------------------

# PHASE 2 --- Timer Engine

### Objective

Implement a reliable study timer.

### Tasks

-   Stopwatch.
-   Countdown.
-   Start.
-   Pause.
-   Resume.
-   Stop.
-   Cancel.
-   Reset.
-   Quick presets.
-   Custom duration.
-   Timer state machine.
-   Timestamp-based timer calculation.
-   Timer persistence.
-   Restart recovery.

### Acceptance Criteria

-   Stopwatch works.
-   Countdown works.
-   Pause/resume works.
-   Timer does not drift.
-   Application restart can recover active timer.
-   Invalid state transitions are prevented.
-   Timer never blocks the UI.

------------------------------------------------------------------------

# PHASE 3 --- Study Sessions

### Objective

Persist real study sessions.

### Tasks

-   Subject model.
-   Session model.
-   Session service.
-   Session repository.
-   Start-session dialog.
-   Subject selection.
-   Topic.
-   Notes.
-   Automatic start/end time.
-   Duration calculation.
-   Session completion.
-   Session cancellation.
-   Today's session list.
-   Sessions page.

### Acceptance Criteria

-   Every completed session is saved.
-   Duration is correct.
-   Date/time is correct.
-   Multiple sessions on the same day work.
-   Session history displays correctly.

------------------------------------------------------------------------

# PHASE 4 --- Goals

### Objective

Implement study goals.

### Tasks

-   Daily goals.
-   Weekly goals.
-   Monthly goals.
-   Goal creation.
-   Goal editing.
-   Goal deletion.
-   Goal activation.
-   Goal progress.
-   Remaining study time.
-   Progress bars.
-   Circular progress.

### Acceptance Criteria

For a 6-hour daily goal:

If the user studies 4 hours:

Progress must show:

`4h / 6h`

`66.7%`

All values must come from actual sessions.

------------------------------------------------------------------------

# PHASE 5 --- Streaks

### Objective

Track study consistency.

### Tasks

-   Current streak.
-   Longest streak.
-   Total study days.
-   Minimum daily threshold.
-   Consecutive calendar-date calculation.
-   Multiple sessions per day.

### Acceptance Criteria

-   Streak is correct after every completed session.
-   Missing study days reset the current streak correctly.
-   Longest historical streak remains preserved.
-   Threshold is configurable.

------------------------------------------------------------------------

# PHASE 6 --- GitHub-Style Activity Heatmap

### Objective

Visualize study consistency.

### Tasks

-   Year selector.
-   Calendar grid.
-   Seven weekday rows.
-   Monthly labels.
-   Study intensity levels.
-   Hover tooltip.
-   Click-to-view-day.
-   Dynamic database data.

### Acceptance Criteria

A day with more study time must have a stronger intensity.

A day with no study must have the empty state.

Clicking a date must show the correct sessions.

------------------------------------------------------------------------

# PHASE 7 --- Calendar

### Objective

Create a calendar-based study view.

### Tasks

-   Monthly calendar.
-   Month navigation.
-   Year navigation.
-   Study indicators.
-   Goal completion indicators.
-   Date details.
-   Daily study summary.

### Acceptance Criteria

Calendar values match session history and goals.

------------------------------------------------------------------------

# PHASE 8 --- Analytics

### Objective

Turn raw study data into useful statistics.

### Tasks

-   Daily analytics.
-   Weekly analytics.
-   Monthly analytics.
-   Subject analytics.
-   Average session.
-   Most productive day.
-   Goal completion.
-   Total sessions.
-   Charts.
-   Subject distribution.

### Acceptance Criteria

Analytics match database calculations.

No values are hard-coded.

------------------------------------------------------------------------

# PHASE 9 --- Search and Filtering

### Objective

Make historical study data easy to find.

### Tasks

-   Global search.
-   Ctrl + K.
-   Session search.
-   Subject search.
-   Topic search.
-   Notes search.
-   Date filtering.
-   Subject filtering.
-   Session-type filtering.
-   Status filtering.
-   Sorting.

### Acceptance Criteria

Search results are relevant and fast.

------------------------------------------------------------------------

# PHASE 10 --- Notifications and Alarm

### Objective

Provide reliable timer completion feedback.

### Tasks

-   Desktop notifications.
-   Alarm sound.
-   Enable/disable settings.
-   Custom sound if practical.
-   Completion notification.
-   Volume setting if supported.

### Acceptance Criteria

Countdown completion triggers the configured notification/alarm exactly
once.

------------------------------------------------------------------------

# PHASE 11 --- Settings and Data Management

### Objective

Make the application configurable and maintainable.

### Tasks

-   General settings.
-   Timer settings.
-   Alarm settings.
-   Notification settings.
-   Theme settings.
-   Streak threshold.
-   Database information.
-   CSV export.
-   JSON export.
-   Data backup.
-   Data restore if implemented.
-   Clear-data confirmation.

### Acceptance Criteria

Settings persist after restart.

Exported data can be loaded successfully.

------------------------------------------------------------------------

# PHASE 12 --- Reliability and Testing

### Objective

Make the application stable.

### Tasks

-   Unit tests.
-   Integration tests.
-   Timer tests.
-   Database tests.
-   Goal tests.
-   Streak tests.
-   Analytics tests.
-   Error handling.
-   Logging.
-   Recovery testing.
-   UI regression checks.

### Acceptance Criteria

Core business logic has strong test coverage.

Known bugs are resolved.

------------------------------------------------------------------------

# PHASE 13 --- Packaging

### Objective

Create a usable Windows application.

### Tasks

-   PyInstaller configuration.
-   Application icon.
-   Resource packaging.
-   Sound packaging.
-   Configuration packaging.
-   Test clean installation.
-   Test executable on Windows.
-   Write build instructions.

### Acceptance Criteria

The application can be packaged into an executable and run without a
development environment.

------------------------------------------------------------------------

# PHASE 14 --- ML Foundation

### Objective

Prepare real study data for future ML.

Do not build predictive models until enough real data exists.

### Tasks

-   Create data export pipeline.
-   Create feature engineering utilities.
-   Create training dataset generator.
-   Create ML experiment notebooks separately.
-   Add data validation.
-   Document feature definitions.

Potential future features:

-   hour_of_day
-   day_of_week
-   subject
-   recent study time
-   recent session count
-   current streak
-   goal progress
-   historical averages

### Potential models

-   Study duration prediction.
-   Productive time prediction.
-   Goal completion prediction.
-   Productivity trend prediction.

------------------------------------------------------------------------

# PHASE 15 --- AI Agent Foundation

### Objective

Add an AI Study Coach without coupling it to the database.

### Tasks

Create:

`StudyCoachAgent`

Create service tools:

-   get_today_stats
-   get_week_stats
-   get_month_stats
-   get_subject_stats
-   get_goal_progress
-   get_streak
-   get_recent_sessions

The agent should only interact with these application services.

Do not allow direct database manipulation.

------------------------------------------------------------------------

# PHASE 16 --- AI Study Coach

### Objective

Add natural-language interaction.

Potential capabilities:

-   Study history questions.
-   Productivity explanations.
-   Goal analysis.
-   Study-plan generation.
-   Personalized scheduling.
-   Recommendations.

Example:

User:

"What should I study tomorrow?"

Agent can consider:

-   Active goals
-   Recent subjects
-   Study history
-   Available time
-   Recent consistency

Then create a suggested plan.

AI functionality must be optional and clearly separated from the offline
core application.

------------------------------------------------------------------------

# 57. Phase Completion Rules

After every phase:

1.  Run the application.
2.  Run tests.
3.  Check for regressions.
4.  Verify database integrity.
5.  Verify UI behavior.
6.  Fix discovered errors.
7.  Update documentation.
8.  Commit working changes to Git.
9.  Only then begin the next phase.

Do not continue while known critical errors remain.

------------------------------------------------------------------------

# 58. Coding Standards

Follow:

-   PEP 8
-   Type hints
-   Small functions
-   Single responsibility
-   Clear naming
-   Useful docstrings
-   Modular classes
-   Dependency injection where useful
-   Minimal global state
-   No duplicated business logic
-   No hard-coded configuration
-   No unnecessary dependencies

Prefer composition over tightly coupled classes.

------------------------------------------------------------------------

# 59. Architecture Rules for Coding Agents

When modifying the project:

1.  Read this specification first.
2.  Inspect existing code before changing it.
3.  Preserve working functionality.
4.  Do not rewrite unrelated modules.
5.  Follow the existing architecture.
6.  Do not create duplicate implementations.
7.  Do not introduce dependencies without a reason.
8.  Add tests for important new behavior.
9.  Run tests after changes.
10. Explain significant architectural changes.

If a requirement is unclear, choose the simplest design consistent with
this specification.

Do not invent major features without explicit approval.

------------------------------------------------------------------------

# 60. Definition of Done

A feature is considered complete only when:

-   It works in the UI.
-   Its business logic is implemented correctly.
-   Data is persisted correctly when applicable.
-   Errors are handled.
-   Tests exist for important logic.
-   The application still starts successfully.
-   Existing features still work.
-   The feature follows the architecture.
-   Documentation is updated where necessary.

------------------------------------------------------------------------

# 61. Final Product Vision

The finished StudyTrack application should feel like a polished personal
productivity platform.

The long-term architecture is:

``` text
                 ┌────────────────────┐
                 │     StudyTrack     │
                 └─────────┬──────────┘
                           │
             ┌─────────────┴─────────────┐
             │                           │
       Core Productivity            Data Platform
             │                           │
     Timer / Goals / Streak        Study Sessions
     Calendar / Analytics           Date / Time
             │                       Subject / Topic
             │                           │
             └─────────────┬─────────────┘
                           │
                    Historical Data
                           │
              ┌────────────┴────────────┐
              │                         │
             ML                    AI Agents
              │                         │
       Predictions                Study Coach
       Patterns                   Study Plans
       Forecasting                Recommendations
```

The most important development principle is:

**Reliable data collection → analytics → ML → AI agents**

Do not sacrifice the core application in order to add AI prematurely.

The first version must already be valuable as a study tracker without
any ML or AI.

------------------------------------------------------------------------

# 62. Final Acceptance Checklist

Before calling the application complete, verify:

## Core

-   [ ] Application launches.
-   [ ] Database initializes.
-   [ ] Dashboard works.
-   [ ] Navigation works.

## Timer

-   [ ] Stopwatch works.
-   [ ] Countdown works.
-   [ ] Pause works.
-   [ ] Resume works.
-   [ ] Cancel works.
-   [ ] Alarm works.
-   [ ] Notification works.
-   [ ] Timer survives application restart.

## Sessions

-   [ ] Sessions save correctly.
-   [ ] Start/end time is correct.
-   [ ] Duration is correct.
-   [ ] Subject works.
-   [ ] Topic works.
-   [ ] Notes work.
-   [ ] History works.
-   [ ] Editing works.
-   [ ] Deletion works.

## Goals

-   [ ] Daily goal works.
-   [ ] Weekly goal works.
-   [ ] Monthly goal works.
-   [ ] Progress is accurate.

## Streaks

-   [ ] Current streak works.
-   [ ] Longest streak works.
-   [ ] Threshold works.
-   [ ] Missing days are handled.

## Visualization

-   [ ] Activity heatmap works.
-   [ ] Calendar works.
-   [ ] Charts work.
-   [ ] Subject distribution works.

## Analytics

-   [ ] Daily analytics work.
-   [ ] Weekly analytics work.
-   [ ] Monthly analytics work.
-   [ ] Subject analytics work.
-   [ ] Quick stats work.

## Data

-   [ ] CSV export works.
-   [ ] JSON export works.
-   [ ] Database remains consistent.

## Quality

-   [ ] Tests pass.
-   [ ] Logging works.
-   [ ] Error handling works.
-   [ ] UI is responsive.
-   [ ] No critical known bugs remain.

## Packaging

-   [ ] Windows executable builds.
-   [ ] Executable launches.
-   [ ] Resources are packaged.
-   [ ] Documentation is complete.

------------------------------------------------------------------------

# 63. Final Instruction to the Coding Agent

Treat this document as the **single source of truth for the StudyTrack
product specification**.

Do not implement all phases at once.

Start with the current requested phase only.

Before coding:

1.  Read this entire specification.
2.  Inspect the repository.
3.  Inspect the provided UI reference image.
4.  Determine what already exists.
5.  Make the smallest clean change required.

After coding:

1.  Run tests.
2.  Run the application.
3.  Verify the relevant acceptance criteria.
4.  Fix errors.
5.  Report files changed.
6.  Report tests performed.
7.  Report remaining limitations.

Never implement ML or AI features before the core data and analytics
architecture is stable unless explicitly instructed to do so.

The primary objective is a reliable, polished, maintainable desktop
study tracker that can evolve into an ML- and AI-powered personal study
system.

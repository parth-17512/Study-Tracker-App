# StudyTrack V2 — Complete Implementation & Release Specification

## Document Purpose

This document is the single implementation specification for **StudyTrack V2**.

The coding agent must use this document as the source of truth for the V2 upgrade.

The objective is not to rewrite the entire application. The objective is to:

- Preserve all existing V1 user data.
- Fix the identified V1 bugs.
- Improve the timer and session accounting.
- Upgrade the AI Coach.
- Add RAG over user notes.
- Persist AI Coach conversations.
- Improve the Notes system.
- Add AI-powered note formatting.
- Add XP-based gamification.
- Improve the dashboard.
- Remove the unnecessary destructive data-wipe control.
- Add automated tests.
- Safely migrate V1 → V2.
- Produce a stable V2 release.

---

# 1. Critical Instructions for the Coding Agent

## 1.1 Inspect Before Modifying

Before changing code, inspect the existing project.

Identify:

1. Application entry point.
2. UI framework.
3. Current project architecture.
4. Database technology.
5. Database location.
6. Database schema.
7. Existing migration mechanism, if any.
8. Timer implementation.
9. Session-recording implementation.
10. Notes implementation.
11. Folder/tree implementation.
12. Current AI Coach implementation.
13. Current LLM integration.
14. Existing vector database/RAG implementation, if any.
15. Dashboard implementation.
16. Settings/Data Management implementation.
17. Existing tests.
18. Packaging/build process.
19. Installer/update process.
20. Current user-data directories.

Do not make assumptions about the existing codebase.

---

# 2. Development Strategy

Implement V2 incrementally.

Do NOT attempt a complete rewrite.

The agent must work in phases:

```text
Phase 0  → Codebase Audit
Phase 1  → Data Safety & Persistence
Phase 2  → Database Migration & Backup
Phase 3  → Timer Engine Fix
Phase 4  → Session Recording Fix
Phase 5  → Notes Indexing Fix
Phase 6  → Notes UX Improvements
Phase 7  → AI Notes Formatting
Phase 8  → AI Coach Read-Only Architecture
Phase 9  → RAG
Phase 10 → AI Chat History
Phase 11 → XP/Gamification
Phase 12 → Dashboard
Phase 13 → Settings Cleanup
Phase 14 → Integration Testing
Phase 15 → V1 → V2 Upgrade Testing
Phase 16 → Release Build
```

The agent must complete and verify each phase before moving to the next.

---

# 3. Priority System

Use the following priorities.

## P0 — Critical

Must work before V2 release.

- Data preservation.
- Database migration.
- Database backup.
- Timer correctness.
- Session duration correctness.
- No data destruction during update.

## P1 — High

Required V2 functionality.

- AI Coach improvements.
- Read-only Notes access.
- RAG.
- AI chat persistence.
- Notes indexing.
- AI Notes formatting.
- XP system.
- Dashboard XP.

## P2 — Medium

Quality-of-life improvements.

- Collapse All folders.
- Settings cleanup.
- UI improvements.
- Additional analytics/polish.

---

# Phase 0 — CODEBASE AUDIT

## Goal

Understand the existing application before making changes.

## Tasks

### 0.1 Inspect project structure

Document:

```text
src/
app/
services/
repositories/
models/
ui/
database/
tests/
resources/
```

Use the actual structure of the project.

### 0.2 Identify database

Determine:

- Database type.
- Database file path.
- ORM.
- Schema.
- Existing migrations.
- Existing backup logic.

### 0.3 Identify timer logic

Find:

- Timer start.
- Timer pause.
- Timer resume.
- Timer completion.
- Timer cancellation.
- Countdown calculation.
- Session recording.
- Notification handling.

### 0.4 Identify Notes

Find:

- Note model.
- Note editor.
- Numbering implementation.
- Folder tree.
- Folder expand/collapse.
- Note persistence.

### 0.5 Identify AI Coach

Find:

- Chat UI.
- LLM service.
- Prompt system.
- Context retrieval.
- Existing memory.
- Existing RAG/vector store, if any.

### 0.6 Identify packaging

Determine:

- PyInstaller or other packager.
- Installer behavior.
- Executable location.
- Current database location.
- Whether update/reinstall deletes application directory.

## Deliverable

Before implementing Phase 1, create a short internal architecture report:

```text
Current Architecture
Database Location
Timer Architecture
Notes Architecture
AI Architecture
Packaging Architecture
Known Risks
Recommended Changes
```

---

# Phase 1 — USER DATA SAFETY

## Goal

Prevent the V1 problem where publishing/updating the application erased existing user data.

This is the highest-priority requirement.

---

## 1.1 Separate Application Code From User Data

User data must not live inside a disposable application installation/build directory.

Preferred Windows location:

```text
%APPDATA%\StudyTrack\
```

Example:

```text
C:\Users\<username>\AppData\Roaming\StudyTrack\
```

Recommended logical structure:

```text
StudyTrack/
│
├── data/
│   ├── studytrack.db
│   ├── backups/
│   └── exports/
│
├── ai/
│   ├── vector_store/
│   └── indexes/
│
├── logs/
│
└── config/
```

The exact structure may follow the existing application architecture.

The key requirement is:

> Updating or replacing the executable must not replace the user's database.

---

## 1.2 Detect Existing Data

At startup:

```text
Application Starts
        ↓
Find persistent data directory
        ↓
Does database exist?
        ↓
YES → Open existing database
NO  → Create new database
```

Never create a fresh database over an existing database.

---

## 1.3 Never Automatically Delete User Data

Do not execute destructive operations during:

- Startup.
- Update.
- Migration.
- Reinstallation.
- First launch of V2.

Never use:

```text
DROP DATABASE
DELETE database file
DELETE user-data directory
RESET ALL DATA
```

as part of a normal upgrade.

---

## 1.4 Preserve Existing Records

Preserve:

- Notes.
- Folders.
- Study sessions.
- Timer history.
- Goals.
- Streaks.
- Settings where appropriate.
- AI conversations if already present.
- Any other user-generated data.

---

## Acceptance Criteria

- [ ] V1 database is detected.
- [ ] Existing records appear in V2.
- [ ] Starting V2 does not create an empty replacement database.
- [ ] Application updates do not delete user data.
- [ ] Reinstall/update behavior is documented.

---

# Phase 2 — DATABASE MIGRATION & BACKUP

## Goal

Safely evolve the V1 database schema into V2.

---

## 2.1 Implement Database Versioning

The database must have a schema version.

Example:

```text
V1
 ↓
Migration 001
 ↓
V2
```

Use the existing ORM/migration framework if present.

If SQLAlchemy is used, consider Alembic.

---

## 2.2 Never Recreate the Database for Schema Changes

Bad:

```text
Delete old database
Create new database
```

Correct:

```text
Existing database
      ↓
Migration
      ↓
Updated database
```

---

## 2.3 Automatic Backup Before Migration

Before modifying the existing database:

```text
Create Backup
      ↓
Verify Backup
      ↓
Run Migration
      ↓
Validate Database
```

Example:

```text
data/backups/

studytrack_backup_2026-09-30_143000.db
```

Use timestamps.

Do not overwrite the only backup.

---

## 2.4 Migration Failure Safety

If migration fails:

1. Do not delete the original database.
2. Preserve the backup.
3. Report the error.
4. Allow rollback/recovery.

Example message:

```text
StudyTrack could not complete the database update.

Your existing data has been preserved.
Please review the backup or retry the migration.
```

---

## 2.5 New V2 Tables

Potential new tables:

```text
chat_sessions
chat_messages
xp_transactions
```

Potential new timer fields:

```text
target_duration
elapsed_duration
started_at
paused_at
last_resumed_at
status
```

Potential RAG metadata:

```text
note_id
chunk_id
embedding_id
updated_at
```

Use migrations to add these.

---

## Acceptance Criteria

- [ ] V1 database upgrades without losing records.
- [ ] Backup is created before migration.
- [ ] Migration is repeat-safe.
- [ ] Migration failure does not destroy original data.
- [ ] Fresh V2 installation works.
- [ ] Existing V1 installation works.

---

# Phase 3 — TIMER ENGINE REWRITE/FIX

## Goal

Fix all timer-related bugs at the underlying service level.

Do not patch only the UI.

---

# 3.1 Timer Bugs to Fix

## Bug A — Pause/Resume loses previous time

Current behavior:

```text
1 hour timer

Study 20 minutes
Pause

Resume later
Study 40 minutes

Recorded:
40 minutes
```

Expected:

```text
Recorded:
60 minutes
```

---

## Bug B — One hour becomes 59:59

Current behavior:

```text
1 hour
→
59m 59s
```

Expected:

```text
1h 0m 0s
```

---

## Bug C — Timer exceeds target when user is away

Current behavior:

```text
Target = 1 hour

Timer completes
User is away for 40 minutes

Recorded:
1h 40m
```

Expected:

```text
Recorded:
1h 0m
```

---

# 3.2 Timer State Machine

Implement explicit states:

```text
IDLE
RUNNING
PAUSED
COMPLETED
CANCELLED
```

Transitions:

```text
IDLE → RUNNING
RUNNING → PAUSED
PAUSED → RUNNING
RUNNING → COMPLETED
RUNNING → CANCELLED
PAUSED → CANCELLED
```

---

# 3.3 Timer Data Model

Maintain:

```text
target_duration
accumulated_active_duration
current_run_started_at
status
```

Optional:

```text
paused_at
completed_at
```

---

# 3.4 Correct Pause Logic

When paused:

```text
active_period =
    current_time - current_run_started_at
```

Then:

```text
accumulated_active_duration += active_period
```

Then:

```text
status = PAUSED
```

---

# 3.5 Correct Resume Logic

When resumed:

```text
current_run_started_at = current_time
status = RUNNING
```

Do not reset accumulated duration.

---

# 3.6 Correct Elapsed Time

When running:

```text
elapsed =
    accumulated_active_duration
    +
    (current_time - current_run_started_at)
```

When paused:

```text
elapsed =
    accumulated_active_duration
```

---

# 3.7 Completion Rule

If:

```text
elapsed >= target_duration
```

then:

```text
elapsed = target_duration
status = COMPLETED
```

Never allow:

```text
elapsed > target_duration
```

for a completed countdown session.

---

# 3.8 Notification Independence

Notification lifecycle must be separate from timer lifecycle.

Correct:

```text
Timer reaches zero
      ↓
Timer = COMPLETED
      ↓
Session = completed
      ↓
Record target duration
      ↓
Notification shown
```

If notification remains open for 40 minutes:

```text
Session remains 1 hour
```

Do not calculate study duration based on notification dismissal time.

---

# 3.9 Manual Cancellation

If:

```text
Target = 1 hour
Actual active time = 25 minutes
User cancels
```

record:

```text
25 minutes
Status = CANCELLED
```

Do not record one hour unless the timer actually completed.

---

# 3.10 Timer Service API

Recommended:

```python
start()
pause()
resume()
cancel()
complete()
get_elapsed()
get_remaining()
get_state()
```

The actual API should match the existing project architecture.

---

# Phase 4 — SESSION RECORDING

## Goal

Ensure the Sessions section receives the correct authoritative duration.

---

## 4.1 Timer Is Source of Truth

The UI must not independently calculate session duration.

Use:

```text
TimerService
      ↓
Final elapsed duration
      ↓
SessionService
      ↓
Database
```

---

## 4.2 Completed Timer

If:

```text
target_duration = 3600
```

and the timer completes:

```text
session.duration = 3600
```

Display:

```text
1h 0m 0s
```

---

## 4.3 Paused Timer

Example:

```text
Target = 3600 sec

First period = 1200 sec
Second period = 2400 sec

Total = 3600 sec
```

Session:

```text
3600 sec
```

---

## 4.4 Exact Duration Representation

Prefer integer seconds or a reliable duration representation.

Do not rely on floating-point UI formatting.

Avoid off-by-one errors.

---

# Phase 5 — NOTES INDEXING FIX

## Goal

Fix ordered list numbering.

---

## 5.1 Current Bug

The editor generates:

```text
1. Point A
1. Point B
1. Point C
1. Point D
```

Expected:

```text
1. Point A
2. Point B
3. Point C
4. Point D
```

---

## 5.2 Sequential Numbering

When the user adds items:

```text
1. First
2. Second
3. Third
4. Fourth
```

When inserting between 2 and 3:

```text
1. First
2. Second
3. New item
4. Third
5. Fourth
```

---

## 5.3 Nested Numbering

If the editor supports nested lists:

```text
1. Machine Learning
   1. Supervised Learning
   2. Unsupervised Learning

2. Deep Learning
   1. CNN
   2. RNN
```

Parent and child numbering must remain independent.

---

## 5.4 Tests

Test:

- Adding an item.
- Removing an item.
- Inserting an item.
- Enter/Return.
- Backspace.
- Nested lists.
- Copy/paste.
- Editing existing numbered notes.

---

# Phase 6 — NOTES UX: COLLAPSE ALL

## Goal

Add a one-click folder collapse function.

---

## 6.1 UI

Add:

```text
Collapse All
```

inside the Notes section.

---

## 6.2 Behavior

Before:

```text
📂 Machine Learning
   📄 Regression
   📄 Classification

📂 Deep Learning
   📄 CNN
   📄 RNN
```

After:

```text
📁 Machine Learning
📁 Deep Learning
```

No data should be changed.

Only UI expansion state changes.

---

## Acceptance Criteria

- [ ] One click collapses all folders.
- [ ] Notes remain unchanged.
- [ ] Folder contents are preserved.
- [ ] Opening folders again works normally.

---

# Phase 7 — AI FORMATTING TOOL FOR NOTES

## Goal

Add an AI tool that improves note formatting without changing the user's ideas.

---

# 7.1 UI

Add a button such as:

```text
✨ AI Format
```

inside the Notes section.

---

# 7.2 Capabilities

The tool should correct:

- Numbering.
- Spelling.
- Grammar where appropriate.
- Indentation.
- Bullet consistency.
- Headings.
- Spacing.
- Basic structure.

---

# 7.3 Example — Numbering

Input:

```text
1. Machine Learning
1. Supervised Learning
1. Regression
```

Output:

```text
1. Machine Learning
2. Supervised Learning
3. Regression
```

---

# 7.4 Example — Spelling

Input:

```text
Gradient decent is an optimazation algorithim.
```

Output:

```text
Gradient descent is an optimization algorithm.
```

---

# 7.5 Example — Indentation

Input:

```text
1. Machine Learning
2. Supervised Learning
3. Regression
```

If the hierarchy is clear, formatting can become:

```text
1. Machine Learning
   1. Supervised Learning
      1. Regression
```

The AI must not invent relationships that are not supported by the user's text.

---

# 7.6 Safety Requirement

The AI must not silently rewrite the user's ideas.

Use:

```text
Original Note
     ↓
AI Formatting
     ↓
Preview
     ↓
User Accepts
     ↓
Save
```

The original content should remain recoverable.

---

# 7.7 AI Formatting Prompt Rules

The formatting model should be instructed:

```text
Preserve the meaning of the user's notes.

Do not add facts.

Do not remove ideas.

Do not invent relationships.

Correct spelling and obvious grammar errors.

Correct numbering.

Correct indentation.

Improve structure only when supported by the existing content.
```

---

# Phase 8 — AI COACH READ-ONLY NOTES ACCESS

## Goal

Upgrade the AI Coach so it can understand the user's notes.

---

# 8.1 AI Coach Capabilities

The AI Coach should be able to:

- Summarize notes.
- Explain notes.
- Answer questions about notes.
- Find related ideas.
- Connect ideas across notes.
- Identify recurring themes.
- Identify possible knowledge gaps.
- Help the user reflect.
- Generate deeper explanations based on their notes.
- Compare multiple notes.

---

# 8.2 Read-Only Requirement

The AI Coach must have READ-ONLY access.

It may:

```text
read_note()
search_notes()
list_notes()
get_note_chunks()
```

It must not have:

```text
create_note()
update_note()
delete_note()
move_note()
rename_note()
```

---

# 8.3 Architecture

Preferred:

```text
User
 ↓
AI Coach
 ↓
Read-Only Notes Interface
 ↓
Notes Repository
 ↓
SQLite
```

Do not give the AI Coach unrestricted database write access.

---

# 8.4 Deep Understanding

The AI Coach should not only summarize.

Example notes:

```text
Gradient Descent
Learning Rate
Loss Function
Optimization
Convergence
```

Question:

```text
What is the main idea connecting these notes?
```

The AI Coach should explain the relationships between the user's ideas.

---

# Phase 9 — RAG IMPLEMENTATION

## Goal

Implement Retrieval-Augmented Generation for the AI Coach.

---

# 9.1 RAG Architecture

```text
User Question
      ↓
Query Embedding
      ↓
Vector Search
      ↓
Relevant Note Chunks
      ↓
Context Construction
      ↓
LLM
      ↓
AI Coach Response
```

---

# 9.2 Note Ingestion

When a note is created or updated:

```text
Note
 ↓
Clean Text
 ↓
Chunk
 ↓
Embedding
 ↓
Vector Store
```

---

# 9.3 Chunking

Prefer paragraph/section-aware chunking.

Avoid blindly splitting text in ways that destroy meaning.

Preserve:

- Heading.
- Paragraph.
- Bullet list.
- Code block where relevant.

---

# 9.4 Vector Store

Prefer a local vector store if the current architecture allows it.

Possible options:

- FAISS.
- ChromaDB.

Priority:

1. Local.
2. Reliable.
3. Easy to rebuild.
4. Easy to back up.
5. Low operational complexity.

---

# 9.5 Metadata

Each vector should maintain metadata such as:

```json
{
  "note_id": 42,
  "chunk_id": 7,
  "title": "Gradient Descent",
  "folder": "Machine Learning",
  "updated_at": "2026-09-30T14:30:00"
}
```

---

# 9.6 Retrieval

Question:

```text
What did I write about regularization?
```

Process:

```text
Question
 ↓
Embedding
 ↓
Top-K similarity search
 ↓
Relevant chunks
 ↓
LLM context
 ↓
Answer
```

---

# 9.7 Source Awareness

Whenever useful, identify the source note.

Example:

```text
Based on your note "Machine Learning Basics":

You described regularization as...
```

Do not fabricate source references.

---

# 9.8 Missing Information

If notes do not contain enough information:

```text
I couldn't find enough information about this topic in your notes.
I can explain the general concept if you want.
```

Do not pretend information came from the user's notes.

---

# 9.9 RAG Synchronization

When a note changes:

```text
Old chunks
 ↓
Remove/update
 ↓
New chunks
 ↓
New embeddings
```

Avoid duplicate vectors.

---

# 9.10 Rebuild Index

Provide a safe mechanism:

```text
Settings
 → AI / RAG
 → Rebuild Knowledge Index
```

The process:

```text
Read Notes
 ↓
Chunk
 ↓
Embed
 ↓
Build Vector Index
 ↓
Validate
```

Original notes must never be modified.

---

# 9.11 Existing V1 Notes

On first V2 launch:

```text
Existing Notes
 ↓
Check Index
 ↓
If missing
 ↓
Build RAG Index
```

This must not alter note content.

---

# Phase 10 — AI COACH CHAT HISTORY

## Goal

Persist AI Coach conversations so the user can reflect on them later.

---

# 10.1 Database

Create:

```text
chat_sessions
```

Suggested fields:

```text
id
title
created_at
updated_at
```

Create:

```text
chat_messages
```

Suggested fields:

```text
id
session_id
role
content
created_at
```

Roles:

```text
user
assistant
system
```

---

# 10.2 Save Automatically

Every user/assistant message should be persisted.

Do not rely only on in-memory state.

---

# 10.3 Chat History UI

Example:

```text
AI COACH

+ New Chat

Previous Chats
-----------------------
Understanding ML
Gradient Descent Review
Weekly Reflection
RAG Questions
September Study Review
```

---

# 10.4 Chat Features

Minimum:

- New Chat.
- Save automatically.
- Open previous chat.
- Rename chat.
- Delete chat.
- Preserve timestamps.

Search can be added if practical.

---

# 10.5 Delete Confirmation

If chat deletion is implemented:

```text
Are you sure you want to delete this conversation?
```

Require confirmation.

---

# Phase 11 — GAMIFICATION / XP SYSTEM

## Goal

Make studying feel like a game while keeping progress meaningful and transparent.

---

# 11.1 XP Rules

Initial rules:

| Activity | XP |
|---|---:|
| 1 focused hour | +10 |
| Complete difficult task | +15 |
| Finish daily target | +20 |
| No social media during session | +5 |
| Complete weekly goal | +50 |
| Miss configured goal | -10 |

---

# 11.2 XP Transactions

Do not store only one XP number.

Create:

```text
xp_transactions
```

Suggested fields:

```text
id
amount
reason
event_type
reference_id
created_at
```

Example:

```text
+10 | Focused hour
+15 | Difficult task
+20 | Daily target
+50 | Weekly goal
-10 | Missed goal
```

---

# 11.3 Duplicate Protection

Rewards must be idempotent.

Example:

Daily target for September 30:

```text
event_type = daily_target
reference_id = 2026-09-30
```

Before awarding:

```text
Has this event already been rewarded?
```

If yes:

```text
Do nothing.
```

---

# 11.4 Focused Hour XP

When a completed study session reaches the configured reward threshold:

```text
+10 XP
```

Avoid awarding the same hour repeatedly.

The exact interpretation of multiple-hour sessions should be clearly defined in code and tested.

---

# 11.5 Difficult Task

Allow tasks to have a difficulty attribute.

Example:

```text
Task:
Implement RAG retrieval

Difficulty:
Difficult

Status:
Completed

Reward:
+15 XP
```

Award once.

---

# 11.6 Daily Goal

Example:

```text
Daily target = 6 hours
Actual = 6 hours
```

Reward:

```text
+20 XP
```

If actual study is below target, do not award completion XP.

---

# 11.7 Weekly Goal

Example:

```text
Weekly target = 25 hours
Actual = 25 hours
```

Reward:

```text
+50 XP
```

Award only once for the week.

---

# 11.8 Missed Goal

If a configured goal is missed:

```text
-10 XP
```

Do not repeatedly deduct XP every time the app starts.

Use a unique goal/date/week reference.

---

# 11.9 No Social Media Reward

If the application already tracks social media usage, use that data.

Do not implement fake or unreliable monitoring.

If the feature does not currently exist, keep the XP event architecture ready for future implementation rather than inventing unreliable behavior.

---

# 11.10 Weekly XP Visualization

Dashboard example:

```text
WEEK 1

Mon  ██████████  50 XP
Tue  ████████    40 XP
Wed  ██████████  50 XP
Thu  ██████      30 XP
Fri  ██████████  50 XP

Total: 220 XP
```

The exact UI can be improved.

The important requirement is visible accumulation.

---

# Phase 12 — DASHBOARD XP WIDGET

## Goal

Make XP visible from the main dashboard.

---

# 12.1 Dashboard

Example:

```text
----------------------------------------
              STUDYTRACK
----------------------------------------

Today's Study
3h 45m

Daily Goal
4h / 6h

🔥 Streak
12 days

🎮 XP
1,240 XP

This Week
220 XP

Weekly Goal
18h / 25h

----------------------------------------
Recent Sessions
----------------------------------------

----------------------------------------
AI Coach
----------------------------------------
```

---

# 12.2 XP Information

Show:

- Total XP.
- Today's XP.
- Weekly XP.
- Current streak where available.
- Weekly goal progress.
- Recent XP events.

---

# Phase 13 — SETTINGS CLEANUP

## Goal

Remove the unnecessary destructive data-wipe button.

---

# 13.1 Remove Wipe Data Button

Inside:

```text
Settings
 → Data Management
```

remove the button that wipes all application data.

Do not leave misleading UI.

---

# 13.2 Safer Data Management

Where appropriate, Data Management may contain:

```text
Export Data
Create Backup
Restore Backup
Open Data Folder
Rebuild RAG Index
```

Only implement options supported by the existing architecture.

---

# Phase 14 — INTEGRATION

## Goal

Make all V2 systems work together.

---

# 14.1 Study Session → XP

```text
Timer
 ↓
Completed Session
 ↓
Session Database
 ↓
XP Evaluation
 ↓
+XP
```

---

# 14.2 Notes → RAG

```text
Note Created/Updated
 ↓
Notes Database
 ↓
RAG Index Update
```

---

# 14.3 Notes → AI Coach

```text
User Question
 ↓
RAG
 ↓
Notes
 ↓
AI Coach
```

---

# 14.4 AI Coach → Chat History

```text
User Message
 ↓
AI Coach
 ↓
Response
 ↓
Save Both Messages
```

---

# 14.5 Goals → XP

```text
Goal
 ↓
Evaluate Completion
 ↓
XP Event
 ↓
XP Transaction
```

---

# Phase 15 — AUTOMATED TESTING

## Goal

Prevent V1 bugs from returning.

---

# 15.1 Database Tests

Create tests:

```text
test_existing_database_is_preserved()
test_database_migration()
test_backup_before_migration()
test_failed_migration_preserves_database()
test_existing_notes_survive_upgrade()
test_existing_sessions_survive_upgrade()
```

---

# 15.2 Timer Tests

Create:

```text
test_timer_start()
test_timer_pause()
test_timer_resume()
test_timer_multiple_pause_resume()
test_timer_completion()
test_timer_exact_one_hour()
test_timer_cannot_exceed_target()
test_notification_does_not_extend_timer()
test_cancelled_timer_records_actual_duration()
```

---

# 15.3 Notes Tests

Create:

```text
test_numbering()
test_numbering_after_insert()
test_numbering_after_delete()
test_nested_numbering()
test_collapse_all()
```

---

# 15.4 RAG Tests

Create:

```text
test_note_indexing()
test_note_update_updates_index()
test_note_search()
test_retrieval()
test_existing_notes_can_be_indexed()
test_rebuild_index()
```

---

# 15.5 Chat Tests

Create:

```text
test_chat_saved()
test_chat_reloaded()
test_multiple_chat_sessions()
test_chat_message_order()
```

---

# 15.6 XP Tests

Create:

```text
test_focused_hour_xp()
test_difficult_task_xp()
test_daily_goal_xp()
test_weekly_goal_xp()
test_negative_xp()
test_duplicate_reward_prevention()
```

---

# Phase 16 — MANUAL QA

## 16.1 Data Upgrade Test

Use a copy of the V1 application/data.

Create:

- Notes.
- Folders.
- Study sessions.
- Goals.
- AI conversations.
- Existing settings.

Then:

```text
V1
 ↓
Install/Upgrade
 ↓
V2
```

Verify every record remains.

---

# 16.2 Timer QA

Test:

### Test A

```text
Target = 1 hour
Run continuously
Complete
```

Expected:

```text
1h 0m 0s
```

### Test B

```text
Target = 1 hour

20m
Pause

40m
Resume

Complete
```

Expected:

```text
1h 0m 0s
```

### Test C

```text
Target = 1 hour

Timer completes
Notification remains open
Wait 40 minutes
```

Expected:

```text
1h 0m 0s
```

### Test D

```text
Target = 1 hour
Run 25 minutes
Cancel
```

Expected:

```text
25m
Status = Cancelled
```

---

# 16.3 Notes QA

Create:

```text
1. First
1. Second
1. Third
1. Fourth
```

Expected:

```text
1. First
2. Second
3. Third
4. Fourth
```

Test nested lists.

Test folder collapse.

Test AI formatting preview.

---

# 16.4 AI Coach QA

Create notes about:

```text
Gradient Descent
Learning Rate
Regularization
Transformers
RAG
```

Ask:

```text
What did I write about regularization?
```

Expected:

The answer should use retrieved note content.

Ask:

```text
How are gradient descent and learning rate related?
```

Expected:

The AI should connect relevant notes.

Ask a question unrelated to the notes.

Expected:

The AI should clearly distinguish general knowledge from information found in the user's notes.

---

# 16.5 Chat History QA

1. Start a new AI chat.
2. Ask multiple questions.
3. Close the application.
4. Reopen.
5. Open previous chat.

Expected:

The full conversation remains.

---

# 16.6 XP QA

Verify:

```text
Focused hour → +10
Difficult task → +15
Daily goal → +20
Weekly goal → +50
Missed goal → -10
```

Verify duplicate events do not generate duplicate rewards.

---

# Phase 17 — SECURITY & PRIVACY REVIEW

Before release, verify:

- AI Coach has no unrestricted filesystem access.
- AI Coach cannot directly write to Notes.
- AI Coach cannot delete notes.
- AI Coach cannot execute arbitrary commands.
- API keys are not hardcoded.
- API keys are not committed to Git.
- Private notes are not unnecessarily written to logs.
- Chat history is stored only where intended.
- Backups are created safely.
- User data is not sent externally unless required by the configured AI service.

---

# Phase 18 — PACKAGING & UPDATE SAFETY

## Goal

Ensure V2 packaging does not repeat the V1 data-loss problem.

---

# 18.1 Build Separation

Application binary:

```text
StudyTrack.exe
```

User data:

```text
%APPDATA%\StudyTrack\
```

These must be separate.

---

# 18.2 Installer Behavior

The installer/update process must:

- Replace application code safely.
- Preserve user-data directory.
- Preserve database.
- Preserve notes.
- Preserve backups.
- Preserve AI chat history.
- Preserve settings where appropriate.

---

# 18.3 Fresh Installation

Fresh installation:

```text
No data exists
 ↓
Create data directory
 ↓
Create database
 ↓
Start application
```

---

# 18.4 Upgrade Installation

Upgrade:

```text
V1 data exists
 ↓
Backup
 ↓
Install V2
 ↓
Detect database
 ↓
Run migrations
 ↓
Validate
 ↓
Start
```

---

# Phase 19 — RELEASE CHECKLIST

Before V2 is published:

## Data

- [ ] User data is stored outside application installation directory.
- [ ] V1 database is detected.
- [ ] V1 → V2 migration works.
- [ ] Backup is created.
- [ ] Migration failure is safe.
- [ ] No startup data reset exists.
- [ ] No update data reset exists.

## Timer

- [ ] Pause/resume works.
- [ ] Multiple pause/resume works.
- [ ] 1 hour = 1 hour.
- [ ] 59:59 bug fixed.
- [ ] Timer cannot exceed target.
- [ ] Notification does not extend timer.
- [ ] Manual cancellation records actual active time.

## Notes

- [ ] Sequential numbering works.
- [ ] Nested numbering works.
- [ ] Collapse All works.
- [ ] AI formatting works.
- [ ] Formatting preview works.
- [ ] Original note can be recovered.

## AI Coach

- [ ] Notes are readable by AI Coach.
- [ ] Notes are read-only to AI Coach.
- [ ] RAG works.
- [ ] Existing notes are indexed.
- [ ] Updated notes update index.
- [ ] Missing context is handled honestly.
- [ ] Chat history persists.

## Gamification

- [ ] XP dashboard exists.
- [ ] Focused hour XP works.
- [ ] Difficult task XP works.
- [ ] Daily target XP works.
- [ ] Weekly goal XP works.
- [ ] Negative XP works.
- [ ] Duplicate rewards are prevented.
- [ ] Weekly XP visualization works.

## Settings

- [ ] Wipe All Data button removed.

## Testing

- [ ] Unit tests pass.
- [ ] Integration tests pass.
- [ ] Manual QA passes.
- [ ] V1 → V2 upgrade test passes.
- [ ] Fresh installation test passes.
- [ ] Restart test passes.
- [ ] Packaging test passes.

---

# Phase 20 — FINAL V2 DEFINITION OF DONE

StudyTrack V2 is ready for publication only when all of the following are true:

```text
Existing user data is safe
        +
V1 → V2 migration works
        +
Backups work
        +
Timer is mathematically correct
        +
Session duration is correct
        +
Notes numbering works
        +
Collapse All works
        +
AI formatting works
        +
AI Coach is read-only
        +
RAG works
        +
Existing notes are indexed
        +
AI chat history persists
        +
XP system works
        +
Dashboard shows XP
        +
Data wipe button is removed
        +
Automated tests pass
        +
Manual QA passes
        +
V1 → V2 upgrade is verified
        +
Release build is verified
```

---

# 21. Recommended Implementation Order

The coding agent must follow this order unless the existing architecture requires a documented adjustment.

```text
STEP 1
Audit existing codebase

↓

STEP 2
Fix persistent data location

↓

STEP 3
Implement database versioning/migrations

↓

STEP 4
Implement automatic database backup

↓

STEP 5
Test V1 → V2 database migration

↓

STEP 6
Fix TimerService

↓

STEP 7
Fix SessionService integration

↓

STEP 8
Write timer regression tests

↓

STEP 9
Fix Notes numbering

↓

STEP 10
Add Collapse All

↓

STEP 11
Add AI Notes formatting

↓

STEP 12
Upgrade AI Coach architecture

↓

STEP 13
Create read-only Notes retrieval interface

↓

STEP 14
Implement RAG ingestion

↓

STEP 15
Implement RAG retrieval

↓

STEP 16
Index existing notes

↓

STEP 17
Implement AI chat persistence

↓

STEP 18
Implement XP transaction system

↓

STEP 19
Connect sessions/goals/tasks to XP

↓

STEP 20
Add XP dashboard

↓

STEP 21
Remove data wipe button

↓

STEP 22
Run integration tests

↓

STEP 23
Run V1 → V2 upgrade test

↓

STEP 24
Build release candidate

↓

STEP 25
Test release candidate

↓

STEP 26
Publish V2
```

---

# 22. Coding Agent Working Rules

For every phase:

### Rule 1

Inspect existing code before changing it.

### Rule 2

Do not rewrite working components unnecessarily.

### Rule 3

Make small, isolated changes.

### Rule 4

Write tests for every bug fix.

### Rule 5

Run the relevant tests after each change.

### Rule 6

Do not delete user data.

### Rule 7

Do not change the database schema without a migration.

### Rule 8

Do not give AI Coach write access to Notes.

### Rule 9

Do not use notification state as timer state.

### Rule 10

Do not calculate timer duration from UI labels.

### Rule 11

Do not silently overwrite original notes with AI-generated formatting.

### Rule 12

Do not award duplicate XP.

### Rule 13

Do not expose API keys in source code.

### Rule 14

Do not proceed to the next phase if the current phase is failing.

---

# 23. Expected Agent Reporting Format

After completing each phase, report:

```text
PHASE: <number>
STATUS: PASS / PARTIAL / BLOCKED

Implemented:
- ...

Files changed:
- ...

Database changes:
- ...

Tests added:
- ...

Tests passed:
- ...

Known issues:
- ...

Next phase:
- ...
```

Do not simply say:

```text
Done.
```

The agent must provide enough information to verify what changed.

---

# 24. Final Architecture Target

The final V2 architecture should conceptually look like:

```text
                         STUDYTRACK V2
                              │
             ┌────────────────┼────────────────┐
             │                │                │
             ▼                ▼                ▼
          Dashboard         Notes          AI Coach
             │                │                │
             │                │                ▼
             │                │             RAG
             │                │                │
             │                │          Vector Store
             │                │
             │                ▼
             │          Notes Repository
             │                │
             │                ▼
             │             SQLite
             │
       ┌─────┼─────────────┐
       │     │             │
       ▼     ▼             ▼
     Goals  Sessions      Tasks
       │     │             │
       └─────┼─────────────┘
             ▼
          XP Service
             │
             ▼
      XP Transactions
```

Persistent storage:

```text
%APPDATA%\StudyTrack\
```

Application code:

```text
Installation Directory
```

These must remain separate.

---

# 25. Final Product Vision

StudyTrack V2 should become a reliable personal learning system.

The user should be able to:

```text
Plan
 ↓
Study
 ↓
Track time accurately
 ↓
Earn XP
 ↓
Write notes
 ↓
Organize notes
 ↓
Format notes with AI
 ↓
Build a personal knowledge base
 ↓
Ask AI Coach questions
 ↓
Retrieve knowledge using RAG
 ↓
Reflect on previous conversations
 ↓
Review progress
 ↓
Improve future study
```

The most important V2 principle is:

> The application should help the user build a long-term personal learning history without ever putting that history at risk during an application update.

---

# 26. Final Instruction

Implement this specification phase by phase.

Do not skip the data-safety and timer phases.

Do not begin with UI polish before the underlying data and timer architecture is reliable.

Do not publish V2 until the V1 → V2 upgrade has been tested using a copy of real V1 data.

The final release must prioritize:

1. Data safety.
2. Correct timer/session accounting.
3. Reliable Notes.
4. Reliable AI Coach.
5. Reliable RAG.
6. Persistent chat history.
7. Transparent XP.
8. Automated regression testing.
9. Safe packaging and upgrade behavior.

**StudyTrack V2 should be an upgrade of the existing application, not a reset or replacement of the user's existing StudyTrack data.**

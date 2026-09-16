# StudyTrack: Build a Better You 🚀

StudyTrack is a comprehensive, offline-first personal desktop application designed to supercharge your productivity, rigorously track your study time, and organize your learning materials. Built with a modern dark-mode aesthetic, rock-solid reliability, and an architecture primed for future AI capabilities, StudyTrack acts as your ultimate personalized learning companion.

Whether you are a student preparing for exams, a professional upskilling, or a lifelong learner, StudyTrack provides the structure and insights needed to achieve your goals consistently.

---

## 🌟 Why StudyTrack?

**Increase Your Productivity & Focus**
- **Deep Work Sessions**: Utilize the built-in Stopwatch and Countdown Timer to dedicate uninterrupted blocks of time to specific subjects or topics.
- **Goal Visualization**: Setting a goal is the first step; tracking it is the next. StudyTrack's dynamic dashboards and progress rings clearly depict the hours you've conquered versus what's left for the day, week, or month.
- **Momentum Building**: The prominent Study Streak tracking motivates you to show up every single day. 

**Track Your Learning Journey**
- **Knowledge Management**: Unlike simple timers, StudyTrack includes a fully integrated, hierarchical **Notes Module**. Create folders, drag-and-drop files, and write comprehensive study notes in a rich Markdown editor. Your study sessions and the knowledge you gain live under the same roof.
- **Categorized Sessions**: Tag every study session with a specific topic or objective. Over time, you build a granular historical record of exactly what you studied, for how long, and when.
- **Visual Analytics**: The GitHub-style Activity Heatmap provides a powerful, at-a-glance view of your study consistency over the past year. 

---

## 🛠️ Core Features

### ⏱️ Advanced Timer & Session Tracking
- **Stopwatch & Pomodoro-style Countdown**: Highly accurate timer engine that tracks elapsed time mathematically, preventing drift and data loss even if the app crashes.
- **Session Topics**: Set a clear objective for every session before you click start.
- **Seamless Recovery**: Close the app mid-session? No problem. The timer state is preserved locally and resumes perfectly upon restart.

### 📊 Dashboard & Analytics
- **At-a-Glance Dashboard**: A beautiful summary screen featuring today's stats, active study streaks, and dynamic circular progress charts showing your daily goal completion.
- **Activity Heatmap**: A detailed visual grid tracking your daily study intensity over months and years.
- **Historical Sessions Table**: Review past sessions, sort by duration, date, or topic, and analyze where your time is going.

### 📝 Integrated Knowledge Management (Notes)
- **Hierarchical File Explorer**: Organize your learning materials with nested folders. Supports intuitive drag-and-drop mechanics.
- **Rich Markdown Editor**: Write notes efficiently using a distraction-free text editor.
- **Formatting Toolbar**: Don't want to type Markdown syntax? Use the built-in toolbar to instantly format headings, bold text, lists, check-boxes, and code blocks.
- **Auto-Save**: Never lose your thoughts. Debounced auto-saving instantly secures your notes to the local database as you type.

### ⚙️ Customizable Settings
- Manage your daily and weekly study targets dynamically.
- Control how your progress rings display and adjust application preferences to match your workflow.

---

## 🏗️ Architecture & Philosophy

StudyTrack is built on the philosophy of **"Reliability before complexity"**.

- **Offline-First & Private**: No cloud sync required, no accounts, no subscriptions. Your data lives securely on your machine using a local SQLite database.
- **Clean Architecture**: Designed with a strict layered architecture (`UI -> Services -> Repositories -> Database`), ensuring business logic is isolated and robust.
- **AI-Ready**: The backend services and data structures are purposefully built to support a future **Gemini AI Study Coach** integration, which will analyze your notes and study habits to provide personalized learning strategies.

---

## 🚀 Setup and Installation

### Requirements
- Python 3.12+
- PySide6 (UI Framework)
- SQLAlchemy (ORM)

### Development
How to run the app in development mode from source:
1. **Clone the repository**:
   ```bash
   git clone https://github.com/parth-17512/Study-Tracker-Agent.git
   cd Study-Tracker-Agent
   ```
2. **Create and activate virtual environment**:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the application**:
   ```bash
   python main.py
   ```

### Build (Creating an Executable)
You can package StudyTrack into a standalone Windows `.exe`.
```bash
python build.py
```
This script automates PyInstaller and produces:
- A directory build (`dist/StudyTrack/StudyTrack.exe`)
- A single-file executable (`dist/StudyTrack.exe`)

---

## 🗄️ User Data & Backups

StudyTrack is built around **privacy and data safety**. Your persistent user data is **never** bundled inside the temporary `.exe` directory.

All persistent data is stored securely in your Windows profile:
`%LOCALAPPDATA%\StudyTrack\`

This directory contains:
- `studytrack.db` (Your entire study history and raw notes)
- `logs\` (Application diagnostic logs)
- `exports\` (Any exported data)
- `settings.json` (Your application preferences)

### Backups & Updates
**Updating the app is safe!** Because your data lives in `%LOCALAPPDATA%`, you can download a new version of `StudyTrack.exe`, replace the old one, and launch it without losing any of your study streaks or notes.

To manually back up your data, simply copy the `%LOCALAPPDATA%\StudyTrack\` folder to a secure location (like a USB drive or cloud storage).

---

*Build a better you, one session at a time.*

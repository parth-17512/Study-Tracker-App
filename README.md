# StudyTrack V2: Build a Better You 🚀

StudyTrack is a comprehensive, offline-first personal desktop application designed to supercharge your productivity, rigorously track your study time, and organize your learning materials. With the massive **V2 Upgrade**, StudyTrack evolves from a simple tracker into an intelligent, AI-powered learning ecosystem with beautiful modern aesthetics, gamification, and deep analytical capabilities.

Whether you are a student preparing for exams, a professional upskilling, or a lifelong learner, StudyTrack provides the structure, insights, and motivation needed to achieve your goals consistently.

---

## 🌟 What's New in V2? (The AI Revolution)

StudyTrack V2 introduces a suite of cutting-edge AI features, seamless UI/UX redesigns, and robust gamification designed to keep you engaged and on track.

### 🤖 AI-Powered Study Coach (RAG Integration)
- **Deep Note Context (RAG):** The built-in AI Study Coach doesn't just give generic advice. It uses **Retrieval-Augmented Generation (ChromaDB)** to read and search through your personal Markdown notes. Ask it to "Summarize my notes on Calculus" and it will read your actual documents to construct the answer!
- **Intelligent Intent Routing:** Powered by **TypeSafe AI's Jev model**, the AI router accurately determines what you are asking for lightning fast, instantly routing you to stats, note retrieval, or general chat.
- **Persistent Chat History:** Your conversations with the Coach are saved locally. You can revisit past study strategies or seamlessly pick up where you left off. 
- **AI Formatting Assistant:** Inside the Notes Editor, click the AI Format button to instantly correct spelling, fix broken list numbering, and beautifully format your raw notes using AI.

### 🧠 Advanced AI Analytical Tool
- **Streaming Live Insights:** Navigate to the Analytics tab to generate a deep-dive AI report on your study habits.
- **Actionable Feedback:** The AI aggregates your lifetime stats, week-over-week trends, and subject distribution to identify your **Strengths**, **Weaknesses**, and actionable steps to increase your focus time. The response streams beautifully into the UI in real-time Markdown.

### 🎮 Gamification & XP System
- **Study to Level Up:** Every focused session you complete earns you XP based on the duration. 
- **Level Progression:** Watch your level increase on the completely redesigned Dashboard. Gamifying your study habits makes consistency addictive and rewarding.

### 🎨 Premium Visual Redesign
- **Polished Dashboard:** The entire dashboard has been rebuilt into a clean, modern, and responsive 2x2 grid layout.
- **Typographic Hierarchy:** Stunning typography, sleek horizontal progress bars, and subtle aesthetic touches make the app feel like a premium, production-ready tool.
- **Beautiful Heatmap:** A GitHub-style Activity Heatmap tracks your daily study intensity over months and years.

---

## 🛠️ Core Features

### ⏱️ Advanced Timer & Session Tracking
- **Stopwatch & Pomodoro-style Countdown:** Highly accurate timer engine that tracks elapsed time mathematically, preventing drift and data loss even if the app crashes.
- **Seamless Recovery:** Close the app mid-session? No problem. The timer state is preserved locally and resumes perfectly upon restart.

### 📝 Integrated Knowledge Management (Notes)
- **Hierarchical File Explorer:** Organize your learning materials with nested folders. Supports intuitive drag-and-drop mechanics.
- **Rich Markdown Editor:** Write notes efficiently using a distraction-free text editor with a built-in formatting toolbar and live UI Markdown rendering.
- **Auto-Save:** Never lose your thoughts. Debounced auto-saving instantly secures your notes to the local database as you type.

### ⚙️ Rock-Solid Architecture
- **Offline-First & Private:** No cloud sync required, no accounts, no subscriptions. Your data lives securely on your machine using a local SQLite database.
- **Safe Migrations:** V2 includes an automated database migration engine that detects older schema versions, safely backs up your legacy data, and seamlessly upgrades it without data loss.

---

## 🚀 Setup and Installation

### Requirements
- Python 3.12+
- PySide6 (UI Framework)
- SQLAlchemy (ORM)
- google-genai, chromadb, sentence-transformers (AI & RAG)

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
4. **Configure API Keys (In-App)**:
   - Launch the app, navigate to **Settings**, and enter your **Google Gemini API Key** and **TypeSafe API Key** to enable the AI features.
5. **Run the application**:
   ```bash
   python main.py
   ```

### Build (Creating an Executable)
You can package StudyTrack into a standalone Windows `.exe`.
```bash
python build.py
```
This script automates PyInstaller and produces a single-file executable (`dist/StudyTrack.exe`).

---

## 🗄️ User Data & Backups

StudyTrack is built around **privacy and data safety**. Your persistent user data is **never** bundled inside the temporary `.exe` directory.

All persistent data is stored securely in your Windows profile:
`%APPDATA%\StudyTrack\` (e.g., `C:\Users\<username>\AppData\Roaming\StudyTrack\`)

This ensures that upgrading to future versions of StudyTrack will **never** overwrite your study sessions, XP, or notes!

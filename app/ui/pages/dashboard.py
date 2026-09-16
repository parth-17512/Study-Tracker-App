from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
from PySide6.QtCore import Qt
from datetime import datetime, timezone
from app.ui.theme import Theme
from app.ui.components.card import Card
from app.services.analytics_service import AnalyticsService

class DashboardPage(QWidget):
    """The main dashboard page showing summary analytics."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.analytics_service = AnalyticsService()
        
        # Hardcode a daily goal for now (e.g. 2 hours). Will move to Settings later.
        self.daily_goal_seconds = 2 * 3600 
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(Theme.SPACING_LARGE, Theme.SPACING_LARGE, Theme.SPACING_LARGE, Theme.SPACING_LARGE)
        self.layout.setSpacing(Theme.SPACING_LARGE)
        
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        # 1. Welcome Header
        self.lbl_welcome = QLabel("Welcome back, User!")
        self.lbl_welcome.setStyleSheet(f"color: {Theme.TEXT_PRIMARY}; font-size: 28px; font-weight: bold;")
        self.layout.addWidget(self.lbl_welcome)
        
        # 2. Metrics Row
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(Theme.SPACING_LARGE)
        
        # 2a. Daily Progress Card
        self.progress_card = Card()
        progress_layout = QVBoxLayout()
        
        lbl_progress_title = QLabel("Daily Goal Progress")
        lbl_progress_title.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-weight: bold;")
        progress_layout.addWidget(lbl_progress_title)
        
        self.lbl_progress_text = QLabel("0h 0m / 2h 0m")
        self.lbl_progress_text.setStyleSheet(f"color: {Theme.TEXT_PRIMARY}; font-size: 24px; font-weight: bold;")
        progress_layout.addWidget(self.lbl_progress_text)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {Theme.BACKGROUND_DARK};
                border: none;
                border-radius: 4px;
                height: 12px;
                text-align: center;
                color: transparent;
            }}
            QProgressBar::chunk {{
                background-color: {Theme.PRIMARY_ACCENT};
                border-radius: 4px;
            }}
        """)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_card.addLayout(progress_layout)
        metrics_layout.addWidget(self.progress_card, stretch=2)
        
        # 2b. Streak Card
        self.streak_card = Card()
        streak_layout = QVBoxLayout()
        
        lbl_streak_title = QLabel("Current Streak")
        lbl_streak_title.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-weight: bold;")
        streak_layout.addWidget(lbl_streak_title)
        
        self.lbl_streak = QLabel("0 Days \U0001F525") # Fire emoji
        self.lbl_streak.setStyleSheet(f"color: {Theme.WARNING_COLOR}; font-size: 36px; font-weight: bold;")
        streak_layout.addWidget(self.lbl_streak)
        
        self.streak_card.addLayout(streak_layout)
        metrics_layout.addWidget(self.streak_card, stretch=1)
        
        self.layout.addLayout(metrics_layout)
        
        # 3. Bottom Row (Recent + Chart)
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(Theme.SPACING_LARGE)
        
        # 3a. Recent Sessions
        self.recent_card = Card()
        recent_layout = QVBoxLayout()
        
        lbl_recent_title = QLabel("Recent Activity")
        lbl_recent_title.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-weight: bold; margin-bottom: 8px;")
        recent_layout.addWidget(lbl_recent_title)
        
        self.recent_list_layout = QVBoxLayout()
        recent_layout.addLayout(self.recent_list_layout)
        recent_layout.addStretch()
        
        self.recent_card.addLayout(recent_layout)
        bottom_layout.addWidget(self.recent_card, stretch=1)
        
        # 3b. Heatmap Activity
        from app.ui.components.heatmap import HeatmapWidget
        self.heatmap = HeatmapWidget(daily_goal_seconds=self.daily_goal_seconds)
        self.heatmap.year_changed.connect(self.load_heatmap_data)
        self.heatmap.day_clicked.connect(self.show_daily_sessions)
        
        bottom_layout.addWidget(self.heatmap, stretch=2)
        
        self.layout.addLayout(bottom_layout)

    def load_heatmap_data(self, year: int):
        data = self.analytics_service.get_yearly_heatmap_data(year)
        self.heatmap.render_grid(year, data)

    def show_daily_sessions(self, clicked_date):
        from app.ui.components.dialogs import DailySessionsDialog
        dialog = DailySessionsDialog(clicked_date, self)
        dialog.exec()

    def load_data(self):
        """Fetch real data and update the UI."""
        now = datetime.now(timezone.utc)
        
        # Daily Total
        daily_seconds = self.analytics_service.get_daily_total_seconds(now)
        h = daily_seconds // 3600
        m = (daily_seconds % 3600) // 60
        
        goal_h = self.daily_goal_seconds // 3600
        goal_m = (self.daily_goal_seconds % 3600) // 60
        
        self.lbl_progress_text.setText(f"{h}h {m}m / {goal_h}h {goal_m}m")
        
        percentage = min(int((daily_seconds / self.daily_goal_seconds) * 100), 100) if self.daily_goal_seconds > 0 else 0
        self.progress_bar.setValue(percentage)
        
        if percentage >= 100:
            self.progress_bar.setStyleSheet(self.progress_bar.styleSheet().replace(Theme.PRIMARY_ACCENT, Theme.SUCCESS_COLOR))
        
        # Streak
        streak = self.analytics_service.calculate_current_streak(now)
        self.lbl_streak.setText(f"{streak} Days \U0001F525")
        
        # Recent Sessions
        recent = self.analytics_service.get_recent_sessions(limit=3)
        
        # Heatmap
        self.load_heatmap_data(self.heatmap.current_year)
        
        # Clear existing
        while self.recent_list_layout.count():
            child = self.recent_list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        if not recent:
            lbl_empty = QLabel("No recent sessions. Start studying!")
            lbl_empty.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-style: italic;")
            self.recent_list_layout.addWidget(lbl_empty)
        else:
            for session in recent:
                from app.utils.time_utils import to_local_time
                local_start = to_local_time(session.start_time)
                date_str = local_start.strftime("%b %d, %H:%M") if local_start else ""
                dur = session.duration_seconds or 0
                dur_str = f"{dur//3600}h {(dur%3600)//60}m" if dur >= 3600 else f"{dur//60}m"
                topic = session.topic or "Focus Session"
                
                lbl = QLabel(f"• {date_str} - {topic} ({dur_str})")
                lbl.setStyleSheet(f"color: {Theme.TEXT_PRIMARY}; margin-bottom: 4px;")
                self.recent_list_layout.addWidget(lbl)

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QScrollArea, QSpinBox
from PySide6.QtCore import Qt
from datetime import datetime, timezone
from app.ui.theme import Theme
from app.ui.components.card import Card
from app.ui.components.button import PrimaryButton
from app.services.analytics_service import AnalyticsService
from app.config.config_manager import ConfigManager

class DashboardPage(QWidget):
    """The main dashboard page showing summary analytics."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.analytics_service = AnalyticsService()
        self.config = ConfigManager()
        
        self.daily_goal_seconds = self.config.get("daily_goal_seconds", 2 * 3600) 
        
        # Outer layout holds a scroll area
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea { background-color: transparent; border: none; }
        """)
        
        scroll_content = QWidget()
        scroll_content.setMinimumWidth(650)
        self.layout = QVBoxLayout(scroll_content)
        self.layout.setContentsMargins(Theme.SPACING_LARGE, Theme.SPACING_LARGE, Theme.SPACING_LARGE, Theme.SPACING_LARGE)
        self.layout.setSpacing(Theme.SPACING_LARGE)
        
        scroll_area.setWidget(scroll_content)
        outer_layout.addWidget(scroll_area)
        
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
        lbl_progress_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        progress_layout.addWidget(lbl_progress_title)
        
        from app.ui.components.progress_pie import ProgressPieChart
        self.progress_pie = ProgressPieChart()
        progress_layout.addWidget(self.progress_pie, alignment=Qt.AlignmentFlag.AlignCenter, stretch=1)
        
        self.lbl_progress_text = QLabel("0h 0m / 2h 0m")
        self.lbl_progress_text.setStyleSheet(f"color: {Theme.TEXT_PRIMARY}; font-size: 18px; font-weight: bold;")
        self.lbl_progress_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        progress_layout.addWidget(self.lbl_progress_text)
        
        self.progress_card.addLayout(progress_layout)
        metrics_layout.addWidget(self.progress_card, stretch=2)
        
        # 2b. Set Goal Card
        self.goal_card = Card()
        goal_layout = QVBoxLayout()
        
        lbl_goal_title = QLabel("Set Daily Goal")
        lbl_goal_title.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-weight: bold;")
        goal_layout.addWidget(lbl_goal_title)
        
        spin_layout = QHBoxLayout()
        self.spin_goal_h = QSpinBox()
        self.spin_goal_h.setRange(0, 24)
        self.spin_goal_h.setSuffix("h")
        self.spin_goal_h.setStyleSheet(f"background-color: {Theme.BACKGROUND_DARK}; color: {Theme.TEXT_PRIMARY}; padding: 4px;")
        
        self.spin_goal_m = QSpinBox()
        self.spin_goal_m.setRange(0, 59)
        self.spin_goal_m.setSuffix("m")
        self.spin_goal_m.setStyleSheet(f"background-color: {Theme.BACKGROUND_DARK}; color: {Theme.TEXT_PRIMARY}; padding: 4px;")
        
        self.spin_goal_h.setValue(self.daily_goal_seconds // 3600)
        self.spin_goal_m.setValue((self.daily_goal_seconds % 3600) // 60)
        
        spin_layout.addWidget(self.spin_goal_h)
        spin_layout.addWidget(self.spin_goal_m)
        goal_layout.addLayout(spin_layout)
        
        self.btn_set_goal = PrimaryButton("Update")
        self.btn_set_goal.clicked.connect(self.update_daily_goal)
        goal_layout.addWidget(self.btn_set_goal)
        
        self.goal_card.addLayout(goal_layout)
        metrics_layout.addWidget(self.goal_card, stretch=1)
        
        # 2c. Streak Card
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

    def update_daily_goal(self):
        h = self.spin_goal_h.value()
        m = self.spin_goal_m.value()
        new_seconds = h * 3600 + m * 60
        if new_seconds > 0:
            self.daily_goal_seconds = new_seconds
            self.config.set("daily_goal_seconds", self.daily_goal_seconds)
            self.heatmap.daily_goal_seconds = self.daily_goal_seconds
            self.load_data()

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
        
        self.progress_pie.set_data(daily_seconds, self.daily_goal_seconds)
        
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

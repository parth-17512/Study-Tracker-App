from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QProgressBar, QScrollArea, QSpinBox
from PySide6.QtCore import Qt, QTimer
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
        
        self.daily_goal_seconds = self.config.get("daily_goal_seconds", 6 * 3600)
        self.goal_unlock_timer = QTimer(self)
        self.goal_unlock_timer.setSingleShot(True)
        self.goal_unlock_timer.timeout.connect(self._refresh_daily_goal_controls)
        
        # Outer layout holds a scroll area
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("QScrollArea { background-color: transparent; border: none; }")
        
        scroll_content = QWidget()
        self.layout = QVBoxLayout(scroll_content)
        self.layout.setContentsMargins(Theme.SPACING_LARGE, Theme.SPACING_LARGE, Theme.SPACING_LARGE, Theme.SPACING_LARGE)
        self.layout.setSpacing(Theme.SPACING_LARGE)
        
        scroll_area.setWidget(scroll_content)
        outer_layout.addWidget(scroll_area)
        
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        # 1. Header
        now = datetime.now(timezone.utc)
        header_layout = QVBoxLayout()
        self.lbl_welcome = QLabel("Good evening, Watcher")
        self.lbl_welcome.setStyleSheet(f"color: {Theme.TEXT_PRIMARY}; font-size: 32px; font-weight: bold;")
        
        lbl_date = QLabel(now.strftime("%B %d, %Y"))
        lbl_date.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-size: 16px; margin-bottom: 12px;")
        
        header_layout.addWidget(self.lbl_welcome)
        header_layout.addWidget(lbl_date)
        self.layout.addLayout(header_layout)
        
        # 2. Grid for Top 4 Cards
        grid = QGridLayout()
        grid.setSpacing(Theme.SPACING_LARGE)
        
        # 2a. Study Time Card
        self.study_time_card = Card()
        study_time_layout = QVBoxLayout()
        
        lbl_st_title = QLabel("FOCUSED STUDY")
        lbl_st_title.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-weight: bold; font-size: 12px; letter-spacing: 1px;")
        study_time_layout.addWidget(lbl_st_title)
        
        self.lbl_study_time = QLabel("0h 0m")
        self.lbl_study_time.setStyleSheet(f"color: {Theme.TEXT_PRIMARY}; font-size: 42px; font-weight: bold; margin: 8px 0px;")
        study_time_layout.addWidget(self.lbl_study_time)
        
        self.lbl_study_context = QLabel("0% of daily target")
        self.lbl_study_context.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-size: 14px;")
        study_time_layout.addWidget(self.lbl_study_context)
        
        self.study_progress = QProgressBar()
        self.study_progress.setFixedHeight(8)
        self.study_progress.setTextVisible(False)
        self.study_progress.setStyleSheet(f"QProgressBar {{ background-color: {Theme.BACKGROUND_DARK}; border: none; border-radius: 4px; }} QProgressBar::chunk {{ background-color: {Theme.PRIMARY_ACCENT}; border-radius: 4px; }}")
        self.study_progress.setMaximum(100)
        self.study_progress.setValue(0)
        study_time_layout.addWidget(self.study_progress)
        
        study_time_layout.addStretch()
        self.study_time_card.addLayout(study_time_layout)
        grid.addWidget(self.study_time_card, 0, 0)
        
        # 2b. Daily Goal Card
        self.goal_card = Card()
        goal_layout = QVBoxLayout()
        
        lbl_goal_title = QLabel("DAILY GOAL")
        lbl_goal_title.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-weight: bold; font-size: 12px; letter-spacing: 1px;")
        goal_layout.addWidget(lbl_goal_title)
        
        self.lbl_goal_progress = QLabel("0h / 0h")
        self.lbl_goal_progress.setStyleSheet(f"color: {Theme.TEXT_PRIMARY}; font-size: 42px; font-weight: bold; margin: 8px 0px;")
        goal_layout.addWidget(self.lbl_goal_progress)
        
        spin_layout = QHBoxLayout()
        self.spin_goal_h = QSpinBox()
        self.spin_goal_h.setRange(0, 24)
        self.spin_goal_h.setSuffix("h")
        self.spin_goal_h.setStyleSheet(f"background-color: {Theme.BACKGROUND_DARK}; color: {Theme.TEXT_PRIMARY}; padding: 4px; font-size: 14px; border-radius: 4px;")
        
        self.spin_goal_m = QSpinBox()
        self.spin_goal_m.setRange(0, 59)
        self.spin_goal_m.setSuffix("m")
        self.spin_goal_m.setStyleSheet(f"background-color: {Theme.BACKGROUND_DARK}; color: {Theme.TEXT_PRIMARY}; padding: 4px; font-size: 14px; border-radius: 4px;")
        
        self.spin_goal_h.setValue(self.daily_goal_seconds // 3600)
        self.spin_goal_m.setValue((self.daily_goal_seconds % 3600) // 60)
        
        spin_layout.addWidget(self.spin_goal_h)
        spin_layout.addWidget(self.spin_goal_m)
        
        self.btn_set_goal = PrimaryButton("Update")
        self.btn_set_goal.clicked.connect(self.update_daily_goal)
        spin_layout.addWidget(self.btn_set_goal)
        spin_layout.addStretch()
        
        goal_layout.addLayout(spin_layout)
        self.lbl_goal_limit = QLabel()
        self.lbl_goal_limit.setWordWrap(True)
        self.lbl_goal_limit.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-size: 12px;")
        goal_layout.addWidget(self.lbl_goal_limit)
        goal_layout.addStretch()
        self.goal_card.addLayout(goal_layout)
        grid.addWidget(self.goal_card, 0, 1)
        
        # 2c. Streak Card
        self.streak_card = Card()
        streak_layout = QVBoxLayout()
        
        lbl_streak_title = QLabel("🔥 CURRENT STREAK")
        lbl_streak_title.setStyleSheet(f"color: {Theme.WARNING_COLOR}; font-weight: bold; font-size: 12px; letter-spacing: 1px;")
        streak_layout.addWidget(lbl_streak_title)
        
        self.lbl_streak = QLabel("0 DAYS")
        self.lbl_streak.setStyleSheet(f"color: {Theme.TEXT_PRIMARY}; font-size: 42px; font-weight: bold; margin: 8px 0px;")
        streak_layout.addWidget(self.lbl_streak)
        
        lbl_streak_sub = QLabel("Keep the momentum going")
        lbl_streak_sub.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-size: 14px;")
        streak_layout.addWidget(lbl_streak_sub)
        
        streak_layout.addStretch()
        self.streak_card.addLayout(streak_layout)
        grid.addWidget(self.streak_card, 1, 0)
        
        # 2d. XP Card
        self.xp_card = Card()
        xp_layout = QVBoxLayout()
        
        lbl_xp_title = QLabel("🎮 STUDY XP")
        lbl_xp_title.setStyleSheet(f"color: {Theme.SUCCESS_COLOR}; font-weight: bold; font-size: 12px; letter-spacing: 1px;")
        xp_layout.addWidget(lbl_xp_title)
        
        self.lbl_xp = QLabel("0 XP")
        self.lbl_xp.setStyleSheet(f"color: {Theme.TEXT_PRIMARY}; font-size: 42px; font-weight: bold; margin: 8px 0px;")
        xp_layout.addWidget(self.lbl_xp)
        
        self.lbl_level = QLabel("Level 1 (0 Total XP)")
        self.lbl_level.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-size: 14px;")
        xp_layout.addWidget(self.lbl_level)
        
        self.xp_progress = QProgressBar()
        self.xp_progress.setFixedHeight(8)
        self.xp_progress.setTextVisible(False)
        self.xp_progress.setStyleSheet(f"QProgressBar {{ background-color: {Theme.BACKGROUND_DARK}; border: none; border-radius: 4px; }} QProgressBar::chunk {{ background-color: {Theme.SUCCESS_COLOR}; border-radius: 4px; }}")
        self.xp_progress.setMaximum(100)
        self.xp_progress.setValue(0)
        xp_layout.addWidget(self.xp_progress)
        
        xp_layout.addStretch()
        self.xp_card.addLayout(xp_layout)
        grid.addWidget(self.xp_card, 1, 1)
        
        # Add grid to main layout
        self.layout.addLayout(grid)
        
        # 3. Full-width study contribution graph
        heatmap_card = Card()
        heatmap_layout = QVBoxLayout()
        
        lbl_heatmap_title = QLabel("ACTIVITY MAP")
        lbl_heatmap_title.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-weight: bold; font-size: 12px; letter-spacing: 1px; margin-bottom: 8px;")
        heatmap_layout.addWidget(lbl_heatmap_title)
        
        from app.ui.components.heatmap import HeatmapWidget
        self.heatmap = HeatmapWidget(daily_goal_seconds=self.daily_goal_seconds)
        self.heatmap.setMinimumHeight(260)
        self.heatmap.year_changed.connect(self.load_heatmap_data)
        self.heatmap.day_clicked.connect(self.show_daily_sessions)
        
        heatmap_layout.addWidget(self.heatmap)
        heatmap_card.addLayout(heatmap_layout)
        self.layout.addWidget(heatmap_card, stretch=1)
        self.layout.addStretch()

    def update_daily_goal(self):
        h = self.spin_goal_h.value()
        m = self.spin_goal_m.value()
        new_seconds = h * 3600 + m * 60
        if new_seconds <= 0:
            self.lbl_goal_limit.setText("Daily goal must be greater than zero.")
            self.lbl_goal_limit.setStyleSheet(f"color: {Theme.WARNING_COLOR}; font-size: 12px;")
            return

        if new_seconds == self.daily_goal_seconds:
            self.lbl_goal_limit.setText(
                "Your daily goal is unchanged, so the weekly change limit was not used."
            )
            return

        if not self.config.can_change_daily_goal():
            self._refresh_daily_goal_controls()
            return

        if not self.config.update_daily_goal(new_seconds):
            self.lbl_goal_limit.setText("The daily goal could not be saved. Please try again.")
            self.lbl_goal_limit.setStyleSheet(f"color: {Theme.WARNING_COLOR}; font-size: 12px;")
            return

        self.daily_goal_seconds = new_seconds
        self.heatmap.daily_goal_seconds = new_seconds
        self._refresh_daily_goal_controls()
        self.load_data()

    def _refresh_daily_goal_controls(self):
        self.goal_unlock_timer.stop()
        available_at = self.config.get_daily_goal_change_available_at()
        now = datetime.now(timezone.utc)
        can_change = available_at is None or now >= available_at

        self.spin_goal_h.setEnabled(can_change)
        self.spin_goal_m.setEnabled(can_change)
        self.btn_set_goal.setEnabled(can_change)

        if can_change:
            self.lbl_goal_limit.setText(
                "You can change your daily goal once every 7 days. Saving a new goal starts the 7-day cooldown."
            )
            self.lbl_goal_limit.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-size: 12px;")
            return

        unlock_local = available_at.astimezone()
        unlock_text = unlock_local.strftime("%b %d, %Y at %I:%M %p")
        self.lbl_goal_limit.setText(
            f"You can change your daily goal once every 7 days. Your next change will be available on {unlock_text}."
        )
        self.lbl_goal_limit.setStyleSheet(f"color: {Theme.WARNING_COLOR}; font-size: 12px;")
        milliseconds_until_unlock = max(1, int((available_at - now).total_seconds() * 1000) + 1)
        self.goal_unlock_timer.start(milliseconds_until_unlock)

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
        
        # Header Greeting
        hour = now.astimezone().hour
        greeting = "Good evening"
        if hour < 12: greeting = "Good morning"
        elif hour < 17: greeting = "Good afternoon"
        self.lbl_welcome.setText(f"{greeting}, Watcher")
        
        # Daily Total
        daily_seconds = self.analytics_service.get_daily_total_seconds(now)
        h = daily_seconds // 3600
        m = (daily_seconds % 3600) // 60
        
        goal_h = self.daily_goal_seconds // 3600
        goal_m = (self.daily_goal_seconds % 3600) // 60
        
        pct = 0
        if self.daily_goal_seconds > 0:
            pct = int((daily_seconds / self.daily_goal_seconds) * 100)
        if pct > 100: pct = 100
        
        self.lbl_study_time.setText(f"{h}h {m}m" if h > 0 else f"{m}m")
        self.lbl_study_context.setText(f"{pct}% of daily target")
        self.study_progress.setValue(pct)
        
        self.lbl_goal_progress.setText(f"{h}h {m}m / {goal_h}h {goal_m}m")
        
        # Streak
        streak = self.analytics_service.calculate_current_streak(now)
        self.lbl_streak.setText(f"{streak} DAYS")
        
        # XP
        from app.services.xp_service import XPService
        xp_service = XPService()
        total_xp = xp_service.get_total_xp()
        level, current_xp, req = xp_service.calculate_level(total_xp)
        
        self.lbl_xp.setText(f"{current_xp} XP")
        self.lbl_level.setText(f"Level {level}  •  {total_xp} Total XP")
        self.xp_progress.setMaximum(req)
        self.xp_progress.setValue(current_xp)
        
        # Heatmap
        self.load_heatmap_data(self.heatmap.current_year)
        self._refresh_daily_goal_controls()

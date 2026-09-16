from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from datetime import datetime, timezone
from app.ui.theme import Theme
from app.ui.components.calendar_widget import StudyCalendarWidget
from app.services.analytics_service import AnalyticsService

class CalendarPage(QWidget):
    """The Calendar page for viewing study history by month."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.analytics_service = AnalyticsService()
        
        from PySide6.QtWidgets import QScrollArea
        
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("QScrollArea { background-color: transparent; border: none; }")
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        self.layout = QVBoxLayout(scroll_content)
        self.layout.setContentsMargins(Theme.SPACING_LARGE, Theme.SPACING_LARGE, Theme.SPACING_LARGE, Theme.SPACING_LARGE)
        self.layout.setSpacing(Theme.SPACING_LARGE)
        
        scroll_area.setWidget(scroll_content)
        outer_layout.addWidget(scroll_area)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Header
        lbl_title = QLabel("Study Calendar")
        lbl_title.setStyleSheet(f"color: {Theme.TEXT_PRIMARY}; font-size: 28px; font-weight: bold;")
        self.layout.addWidget(lbl_title)
        
        lbl_subtitle = QLabel("Review your daily sessions and goal streaks.")
        lbl_subtitle.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-size: 14px; margin-bottom: {Theme.SPACING_REGULAR}px;")
        self.layout.addWidget(lbl_subtitle)
        
        # Calendar Widget
        from app.config.config_manager import ConfigManager
        config = ConfigManager()
        goal_secs = config.get("daily_goal_seconds", 7200)
        
        self.calendar = StudyCalendarWidget(daily_goal_seconds=goal_secs)
        self.calendar.month_changed_event.connect(self.load_month_data)
        self.calendar.day_clicked_event.connect(self.show_daily_sessions)
        
        self.layout.addWidget(self.calendar)
        
    def load_data(self):
        """Called automatically when navigating to this page."""
        # Load the data for the currently displayed month
        year = self.calendar.yearShown()
        month = self.calendar.monthShown()
        self.load_month_data(year, month)
        
    def load_month_data(self, year: int, month: int):
        data = self.analytics_service.get_monthly_study_data(year, month)
        self.calendar.update_data(data)
        
    def show_daily_sessions(self, clicked_date):
        from app.ui.components.dialogs import DailySessionsDialog
        dialog = DailySessionsDialog(clicked_date, self)
        dialog.exec()

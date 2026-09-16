from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from datetime import datetime, timezone
from app.ui.theme import Theme
from app.ui.components.calendar_widget import StudyCalendarWidget
from app.services.analytics_service import AnalyticsService

class CalendarPage(QWidget):
    """The Calendar page for viewing study history by month."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.analytics_service = AnalyticsService()
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(Theme.SPACING_LARGE, Theme.SPACING_LARGE, Theme.SPACING_LARGE, Theme.SPACING_LARGE)
        self.layout.setSpacing(Theme.SPACING_LARGE)
        
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
        # Hardcoding daily goal for now until Settings are implemented
        self.calendar = StudyCalendarWidget(daily_goal_seconds=7200)
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

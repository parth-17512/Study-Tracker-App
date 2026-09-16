from PySide6.QtWidgets import QCalendarWidget
from PySide6.QtCore import Qt, QRect, Signal, QDate
from PySide6.QtGui import QPainter, QColor, QFont, QPen
from datetime import date
from app.ui.theme import Theme

class StudyCalendarWidget(QCalendarWidget):
    """Custom Calendar Widget that paints study intensity markers."""
    
    day_clicked_event = Signal(date)
    month_changed_event = Signal(int, int) # year, month
    
    def __init__(self, daily_goal_seconds: int = 7200, parent=None):
        super().__init__(parent)
        self.daily_goal_seconds = daily_goal_seconds
        self.monthly_data = {}
        
        # Styling the calendar widget to match our dark theme
        self.setStyleSheet(f"""
            QCalendarWidget QWidget {{
                alternate-background-color: {Theme.BACKGROUND_CARD};
                background-color: {Theme.BACKGROUND_CARD};
                color: {Theme.TEXT_PRIMARY};
            }}
            QCalendarWidget QToolButton {{
                background-color: {Theme.BACKGROUND_CARD};
                color: {Theme.TEXT_PRIMARY};
                font-weight: bold;
                border: none;
                padding: 4px;
            }}
            QCalendarWidget QToolButton:hover {{
                background-color: {Theme.BACKGROUND_DARK};
            }}
            QCalendarWidget QMenu {{
                background-color: {Theme.BACKGROUND_CARD};
                color: {Theme.TEXT_PRIMARY};
            }}
            QCalendarWidget QSpinBox {{
                background-color: {Theme.BACKGROUND_DARK};
                color: {Theme.TEXT_PRIMARY};
            }}
            QCalendarWidget QAbstractItemView:enabled {{
                background-color: {Theme.BACKGROUND_DARK};
                color: {Theme.TEXT_PRIMARY};
                selection-background-color: {Theme.PRIMARY_ACCENT};
                selection-color: {Theme.TEXT_PRIMARY};
            }}
            QCalendarWidget QAbstractItemView:disabled {{
                color: {Theme.TEXT_SECONDARY};
            }}
        """)
        
        self.setGridVisible(True)
        self.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        self.setHorizontalHeaderFormat(QCalendarWidget.HorizontalHeaderFormat.ShortDayNames)
        
        # Connect signals
        self.clicked.connect(self.on_day_clicked)
        self.currentPageChanged.connect(self.on_page_changed)
        
    def update_data(self, data: dict):
        self.monthly_data = data
        self.updateCells() # Forces a repaint
        
    def paintCell(self, painter: QPainter, rect: QRect, date_obj: QDate):
        """Override to paint study indicators on the calendar cells."""
        # Call the base class to draw the default text and selection highlights
        super().paintCell(painter, rect, date_obj)
        
        # Convert QDate to Python date
        py_date = date(date_obj.year(), date_obj.month(), date_obj.day())
        
        # Check if we have data for this day
        duration = self.monthly_data.get(py_date, 0)
        
        if duration > 0:
            painter.save()
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # Determine color intensity
            ratio = duration / max(self.daily_goal_seconds, 1)
            if ratio >= 1.0:
                color = QColor(Theme.SUCCESS_COLOR) # Hit goal
            elif ratio >= 0.5:
                color = QColor(Theme.PRIMARY_ACCENT) # Good effort
            else:
                color = QColor(Theme.PRIMARY_ACCENT).darker(150) # Some effort
                
            # Draw a small indicator circle at the bottom center of the cell
            radius = 4
            x = rect.x() + (rect.width() // 2)
            y = rect.bottom() - 8
            
            painter.setBrush(color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(x - radius, y - radius, radius * 2, radius * 2)
            
            painter.restore()

    def on_day_clicked(self, qdate: QDate):
        py_date = date(qdate.year(), qdate.month(), qdate.day())
        self.day_clicked_event.emit(py_date)
        
    def on_page_changed(self, year: int, month: int):
        self.month_changed_event.emit(year, month)

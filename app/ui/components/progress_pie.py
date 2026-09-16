from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QPen, QFont
from PySide6.QtCore import Qt, QRectF
from app.ui.theme import Theme

class ProgressPieChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(120, 120)
        self.studied_seconds = 0
        self.goal_seconds = 1
        
    def set_data(self, studied_seconds: int, goal_seconds: int):
        self.studied_seconds = studied_seconds
        self.goal_seconds = goal_seconds
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Calculate dimensions to keep it a circle
        size = min(self.width(), self.height())
        padding = 10
        rect = QRectF((self.width() - size) / 2 + padding, (self.height() - size) / 2 + padding, size - 2*padding, size - 2*padding)
        
        goal = max(self.goal_seconds, 1)
        studied = min(self.studied_seconds, goal)
        remaining = goal - studied
        
        # QPainter angles are in 1/16ths of a degree. Positive is counter-clockwise.
        # Start at 90 degrees (12 o'clock).
        start_angle = 90 * 16
        
        studied_angle = (studied / goal) * 360 * 16
        remaining_angle = 360 * 16 - studied_angle
        
        # Draw Remaining Slice (Dark Background)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(Theme.BACKGROUND_DARK))
        # Draw from the end of the studied angle
        painter.drawPie(rect, start_angle - studied_angle, -remaining_angle)
        
        # Draw Studied Slice (Accent Color)
        color = QColor(Theme.PRIMARY_ACCENT)
        if studied >= goal:
            color = QColor(Theme.SUCCESS_COLOR)
            
        painter.setBrush(color)
        if studied_angle > 0:
            painter.drawPie(rect, start_angle, -studied_angle)
            
        # Optional: Make it a Donut Chart
        inner_margin = size * 0.25 # Adjust thickness
        inner_rect = rect.adjusted(inner_margin, inner_margin, -inner_margin, -inner_margin)
        painter.setBrush(QColor(Theme.BACKGROUND_CARD))
        painter.drawEllipse(inner_rect)
        
        # Draw Percentage inside
        painter.setPen(QColor(Theme.TEXT_PRIMARY))
        font = painter.font()
        font.setBold(True)
        # Scale font based on size
        font.setPixelSize(int(size * 0.15))
        painter.setFont(font)
        
        percent = min(int((self.studied_seconds / goal) * 100), 100)
        painter.drawText(inner_rect, Qt.AlignmentFlag.AlignCenter, f"{percent}%")
        
        painter.end()

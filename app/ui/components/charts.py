from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
from PySide6.QtCore import Qt, QRect, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPainter, QColor, QFont, QPen, QBrush
from datetime import date
from app.ui.theme import Theme

class BarChartWidget(QWidget):
    """Custom Native PySide6 Vertical Bar Chart for the Last 7 Days."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(200)
        self.data_points = {} # Dict[date, int seconds]
        self.max_value = 1
        
    def set_data(self, data: dict):
        self.data_points = data
        if self.data_points:
            self.max_value = max(self.data_points.values())
        if self.max_value == 0:
            self.max_value = 1 # Avoid div by zero
        self.update()
        
    def paintEvent(self, event):
        if not self.data_points:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        
        # Dimensions
        padding_left = 40
        padding_bottom = 30
        padding_top = 20
        padding_right = 20
        
        chart_width = width - padding_left - padding_right
        chart_height = height - padding_bottom - padding_top
        
        # Draw axes
        painter.setPen(QPen(QColor(Theme.BORDER_COLOR), 1))
        painter.drawLine(padding_left, height - padding_bottom, width - padding_right, height - padding_bottom)
        
        # We have 7 days
        days = list(self.data_points.items())
        days.sort(key=lambda x: x[0]) # ensure chronological order
        
        if not days:
            return
            
        bar_width = min(40, chart_width // len(days) - 10)
        spacing = (chart_width - (bar_width * len(days))) / (len(days) + 1)
        
        # Draw bars
        painter.setFont(QFont(Theme.FONT_FAMILY, 8))
        
        for i, (d, sec) in enumerate(days):
            x = padding_left + spacing + (i * (bar_width + spacing))
            
            # Calculate bar height
            bar_h = int((sec / self.max_value) * chart_height)
            y = height - padding_bottom - bar_h
            
            # Draw bar
            # Use gradient or solid color based on today
            is_today = (i == len(days) - 1)
            color = QColor(Theme.SUCCESS_COLOR) if is_today else QColor(Theme.PRIMARY_ACCENT)
            
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(color))
            # Draw rounded rect for the bar
            painter.drawRoundedRect(int(x), int(y), int(bar_width), int(bar_h), 4, 4)
            
            # Draw X axis label
            painter.setPen(QColor(Theme.TEXT_SECONDARY))
            day_str = d.strftime("%a") # e.g. "Mon"
            text_rect = QRect(int(x), int(height - padding_bottom + 5), int(bar_width), 20)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, day_str)
            
            # Draw Tooltip text on top if there's data
            if sec > 0:
                h = sec // 3600
                m = (sec % 3600) // 60
                val_str = f"{h}h{m}m" if h > 0 else f"{m}m"
                painter.setPen(QColor(Theme.TEXT_PRIMARY))
                val_rect = QRect(int(x - 10), int(y - 20), int(bar_width + 20), 20)
                painter.drawText(val_rect, Qt.AlignmentFlag.AlignCenter, val_str)


class DistributionChartWidget(QWidget):
    """Layout-based Horizontal Bar Chart for Topic Distribution."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(Theme.SPACING_REGULAR)
        
    def set_data(self, data: dict):
        """data is dict mapping topic_name -> total_seconds"""
        # Clear layout
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        if not data:
            lbl = QLabel("No data available.")
            lbl.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-style: italic;")
            self.layout.addWidget(lbl)
            return
            
        total_seconds = sum(data.values())
        if total_seconds == 0:
            total_seconds = 1
            
        # Sort by duration descending
        sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)
        
        # Colors to cycle through
        colors = [
            Theme.PRIMARY_ACCENT,
            Theme.SECONDARY_ACCENT,
            Theme.SUCCESS_COLOR,
            Theme.WARNING_COLOR,
            "#ec4899" # Pink
        ]
        
        for i, (topic, sec) in enumerate(sorted_data):
            row = QWidget()
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            
            percentage = (sec / total_seconds) * 100
            
            # Label
            lbl_topic = QLabel(topic)
            lbl_topic.setFixedWidth(120)
            lbl_topic.setStyleSheet(f"color: {Theme.TEXT_PRIMARY}; font-weight: bold;")
            
            # Progress Bar acting as horizontal bar
            bar = QProgressBar()
            bar.setFixedHeight(12)
            bar.setTextVisible(False)
            bar.setMaximum(100)
            bar.setValue(int(percentage))
            
            color = colors[i % len(colors)]
            bar.setStyleSheet(f"""
                QProgressBar {{
                    background-color: {Theme.BACKGROUND_DARK};
                    border: none;
                    border-radius: 4px;
                }}
                QProgressBar::chunk {{
                    background-color: {color};
                    border-radius: 4px;
                }}
            """)
            
            # Value Label
            h = sec // 3600
            m = (sec % 3600) // 60
            time_str = f"{h}h {m}m" if h > 0 else f"{m}m"
            
            lbl_val = QLabel(f"{percentage:.1f}% ({time_str})")
            lbl_val.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-size: 12px;")
            
            row_layout.addWidget(lbl_topic)
            row_layout.addWidget(bar)
            row_layout.addWidget(lbl_val)
            
            self.layout.addWidget(row)
            
        self.layout.addStretch()

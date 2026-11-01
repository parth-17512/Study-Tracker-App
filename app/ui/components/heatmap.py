from PySide6.QtWidgets import (
    QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QComboBox, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from datetime import date, timedelta
from app.ui.theme import Theme

class DayCell(QFrame):
    """A single cell in the heatmap representing one day."""
    clicked = Signal(date)
    
    def __init__(self, day_date: date, parent=None):
        super().__init__(parent)
        self.day_date = day_date
        self.setFixedSize(16, 16)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("background-color: #2a2b33; border-radius: 3px;")
        
    def set_intensity(self, duration_seconds: int, daily_goal_seconds: int):
        """Sets the background color and rich tooltip based on study intensity."""
        date_str = self.day_date.strftime("%A, %b %d, %Y")
        if duration_seconds == 0:
            self.setStyleSheet("background-color: #2a2b33; border-radius: 3px;")
            self.setToolTip(f"{date_str}\nNo study activity recorded")
            return
            
        if daily_goal_seconds <= 0:
            daily_goal_seconds = 7200
            
        ratio = duration_seconds / daily_goal_seconds
        
        # GitHub-style 4-level green intensity scale
        if ratio < 0.25:
            color = "#486749"  # Level 1
            lvl_name = "Light"
        elif ratio < 0.50:
            color = "#588c5a"  # Level 2
            lvl_name = "Moderate"
        elif ratio < 0.75:
            color = "#68b26a"  # Level 3
            lvl_name = "Strong"
        else:
            color = "#7ade7f"  # Level 4
            lvl_name = "Goal Reached"
            
        self.setStyleSheet(f"background-color: {color}; border-radius: 3px;")
        
        h = duration_seconds // 3600
        m = (duration_seconds % 3600) // 60
        time_str = f"{h}h {m}m" if h > 0 else f"{m}m"
        pct_str = f"{int(ratio * 100)}%"
        self.setToolTip(f"{date_str}\n{time_str} focus time ({pct_str} of goal - {lvl_name})\nClick to view sessions")
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.day_date)
        super().mousePressEvent(event)

class HeatmapWidget(QWidget):
    """Expanded GitHub-style activity contribution graph for a full year."""
    
    day_clicked = Signal(date)
    year_changed = Signal(int)
    
    def __init__(self, daily_goal_seconds: int = 7200, parent=None):
        super().__init__(parent)
        self.daily_goal_seconds = daily_goal_seconds
        self.current_year = date.today().year
        self.setMinimumHeight(210)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(16, 16, 16, 16)
        self.main_layout.setSpacing(Theme.SPACING_REGULAR)
        
        self.setStyleSheet(f"""
            HeatmapWidget {{
                background-color: #21252b;
                border-radius: 8px;
                border: 1px solid {Theme.BORDER_COLOR};
            }}
        """)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Top Header (Title + Summary Stats + Year Selector)
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)
        
        title = QLabel("Study Consistency Contribution Graph")
        title.setStyleSheet(f"color: {Theme.TEXT_PRIMARY}; font-weight: bold; font-size: 16px; background: transparent;")
        header_layout.addWidget(title)

        self.lbl_stats = QLabel("Loading activity...")
        self.lbl_stats.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-size: 13px; background: transparent;")
        header_layout.addWidget(self.lbl_stats)
        
        header_layout.addStretch()
        
        self.year_combo = QComboBox()
        for y in range(self.current_year, self.current_year - 4, -1):
            self.year_combo.addItem(str(y), y)
        
        self.year_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {Theme.BACKGROUND_DARK};
                color: {Theme.TEXT_PRIMARY};
                border: 1px solid {Theme.BORDER_COLOR};
                border-radius: 4px;
                padding: 4px 8px;
                font-weight: bold;
            }}
        """)
        self.year_combo.currentIndexChanged.connect(self.on_year_combo_changed)
        header_layout.addWidget(self.year_combo)
        
        self.main_layout.addLayout(header_layout)
        
        # Grid Layout for the Heatmap
        self.grid_widget = QWidget()
        self.grid_widget.setStyleSheet("background: transparent;")
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setContentsMargins(0, 4, 0, 4)
        self.grid_layout.setSpacing(4)
        
        # Weekday Labels
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for r, d in enumerate(days):
            lbl = QLabel(d)
            lbl.setStyleSheet("color: #8b929c; font-size: 11px; background: transparent;")
            self.grid_layout.addWidget(lbl, r + 1, 0)
                
        self.heatmap_scroll = QScrollArea()
        self.heatmap_scroll.setWidgetResizable(True)
        self.heatmap_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.heatmap_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.heatmap_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self.heatmap_scroll.setWidget(self.grid_widget)
        
        self.main_layout.addWidget(self.heatmap_scroll, stretch=1)
        
        # Legend
        legend_layout = QHBoxLayout()
        legend_layout.addStretch()
        
        less_lbl = QLabel("Less")
        less_lbl.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-size: 11px; background: transparent;")
        legend_layout.addWidget(less_lbl)

        # Empty swatch
        empty_swatch = QFrame()
        empty_swatch.setFixedSize(14, 14)
        empty_swatch.setStyleSheet("background-color: #2a2b33; border-radius: 3px;")
        empty_swatch.setToolTip("No activity")
        legend_layout.addWidget(empty_swatch)
        
        legend_colors = ["#486749", "#588c5a", "#68b26a", "#7ade7f"]
        for color in legend_colors:
            swatch = QFrame()
            swatch.setFixedSize(14, 14)
            swatch.setStyleSheet(f"background-color: {color}; border-radius: 3px;")
            legend_layout.addWidget(swatch)
            
        more_lbl = QLabel("More")
        more_lbl.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-size: 11px; background: transparent;")
        legend_layout.addWidget(more_lbl)
        
        self.main_layout.addLayout(legend_layout)
        
        self.cells = {}

    def on_year_combo_changed(self, index):
        year = self.year_combo.currentData()
        if year != self.current_year:
            self.current_year = year
            self.year_changed.emit(year)

    def render_grid(self, year: int, data: dict):
        """Builds the 365/366 day grid for the given year and updates summary."""
        for cell in self.cells.values():
            self.grid_layout.removeWidget(cell)
            cell.deleteLater()
        self.cells.clear()
        
        # Compute summary stats for the year
        total_seconds = sum(data.values())
        active_days = sum(1 for s in data.values() if s > 0)
        total_h = total_seconds // 3600
        total_m = (total_seconds % 3600) // 60
        dur_str = f"{total_h}h {total_m}m" if total_h > 0 else f"{total_m}m"
        
        self.lbl_stats.setText(f"• {active_days} active study days • {dur_str} total focus in {year}")

        start_date = date(year, 1, 1)
        day_of_week = start_date.weekday()
        current_date = start_date
        
        col = 1
        row = day_of_week + 1
        months_added = set()
        
        while current_date.year == year:
            if current_date.day == 1 or (current_date == start_date):
                if current_date.month not in months_added:
                    m_lbl = QLabel(current_date.strftime("%b"))
                    m_lbl.setStyleSheet("color: #8b929c; font-size: 11px; font-weight: bold; background: transparent;")
                    self.grid_layout.addWidget(m_lbl, 0, col)
                    months_added.add(current_date.month)
            
            cell = DayCell(current_date)
            duration = data.get(current_date, 0)
            cell.set_intensity(duration, self.daily_goal_seconds)
            cell.clicked.connect(self.day_clicked.emit)
            
            self.grid_layout.addWidget(cell, row, col)
            self.cells[current_date] = cell
            
            current_date += timedelta(days=1)
            row += 1
            if row > 7:
                row = 1
                col += 1

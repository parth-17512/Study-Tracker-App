from PySide6.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QComboBox, QScrollArea, QSizePolicy
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPalette
from datetime import date, timedelta
from app.ui.theme import Theme

class DayCell(QFrame):
    """A single cell in the heatmap representing one day."""
    clicked = Signal(date)
    
    def __init__(self, day_date: date, parent=None):
        super().__init__(parent)
        self.day_date = day_date
        self.setFixedSize(18, 18)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        # Default empty state
        self.setStyleSheet("background-color: #2a2b33; border-radius: 4px;")
        
    def set_intensity(self, duration_seconds: int, daily_goal_seconds: int):
        """Sets the background color based on study intensity."""
        if duration_seconds == 0:
            self.setStyleSheet("background-color: #2a2b33; border-radius: 4px;")
            self.setToolTip(f"{self.day_date.strftime('%b %d, %Y')}: No activity")
            return
            
        # Avoid division by zero
        if daily_goal_seconds <= 0:
            daily_goal_seconds = 1
            
        ratio = duration_seconds / daily_goal_seconds
        
        # Custom green color scale to match Heat.js reference
        if ratio < 0.25:
            color = "#486749"  # Level 1
        elif ratio < 0.50:
            color = "#588c5a"  # Level 2
        elif ratio < 0.75:
            color = "#68b26a"  # Level 3
        else:
            color = "#7ade7f"  # Level 4
            
        self.setStyleSheet(f"background-color: {color}; border-radius: 4px;")
        
        # Update tooltip
        h = duration_seconds // 3600
        m = (duration_seconds % 3600) // 60
        time_str = f"{h}h {m}m" if h > 0 else f"{m}m"
        self.setToolTip(f"{self.day_date.strftime('%b %d, %Y')}: {time_str}")
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.day_date)
        super().mousePressEvent(event)

class HeatmapWidget(QWidget):
    """GitHub-style activity heatmap for a full year."""
    
    day_clicked = Signal(date) # Signal emitted when a day is clicked
    year_changed = Signal(int)
    
    def __init__(self, daily_goal_seconds: int = 7200, parent=None):
        super().__init__(parent)
        self.daily_goal_seconds = daily_goal_seconds
        self.current_year = date.today().year
        self.setMinimumHeight(180)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(12, 12, 12, 12)
        self.main_layout.setSpacing(Theme.SPACING_SMALL)
        
        # Give the whole widget a card-like background matching the image
        self.setStyleSheet(f"""
            HeatmapWidget {{
                background-color: #21252b;
                border-radius: 8px;
                border: 1px solid {Theme.BORDER_COLOR};
            }}
        """)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Top Header (Title + Year Selector)
        header_layout = QHBoxLayout()
        
        title = QLabel("Study Activity")
        title.setStyleSheet(f"color: {Theme.TEXT_PRIMARY}; font-weight: bold; font-size: 16px; background: transparent;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        self.year_combo = QComboBox()
        # Add current year and past 2 years
        for y in range(self.current_year, self.current_year - 3, -1):
            self.year_combo.addItem(str(y), y)
        
        self.year_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {Theme.BACKGROUND_DARK};
                color: {Theme.TEXT_PRIMARY};
                border: 1px solid {Theme.BORDER_COLOR};
                border-radius: 4px;
                padding: 4px;
            }}
        """)
        self.year_combo.currentIndexChanged.connect(self.on_year_combo_changed)
        header_layout.addWidget(self.year_combo)
        
        self.main_layout.addLayout(header_layout)
        
        # Grid Layout for the Heatmap
        self.grid_widget = QWidget()
        self.grid_widget.setStyleSheet("background: transparent;")
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(4)
        
        # Weekday Labels
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for r, d in enumerate(days):
            lbl = QLabel(d)
            lbl.setStyleSheet(f"color: #8b929c; font-size: 11px; background: transparent;")
            self.grid_layout.addWidget(lbl, r + 1, 0) # +1 because row 0 is for months
                
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
        less_lbl.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-size: 10px; background: transparent;")
        legend_layout.addWidget(less_lbl)
        
        legend_colors = ["#486749", "#588c5a", "#68b26a", "#7ade7f"]
        for color in legend_colors:
            swatch = QFrame()
            swatch.setFixedSize(14, 14)
            swatch.setStyleSheet(f"background-color: {color}; border-radius: 4px;")
            legend_layout.addWidget(swatch)
            
        more_lbl = QLabel("More")
        more_lbl.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-size: 10px; background: transparent;")
        legend_layout.addWidget(more_lbl)
        
        self.main_layout.addLayout(legend_layout)
        
        # We will generate the grid dynamically when data is loaded
        self.cells = {} # mapping date -> DayCell

    def on_year_combo_changed(self, index):
        year = self.year_combo.currentData()
        if year != self.current_year:
            self.current_year = year
            self.year_changed.emit(year)

    def render_grid(self, year: int, data: dict):
        """Builds the 365/366 day grid for the given year and populates colors."""
        # Clear existing cells
        for cell in self.cells.values():
            self.grid_layout.removeWidget(cell)
            cell.deleteLater()
        self.cells.clear()
        
        # Calculate start date (Jan 1)
        start_date = date(year, 1, 1)
        
        # Find the monday of that week (0 = Monday, 6 = Sunday)
        day_of_week = start_date.weekday()
        current_date = start_date
        
        col = 1
        row = day_of_week + 1 # +1 to leave row 0 for months
        
        months_added = set()
        
        # Draw all days in the year
        while current_date.year == year:
            # Check if this is the start of a month or the first cell (so we place a month label)
            if current_date.day == 1 or (current_date == start_date):
                if current_date.month not in months_added:
                    # Place month label
                    m_lbl = QLabel(current_date.strftime("%b"))
                    m_lbl.setStyleSheet(f"color: #8b929c; font-size: 11px; background: transparent;")
                    self.grid_layout.addWidget(m_lbl, 0, col)
                    months_added.add(current_date.month)
            
            cell = DayCell(current_date)
            
            # Fetch data
            duration = data.get(current_date, 0)
            cell.set_intensity(duration, self.daily_goal_seconds)
            
            # Connect signal
            cell.clicked.connect(self.day_clicked.emit)
            
            self.grid_layout.addWidget(cell, row, col)
            self.cells[current_date] = cell
            
            current_date += timedelta(days=1)
            row += 1
            if row > 7: # Rows are 1-7 (Mon-Sun)
                row = 1
                col += 1


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
        self.setFixedSize(14, 14)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        # Default empty state — visible dark cell (like GitHub's empty squares)
        self.setStyleSheet("background-color: #161b22; border-radius: 2px;")
        
    def set_intensity(self, duration_seconds: int, daily_goal_seconds: int):
        """Sets the background color based on study intensity using GitHub green palette."""
        if duration_seconds == 0:
            self.setStyleSheet("background-color: #161b22; border-radius: 2px;")
            self.setToolTip(f"{self.day_date.strftime('%b %d, %Y')}: No activity")
            return
            
        # Avoid division by zero
        if daily_goal_seconds <= 0:
            daily_goal_seconds = 1
            
        ratio = duration_seconds / daily_goal_seconds
        
        # GitHub-style green color scale
        if ratio < 0.25:
            color = "#0e4429"  # Level 1 — darkest green
        elif ratio < 0.50:
            color = "#006d32"  # Level 2
        elif ratio < 0.75:
            color = "#26a641"  # Level 3
        elif ratio < 1.0:
            color = "#39d353"  # Level 4 — bright green
        else:
            color = "#39d353"  # Overachieved — same bright green
            
        self.setStyleSheet(f"background-color: {color}; border-radius: 2px;")
        
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
        
        # Give the whole widget a card-like background
        self.setStyleSheet(f"""
            HeatmapWidget {{
                background-color: {Theme.BACKGROUND_CARD};
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
        
        # Horizontal scroll area for the grid so it scrolls on small windows
        self.grid_scroll = QScrollArea()
        self.grid_scroll.setWidgetResizable(False)
        self.grid_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.grid_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.grid_scroll.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollBar:horizontal { height: 6px; background: transparent; }
            QScrollBar::handle:horizontal { background: #333; border-radius: 3px; }
        """)
        
        # Grid Layout for the Heatmap
        self.grid_widget = QWidget()
        self.grid_widget.setStyleSheet("background: transparent;")
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(3)
        
        # Weekday Labels
        days = ["Mon", "", "Wed", "", "Fri", "", ""]
        for r, d in enumerate(days):
            if d:
                lbl = QLabel(d)
                lbl.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-size: 10px; background: transparent;")
                self.grid_layout.addWidget(lbl, r, 0)
        
        self.grid_scroll.setWidget(self.grid_widget)
        self.main_layout.addWidget(self.grid_scroll, stretch=1)
        
        # Legend
        legend_layout = QHBoxLayout()
        legend_layout.addStretch()
        
        less_lbl = QLabel("Less")
        less_lbl.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-size: 10px; background: transparent;")
        legend_layout.addWidget(less_lbl)
        
        legend_colors = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
        for color in legend_colors:
            swatch = QFrame()
            swatch.setFixedSize(12, 12)
            swatch.setStyleSheet(f"background-color: {color}; border-radius: 2px;")
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
        # We want column 1 to be the week containing Jan 1
        day_of_week = start_date.weekday()
        
        # Current drawing date
        current_date = start_date
        
        col = 1
        row = day_of_week
        
        # Draw all days in the year
        while current_date.year == year:
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
            if row > 6:
                row = 0
                col += 1


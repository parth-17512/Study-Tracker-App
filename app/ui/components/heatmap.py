from PySide6.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QComboBox
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
        self.setFixedSize(12, 12)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        # Default empty state
        self.setStyleSheet(f"background-color: {Theme.BACKGROUND_DARK}; border-radius: 2px;")
        
    def set_intensity(self, duration_seconds: int, daily_goal_seconds: int):
        """Sets the background color based on study intensity."""
        if duration_seconds == 0:
            self.setStyleSheet(f"background-color: {Theme.BACKGROUND_DARK}; border-radius: 2px;")
            return
            
        # Avoid division by zero
        if daily_goal_seconds <= 0:
            daily_goal_seconds = 1
            
        ratio = duration_seconds / daily_goal_seconds
        
        # We will interpolate between a very dark green and a bright green
        # Primary accent is purple in our theme, but standard GitHub is green. 
        # Let's use a nice purple/accent scale to match the theme.
        # Theme.PRIMARY_ACCENT is "#7B61FF"
        
        # Color mapping (Simplified)
        if ratio < 0.25:
            color = "#3A2A85" # Very dark purple
        elif ratio < 0.50:
            color = "#523BA8" # Dark purple
        elif ratio < 0.75:
            color = "#6347CC" # Medium purple
        elif ratio < 1.0:
            color = Theme.PRIMARY_ACCENT # Standard
        else:
            color = Theme.SUCCESS_COLOR # Overachieved (Green)
            
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
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(Theme.SPACING_REGULAR)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Top Header (Title + Year Selector)
        header_layout = QHBoxLayout()
        
        title = QLabel("Study Activity")
        title.setStyleSheet(f"color: {Theme.TEXT_PRIMARY}; font-weight: bold; font-size: 16px;")
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
        
        self.layout.addLayout(header_layout)
        
        # Grid Layout for the Heatmap
        # We need a scroll area or just let it resize. A 12x12 block * 53 weeks = ~636px wide minimum.
        # It should fit fine in 1280x720 window.
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(4)
        
        # Weekday Labels
        days = ["Mon", "Wed", "Fri"]
        day_rows = [0, 2, 4] # Render on these rows (Mon=0, Tue=1, Wed=2...)
        for d, r in zip(days, day_rows):
            lbl = QLabel(d)
            lbl.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-size: 10px;")
            self.grid_layout.addWidget(lbl, r, 0)
            
        self.layout.addWidget(self.grid_widget)
        self.layout.addStretch()
        
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

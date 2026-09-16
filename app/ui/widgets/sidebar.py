from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QSizePolicy
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QCursor
from app.ui.theme import Theme

class SidebarButton(QPushButton):
    """A styled navigation button for the sidebar."""
    def __init__(self, text, icon_text="", parent=None):
        super().__init__(text, parent)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setStyleSheet(f"""
            SidebarButton {{
                text-align: left;
                padding: 12px 16px;
                border: none;
                border-radius: 8px;
                background-color: transparent;
                color: {Theme.TEXT_SECONDARY};
                font-size: {Theme.FONT_SIZE_REGULAR};
                font-weight: bold;
            }}
            SidebarButton:hover {{
                background-color: {Theme.BACKGROUND_CARD_HOVER};
                color: {Theme.TEXT_PRIMARY};
            }}
            SidebarButton:checked {{
                background-color: {Theme.PRIMARY_ACCENT}22; /* 22 is slight opacity in hex */
                color: {Theme.PRIMARY_ACCENT};
            }}
        """)
        self.setCheckable(True)

class Sidebar(QWidget):
    """The left navigation sidebar."""
    
    navigation_requested = Signal(str) # Signal emitted when a nav item is clicked
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(220)
        
        self.setStyleSheet(f"""
            Sidebar {{
                background-color: {Theme.BACKGROUND_CARD};
                border-right: 1px solid {Theme.BORDER_COLOR};
            }}
        """)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(Theme.SPACING_REGULAR, Theme.SPACING_LARGE, Theme.SPACING_REGULAR, Theme.SPACING_LARGE)
        self.layout.setSpacing(Theme.SPACING_SMALL)
        
        # App Title
        title = QLabel("StudyTrack")
        title.setStyleSheet(f"""
            color: {Theme.TEXT_PRIMARY};
            font-size: {Theme.FONT_SIZE_XLARGE};
            font-weight: bold;
            padding-left: 16px;
            padding-bottom: 24px;
        """)
        self.layout.addWidget(title)
        
        # Navigation Items
        self.nav_items = {
            "dashboard": SidebarButton("Dashboard"),
            "timer": SidebarButton("Timer"),
            "sessions": SidebarButton("Sessions"),
            "notes": SidebarButton("Notes"),
            "analytics": SidebarButton("Analytics"),
            "coach": SidebarButton("Coach"),
            "calendar": SidebarButton("Calendar"),
            "settings": SidebarButton("Settings")
        }
        
        for key, btn in self.nav_items.items():
            # Create a closure to capture the current key
            btn.clicked.connect(lambda checked=False, k=key: self.on_nav_clicked(k))
            self.layout.addWidget(btn)
            
        self.layout.addStretch()
        
        # Set initial active state
        self.active_key = None
        self.set_active("dashboard")
        
    def on_nav_clicked(self, key):
        self.set_active(key)
        self.navigation_requested.emit(key)
        
    def set_active(self, key):
        if self.active_key and self.active_key in self.nav_items:
            self.nav_items[self.active_key].setChecked(False)
            
        if key in self.nav_items:
            self.nav_items[key].setChecked(True)
            self.active_key = key

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit
from PySide6.QtCore import Qt
from app.ui.theme import Theme

class Topbar(QWidget):
    """The top bar containing search and user actions."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(70)
        
        self.setStyleSheet(f"""
            Topbar {{
                background-color: {Theme.BACKGROUND_DARK};
                border-bottom: 1px solid {Theme.BORDER_COLOR};
            }}
        """)
        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(Theme.SPACING_LARGE, 0, Theme.SPACING_LARGE, 0)
        
        # Page Title (dynamically updated)
        self.title_label = QLabel("Dashboard")
        self.title_label.setStyleSheet(f"""
            color: {Theme.TEXT_PRIMARY};
            font-size: {Theme.FONT_SIZE_LARGE};
            font-weight: bold;
        """)
        self.layout.addWidget(self.title_label)
        
        self.layout.addStretch()
        
        # Search Bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search sessions, topics... (Ctrl+K)")
        self.search_input.setFixedWidth(300)
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {Theme.BACKGROUND_CARD};
                color: {Theme.TEXT_PRIMARY};
                border: 1px solid {Theme.BORDER_COLOR};
                border-radius: 6px;
                padding: 8px 12px;
            }}
            QLineEdit:focus {{
                border: 1px solid {Theme.PRIMARY_ACCENT};
            }}
        """)
        self.layout.addWidget(self.search_input)
        
        # Placeholders for notifications and profile
        notif_label = QLabel("🔔")
        notif_label.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; padding-left: 16px;")
        self.layout.addWidget(notif_label)
        
    def set_title(self, title: str):
        self.title_label.setText(title)

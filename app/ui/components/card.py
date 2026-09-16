from PySide6.QtWidgets import QFrame, QVBoxLayout, QSizePolicy
from app.ui.theme import Theme

class Card(QFrame):
    """A reusable rounded card widget."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        # Apply the card styling
        self.setStyleSheet(f"""
            Card {{
                background-color: {Theme.BACKGROUND_CARD};
                border: 1px solid {Theme.BORDER_COLOR};
                border-radius: 12px;
            }}
        """)
        
        # Set up a default vertical layout for the card contents
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(Theme.SPACING_REGULAR, Theme.SPACING_REGULAR, Theme.SPACING_REGULAR, Theme.SPACING_REGULAR)
        self.layout.setSpacing(Theme.SPACING_SMALL)
        
    def addWidget(self, widget):
        self.layout.addWidget(widget)
        
    def addLayout(self, layout):
        self.layout.addLayout(layout)

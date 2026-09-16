from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor
from app.ui.theme import Theme

class PrimaryButton(QPushButton):
    """A reusable primary action button."""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setStyleSheet(f"""
            PrimaryButton {{
                background-color: {Theme.PRIMARY_ACCENT};
                color: {Theme.TEXT_PRIMARY};
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
                font-weight: bold;
            }}
            PrimaryButton:hover {{
                background-color: {Theme.PRIMARY_ACCENT_HOVER};
            }}
            PrimaryButton:pressed {{
                background-color: {Theme.SECONDARY_ACCENT};
            }}
        """)

class SecondaryButton(QPushButton):
    """A reusable secondary action button."""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setStyleSheet(f"""
            SecondaryButton {{
                background-color: transparent;
                color: {Theme.TEXT_PRIMARY};
                border: 1px solid {Theme.BORDER_COLOR};
                border-radius: 6px;
                padding: 10px 16px;
            }}
            SecondaryButton:hover {{
                background-color: {Theme.BACKGROUND_CARD_HOVER};
            }}
        """)

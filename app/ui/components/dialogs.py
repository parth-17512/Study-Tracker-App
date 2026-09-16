from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt
from app.ui.theme import Theme
from app.ui.components.button import PrimaryButton, SecondaryButton

class ResumeTimerDialog(QDialog):
    """Dialog presented on startup if an abandoned timer is found."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Active Session Found")
        self.setFixedSize(400, 200)
        self.setStyleSheet(f"background-color: {Theme.BACKGROUND_CARD}; color: {Theme.TEXT_PRIMARY};")
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(Theme.SPACING_LARGE, Theme.SPACING_LARGE, Theme.SPACING_LARGE, Theme.SPACING_LARGE)
        self.layout.setSpacing(Theme.SPACING_LARGE)
        
        # Message
        message = QLabel("An active study session from a previous run was found.\n\nWould you like to resume it or discard it?")
        message.setWordWrap(True)
        message.setStyleSheet(f"font-size: {Theme.FONT_SIZE_REGULAR};")
        self.layout.addWidget(message)
        
        self.layout.addStretch()
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        self.btn_discard = SecondaryButton("Discard")
        self.btn_discard.clicked.connect(self.reject)
        
        self.btn_resume = PrimaryButton("Resume")
        self.btn_resume.clicked.connect(self.accept)
        
        buttons_layout.addWidget(self.btn_discard)
        buttons_layout.addWidget(self.btn_resume)
        
        self.layout.addLayout(buttons_layout)

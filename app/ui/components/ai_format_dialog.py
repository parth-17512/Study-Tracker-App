from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit
from PySide6.QtCore import Qt
from app.ui.theme import Theme
from app.ui.components.button import PrimaryButton, SecondaryButton

class AIFmtPreviewDialog(QDialog):
    """Dialog to preview AI formatted notes before saving."""
    
    def __init__(self, original_md: str, formatted_md: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Review AI Formatting")
        self.setFixedSize(800, 600)
        self.setStyleSheet(f"background-color: {Theme.BACKGROUND_CARD}; color: {Theme.TEXT_PRIMARY};")
        
        self.layout = QVBoxLayout(self)
        
        lbl_msg = QLabel("The AI has formatted your notes. Please review the changes.")
        lbl_msg.setStyleSheet(f"font-size: {Theme.FONT_SIZE_REGULAR}; margin-bottom: 10px;")
        self.layout.addWidget(lbl_msg)
        
        split_layout = QHBoxLayout()
        
        # Original
        orig_layout = QVBoxLayout()
        orig_layout.addWidget(QLabel("Original Note:"))
        self.orig_edit = QTextEdit()
        self.orig_edit.setReadOnly(True)
        self.orig_edit.setMarkdown(original_md)
        self.orig_edit.setStyleSheet(f"background-color: {Theme.BACKGROUND_DARK}; border: 1px solid {Theme.BORDER_COLOR}; color: {Theme.TEXT_PRIMARY};")
        orig_layout.addWidget(self.orig_edit)
        split_layout.addLayout(orig_layout)
        
        # Formatted
        new_layout = QVBoxLayout()
        new_layout.addWidget(QLabel("AI Formatted Note:"))
        self.new_edit = QTextEdit()
        self.new_edit.setReadOnly(True)
        self.new_edit.setMarkdown(formatted_md)
        self.new_edit.setStyleSheet(f"background-color: {Theme.BACKGROUND_DARK}; border: 1px solid {Theme.SUCCESS_COLOR}; color: {Theme.TEXT_PRIMARY};")
        new_layout.addWidget(self.new_edit)
        split_layout.addLayout(new_layout)
        
        self.layout.addLayout(split_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        self.btn_reject = SecondaryButton("Reject Changes")
        self.btn_reject.clicked.connect(self.reject)
        
        self.btn_accept = PrimaryButton("Accept & Save")
        self.btn_accept.clicked.connect(self.accept)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.btn_reject)
        buttons_layout.addWidget(self.btn_accept)
        
        self.layout.addLayout(buttons_layout)

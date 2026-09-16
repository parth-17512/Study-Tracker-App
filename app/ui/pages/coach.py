from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QScrollArea, QFrame,
    QTextEdit, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer
from app.ui.theme import Theme
from app.config.config_manager import ConfigManager
from app.ai.agent import StudyCoachAgent
from app.ai.providers.mock import MockLLMProvider
from app.ai.providers.gemini import GeminiProvider

class ChatBubble(QFrame):
    """A custom widget to render chat bubbles."""
    def __init__(self, text: str, is_user: bool = False, parent=None):
        super().__init__(parent)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        self.label = QLabel(text)
        self.label.setWordWrap(True)
        self.label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        
        if is_user:
            self.label.setStyleSheet(f"""
                background-color: {Theme.PRIMARY_ACCENT};
                color: {Theme.TEXT_PRIMARY};
                border-radius: 10px;
                padding: 10px;
            """)
            layout.addStretch()
            layout.addWidget(self.label)
        else:
            self.label.setStyleSheet(f"""
                background-color: {Theme.BACKGROUND_CARD};
                color: {Theme.TEXT_SECONDARY};
                border: 1px solid {Theme.BORDER_COLOR};
                border-radius: 10px;
                padding: 10px;
            """)
            layout.addWidget(self.label)
            layout.addStretch()

class CoachPage(QWidget):
    """The AI Study Coach interface."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.config = ConfigManager()
        self.init_agent()
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setSpacing(20)
        
        # Header
        header = QLabel("AI Study Coach")
        header.setStyleSheet(f"color: {Theme.TEXT_PRIMARY}; font-size: 24px; font-weight: bold;")
        self.layout.addWidget(header)
        
        # Chat History Scroll Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: transparent;
                border: none;
            }}
            QScrollBar:vertical {{
                background-color: {Theme.BACKGROUND_DARK};
                width: 10px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {Theme.BACKGROUND_CARD_HOVER};
                border-radius: 5px;
            }}
        """)
        
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.chat_container)
        self.layout.addWidget(self.scroll_area)
        
        # Input Area
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ask your coach a question (e.g., 'What is my streak?')...")
        self.input_field.setStyleSheet(f"""
            QLineEdit {{
                background-color: {Theme.BACKGROUND_CARD};
                color: {Theme.TEXT_PRIMARY};
                border: 1px solid {Theme.BORDER_COLOR};
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border: 1px solid {Theme.PRIMARY_ACCENT};
            }}
        """)
        self.input_field.returnPressed.connect(self.send_message)
        
        self.send_btn = QPushButton("Send")
        self.send_btn.setCursor(Qt.PointingHandCursor)
        self.send_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.PRIMARY_ACCENT};
                color: {Theme.TEXT_PRIMARY};
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {Theme.PRIMARY_ACCENT_HOVER};
            }}
        """)
        self.send_btn.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_btn)
        
        self.layout.addLayout(input_layout)
        
        # Welcome message
        self.add_coach_message("Hello! I am your AI Study Coach. How can I help you optimize your study sessions today?")

    def init_agent(self):
        """Initializes the correct LLM provider based on config."""
        api_key = self.config.get("gemini_api_key", "").strip()
        
        if api_key:
            provider = GeminiProvider(api_key)
        else:
            provider = MockLLMProvider()
            
        self.agent = StudyCoachAgent(provider)
        
    def add_user_message(self, text: str):
        bubble = ChatBubble(text, is_user=True)
        self.chat_layout.addWidget(bubble)
        self.scroll_to_bottom()
        
    def add_coach_message(self, text: str):
        bubble = ChatBubble(text, is_user=False)
        self.chat_layout.addWidget(bubble)
        self.scroll_to_bottom()
        
    def scroll_to_bottom(self):
        # Allow UI to process events then scroll
        QTimer.singleShot(50, lambda: self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        ))
        
    def send_message(self):
        text = self.input_field.text().strip()
        if not text:
            return
            
        self.input_field.clear()
        self.add_user_message(text)
        
        # Disable input while processing
        self.input_field.setEnabled(False)
        self.send_btn.setEnabled(False)
        
        # In a real app, this should be dispatched to a QThread to avoid freezing the UI,
        # but for Phase 16 foundational limits, we run it synchronously.
        try:
            # Re-init agent in case API key changed in settings
            self.init_agent()
            response = self.agent.chat(text)
            self.add_coach_message(response)
        except Exception as e:
            self.add_coach_message(f"An error occurred: {str(e)}")
        finally:
            self.input_field.setEnabled(True)
            self.send_btn.setEnabled(True)
            self.input_field.setFocus()

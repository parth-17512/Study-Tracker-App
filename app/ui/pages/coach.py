from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QScrollArea, QFrame,
    QTextEdit, QSizePolicy, QListWidget, QListWidgetItem, QMenu, QMessageBox, QInputDialog, QApplication
)
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from app.ui.theme import Theme
from app.config.config_manager import ConfigManager
from app.ai.agent import StudyCoachAgent
from app.ai.providers.mock import MockLLMProvider
from app.ai.providers.gemini import GeminiProvider
from app.services.chat_service import ChatService

class ChatBubble(QFrame):
    """A custom widget to render chat bubbles."""
    def __init__(self, text: str, is_user: bool = False, parent=None):
        super().__init__(parent)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        self.label = QLabel(text)
        self.label.setWordWrap(True)
        if not is_user:
            self.label.setTextFormat(Qt.MarkdownText)
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

class AICoachWorker(QThread):
    response_ready = Signal(str, str)
    error = Signal(str)
    
    def __init__(self, text, agent):
        super().__init__()
        self.text = text
        self.agent = agent
        
    def run(self):
        try:
            from app.services.coach_service import CoachService
            service = CoachService(self.agent)
            response = service.process_query(self.text)
            provider = self.agent.provider
            provider_name = getattr(provider, "last_used_provider_name", None)
            if not provider_name:
                provider_name = (
                    "No LLM provider available"
                    if response.startswith("All configured LLM providers failed")
                    else "Grounded local data"
                )
            self.response_ready.emit(response, provider_name)
        except Exception as e:
            self.error.emit(str(e))

class CoachPage(QWidget):
    """The AI Study Coach interface."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.config = ConfigManager()
        self.chat_service = ChatService()
        self.current_session_id = None
        self.init_agent()
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # --- Sidebar ---
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(250)
        self.sidebar.setStyleSheet(f"background-color: {Theme.BACKGROUND_DARK}; border-right: 1px solid {Theme.BORDER_COLOR};")
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(15, 20, 15, 20)
        
        self.btn_new_chat = QPushButton("+ New Chat")
        self.btn_new_chat.setCursor(Qt.PointingHandCursor)
        self.btn_new_chat.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.PRIMARY_ACCENT};
                color: {Theme.TEXT_PRIMARY};
                border-radius: 6px;
                padding: 10px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {Theme.PRIMARY_ACCENT_HOVER};
            }}
        """)
        self.btn_new_chat.clicked.connect(self.new_chat)
        sidebar_layout.addWidget(self.btn_new_chat)
        
        lbl_history = QLabel("Previous Chats")
        lbl_history.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-size: 12px; font-weight: bold; margin-top: 15px;")
        sidebar_layout.addWidget(lbl_history)
        
        self.session_list = QListWidget()
        self.session_list.setStyleSheet(f"""
            QListWidget {{
                background-color: transparent;
                border: none;
                color: {Theme.TEXT_PRIMARY};
            }}
            QListWidget::item {{
                padding: 10px;
                border-radius: 6px;
            }}
            QListWidget::item:selected {{
                background-color: {Theme.BACKGROUND_CARD};
            }}
            QListWidget::item:hover {{
                background-color: {Theme.BACKGROUND_CARD_HOVER};
            }}
        """)
        self.session_list.itemClicked.connect(self.load_session)
        self.session_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.session_list.customContextMenuRequested.connect(self.show_context_menu)
        sidebar_layout.addWidget(self.session_list)
        
        self.btn_delete_chat = QPushButton("🗑 Delete Selected Chat")
        self.btn_delete_chat.setCursor(Qt.PointingHandCursor)
        self.btn_delete_chat.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {Theme.DANGER_COLOR};
                border-radius: 6px;
                padding: 10px;
                font-weight: bold;
                border: 1px solid {Theme.DANGER_COLOR};
            }}
            QPushButton:hover {{
                background-color: {Theme.DANGER_COLOR};
                color: {Theme.TEXT_PRIMARY};
            }}
        """)
        self.btn_delete_chat.clicked.connect(self.delete_selected_chat)
        sidebar_layout.addWidget(self.btn_delete_chat)
        
        main_layout.addWidget(self.sidebar)
        
        # --- Main Chat Area ---
        self.chat_area = QWidget()
        self.layout = QVBoxLayout(self.chat_area)
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setSpacing(20)
        
        # Header
        self.header = QLabel("AI Study Coach")
        self.header.setStyleSheet(f"color: {Theme.TEXT_PRIMARY}; font-size: 24px; font-weight: bold;")
        self.layout.addWidget(self.header)
        
        main_layout.addWidget(self.chat_area, stretch=1)
        
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
        self.layout.addWidget(self.scroll_area, stretch=1)
        
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
        
        self.refresh_session_list()
        self.new_chat()

    def refresh_session_list(self):
        self.session_list.clear()
        sessions = self.chat_service.get_all_sessions()
        for session in sessions:
            item = QListWidgetItem(session.title)
            item.setData(Qt.UserRole, session.id)
            self.session_list.addItem(item)
            
    def new_chat(self):
        self.current_session_id = None
        self.header.setText("New Chat")
        self.clear_chat()
        self.add_coach_message("Hello! I am your AI Study Coach. How can I help you optimize your study sessions today?")
        
    def clear_chat(self):
        while self.chat_layout.count():
            child = self.chat_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
    def load_session(self, item):
        session_id = item.data(Qt.UserRole)
        self.current_session_id = session_id
        self.header.setText(item.text())
        self.clear_chat()
        
        messages = self.chat_service.get_messages(session_id)
        for msg in messages:
            if msg.role == "user":
                self.add_user_message(msg.content, persist=False)
            else:
                self.add_coach_message(msg.content, persist=False)
                
    def show_context_menu(self, pos):
        item = self.session_list.itemAt(pos)
        if not item:
            return
            
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {Theme.BACKGROUND_CARD};
                color: {Theme.TEXT_PRIMARY};
                border: 1px solid {Theme.BORDER_COLOR};
            }}
            QMenu::item:selected {{
                background-color: {Theme.PRIMARY_ACCENT};
            }}
        """)
        
        rename_action = menu.addAction("Rename")
        delete_action = menu.addAction("Delete")
        
        action = menu.exec(self.session_list.mapToGlobal(pos))
        session_id = item.data(Qt.UserRole)
        
        if action == rename_action:
            new_title, ok = QInputDialog.getText(self, "Rename Chat", "Enter new title:", QLineEdit.Normal, item.text())
            if ok and new_title.strip():
                self.chat_service.rename_session(session_id, new_title.strip())
                self.refresh_session_list()
                if self.current_session_id == session_id:
                    self.header.setText(new_title.strip())
        elif action == delete_action:
            reply = QMessageBox.question(self, "Delete Chat", "Are you sure you want to delete this conversation?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.chat_service.delete_session(session_id)
                self.refresh_session_list()
                if self.current_session_id == session_id:
                    self.new_chat()

    def delete_selected_chat(self):
        item = self.session_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Delete Chat", "Please select a chat to delete.")
            return
            
        session_id = item.data(Qt.UserRole)
        reply = QMessageBox.question(self, "Delete Chat", "Are you sure you want to delete this conversation?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.chat_service.delete_session(session_id)
            self.refresh_session_list()
            if self.current_session_id == session_id:
                self.new_chat()

    def init_agent(self):
        """Initializes the LLM provider router based on config."""
        from app.ai.providers.router import FallbackProviderRouter
        router = FallbackProviderRouter(self.config)
        self.agent = StudyCoachAgent(router)
        
    def add_user_message(self, text: str, persist: bool = True):
        bubble = ChatBubble(text, is_user=True)
        self.chat_layout.addWidget(bubble)
        self.scroll_to_bottom()
        if persist and self.current_session_id:
            self.chat_service.add_message(self.current_session_id, "user", text)
        
    def add_coach_message(self, text: str, persist: bool = True):
        bubble = ChatBubble(text, is_user=False)
        self.chat_layout.addWidget(bubble)
        self.scroll_to_bottom()
        if persist and self.current_session_id:
            self.chat_service.add_message(self.current_session_id, "assistant", text)
        
    def scroll_to_bottom(self):
        # Allow UI to process events then scroll
        QTimer.singleShot(50, lambda: self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        ))
        
    def send_message(self):
        text = self.input_field.text().strip()
        if not text:
            return
            
        if not self.current_session_id:
            # Generate a title from the first message
            title = text[:30] + "..." if len(text) > 30 else text
            session = self.chat_service.create_session(title=title)
            self.current_session_id = session.id
            self.refresh_session_list()
            self.header.setText(title)
            
        self.input_field.clear()
        self.add_user_message(text, persist=True)
        
        # Show Thinking bubble
        self.thinking_bubble = ChatBubble("Thinking...", is_user=False)
        self.chat_layout.addWidget(self.thinking_bubble)
        self.scroll_to_bottom()
        
        # Disable input while processing
        self.input_field.setEnabled(False)
        self.send_btn.setEnabled(False)
        
        # Start worker
        self.init_agent()
        self.worker = AICoachWorker(text, self.agent)
        self.worker.response_ready.connect(self.on_worker_finished)
        self.worker.error.connect(self.on_worker_error)
        self.worker.start()

    def on_worker_finished(self, response: str, provider_name: str):
        self.thinking_bubble.deleteLater()
        self.add_coach_message(f"{response}\n\n*Provider: {provider_name}*")
        self.finish_processing()
        
    def on_worker_error(self, error_str: str):
        self.thinking_bubble.deleteLater()
        self.add_coach_message(f"An error occurred: {error_str}")
        self.finish_processing()
        
    def finish_processing(self):
        self.input_field.setEnabled(True)
        self.send_btn.setEnabled(True)
        self.input_field.setFocus()

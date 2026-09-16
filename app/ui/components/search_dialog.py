from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem
from PySide6.QtCore import Qt, Signal
from app.ui.theme import Theme
from app.services.session_service import SessionService

class SearchDialog(QDialog):
    """Global Search Palette triggered by Ctrl+K."""
    
    session_selected = Signal(int) # Emits the session_id
    
    def __init__(self, session_service: SessionService, parent=None):
        super().__init__(parent)
        self.session_service = session_service
        self.setWindowTitle("Global Search")
        self.setFixedSize(500, 400)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {Theme.BACKGROUND_CARD};
                color: {Theme.TEXT_PRIMARY};
                border: 1px solid {Theme.BORDER_COLOR};
                border-radius: 8px;
            }}
        """)
        
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(Theme.SPACING_REGULAR, Theme.SPACING_REGULAR, Theme.SPACING_REGULAR, Theme.SPACING_REGULAR)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search sessions by topic or notes... (Press Esc to close)")
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {Theme.BACKGROUND_DARK};
                color: {Theme.TEXT_PRIMARY};
                border: 1px solid {Theme.PRIMARY_ACCENT};
                border-radius: 4px;
                padding: 10px;
                font-size: 16px;
            }}
        """)
        self.search_input.textChanged.connect(self.perform_search)
        self.layout.addWidget(self.search_input)
        
        self.results_list = QListWidget()
        self.results_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {Theme.BACKGROUND_DARK};
                border: 1px solid {Theme.BORDER_COLOR};
                border-radius: 4px;
            }}
            QListWidget::item {{
                padding: 12px;
                border-bottom: 1px solid {Theme.BORDER_COLOR};
            }}
            QListWidget::item:selected {{
                background-color: {Theme.PRIMARY_ACCENT};
                color: {Theme.TEXT_PRIMARY};
            }}
        """)
        self.results_list.itemClicked.connect(self.on_item_clicked)
        self.layout.addWidget(self.results_list)
        
        self.results = []
        
        # Center on screen
        if parent:
            center_point = parent.geometry().center()
            self.move(center_point.x() - self.width() // 2, center_point.y() - self.height() // 2)

    def perform_search(self, text):
        self.results_list.clear()
        
        if not text.strip():
            return
            
        self.results = self.session_service.search_sessions(text_query=text)
        
        for s in self.results:
            topic = s.topic or "Uncategorized"
            from app.utils.time_utils import to_local_time
            local_start = to_local_time(s.start_time)
            date_str = local_start.strftime("%b %d, %Y") if local_start else "Unknown Date"
            
            # Preview notes
            notes = s.notes or ""
            notes_preview = (notes[:40] + "...") if len(notes) > 40 else notes
            
            item_text = f"{topic} ({date_str})\n{notes_preview}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, s.id)
            self.results_list.addItem(item)
            
    def on_item_clicked(self, item):
        session_id = item.data(Qt.ItemDataRole.UserRole)
        self.session_selected.emit(session_id)
        self.accept()

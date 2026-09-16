from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTableWidget, QTableWidgetItem, 
    QHeaderView, QMessageBox, QLineEdit, QComboBox
)
from PySide6.QtCore import Qt
from app.ui.theme import Theme
from app.ui.components.card import Card
from app.ui.components.button import PrimaryButton, SecondaryButton
from app.services.session_service import SessionService
from app.ui.components.dialogs import EditSessionDialog

class SessionsPage(QWidget):
    """Page for viewing and managing study sessions."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.session_service = SessionService()
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(Theme.SPACING_LARGE, Theme.SPACING_LARGE, Theme.SPACING_LARGE, Theme.SPACING_LARGE)
        self.layout.setSpacing(Theme.SPACING_LARGE)
        
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        # Card Container
        card = Card()
        card_layout = QVBoxLayout()
        
        # Action Buttons
        actions_layout = QHBoxLayout()
        
        self.btn_refresh = SecondaryButton("Refresh")
        self.btn_refresh.clicked.connect(self.load_data)
        
        self.btn_edit = SecondaryButton("Edit Selected")
        self.btn_edit.clicked.connect(self.edit_session)
        self.btn_edit.setEnabled(False)
        
        self.btn_delete = SecondaryButton("Delete Selected")
        self.btn_delete.setStyleSheet(self.btn_delete.styleSheet() + f" color: {Theme.WARNING_COLOR}; border-color: {Theme.WARNING_COLOR};")
        self.btn_delete.clicked.connect(self.delete_session)
        self.btn_delete.setEnabled(False)
        
        actions_layout.addWidget(self.btn_refresh)
        actions_layout.addStretch()
        actions_layout.addWidget(self.btn_edit)
        actions_layout.addWidget(self.btn_delete)
        
        card_layout.addLayout(actions_layout)
        
        # --- Filter Bar ---
        filter_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search sessions...")
        self.search_input.setStyleSheet(f"background-color: {Theme.BACKGROUND_DARK}; color: {Theme.TEXT_PRIMARY}; padding: 4px;")
        self.search_input.textChanged.connect(self.load_data)
        filter_layout.addWidget(self.search_input)
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(["All", "COMPLETED", "CANCELLED", "RUNNING", "PAUSED"])
        self.status_combo.setStyleSheet(f"background-color: {Theme.BACKGROUND_DARK}; color: {Theme.TEXT_PRIMARY};")
        self.status_combo.currentTextChanged.connect(self.load_data)
        filter_layout.addWidget(self.status_combo)
        
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["newest", "oldest", "longest", "shortest"])
        self.sort_combo.setStyleSheet(f"background-color: {Theme.BACKGROUND_DARK}; color: {Theme.TEXT_PRIMARY};")
        self.sort_combo.currentTextChanged.connect(self.load_data)
        filter_layout.addWidget(self.sort_combo)
        
        card_layout.addLayout(filter_layout)
        # --- End Filter Bar ---
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Date", "Topic", "Duration", "Status"])
        
        # Styling the table
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {Theme.BACKGROUND_CARD};
                color: {Theme.TEXT_PRIMARY};
                gridline-color: {Theme.BORDER_COLOR};
                border: 1px solid {Theme.BORDER_COLOR};
                border-radius: 4px;
            }}
            QHeaderView::section {{
                background-color: {Theme.BACKGROUND_DARK};
                color: {Theme.TEXT_SECONDARY};
                padding: 8px;
                border: none;
                font-weight: bold;
            }}
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {Theme.BORDER_COLOR};
            }}
            QTableWidget::item:selected {{
                background-color: {Theme.PRIMARY_ACCENT};
            }}
        """)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        self.table.doubleClicked.connect(self.edit_session)
        
        card_layout.addWidget(self.table)
        card.addLayout(card_layout)
        
        self.layout.addWidget(card)

    def load_data(self):
        # Read filters
        text_query = self.search_input.text().strip() or None
        status = self.status_combo.currentText()
        order_by = self.sort_combo.currentText()
        
        sessions = self.session_service.search_sessions(
            text_query=text_query,
            status=status,
            order_by=order_by
        )
        
        self.table.setRowCount(0) # Clear
        for row, session in enumerate(sessions):
            self.table.insertRow(row)
            
            # Format date
            date_str = session.start_time.strftime("%Y-%m-%d %H:%M") if session.start_time else "Unknown"
            
            # Format duration
            d = session.duration_seconds or 0
            h = d // 3600
            m = (d % 3600) // 60
            s = d % 60
            dur_str = f"{h}h {m}m {s}s" if h > 0 else f"{m}m {s}s"
            
            # Topic
            topic_str = session.topic or "Uncategorized"
            
            item_date = QTableWidgetItem(date_str)
            item_date.setData(Qt.ItemDataRole.UserRole, session.id) # Store ID silently
            
            self.table.setItem(row, 0, item_date)
            self.table.setItem(row, 1, QTableWidgetItem(topic_str))
            self.table.setItem(row, 2, QTableWidgetItem(dur_str))
            self.table.setItem(row, 3, QTableWidgetItem(session.status or ""))

    def on_selection_changed(self):
        has_selection = len(self.table.selectedItems()) > 0
        self.btn_edit.setEnabled(has_selection)
        self.btn_delete.setEnabled(has_selection)

    def get_selected_session_id(self):
        selected = self.table.selectedItems()
        if not selected:
            return None
        # ID is stored in the UserRole of column 0
        row = selected[0].row()
        item = self.table.item(row, 0)
        return item.data(Qt.ItemDataRole.UserRole)
        return None

    def edit_session(self):
        session_id = self.get_selected_session_id()
        if not session_id:
            return
            
        session = self.session_service.get_session(session_id)
        if not session:
            return
            
        dialog = EditSessionDialog(session, self)
        if dialog.exec():
            # Update DB
            updates = dialog.get_updates()
            self.session_service.update_session(session_id, updates)
            self.load_data()

    def delete_session(self):
        session_id = self.get_selected_session_id()
        if not session_id:
            return
            
        # Confirmation
        msg = QMessageBox(self)
        msg.setWindowTitle("Delete Session")
        msg.setText("Are you sure you want to delete this session? This cannot be undone.")
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setDefaultButton(QMessageBox.StandardButton.No)
        
        # Apply dark theme to messagebox
        msg.setStyleSheet(f"background-color: {Theme.BACKGROUND_CARD}; color: {Theme.TEXT_PRIMARY};")
        
        if msg.exec() == QMessageBox.StandardButton.Yes:
            self.session_service.delete_session(session_id)
            self.load_data()

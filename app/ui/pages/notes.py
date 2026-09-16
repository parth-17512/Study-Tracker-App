from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QTreeView, 
    QTextEdit, QPushButton, QLabel, QMenu, QMessageBox, 
    QInputDialog, QAbstractItemView
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QStandardItemModel, QStandardItem, QAction
from app.ui.theme import Theme
from app.services.note_service import NoteService
from app.ui.components.button import PrimaryButton, SecondaryButton

NODE_ID_ROLE = Qt.UserRole + 1
IS_FOLDER_ROLE = Qt.UserRole + 2

class NoteItem(QStandardItem):
    def __init__(self, node):
        super().__init__()
        self.setData(node.id, NODE_ID_ROLE)
        self.setData(node.is_folder, IS_FOLDER_ROLE)
        self.setEditable(False)
        self.update_name(node.name)
        
    def update_name(self, name):
        is_folder = self.data(IS_FOLDER_ROLE)
        icon_str = "📁 " if is_folder else "📄 "
        self.setText(icon_str + name)

class NotesTreeView(QTreeView):
    def __init__(self, service: NoteService):
        super().__init__()
        self.service = service
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setStyleSheet(f"""
            QTreeView {{
                background-color: {Theme.BACKGROUND_CARD};
                color: {Theme.TEXT_PRIMARY};
                border: 1px solid {Theme.BORDER_COLOR};
                border-radius: 8px;
            }}
            QTreeView::item:selected {{
                background-color: {Theme.PRIMARY_ACCENT};
            }}
        """)
        
    def dropEvent(self, event):
        source_index = self.selectedIndexes()[0] if self.selectedIndexes() else None
        if not source_index:
            event.ignore()
            return
            
        drop_index = self.indexAt(event.position().toPoint())
        model = self.model()
        source_item = model.itemFromIndex(source_index)
        
        target_parent_id = None
        if drop_index.isValid():
            target_item = model.itemFromIndex(drop_index)
            drop_indicator = self.dropIndicatorPosition()
            
            if drop_indicator == QAbstractItemView.OnItem:
                if target_item.data(IS_FOLDER_ROLE):
                    target_parent_id = target_item.data(NODE_ID_ROLE)
                else:
                    parent_item = target_item.parent()
                    target_parent_id = parent_item.data(NODE_ID_ROLE) if parent_item else None
            else:
                parent_item = target_item.parent()
                target_parent_id = parent_item.data(NODE_ID_ROLE) if parent_item else None
                
        success = self.service.move_node(source_item.data(NODE_ID_ROLE), target_parent_id)
        if success:
            super().dropEvent(event)
        else:
            event.ignore()
            QMessageBox.warning(self, "Invalid Move", "Cannot move a folder into itself or its descendants.")

class MarkdownToolbar(QWidget):
    def __init__(self, text_edit: QTextEdit):
        super().__init__()
        self.text_edit = text_edit
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(4)
        
        self._add_btn("B", "Bold", "**", "**")
        self._add_btn("I", "Italic", "*", "*")
        self._add_btn("S", "Strikethrough", "~~", "~~")
        self._add_btn("H1", "Heading 1", "# ", "")
        self._add_btn("H2", "Heading 2", "## ", "")
        self._add_btn("•", "Bullet List", "- ", "")
        self._add_btn("1.", "Numbered List", "1. ", "")
        self._add_btn("☑", "Checklist", "- [ ] ", "")
        self._add_btn("</>", "Code Block", "```\n", "\n```")
        self._add_btn("❝", "Blockquote", "> ", "")
        self._add_btn("―", "Separator", "\n---\n", "")
        self._add_btn("🔗", "Link", "[", "](url)")
        self.layout.addStretch()

    def _add_btn(self, text, tooltip, prefix, suffix):
        btn = QPushButton(text)
        btn.setToolTip(tooltip)
        btn.setFixedSize(30, 30)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.BACKGROUND_CARD};
                color: {Theme.TEXT_PRIMARY};
                border: 1px solid {Theme.BORDER_COLOR};
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {Theme.BACKGROUND_CARD_HOVER};
            }}
        """)
        btn.clicked.connect(lambda: self._apply_format(prefix, suffix))
        self.layout.addWidget(btn)

    def _apply_format(self, prefix, suffix):
        cursor = self.text_edit.textCursor()
        selected_text = cursor.selectedText()
        if not selected_text and not suffix and prefix.endswith(" "):
            cursor.movePosition(cursor.StartOfBlock)
            cursor.insertText(prefix)
        else:
            cursor.insertText(f"{prefix}{selected_text}{suffix}")
        self.text_edit.setTextCursor(cursor)
        self.text_edit.setFocus()

class NotesPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.service = NoteService()
        self.current_note_id = None
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(Theme.SPACING_LARGE, Theme.SPACING_LARGE, Theme.SPACING_LARGE, Theme.SPACING_LARGE)
        
        self.splitter = QSplitter(Qt.Horizontal)
        self.layout.addWidget(self.splitter)
        
        # Left Panel - Tree
        self.tree_widget = QWidget()
        self.tree_layout = QVBoxLayout(self.tree_widget)
        self.tree_layout.setContentsMargins(0, 0, 0, 0)
        
        self.tree_btn_layout = QHBoxLayout()
        self.btn_new_file = PrimaryButton("New File")
        self.btn_new_file.clicked.connect(self.create_file)
        self.btn_new_folder = SecondaryButton("New Folder")
        self.btn_new_folder.clicked.connect(self.create_folder)
        self.tree_btn_layout.addWidget(self.btn_new_file)
        self.tree_btn_layout.addWidget(self.btn_new_folder)
        self.tree_layout.addLayout(self.tree_btn_layout)
        
        self.tree = NotesTreeView(self.service)
        self.tree.setHeaderHidden(True)
        self.model = QStandardItemModel()
        self.tree.setModel(self.model)
        self.tree_layout.addWidget(self.tree)
        self.splitter.addWidget(self.tree_widget)
        
        # Right Panel - Editor
        self.editor_widget = QWidget()
        self.editor_layout = QVBoxLayout(self.editor_widget)
        self.editor_layout.setContentsMargins(0, 0, 0, 0)
        
        self.toolbar = MarkdownToolbar(QTextEdit()) # temporary, will replace
        self.editor_layout.addWidget(self.toolbar)
        
        self.editor = QTextEdit()
        self.toolbar.text_edit = self.editor # wire it up properly
        
        self.editor.setStyleSheet(f"""
            QTextEdit {{
                background-color: {Theme.BACKGROUND_CARD};
                color: {Theme.TEXT_PRIMARY};
                border: 1px solid {Theme.BORDER_COLOR};
                border-radius: 8px;
                padding: 12px;
                font-family: 'Segoe UI', Consolas, sans-serif;
                font-size: 14px;
            }}
        """)
        self.editor.setEnabled(False)
        self.toolbar.setEnabled(False)
        self.editor_layout.addWidget(self.editor)
        
        self.status_label = QLabel("No file selected")
        self.status_label.setStyleSheet(f"color: {Theme.TEXT_SECONDARY};")
        self.editor_layout.addWidget(self.status_label)
        
        self.splitter.addWidget(self.editor_widget)
        self.splitter.setSizes([300, 700])
        
        # Auto-save Timer
        self.save_timer = QTimer(self)
        self.save_timer.setSingleShot(True)
        self.save_timer.setInterval(1000)
        self.save_timer.timeout.connect(self.auto_save)
        
        self.editor.textChanged.connect(self.on_text_changed)
        self.tree.selectionModel().selectionChanged.connect(self.on_tree_selection)
        
        # Context Menu
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        
        self.load_tree()
        
    def load_tree(self):
        self.model.clear()
        nodes = self.service.get_all_nodes()
        
        node_dict = {n.id: NoteItem(n) for n in nodes}
        root_items = []
        
        for n in nodes:
            item = node_dict[n.id]
            if n.parent_id and n.parent_id in node_dict:
                node_dict[n.parent_id].appendRow(item)
            else:
                root_items.append(item)
                
        for item in root_items:
            self.model.appendRow(item)
            
        self.tree.expandAll()
        
    def get_selected_item(self):
        indexes = self.tree.selectedIndexes()
        if not indexes: return None
        return self.model.itemFromIndex(indexes[0])
        
    def create_file(self):
        parent_item = self.get_selected_item()
        parent_id = None
        if parent_item:
            parent_id = parent_item.data(NODE_ID_ROLE) if parent_item.data(IS_FOLDER_ROLE) else (parent_item.parent().data(NODE_ID_ROLE) if parent_item.parent() else None)
            
        name, ok = QInputDialog.getText(self, "New File", "File Name:")
        if ok and name:
            self.service.create_node(name, is_folder=False, parent_id=parent_id)
            self.load_tree()
            
    def create_folder(self):
        parent_item = self.get_selected_item()
        parent_id = None
        if parent_item:
            parent_id = parent_item.data(NODE_ID_ROLE) if parent_item.data(IS_FOLDER_ROLE) else (parent_item.parent().data(NODE_ID_ROLE) if parent_item.parent() else None)
            
        name, ok = QInputDialog.getText(self, "New Folder", "Folder Name:")
        if ok and name:
            self.service.create_node(name, is_folder=True, parent_id=parent_id)
            self.load_tree()

    def show_context_menu(self, pos):
        item = self.get_selected_item()
        if not item: return
        
        menu = QMenu(self)
        menu.setStyleSheet(f"background-color: {Theme.BACKGROUND_CARD}; color: {Theme.TEXT_PRIMARY};")
        
        rename_action = QAction("Rename", self)
        rename_action.triggered.connect(self.rename_item)
        menu.addAction(rename_action)
        
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(self.delete_item)
        menu.addAction(delete_action)
        
        menu.exec_(self.tree.viewport().mapToGlobal(pos))
        
    def rename_item(self):
        item = self.get_selected_item()
        if not item: return
        
        node = self.service.get_note(item.data(NODE_ID_ROLE))
        if not node: return
        
        new_name, ok = QInputDialog.getText(self, "Rename", "New Name:", text=node.name)
        if ok and new_name:
            self.service.rename_node(item.data(NODE_ID_ROLE), new_name)
            self.load_tree()
            
    def delete_item(self):
        item = self.get_selected_item()
        if not item: return
        
        reply = QMessageBox.question(self, "Delete", f"Are you sure you want to delete '{item.text()}'?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.service.delete_node(item.data(NODE_ID_ROLE))
            if self.current_note_id == item.data(NODE_ID_ROLE):
                self.editor.clear()
                self.editor.setEnabled(False)
                self.toolbar.setEnabled(False)
                self.current_note_id = None
                self.status_label.setText("No file selected")
            self.load_tree()

    def on_tree_selection(self, selected, deselected):
        item = self.get_selected_item()
        if not item or item.data(IS_FOLDER_ROLE):
            self.editor.setEnabled(False)
            self.toolbar.setEnabled(False)
            self.editor.clear()
            self.current_note_id = None
            self.status_label.setText("No file selected")
            return
            
        self.editor.setEnabled(True)
        self.toolbar.setEnabled(True)
        self.current_note_id = item.data(NODE_ID_ROLE)
        
        self.editor.blockSignals(True)
        node = self.service.get_note(item.data(NODE_ID_ROLE))
        self.editor.setText(node.content if node.content else "")
        self.editor.blockSignals(False)
        self.status_label.setText("Saved")
        
    def on_text_changed(self):
        if self.current_note_id:
            self.status_label.setText("Unsaved changes...")
            self.save_timer.start()
            
    def auto_save(self):
        if not self.current_note_id: return
        self.status_label.setText("Saving...")
        content = self.editor.toPlainText()
        success = self.service.update_node_content(self.current_note_id, content)
        if success:
            self.status_label.setText("Saved")
        else:
            self.status_label.setText("Save failed! Please check your connection or database.")

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

from PySide6.QtGui import QTextCharFormat, QTextBlockFormat, QTextListFormat, QFont, QTextCursor, QColor

class MarkdownToolbar(QWidget):
    def __init__(self, text_edit: QTextEdit):
        super().__init__()
        self.text_edit = text_edit
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(4)
        
        self._add_btn("B", "Bold", self._toggle_bold)
        self._add_btn("I", "Italic", self._toggle_italic)
        self._add_btn("S", "Strikethrough", self._toggle_strike)
        self._add_btn("H1", "Heading 1", lambda: self._set_heading(1))
        self._add_btn("H2", "Heading 2", lambda: self._set_heading(2))
        self._add_btn("•", "Bullet List", lambda: self._set_list(QTextListFormat.ListDisc))
        self._add_btn("1.", "Numbered List", lambda: self._set_list(QTextListFormat.ListDecimal))
        self._add_btn("☑", "Checklist", self._insert_checklist)
        self._add_btn("</>", "Code Block", self._insert_code)
        self.layout.addStretch()

    def _add_btn(self, text, tooltip, callback):
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
        btn.clicked.connect(callback)
        self.layout.addWidget(btn)

    def _toggle_bold(self):
        cursor = self.text_edit.textCursor()
        fmt = QTextCharFormat()
        weight = QFont.Bold if cursor.charFormat().fontWeight() != QFont.Bold else QFont.Normal
        fmt.setFontWeight(weight)
        cursor.mergeCharFormat(fmt)
        self.text_edit.setFocus()
        
    def _toggle_italic(self):
        cursor = self.text_edit.textCursor()
        fmt = QTextCharFormat()
        fmt.setFontItalic(not cursor.charFormat().fontItalic())
        cursor.mergeCharFormat(fmt)
        self.text_edit.setFocus()

    def _toggle_strike(self):
        cursor = self.text_edit.textCursor()
        fmt = QTextCharFormat()
        fmt.setFontStrikeOut(not cursor.charFormat().fontStrikeOut())
        cursor.mergeCharFormat(fmt)
        self.text_edit.setFocus()

    def _set_heading(self, level):
        cursor = self.text_edit.textCursor()
        fmt = QTextBlockFormat()
        # Toggle off if already heading
        if cursor.blockFormat().headingLevel() == level:
            fmt.setHeadingLevel(0)
        else:
            fmt.setHeadingLevel(level)
        cursor.mergeBlockFormat(fmt)
        
        # Adjust font size visually
        char_fmt = QTextCharFormat()
        if level > 0:
            char_fmt.setFontWeight(QFont.Bold)
            char_fmt.setFontPointSize(24 - (level * 4))
        else:
            char_fmt.setFontWeight(QFont.Normal)
            char_fmt.setFontPointSize(14)
        cursor.mergeCharFormat(char_fmt)
        self.text_edit.setFocus()

    def _set_list(self, style):
        cursor = self.text_edit.textCursor()
        cursor.beginEditBlock()
        if cursor.currentList():
            # Remove list
            block_fmt = cursor.blockFormat()
            block_fmt.setObjectIndex(-1)
            cursor.setBlockFormat(block_fmt)
        else:
            list_fmt = QTextListFormat()
            list_fmt.setStyle(style)
            cursor.createList(list_fmt)
        cursor.endEditBlock()
        self.text_edit.setFocus()

    def _insert_checklist(self):
        cursor = self.text_edit.textCursor()
        cursor.beginEditBlock()
        
        # Must be inside a list for checklist to render
        if not cursor.currentList():
            list_fmt = QTextListFormat()
            list_fmt.setStyle(QTextListFormat.ListDisc)
            cursor.createList(list_fmt)
            
        bfmt = cursor.blockFormat()
        # Toggle checklist marker: 1=unchecked, 0=none
        marker = 1 if bfmt.property(4256) != 1 else 0
        bfmt.setProperty(4256, marker)
        cursor.setBlockFormat(bfmt)
        
        cursor.endEditBlock()
        self.text_edit.setFocus()

    def _insert_code(self):
        cursor = self.text_edit.textCursor()
        cursor.beginEditBlock()
        
        bfmt = cursor.blockFormat()
        is_code = bfmt.nonBreakableLines()
        
        # Toggle code block state
        bfmt.setNonBreakableLines(not is_code)
        if not is_code:
            bfmt.setLeftMargin(10)
            bfmt.setRightMargin(10)
        else:
            bfmt.setLeftMargin(0)
            bfmt.setRightMargin(0)
        cursor.setBlockFormat(bfmt)
        
        fmt = QTextCharFormat()
        fmt.setFontFixedPitch(not is_code)
        if not is_code:
            fmt.setFontFamily("Courier")
            fmt.setBackground(QColor(Theme.BACKGROUND_CARD_HOVER))
        else:
            fmt.setFontFamily("")
            fmt.setBackground(Qt.transparent)
            
        cursor.mergeCharFormat(fmt)
        cursor.endEditBlock()
        self.text_edit.setFocus()

from app.ui.components.markdown_editor import MarkdownEditor

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
        
        self.btn_collapse_all = SecondaryButton("Collapse All")
        self.btn_collapse_all.clicked.connect(self.collapse_all_folders)
        
        self.tree_btn_layout.addWidget(self.btn_new_file)
        self.tree_btn_layout.addWidget(self.btn_new_folder)
        self.tree_layout.addLayout(self.tree_btn_layout)
        
        # Add collapse all button below new file/folder
        self.tree_btn_layout_bottom = QHBoxLayout()
        self.tree_btn_layout_bottom.addWidget(self.btn_collapse_all)
        self.tree_layout.addLayout(self.tree_btn_layout_bottom)
        
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
        
        self.toolbar_layout = QHBoxLayout()
        self.toolbar_layout.setContentsMargins(0, 0, 0, 0)
        
        self.editor = MarkdownEditor()
        self.toolbar = MarkdownToolbar(self.editor)
        self.toolbar_layout.addWidget(self.toolbar)
        
        self.btn_ai_format = SecondaryButton("✨ AI Format")
        self.btn_ai_format.setToolTip("Automatically format your notes using AI without changing their meaning.")
        self.btn_ai_format.setEnabled(False) # Enabled when a note is loaded
        self.btn_ai_format.clicked.connect(self.run_ai_format)
        self.toolbar_layout.addWidget(self.btn_ai_format)
        
        self.editor_layout.addLayout(self.toolbar_layout)
        
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

    def collapse_all_folders(self):
        """Collapse all nodes in the tree view as required by Phase 6."""
        self.tree.collapseAll()

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
                self.btn_ai_format.setEnabled(False)
                self.current_note_id = None
                self.status_label.setText("No file selected")
            self.load_tree()

    def on_tree_selection(self, selected, deselected):
        item = self.get_selected_item()
        if not item or item.data(IS_FOLDER_ROLE):
            self.editor.setEnabled(False)
            self.toolbar.setEnabled(False)
            self.btn_ai_format.setEnabled(False)
            self.editor.clear()
            self.current_note_id = None
            self.status_label.setText("No file selected")
            return
            
        self.editor.setEnabled(True)
        self.toolbar.setEnabled(True)
        self.btn_ai_format.setEnabled(True)
        self.current_note_id = item.data(NODE_ID_ROLE)
        
        self.editor.blockSignals(True)
        node = self.service.get_note(item.data(NODE_ID_ROLE))
        self.editor.setMarkdown(node.content if node.content else "")
        self.editor.blockSignals(False)
        self.status_label.setText("Saved")
        
    def on_text_changed(self):
        if self.current_note_id:
            self.status_label.setText("Unsaved changes...")
            self.save_timer.start()
            
    def auto_save(self):
        if not self.current_note_id: return
        self.status_label.setText("Saving...")
        content = self.editor.toMarkdown()
        success = self.service.update_node_content(self.current_note_id, content)
        if success:
            self.status_label.setText("Saved")
        else:
            self.status_label.setText("Save failed! Please check your connection or database.")

    def run_ai_format(self):
        if not self.current_note_id: return
        
        content = self.editor.toMarkdown()
        if not content.strip():
            return
            
        from app.config.config_manager import ConfigManager
        from app.ai.providers.gemini import GeminiProvider
        from app.ai.providers.mock import MockLLMProvider
        from app.ai.agent import StudyCoachAgent
        from app.ui.components.ai_format_dialog import AIFmtPreviewDialog
        from PySide6.QtWidgets import QApplication, QMessageBox
        
        config = ConfigManager()
        api_key = config.get("gemini_api_key", "").strip()
        provider = GeminiProvider(api_key) if api_key else MockLLMProvider()
        agent = StudyCoachAgent(provider)
        
        self.status_label.setText("✨ AI Formatting in progress...")
        QApplication.processEvents()
        
        try:
            formatted_content = agent.format_note(content)
            
            dialog = AIFmtPreviewDialog(content, formatted_content, self)
            if dialog.exec_():
                self.editor.setMarkdown(formatted_content)
                self.auto_save()
        except Exception as e:
            QMessageBox.warning(self, "AI Format Error", f"Error formatting note: {e}")
        finally:
            self.status_label.setText("Saved" if self.current_note_id else "No file selected")

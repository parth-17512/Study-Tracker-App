import re
from PySide6.QtWidgets import QTextEdit
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor

class MarkdownEditor(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.textChanged.connect(self._auto_renumber_lists)
        self._is_renumbering = False

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            cursor = self.textCursor()
            block = cursor.block()
            text = block.text()
            
            # Check for numbered list
            num_match = re.match(r'^(\s*)(\d+)\.\s(.*)', text)
            if num_match:
                indent = num_match.group(1)
                content = num_match.group(3)
                
                if not content.strip():
                    # If empty list item, exit list by clearing the line
                    cursor.movePosition(QTextCursor.StartOfBlock, QTextCursor.KeepAnchor)
                    cursor.removeSelectedText()
                    super().keyPressEvent(event)
                    return
                else:
                    # Insert next item
                    # The number doesn't matter here because _auto_renumber_lists will fix it immediately!
                    # So we can just insert "1. " and let the auto-renumber do its job.
                    super().keyPressEvent(event)
                    self.insertPlainText(f"{indent}1. ")
                    return
                    
            # Check for bullet list
            bul_match = re.match(r'^(\s*)([-*+])\s(.*)', text)
            if bul_match:
                indent = bul_match.group(1)
                bullet = bul_match.group(2)
                content = bul_match.group(3)
                
                # Check for checklist
                check_match = re.match(r'^\[([ xX])\]\s+(.*)', content)
                
                if (check_match and not check_match.group(2).strip()) or (not check_match and not content.strip()):
                    # Empty bullet/checklist -> exit list
                    cursor.movePosition(QTextCursor.StartOfBlock, QTextCursor.KeepAnchor)
                    cursor.removeSelectedText()
                    super().keyPressEvent(event)
                    return
                else:
                    super().keyPressEvent(event)
                    if check_match:
                        self.insertPlainText(f"{indent}{bullet} [ ] ")
                    else:
                        self.insertPlainText(f"{indent}{bullet} ")
                    return
                    
        super().keyPressEvent(event)

    def _auto_renumber_lists(self):
        """Automatically renumbers ordered lists without losing cursor position/undo history."""
        if self._is_renumbering:
            return
            
        self._is_renumbering = True
        try:
            doc = self.document()
            cursor = QTextCursor(doc)
            cursor.beginEditBlock()
            
            stack = [] # stores (indent_len, current_number)
            
            block = doc.begin()
            while block.isValid():
                text = block.text()
                match = re.match(r'^(\s*)(\d+)\.\s(.*)', text)
                
                if match:
                    indent_str = match.group(1)
                    indent = len(indent_str)
                    current_num_str = match.group(2)
                    content = match.group(3)
                    
                    while stack and stack[-1][0] > indent:
                        stack.pop()
                        
                    if not stack or stack[-1][0] < indent:
                        stack.append((indent, 1))
                    else:
                        stack[-1] = (indent, stack[-1][1] + 1)
                        
                    expected_num = stack[-1][1]
                    
                    if int(current_num_str) != expected_num:
                        # Need to update just the number to preserve undo history and selection correctly
                        # Find the exact start and end of the number
                        b_cursor = QTextCursor(block)
                        b_cursor.setPosition(block.position() + indent)
                        b_cursor.setPosition(block.position() + indent + len(current_num_str), QTextCursor.KeepAnchor)
                        b_cursor.insertText(str(expected_num))
                else:
                    # If it's an empty line, do we break the list?
                    # Generally, standard markdown lists can span empty lines if indented.
                    # But for simplicity, we'll reset if it's completely non-indented text.
                    if text.strip() and not re.match(r'^\s+', text):
                        stack.clear()
                        
                block = block.next()
                
            cursor.endEditBlock()
        finally:
            self._is_renumbering = False

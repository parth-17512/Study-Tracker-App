from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt
from datetime import datetime, date, timedelta, timezone
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

from PySide6.QtWidgets import QFormLayout, QLineEdit, QSpinBox, QTextEdit
class EditSessionDialog(QDialog):
    """Dialog to edit an existing study session."""
    
    def __init__(self, session_obj, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Session")
        self.setFixedSize(400, 350)
        self.setStyleSheet(f"background-color: {Theme.BACKGROUND_CARD}; color: {Theme.TEXT_PRIMARY};")
        
        self.layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        # Notes
        self.notes_input = QTextEdit()
        self.notes_input.setPlainText(session_obj.notes or "")
        self.notes_input.setStyleSheet(f"background-color: {Theme.BACKGROUND_DARK}; border: 1px solid {Theme.BORDER_COLOR}; color: {Theme.TEXT_PRIMARY};")
        form_layout.addRow("Notes:", self.notes_input)
        
        # Duration adjustments
        d = session_obj.duration_seconds or 0
        self.spin_hours = QSpinBox()
        self.spin_hours.setRange(0, 99)
        self.spin_hours.setValue(d // 3600)
        self.spin_hours.setStyleSheet(f"background-color: {Theme.BACKGROUND_DARK}; color: {Theme.TEXT_PRIMARY};")
        
        self.spin_mins = QSpinBox()
        self.spin_mins.setRange(0, 59)
        self.spin_mins.setValue((d % 3600) // 60)
        self.spin_mins.setStyleSheet(f"background-color: {Theme.BACKGROUND_DARK}; color: {Theme.TEXT_PRIMARY};")
        
        duration_layout = QHBoxLayout()
        duration_layout.addWidget(self.spin_hours)
        duration_layout.addWidget(QLabel("h"))
        duration_layout.addWidget(self.spin_mins)
        duration_layout.addWidget(QLabel("m"))
        
        form_layout.addRow("Duration:", duration_layout)
        
        self.layout.addLayout(form_layout)
        self.layout.addStretch()
        
        # Buttons
        buttons_layout = QHBoxLayout()
        self.btn_cancel = SecondaryButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)
        
        self.btn_save = PrimaryButton("Save")
        self.btn_save.clicked.connect(self.accept)
        
        buttons_layout.addWidget(self.btn_cancel)
        buttons_layout.addWidget(self.btn_save)
        self.layout.addLayout(buttons_layout)

    def get_updates(self):
        h = self.spin_hours.value()
        m = self.spin_mins.value()
        total_sec = (h * 3600) + (m * 60)
        return {
            "notes": self.notes_input.toPlainText(),
            "duration_seconds": total_sec
        }

from app.services.analytics_service import AnalyticsService
from PySide6.QtWidgets import QListWidget, QListWidgetItem
class DailySessionsDialog(QDialog):
    """Displays all sessions for a specific clicked date on the heatmap."""
    
    def __init__(self, target_date: date, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Sessions for {target_date.strftime('%B %d, %Y')}")
        self.setFixedSize(400, 300)
        self.setStyleSheet(f"background-color: {Theme.BACKGROUND_CARD}; color: {Theme.TEXT_PRIMARY};")
        
        self.layout = QVBoxLayout(self)
        
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet(f"""
            QListWidget {{
                background-color: {Theme.BACKGROUND_DARK};
                border: 1px solid {Theme.BORDER_COLOR};
                border-radius: 4px;
            }}
            QListWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {Theme.BORDER_COLOR};
            }}
        """)
        self.layout.addWidget(self.list_widget)
        
        # Close button
        btn_close = PrimaryButton("Close")
        btn_close.clicked.connect(self.accept)
        self.layout.addWidget(btn_close)
        
        self.load_sessions(target_date)
        
    def load_sessions(self, target_date):
        service = AnalyticsService()
        
        # Get start and end of that specific day
        start = datetime.combine(target_date, datetime.min.time()).replace(tzinfo=timezone.utc)
        end = start + timedelta(days=1)
        
        sessions = service.session_repo.get_by_date_range(start, end)
        
        if not sessions:
            self.list_widget.addItem(QListWidgetItem("No sessions on this date."))
            return
            
        for s in sessions:
            dur = s.duration_seconds or 0
            m = dur // 60
            title = s.topic or "Uncategorized"
            from app.utils.time_utils import to_local_time
            local_start = to_local_time(s.start_time)
            item_text = f"{local_start.strftime('%H:%M')} | {title} | {m} mins"
            if s.notes:
                item_text += f"\n- {s.notes}"
            item = QListWidgetItem(item_text)
            self.list_widget.addItem(item)

class AlarmDialog(QDialog):
    """An aggressive, always-on-top dialog for timer completion."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Session Complete!")
        self.setFixedSize(400, 250)
        
        # Make it always on top
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint)
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {Theme.BACKGROUND_CARD};
                border: 2px solid {Theme.SUCCESS_COLOR};
                border-radius: 8px;
            }}
        """)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(Theme.SPACING_LARGE, Theme.SPACING_LARGE, Theme.SPACING_LARGE, Theme.SPACING_LARGE)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_title = QLabel("Time's Up!")
        lbl_title.setStyleSheet(f"color: {Theme.SUCCESS_COLOR}; font-size: 36px; font-weight: bold;")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(lbl_title)
        
        lbl_msg = QLabel("Your countdown has finished.\nGreat job!")
        lbl_msg.setStyleSheet(f"color: {Theme.TEXT_PRIMARY}; font-size: 18px;")
        lbl_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(lbl_msg)
        
        self.layout.addSpacing(20)
        
        btn_ok = PrimaryButton("OK - Stop Alarm")
        btn_ok.setMinimumHeight(50)
        btn_ok.clicked.connect(self.accept)
        self.layout.addWidget(btn_ok)

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QStackedWidget, QSpinBox, QRadioButton, QButtonGroup, QSpacerItem, QSizePolicy, QLineEdit
from PySide6.QtCore import Qt, QTimer as QtCoreTimer
from app.ui.theme import Theme
from app.ui.components.card import Card
from app.ui.components.button import PrimaryButton, SecondaryButton
from app.services.timer_service import TimerService
from app.timer.timer_state import TimerState, TimerMode

from app.services.notification_service import NotificationService

class TimerPage(QWidget):
    """The timer page featuring a stopwatch and countdown mode."""
    
    def __init__(self, timer_service: TimerService, notification_service: NotificationService, parent=None):
        super().__init__(parent)
        self.timer_service = timer_service
        self.notification_service = notification_service
        
        from PySide6.QtWidgets import QScrollArea
        
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("QScrollArea { background-color: transparent; border: none; }")
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        self.layout = QVBoxLayout(scroll_content)
        self.layout.setContentsMargins(Theme.SPACING_LARGE, Theme.SPACING_LARGE, Theme.SPACING_LARGE, Theme.SPACING_LARGE)
        self.layout.setSpacing(Theme.SPACING_LARGE)
        
        scroll_area.setWidget(scroll_content)
        outer_layout.addWidget(scroll_area)
        
        # UI Update Loop
        self.update_timer = QtCoreTimer(self)
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.setInterval(100) # 100ms for smooth UI updates
        
        self.setup_ui()
        self.sync_ui_state()

    def setup_ui(self):
        # 1. Mode Selector (Stopwatch / Countdown)
        mode_layout = QHBoxLayout()
        self.mode_group = QButtonGroup(self)
        
        self.radio_stopwatch = QRadioButton("Stopwatch")
        self.radio_stopwatch.setStyleSheet(f"color: {Theme.TEXT_PRIMARY}; font-weight: bold;")
        self.radio_stopwatch.setChecked(True)
        self.mode_group.addButton(self.radio_stopwatch, 0)
        
        self.radio_countdown = QRadioButton("Countdown")
        self.radio_countdown.setStyleSheet(f"color: {Theme.TEXT_PRIMARY}; font-weight: bold;")
        self.mode_group.addButton(self.radio_countdown, 1)
        
        self.mode_group.idClicked.connect(self.on_mode_changed)
        
        mode_layout.addStretch()
        mode_layout.addWidget(self.radio_stopwatch)
        mode_layout.addWidget(self.radio_countdown)
        mode_layout.addStretch()
        self.layout.addLayout(mode_layout)
        
        # 2. Main Timer Card
        timer_card = Card()
        timer_layout = QVBoxLayout()
        timer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        timer_layout.setSpacing(Theme.SPACING_LARGE)
        
        # Topic Input
        self.topic_input = QLineEdit()
        self.topic_input.setPlaceholderText("What are you focusing on? (Optional)")
        self.topic_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {Theme.BACKGROUND_DARK};
                color: {Theme.TEXT_PRIMARY};
                border: 1px solid {Theme.BORDER_COLOR};
                border-radius: 6px;
                padding: 10px;
                font-size: 16px;
            }}
            QLineEdit:focus {{
                border: 1px solid {Theme.PRIMARY_ACCENT};
            }}
        """)
        self.topic_input.setMaximumWidth(400)
        timer_layout.addWidget(self.topic_input, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Input for Countdown (Hidden in Stopwatch mode)
        self.duration_input_widget = QWidget()
        duration_layout = QHBoxLayout(self.duration_input_widget)
        duration_layout.setContentsMargins(0, 0, 0, 0)
        duration_layout.setSpacing(12)
        
        spinbox_style = f"""
            QSpinBox {{
                background-color: {Theme.BACKGROUND_CARD};
                color: {Theme.TEXT_PRIMARY};
                border: 1px solid {Theme.BORDER_COLOR};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 20px;
                font-weight: bold;
                min-width: 80px;
            }}
            QSpinBox::up-button {{
                subcontrol-origin: border;
                subcontrol-position: top right;
                width: 24px;
                border-left: 1px solid {Theme.BORDER_COLOR};
                background-color: {Theme.BACKGROUND_CARD_HOVER};
                border-top-right-radius: 6px;
            }}
            QSpinBox::down-button {{
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                width: 24px;
                border-left: 1px solid {Theme.BORDER_COLOR};
                background-color: {Theme.BACKGROUND_CARD_HOVER};
                border-bottom-right-radius: 6px;
            }}
            QSpinBox::up-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-bottom: 6px solid {Theme.TEXT_PRIMARY};
                width: 0; height: 0;
            }}
            QSpinBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {Theme.TEXT_PRIMARY};
                width: 0; height: 0;
            }}
        """
        
        lbl_hours = QLabel("Hours")
        lbl_hours.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-size: 14px; font-weight: bold;")
        
        self.spin_hours = QSpinBox()
        self.spin_hours.setRange(0, 23)
        self.spin_hours.setStyleSheet(spinbox_style)
        self.spin_hours.setButtonSymbols(QSpinBox.UpDownArrows)
        
        lbl_mins = QLabel("Minutes")
        lbl_mins.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-size: 14px; font-weight: bold;")
        
        self.spin_mins = QSpinBox()
        self.spin_mins.setRange(0, 59)
        self.spin_mins.setValue(25) # Default pomodoro
        self.spin_mins.setStyleSheet(spinbox_style)
        self.spin_mins.setButtonSymbols(QSpinBox.UpDownArrows)
        
        self.spin_hours.valueChanged.connect(self.update_display)
        self.spin_mins.valueChanged.connect(self.update_display)
        
        duration_layout.addStretch()
        duration_layout.addWidget(lbl_hours)
        duration_layout.addWidget(self.spin_hours)
        duration_layout.addWidget(lbl_mins)
        duration_layout.addWidget(self.spin_mins)
        duration_layout.addStretch()
        self.duration_input_widget.hide() # Default is stopwatch
        
        timer_layout.addWidget(self.duration_input_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Large Display
        self.time_display = QLabel("00:00:00")
        self.time_display.setStyleSheet(f"color: {Theme.PRIMARY_ACCENT}; font-size: 72px; font-weight: bold;")
        self.time_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        timer_layout.addWidget(self.time_display)
        
        timer_card.addLayout(timer_layout)
        self.layout.addWidget(timer_card, stretch=1)
        
        # 3. Controls
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(Theme.SPACING_LARGE)
        controls_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.btn_start = PrimaryButton("Start")
        self.btn_start.clicked.connect(self.start_timer)
        
        self.btn_pause = SecondaryButton("Pause")
        self.btn_pause.clicked.connect(self.pause_timer)
        
        self.btn_resume = PrimaryButton("Resume")
        self.btn_resume.clicked.connect(self.resume_timer)
        
        self.btn_complete = PrimaryButton("Complete")
        self.btn_complete.clicked.connect(self.complete_timer)
        self.btn_complete.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.SUCCESS_COLOR};
                color: {Theme.TEXT_PRIMARY};
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
                font-weight: bold;
            }}
        """)
        
        self.btn_cancel = SecondaryButton("Cancel")
        self.btn_cancel.clicked.connect(self.cancel_timer)
        
        controls_layout.addWidget(self.btn_start)
        controls_layout.addWidget(self.btn_pause)
        controls_layout.addWidget(self.btn_resume)
        controls_layout.addWidget(self.btn_complete)
        controls_layout.addWidget(self.btn_cancel)
        
        self.layout.addLayout(controls_layout)

    def on_mode_changed(self, id):
        if self.timer_service.engine.state != TimerState.IDLE:
            # Prevent mode change while running/paused
            current_is_countdown = (self.timer_service.engine.mode == TimerMode.COUNTDOWN)
            self.radio_countdown.blockSignals(True)
            self.radio_stopwatch.blockSignals(True)
            self.radio_countdown.setChecked(current_is_countdown)
            self.radio_stopwatch.setChecked(not current_is_countdown)
            self.radio_countdown.blockSignals(False)
            self.radio_stopwatch.blockSignals(False)
            return

        if id == 0: # Stopwatch
            self.duration_input_widget.hide()
            self.time_display.setText("00:00:00")
        else: # Countdown
            self.duration_input_widget.show()
            self.update_display() # Updates based on spinbox values

    def format_time(self, seconds: int) -> str:
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        if h > 0:
            return f"{h:02d}:{m:02d}:{s:02d}"
        return f"{m:02d}:{s:02d}"

    def update_display(self):
        engine = self.timer_service.engine
        
        if engine.state == TimerState.IDLE:
            if self.radio_countdown.isChecked():
                total_secs = (self.spin_hours.value() * 3600) + (self.spin_mins.value() * 60)
                self.time_display.setText(self.format_time(total_secs))
            else:
                self.time_display.setText("00:00")
            return
            
        if engine.mode == TimerMode.STOPWATCH:
            secs = engine.get_elapsed_seconds()
            self.time_display.setText(self.format_time(secs))
        else:
            secs = engine.get_remaining_seconds()
            self.time_display.setText(self.format_time(secs))
            if secs == 0 and engine.state == TimerState.RUNNING:
                # Auto-complete and Notify
                self.notification_service.play_alarm()
                self.timer_service.complete()
                self.sync_ui_state()
                
                # Show persistent alarm dialog
                from app.ui.components.dialogs import AlarmDialog
                dialog = AlarmDialog(self)
                dialog.exec()
                
                # Stop alarm when dialog closes
                self.notification_service.stop_alarm()

    def sync_ui_state(self):
        state = self.timer_service.engine.state
        
        # Mode selector visibility
        self.radio_stopwatch.setEnabled(state == TimerState.IDLE)
        self.radio_countdown.setEnabled(state == TimerState.IDLE)
        
        if state != TimerState.IDLE:
            if self.timer_service.engine.mode == TimerMode.COUNTDOWN:
                self.radio_countdown.setChecked(True)
            else:
                self.radio_stopwatch.setChecked(True)
        
        # Input visibility
        self.duration_input_widget.setVisible(state == TimerState.IDLE and self.radio_countdown.isChecked())
        
        self.topic_input.setEnabled(state == TimerState.IDLE)
        if state != TimerState.IDLE and self.timer_service.engine.topic:
            self.topic_input.setText(self.timer_service.engine.topic)
        
        # Button visibility
        self.btn_start.setVisible(state == TimerState.IDLE)
        self.btn_pause.setVisible(state == TimerState.RUNNING)
        self.btn_resume.setVisible(state == TimerState.PAUSED)
        self.btn_complete.setVisible(state in (TimerState.RUNNING, TimerState.PAUSED))
        self.btn_cancel.setVisible(state in (TimerState.RUNNING, TimerState.PAUSED))
        
        if state == TimerState.RUNNING:
            self.update_timer.start()
        elif state == TimerState.IDLE:
            self.update_timer.stop()
            self.update_display()
        else:
            # Paused/Completed/Cancelled
            self.update_timer.stop()
            self.update_display()

    def start_timer(self):
        topic = self.topic_input.text().strip() or None
        
        if self.radio_stopwatch.isChecked():
            self.timer_service.start_stopwatch(topic=topic)
        else:
            total_secs = (self.spin_hours.value() * 3600) + (self.spin_mins.value() * 60)
            if total_secs == 0:
                return # Cannot start 0 duration
            self.timer_service.start_countdown(duration_seconds=total_secs, topic=topic)
            
        self.sync_ui_state()

    def pause_timer(self):
        self.timer_service.pause()
        self.sync_ui_state()

    def resume_timer(self):
        self.timer_service.resume()
        self.sync_ui_state()

    def complete_timer(self):
        self.timer_service.complete()
        self.sync_ui_state()

    def cancel_timer(self):
        self.timer_service.cancel()
        self.sync_ui_state()

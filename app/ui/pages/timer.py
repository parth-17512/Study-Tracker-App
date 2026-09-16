from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QStackedWidget, QSpinBox, QRadioButton, QButtonGroup, QSpacerItem, QSizePolicy
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
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(Theme.SPACING_LARGE, Theme.SPACING_LARGE, Theme.SPACING_LARGE, Theme.SPACING_LARGE)
        self.layout.setSpacing(Theme.SPACING_LARGE)
        
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
        
        # Input for Countdown (Hidden in Stopwatch mode)
        self.duration_input_widget = QWidget()
        duration_layout = QHBoxLayout(self.duration_input_widget)
        duration_layout.setContentsMargins(0, 0, 0, 0)
        
        self.spin_hours = QSpinBox()
        self.spin_hours.setRange(0, 23)
        self.spin_hours.setSuffix(" h")
        
        self.spin_mins = QSpinBox()
        self.spin_mins.setRange(0, 59)
        self.spin_mins.setSuffix(" m")
        self.spin_mins.setValue(25) # Default pomodoro
        
        self.spin_hours.valueChanged.connect(self.update_display)
        self.spin_mins.valueChanged.connect(self.update_display)
        
        duration_layout.addWidget(self.spin_hours)
        duration_layout.addWidget(self.spin_mins)
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
                self.notification_service.notify_session_complete()
                self.timer_service.complete()
                self.sync_ui_state()

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
        if self.radio_stopwatch.isChecked():
            self.timer_service.start_stopwatch()
        else:
            total_secs = (self.spin_hours.value() * 3600) + (self.spin_mins.value() * 60)
            if total_secs == 0:
                return # Cannot start 0 duration
            self.timer_service.start_countdown(duration_seconds=total_secs)
            
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

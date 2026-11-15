from datetime import date, datetime

from PySide6.QtCore import QTime
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QTimeEdit,
    QVBoxLayout,
)

from app.ui.components.button import PrimaryButton, SecondaryButton
from app.ui.theme import Theme


class ActivityDialog(QDialog):
    """Dialog for adding or editing a same-day Rest or Other activity."""

    def __init__(self, target_date: date, activity=None, parent=None):
        super().__init__(parent)
        self.target_date = target_date
        self.activity = activity
        self.setWindowTitle("Edit Activity" if activity else "Add Activity")
        self.setMinimumWidth(360)
        self.setStyleSheet(
            f"QDialog {{ background-color: {Theme.BACKGROUND_CARD}; color: {Theme.TEXT_PRIMARY}; }}"
        )

        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(Theme.SPACING_REGULAR)

        self.category_input = QComboBox()
        self.category_input.addItem("Rest", "rest")
        self.category_input.addItem("Other activity", "other")
        self.category_input.setStyleSheet(
            f"background-color: {Theme.BACKGROUND_DARK}; color: {Theme.TEXT_PRIMARY}; padding: 6px;"
        )

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. Lunch, walk, commute")
        self.name_input.setStyleSheet(
            f"background-color: {Theme.BACKGROUND_DARK}; color: {Theme.TEXT_PRIMARY}; padding: 6px;"
        )

        self.start_input = QTimeEdit()
        self.start_input.setDisplayFormat("HH:mm")
        self.start_input.setTime(QTime(9, 0))
        self.start_input.setStyleSheet(
            f"background-color: {Theme.BACKGROUND_DARK}; color: {Theme.TEXT_PRIMARY}; padding: 6px;"
        )

        self.end_input = QTimeEdit()
        self.end_input.setDisplayFormat("HH:mm")
        self.end_input.setTime(QTime(10, 0))
        self.end_input.setStyleSheet(
            f"background-color: {Theme.BACKGROUND_DARK}; color: {Theme.TEXT_PRIMARY}; padding: 6px;"
        )

        self.notes_input = QPlainTextEdit()
        self.notes_input.setPlaceholderText("Optional note")
        self.notes_input.setMaximumHeight(90)
        self.notes_input.setStyleSheet(
            f"background-color: {Theme.BACKGROUND_DARK}; color: {Theme.TEXT_PRIMARY}; padding: 6px;"
        )

        form.addRow("Category:", self.category_input)
        form.addRow("Activity name:", self.name_input)
        form.addRow("Start time:", self.start_input)
        form.addRow("End time:", self.end_input)
        form.addRow("Note:", self.notes_input)
        layout.addLayout(form)

        info = QLabel(
            "Blocks must start and end on this date. End time must be later than start time; "
            "overnight activities are not supported. Study sessions are added automatically."
        )
        info.setWordWrap(True)
        info.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-size: 12px;")
        layout.addWidget(info)

        self.feedback = QLabel()
        self.feedback.setWordWrap(True)
        self.feedback.setStyleSheet(f"color: {Theme.WARNING_COLOR};")
        layout.addWidget(self.feedback)

        buttons = QHBoxLayout()
        buttons.addStretch()
        cancel_button = SecondaryButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        self.save_button = PrimaryButton("Save Activity")
        self.save_button.clicked.connect(self._validate_and_accept)
        buttons.addWidget(cancel_button)
        buttons.addWidget(self.save_button)
        layout.addLayout(buttons)

        if activity:
            category_index = self.category_input.findData(activity["category"])
            if category_index >= 0:
                self.category_input.setCurrentIndex(category_index)
            self.name_input.setText(activity["name"])
            self.start_input.setTime(QTime(activity["start"].hour, activity["start"].minute))
            self.end_input.setTime(QTime(activity["end"].hour, activity["end"].minute))
            self.notes_input.setPlainText(activity.get("notes", ""))

    def _validate_and_accept(self):
        if not self.name_input.text().strip():
            self.feedback.setText("Enter an activity name.")
            return
        if self.end_input.time() <= self.start_input.time():
            self.feedback.setText(
                "End time must be later than start time. Overnight blocks are not supported."
            )
            return
        self.accept()

    def get_data(self):
        start_time = self.start_input.time().toPython()
        end_time = self.end_input.time().toPython()
        return {
            "category": self.category_input.currentData(),
            "name": self.name_input.text().strip(),
            "start_time": datetime.combine(self.target_date, start_time),
            "end_time": datetime.combine(self.target_date, end_time),
            "notes": self.notes_input.toPlainText().strip(),
        }

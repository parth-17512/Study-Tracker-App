from datetime import date, timedelta

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QDateEdit,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.services.timeline_service import TimelineService, TimelineValidationError
from app.ui.components.activity_dialog import ActivityDialog
from app.ui.components.button import PrimaryButton, SecondaryButton
from app.ui.components.card import Card
from app.ui.components.timeline_bar import TimelineBar
from app.ui.theme import Theme


class TimestampPage(QWidget):
    """Date-based 24-hour timeline with study sessions and editable activities."""

    CATEGORY_COLORS = {
        "study": Theme.PRIMARY_ACCENT,
        "rest": Theme.SUCCESS_COLOR,
        "other": Theme.WARNING_COLOR,
        "unallocated": Theme.TEXT_SECONDARY,
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.timeline_service = TimelineService()
        self.selected_date = date.today()
        self.summary_values = {}
        self.summary_cards = []

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet(
            "QScrollArea { background-color: transparent; border: none; }"
        )

        content = QWidget()
        content.setStyleSheet("background-color: transparent;")
        self.layout = QVBoxLayout(content)
        self.layout.setContentsMargins(
            Theme.SPACING_LARGE, Theme.SPACING_LARGE,
            Theme.SPACING_LARGE, Theme.SPACING_LARGE,
        )
        self.layout.setSpacing(Theme.SPACING_LARGE)
        self.scroll_area.setWidget(content)
        outer_layout.addWidget(self.scroll_area)

        self._setup_date_controls()
        self._setup_summary()
        self._setup_timeline()
        self._setup_activity_list()
        self.load_data()

    def _setup_date_controls(self):
        header = QHBoxLayout()
        self.prev_btn = SecondaryButton("<")
        self.prev_btn.setToolTip("Previous day")
        self.prev_btn.clicked.connect(lambda: self._set_date(self.selected_date - timedelta(days=1)))

        self.date_label = QLabel()
        self.date_label.setStyleSheet(
            f"color: {Theme.TEXT_PRIMARY}; font-size: 20px; font-weight: bold;"
        )

        self.date_picker = QDateEdit()
        self.date_picker.setCalendarPopup(True)
        self.date_picker.setDisplayFormat("ddd, MMM d, yyyy")
        self.date_picker.setDate(QDate.currentDate())
        self.date_picker.setStyleSheet(
            f"background-color: {Theme.BACKGROUND_DARK}; color: {Theme.TEXT_PRIMARY}; "
            f"border: 1px solid {Theme.BORDER_COLOR}; border-radius: 5px; padding: 6px;"
        )
        self.date_picker.dateChanged.connect(self._date_picker_changed)

        self.today_btn = SecondaryButton("Today")
        self.today_btn.clicked.connect(lambda: self._set_date(date.today()))
        self.next_btn = SecondaryButton(">")
        self.next_btn.setToolTip("Next day")
        self.next_btn.clicked.connect(lambda: self._set_date(self.selected_date + timedelta(days=1)))

        header.addWidget(self.prev_btn)
        header.addWidget(self.date_picker)
        header.addWidget(self.next_btn)
        header.addWidget(self.today_btn)
        header.addStretch()
        self.layout.addLayout(header)

    def _setup_summary(self):
        summary_card = Card()
        summary_layout = QVBoxLayout()
        title = QLabel("DAILY SUMMARY")
        title.setStyleSheet(
            f"color: {Theme.TEXT_SECONDARY}; font-size: 12px; "
            "font-weight: bold; letter-spacing: 1px;"
        )
        summary_layout.addWidget(title)

        self.summary_grid = QGridLayout()
        self.summary_grid.setSpacing(Theme.SPACING_SMALL)
        for key, label in (
            ("categorized_total", "Total categorized"),
            ("study", "Study"),
            ("rest", "Rest"),
            ("other", "Other activity"),
            ("unallocated", "Unallocated"),
        ):
            metric = Card()
            row = QHBoxLayout()
            label_widget = QLabel(label)
            label_widget.setStyleSheet(f"color: {Theme.TEXT_SECONDARY};")
            value_widget = QLabel("0m")
            value_widget.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            value_widget.setStyleSheet(
                f"color: {Theme.TEXT_PRIMARY}; font-size: 20px; font-weight: bold;"
            )
            row.addWidget(label_widget)
            row.addStretch()
            row.addWidget(value_widget)
            metric.addLayout(row)
            self.summary_cards.append(metric)
            self.summary_grid.addWidget(metric, 0, 0)
            self.summary_values[key] = value_widget
        summary_layout.addLayout(self.summary_grid)
        summary_card.addLayout(summary_layout)
        self.layout.addWidget(summary_card)
        self._arrange_summary_cards()

    def _setup_timeline(self):
        card = Card()
        layout = QVBoxLayout()
        title = QLabel("24-HOUR TIMELINE")
        title.setStyleSheet(
            f"color: {Theme.TEXT_SECONDARY}; font-size: 12px; "
            "font-weight: bold; letter-spacing: 1px;"
        )
        layout.addWidget(title)

        self.unallocated_notice = QLabel(
            "Unallocated time has not been categorized; it is not necessarily confirmed inactivity."
        )
        self.unallocated_notice.setWordWrap(True)
        self.unallocated_notice.setStyleSheet(
            f"color: {Theme.TEXT_SECONDARY}; font-size: 12px;"
        )
        layout.addWidget(self.unallocated_notice)

        self.timeline_bar = TimelineBar()
        layout.addWidget(self.timeline_bar)

        legend = QHBoxLayout()
        for category, label in (
            ("study", "Study"),
            ("rest", "Rest"),
            ("other", "Other"),
            ("unallocated", "Unallocated"),
        ):
            item = QLabel(f"■ {label}")
            item.setStyleSheet(f"color: {self.CATEGORY_COLORS[category]};")
            legend.addWidget(item)
        legend.addStretch()
        layout.addLayout(legend)
        card.addLayout(layout)
        self.layout.addWidget(card)

    def _setup_activity_list(self):
        card = Card()
        layout = QVBoxLayout()
        heading = QHBoxLayout()
        title = QLabel("ACTIVITIES")
        title.setStyleSheet(
            f"color: {Theme.TEXT_SECONDARY}; font-size: 12px; "
            "font-weight: bold; letter-spacing: 1px;"
        )
        self.add_activity_btn = PrimaryButton("Add Activity")
        self.add_activity_btn.clicked.connect(self.add_activity)
        heading.addWidget(title)
        heading.addStretch()
        heading.addWidget(self.add_activity_btn)
        layout.addLayout(heading)

        self.activity_list_layout = QVBoxLayout()
        self.activity_list_layout.setSpacing(Theme.SPACING_SMALL)
        layout.addLayout(self.activity_list_layout)
        card.addLayout(layout)
        self.layout.addWidget(card)
        self.layout.addStretch()

    def _arrange_summary_cards(self):
        if not hasattr(self, "summary_grid"):
            return
        while self.summary_grid.count():
            self.summary_grid.takeAt(0)
        columns = 1 if self.width() < 620 else 3
        for index, card in enumerate(self.summary_cards):
            self.summary_grid.addWidget(card, index // columns, index % columns)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._arrange_summary_cards()

    def _date_picker_changed(self, selected):
        self.selected_date = selected.toPython()
        self.load_data()

    def _set_date(self, selected_date: date):
        self.selected_date = selected_date
        self.date_picker.blockSignals(True)
        self.date_picker.setDate(QDate(
            selected_date.year, selected_date.month, selected_date.day
        ))
        self.date_picker.blockSignals(False)
        self.load_data()

    def previous_day(self):
        self._set_date(self.selected_date - timedelta(days=1))

    def next_day(self):
        self._set_date(self.selected_date + timedelta(days=1))

    def load_data(self):
        self.date_label.setText(self.selected_date.strftime("%A, %B %d, %Y"))
        timeline = self.timeline_service.get_day_timeline(self.selected_date)
        summary = timeline["summary"]

        for key, value in summary.items():
            if key in self.summary_values:
                self.summary_values[key].setText(self._format_duration(value))

        self.timeline_bar.set_segments(timeline["segments"])
        self._render_segments(timeline["segments"])

    def _render_segments(self, segments):
        while self.activity_list_layout.count():
            item = self.activity_list_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        for segment in segments:
            self.activity_list_layout.addWidget(self._create_segment_row(segment))

        if not any(segment["category"] != "unallocated" for segment in segments):
            empty = QLabel(
                "No recorded activities for this day. Completed study sessions appear automatically; "
                "use Add Activity to record Rest or Other time."
            )
            empty.setWordWrap(True)
            empty.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; padding: 8px;")
            self.activity_list_layout.addWidget(empty)

    def _create_segment_row(self, segment):
        card = Card()
        row = QHBoxLayout()
        category = segment["category"]
        start = self._format_clock(segment["start_seconds"])
        end = self._format_clock(segment["end_seconds"])
        time_label = QLabel(f"{start}–{end}")
        time_label.setMinimumWidth(92)
        time_label.setStyleSheet(
            f"color: {Theme.TEXT_PRIMARY}; font-weight: bold;"
        )

        details = QVBoxLayout()
        title = QLabel(f"{segment['name']} · {self._format_duration(segment['duration_seconds'])}")
        title.setWordWrap(True)
        title.setStyleSheet(f"color: {Theme.TEXT_PRIMARY};")
        details.addWidget(title)
        if segment.get("notes"):
            note = QLabel(segment["notes"])
            note.setWordWrap(True)
            note.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-size: 12px;")
            details.addWidget(note)

        category_label = QLabel(category.capitalize())
        category_label.setStyleSheet(
            f"color: {self.CATEGORY_COLORS.get(category, Theme.TEXT_SECONDARY)}; "
            "font-weight: bold;"
        )
        row.addWidget(time_label)
        row.addLayout(details, stretch=1)
        row.addWidget(category_label)

        if segment.get("block_id") is not None:
            edit_button = SecondaryButton("Edit")
            edit_button.clicked.connect(
                lambda checked=False, item=dict(segment): self.edit_activity(item)
            )
            delete_button = SecondaryButton("Delete")
            delete_button.clicked.connect(
                lambda checked=False, block_id=segment["block_id"]: self.delete_activity(block_id)
            )
            row.addWidget(edit_button)
            row.addWidget(delete_button)

        card.addLayout(row)
        return card

    def add_activity(self):
        dialog = ActivityDialog(self.selected_date, parent=self)
        if dialog.exec():
            self._save_activity(dialog.get_data())

    def edit_activity(self, segment):
        dialog = ActivityDialog(self.selected_date, activity=segment, parent=self)
        if dialog.exec():
            self._save_activity(dialog.get_data(), block_id=segment["block_id"])

    def _save_activity(self, activity, block_id=None):
        try:
            if block_id is None:
                self.timeline_service.create_activity_block(
                    self.selected_date, **activity
                )
            else:
                updated = self.timeline_service.update_activity_block(
                    block_id, self.selected_date, **activity
                )
                if not updated:
                    QMessageBox.warning(
                        self, "Activity not found",
                        "This activity no longer exists. The timeline will be refreshed.",
                    )
        except TimelineValidationError as exc:
            QMessageBox.warning(self, "Cannot save activity", str(exc))
            return
        self.load_data()

    def delete_activity(self, block_id):
        result = QMessageBox.question(
            self,
            "Delete activity",
            "Delete this activity block?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if result != QMessageBox.StandardButton.Yes:
            return
        if not self.timeline_service.delete_activity_block(block_id):
            QMessageBox.warning(
                self, "Activity not found",
                "This activity no longer exists. The timeline will be refreshed.",
            )
        self.load_data()

    @staticmethod
    def _format_duration(seconds: int) -> str:
        hours, remainder = divmod(max(0, int(seconds)), 3600)
        minutes = remainder // 60
        if hours and minutes:
            return f"{hours}h {minutes}m"
        if hours:
            return f"{hours}h"
        return f"{minutes}m"

    @staticmethod
    def _format_clock(seconds: int) -> str:
        if seconds >= 86400:
            return "24:00"
        return f"{seconds // 3600:02d}:{(seconds % 3600) // 60:02d}"

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QToolTip, QWidget

from app.ui.theme import Theme


class TimelineBar(QWidget):
    """Paint a proportional, color-coded view of the complete 24-hour day."""

    COLORS = {
        "study": Theme.PRIMARY_ACCENT,
        "rest": Theme.SUCCESS_COLOR,
        "other": Theme.WARNING_COLOR,
        "unallocated": Theme.BACKGROUND_CARD_HOVER,
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.segments = []
        self.setMinimumHeight(92)
        self.setMouseTracking(True)

    def set_segments(self, segments):
        self.segments = list(segments)
        self.update()

    def _track_bounds(self):
        left = 40
        right = max(left + 1, self.width() - 12)
        return left, right, right - left

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        left, right, track_width = self._track_bounds()
        track_top = 18
        track_height = 30

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(Theme.BACKGROUND_DARK))
        painter.drawRoundedRect(left, track_top, track_width, track_height, 6, 6)

        for segment in self.segments:
            start = segment["start_seconds"] / 86400
            end = segment["end_seconds"] / 86400
            x = left + start * track_width
            segment_width = max(0, (end - start) * track_width)
            if segment_width <= 0:
                continue
            color = QColor(self.COLORS.get(segment["category"], Theme.BORDER_COLOR))
            painter.setBrush(color)
            painter.drawRect(int(x), track_top, max(1, int(segment_width + 0.5)), track_height)
            if segment_width >= 54:
                painter.setPen(QColor(Theme.TEXT_PRIMARY))
                painter.drawText(
                    int(x) + 5,
                    track_top,
                    max(0, int(segment_width) - 10),
                    track_height,
                    Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                    segment["category"].capitalize(),
                )
                painter.setPen(Qt.PenStyle.NoPen)

        painter.setPen(QPen(QColor(Theme.BORDER_COLOR), 1))
        for hour in range(0, 25, 4):
            x = left + track_width * hour / 24
            painter.drawLine(int(x), track_top - 3, int(x), track_top + track_height + 3)
            label = f"{hour:02d}:00"
            if hour == 24:
                painter.drawText(int(x) - 40, 76, 40, 16, Qt.AlignmentFlag.AlignRight, label)
            elif hour == 0:
                painter.drawText(int(x), 76, 46, 16, Qt.AlignmentFlag.AlignLeft, label)
            else:
                painter.drawText(int(x) - 23, 76, 46, 16, Qt.AlignmentFlag.AlignHCenter, label)

        painter.end()

    def mouseMoveEvent(self, event):
        left, right, track_width = self._track_bounds()
        x = event.position().x()
        if track_width <= 0 or x < left or x > right:
            QToolTip.hideText()
            return

        position = (x - left) / track_width * 86400
        for segment in self.segments:
            if segment["start_seconds"] <= position < segment["end_seconds"]:
                start = self._format_time(segment["start_seconds"])
                end = self._format_time(segment["end_seconds"])
                QToolTip.showText(
                    event.globalPosition().toPoint(),
                    f"{segment['name']} ({segment['category'].capitalize()})\n"
                    f"{start}–{end} · {self._format_duration(segment['duration_seconds'])}",
                    self,
                )
                return
        QToolTip.hideText()

    @staticmethod
    def _format_time(seconds):
        if seconds >= 86400:
            return "24:00"
        return f"{seconds // 3600:02d}:{(seconds % 3600) // 60:02d}"

    @staticmethod
    def _format_duration(seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes = remainder // 60
        if hours and minutes:
            return f"{hours}h {minutes}m"
        if hours:
            return f"{hours}h"
        return f"{minutes}m"

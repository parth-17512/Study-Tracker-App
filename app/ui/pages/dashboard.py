from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt
from app.ui.theme import Theme
from app.ui.components.card import Card

class MetricCard(Card):
    """A specific card for displaying a top metric."""
    def __init__(self, title, value, subtitle="", progress=None, parent=None):
        super().__init__(parent)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-weight: bold;")
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"color: {Theme.TEXT_PRIMARY}; font-size: {Theme.FONT_SIZE_XXLARGE}; font-weight: bold;")
        
        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-size: {Theme.FONT_SIZE_SMALL};")
        
        self.addWidget(title_label)
        self.addWidget(value_label)
        self.addWidget(subtitle_label)

class DashboardPage(QWidget):
    """The main dashboard view."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(Theme.SPACING_LARGE, Theme.SPACING_LARGE, Theme.SPACING_LARGE, Theme.SPACING_LARGE)
        self.layout.setSpacing(Theme.SPACING_LARGE)
        
        # Metrics Row
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(Theme.SPACING_REGULAR)
        
        # Add placeholder metrics
        self.today_card = MetricCard("Today's Study", "4h 20m", "of 6h goal")
        self.streak_card = MetricCard("Current Streak", "12 days", "Longest: 27 days")
        self.total_card = MetricCard("Total Study Time", "245h 30m", "Across 89 study days")
        self.weekly_card = MetricCard("Weekly Goal", "28h / 35h", "80% completed")
        
        metrics_layout.addWidget(self.today_card)
        metrics_layout.addWidget(self.streak_card)
        metrics_layout.addWidget(self.total_card)
        metrics_layout.addWidget(self.weekly_card)
        
        self.layout.addLayout(metrics_layout)
        
        # Main content row
        content_layout = QHBoxLayout()
        content_layout.setSpacing(Theme.SPACING_REGULAR)
        
        # Timer placeholder
        timer_card = Card()
        timer_label = QLabel("Study Timer")
        timer_label.setStyleSheet(f"color: {Theme.TEXT_PRIMARY}; font-size: {Theme.FONT_SIZE_LARGE}; font-weight: bold;")
        timer_card.addWidget(timer_label)
        timer_card.layout.addStretch()
        content_layout.addWidget(timer_card, stretch=2)
        
        # Today's Sessions placeholder
        sessions_card = Card()
        sessions_label = QLabel("Today's Sessions")
        sessions_label.setStyleSheet(f"color: {Theme.TEXT_PRIMARY}; font-size: {Theme.FONT_SIZE_LARGE}; font-weight: bold;")
        sessions_card.addWidget(sessions_label)
        sessions_card.layout.addStretch()
        content_layout.addWidget(sessions_card, stretch=1)
        
        self.layout.addLayout(content_layout)
        
        # Add a placeholder for heatmap at the bottom
        heatmap_card = Card()
        heatmap_label = QLabel("Study Activity (Heatmap Placeholder)")
        heatmap_label.setStyleSheet(f"color: {Theme.TEXT_PRIMARY}; font-size: {Theme.FONT_SIZE_LARGE}; font-weight: bold;")
        heatmap_card.addWidget(heatmap_label)
        heatmap_card.layout.addStretch()
        
        self.layout.addWidget(heatmap_card)

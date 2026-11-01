from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea
from PySide6.QtCore import Qt, QThread, Signal
from datetime import datetime, timezone
from app.ui.theme import Theme
from app.ui.components.card import Card
from app.ui.components.button import PrimaryButton, SecondaryButton
from app.ui.components.charts import BarChartWidget, DistributionChartWidget
from app.services.analytics_service import AnalyticsService
from app.ai.agent import StudyCoachAgent

class AIInsightsWorker(QThread):
    chunk_received = Signal(str)
    finished = Signal()
    error = Signal(str)
    
    def __init__(self, stats_context: str):
        super().__init__()
        self.stats_context = stats_context
        
    def run(self):
        try:
            from app.ai.providers.router import FallbackProviderRouter
            router = FallbackProviderRouter()
            prompt = (
                "You are an Advanced Analytical AI for a student's study tracker app. "
                "Based on the following stats, provide a daily summary with key insights, "
                "identify strengths and weaknesses, suggest areas to improve, and offer "
                "actionable advice on how to sustainably increase focus time.\n\n"
                f"Data Context:\n{self.stats_context}\n\n"
                "Format your response elegantly in Markdown using headers, bold text, and lists."
            )
            response = router.generate_text(prompt)
            provider = router.last_used_provider_name or "No LLM provider succeeded"
            self.chunk_received.emit(f"{response}\n\n*Provider: {provider}*")
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

class SubjectGroupingWorker(QThread):
    completed = Signal(dict, str)
    failed = Signal(str)

    def __init__(self, topic_distribution, parent=None):
        super().__init__(parent)
        self.topic_distribution = dict(topic_distribution)

    def run(self):
        try:
            from app.services.subject_grouping_service import SubjectGroupingService
            service = SubjectGroupingService()
            grouped = service.group_topics(self.topic_distribution)
            provider = service.router.last_used_provider_name or "Conservative local grouping"
            self.completed.emit(grouped, provider)
        except Exception as e:
            self.failed.emit(str(e))

class AnalyticsPage(QWidget):
    """Deep analytics and charts for study data."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.analytics_service = AnalyticsService()
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll area for deep analytics
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background-color: transparent;")
        self.layout = QVBoxLayout(self.scroll_content)
        self.layout.setContentsMargins(Theme.SPACING_LARGE, Theme.SPACING_LARGE, Theme.SPACING_LARGE, Theme.SPACING_LARGE)
        self.layout.setSpacing(Theme.SPACING_LARGE)
        
        self.scroll.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.scroll, stretch=1)
        
        self.showing_ai_grouped = False
        self.cached_grouped_data = None
        self.setup_ui()
        
    def setup_ui(self):
        # Header
        lbl_title = QLabel("Advanced Analytics")
        lbl_title.setStyleSheet(f"color: {Theme.TEXT_PRIMARY}; font-size: 28px; font-weight: bold;")
        self.layout.addWidget(lbl_title)
        
        # 1. Summary Stats Row
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(Theme.SPACING_LARGE)
        
        self.lbl_total_sessions = self._create_stat_card(stats_layout, "Total Sessions", "0")
        self.lbl_total_time = self._create_stat_card(stats_layout, "Total Study Time", "0h 0m")
        self.lbl_avg_session = self._create_stat_card(stats_layout, "Avg Session", "0m")
        self.lbl_best_day = self._create_stat_card(stats_layout, "Best Day", "-")
        
        self.layout.addLayout(stats_layout)
        
        # 2. Period Comparisons Row
        comp_layout = QHBoxLayout()
        comp_layout.setSpacing(Theme.SPACING_LARGE)
        
        # Week Card
        week_card = Card()
        week_layout = QVBoxLayout()
        lbl_week_title = QLabel("This Week vs Last Week")
        lbl_week_title.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-weight: bold;")
        week_layout.addWidget(lbl_week_title)
        
        self.lbl_week_comp = QLabel("No data")
        self.lbl_week_comp.setStyleSheet(f"color: {Theme.TEXT_PRIMARY}; font-size: 18px;")
        week_layout.addWidget(self.lbl_week_comp)
        week_card.addLayout(week_layout)
        comp_layout.addWidget(week_card)
        
        # Month Card
        month_card = Card()
        month_layout = QVBoxLayout()
        lbl_month_title = QLabel("This Month vs Last Month")
        lbl_month_title.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-weight: bold;")
        month_layout.addWidget(lbl_month_title)
        
        self.lbl_month_comp = QLabel("No data")
        self.lbl_month_comp.setStyleSheet(f"color: {Theme.TEXT_PRIMARY}; font-size: 18px;")
        month_layout.addWidget(self.lbl_month_comp)
        month_card.addLayout(month_layout)
        comp_layout.addWidget(month_card)
        
        self.layout.addLayout(comp_layout)
        
        # 3. Charts Row
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(Theme.SPACING_LARGE)
        
        # 7 Days Bar Chart
        bar_card = Card()
        bar_layout = QVBoxLayout()
        lbl_bar_title = QLabel("Last 7 Days Activity")
        lbl_bar_title.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-weight: bold;")
        bar_layout.addWidget(lbl_bar_title)
        
        self.bar_chart = BarChartWidget()
        bar_layout.addWidget(self.bar_chart)
        bar_card.addLayout(bar_layout)
        charts_layout.addWidget(bar_card, stretch=1)

        # Topic Distribution
        dist_card = Card()
        dist_layout = QVBoxLayout()

        dist_header = QHBoxLayout()
        lbl_dist_title = QLabel("Top 10 Subjects by Study Time")
        lbl_dist_title.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-weight: bold;")
        dist_header.addWidget(lbl_dist_title)
        dist_header.addStretch()

        self.btn_toggle_grouping = SecondaryButton("Group with AI 🤖")
        self.btn_toggle_grouping.setFixedHeight(28)
        self.btn_toggle_grouping.setStyleSheet(f"font-size: 11px; padding: 4px 10px; border-radius: 4px;")
        self.btn_toggle_grouping.clicked.connect(self.toggle_subject_grouping)
        dist_header.addWidget(self.btn_toggle_grouping)

        dist_layout.addLayout(dist_header)

        self.lbl_grouping_status = QLabel("")
        self.lbl_grouping_status.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-size: 11px; font-style: italic; margin-bottom: 4px;")
        dist_layout.addWidget(self.lbl_grouping_status)
        
        self.dist_chart = DistributionChartWidget()
        self.dist_chart.setFixedHeight(340)
        dist_layout.addWidget(self.dist_chart)
        dist_card.addLayout(dist_layout)
        charts_layout.addWidget(dist_card, stretch=1)
        
        self.layout.addLayout(charts_layout)
        
        # 4. Advanced AI Insights
        self.ai_card = Card()
        ai_layout = QVBoxLayout()
        
        lbl_ai_title = QLabel("🤖 AI Study Analysis")
        lbl_ai_title.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-weight: bold; font-size: 16px;")
        ai_layout.addWidget(lbl_ai_title)
        
        self.btn_generate_insights = PrimaryButton("Generate AI Insights")
        self.btn_generate_insights.clicked.connect(self.generate_insights)
        ai_layout.addWidget(self.btn_generate_insights)
        
        self.lbl_ai_insights = QLabel("Click the button above to deeply analyze your study habits and get actionable advice.")
        self.lbl_ai_insights.setWordWrap(True)
        self.lbl_ai_insights.setTextFormat(Qt.MarkdownText)
        self.lbl_ai_insights.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.lbl_ai_insights.setStyleSheet(f"color: {Theme.TEXT_PRIMARY}; font-size: 14px; margin-top: 10px;")
        ai_layout.addWidget(self.lbl_ai_insights)
        
        self.ai_card.addLayout(ai_layout)
        self.layout.addWidget(self.ai_card)
        
        self.layout.addStretch()
        
    def _create_stat_card(self, parent_layout, title, default_val):
        card = Card()
        layout = QVBoxLayout()
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-size: 12px; font-weight: bold;")
        layout.addWidget(lbl_title)
        
        lbl_val = QLabel(default_val)
        lbl_val.setStyleSheet(f"color: {Theme.TEXT_PRIMARY}; font-size: 24px; font-weight: bold;")
        layout.addWidget(lbl_val)
        
        card.addLayout(layout)
        parent_layout.addWidget(card)
        return lbl_val

    def load_data(self):
        """Called automatically when navigating to this page."""
        now = datetime.now(timezone.utc)
        
        # 1. Summary Stats
        stats = self.analytics_service.get_summary_stats()
        self.lbl_total_sessions.setText(str(stats["total_sessions"]))
        
        ts = stats["total_seconds"]
        self.lbl_total_time.setText(f"{ts//3600}h {(ts%3600)//60}m" if ts > 0 else "0h 0m")
        
        av = stats["avg_session_seconds"]
        self.lbl_avg_session.setText(f"{av//3600}h {(av%3600)//60}m" if av >= 3600 else f"{av//60}m")
        
        best = stats["best_day"]
        if best:
            bs = stats["best_day_seconds"]
            bstr = f"{bs//3600}h {(bs%3600)//60}m" if bs >= 3600 else f"{bs//60}m"
            self.lbl_best_day.setText(f"{best.strftime('%b %d')} ({bstr})")
        else:
            self.lbl_best_day.setText("-")
            
        # 2. Period Comparisons
        comps = self.analytics_service.get_period_comparisons(now)
        
        # Week
        tw = comps["this_week"]
        lw = comps["last_week"]
        self._set_comparison_label(self.lbl_week_comp, tw, lw)
        
        # Month
        tm = comps["this_month"]
        lm = comps["last_month"]
        self._set_comparison_label(self.lbl_month_comp, tm, lm)
        
        # 3. Charts
        bar_data = self.analytics_service.get_last_7_days_chart_data(now)
        self.bar_chart.set_data(bar_data)
        
        self.refresh_distribution_view()

    def toggle_subject_grouping(self):
        self.showing_ai_grouped = not self.showing_ai_grouped
        if self.showing_ai_grouped:
            self.btn_toggle_grouping.setText("View Original Subjects")
            self.lbl_grouping_status.setText("Grouping similar topics into learning areas... ⏳")
        else:
            self.btn_toggle_grouping.setText("Group with AI 🤖")
            self.lbl_grouping_status.setText("Showing original subjects.")
        self.refresh_distribution_view()

    def refresh_distribution_view(self):
        dist_data = self.analytics_service.get_topic_distribution()
        if not dist_data:
            self.showing_ai_grouped = False
            self.btn_toggle_grouping.setText("Group with AI 🤖")
            self.dist_chart.set_data({})
            self.lbl_grouping_status.setText("No study sessions recorded yet.")
            self.btn_toggle_grouping.setEnabled(True)
            return

        if self.showing_ai_grouped:
            self.lbl_grouping_status.setText("Grouping similar topics... This may take a moment.")
            self.btn_toggle_grouping.setEnabled(False)
            self.subject_grouping_worker = SubjectGroupingWorker(dist_data, self)
            self.subject_grouping_worker.completed.connect(self._on_grouping_completed)
            self.subject_grouping_worker.failed.connect(self._on_grouping_failed)
            self.subject_grouping_worker.start()
        else:
            self.btn_toggle_grouping.setEnabled(True)
            self.dist_chart.set_data(dist_data)
            self.lbl_grouping_status.setText(
                f"Showing the top 10 of {len(dist_data)} original subjects by study time."
            )

    def _on_grouping_completed(self, grouped, provider_name):
        if not self.showing_ai_grouped:
            return
        self.btn_toggle_grouping.setEnabled(True)
        self.dist_chart.set_grouped_data(grouped)
        num_groups = len(grouped.get("groups", []))
        num_topics = sum(len(group.get("topics", [])) for group in grouped.get("groups", []))
        self.lbl_grouping_status.setText(
            f"Grouped {num_topics} topics into {num_groups} learning areas using {provider_name}. "
            f"Showing the top 10 learning areas by study time."
        )

    def _on_grouping_failed(self, error):
        if not self.showing_ai_grouped:
            return
        self.btn_toggle_grouping.setEnabled(True)
        data = self.analytics_service.get_topic_distribution()
        self.dist_chart.set_data(data)
        self.lbl_grouping_status.setText(
            f"AI grouping failed: {error}. Showing the top 10 original subjects instead."
        )

    def _set_comparison_label(self, label, current_sec, past_sec):
        ch = current_sec // 3600
        cm = (current_sec % 3600) // 60
        curr_str = f"{ch}h {cm}m" if ch > 0 else f"{cm}m"
        
        if past_sec == 0:
            if current_sec == 0:
                label.setText("No data yet.")
                label.setStyleSheet(f"color: {Theme.TEXT_SECONDARY};")
            else:
                label.setText(f"{curr_str} (Up from 0)")
                label.setStyleSheet(f"color: {Theme.SUCCESS_COLOR}; font-size: 18px;")
        else:
            pct = ((current_sec - past_sec) / past_sec) * 100
            arrow = "↑" if pct > 0 else "↓" if pct < 0 else "="
            color = Theme.SUCCESS_COLOR if pct >= 0 else Theme.WARNING_COLOR
            label.setText(f"{curr_str} ({arrow} {abs(pct):.1f}%)")
            label.setStyleSheet(f"color: {color}; font-size: 18px;")

    def generate_insights(self):
        """Generates AI insights based on current analytics data."""
        self.btn_generate_insights.setEnabled(False)
        self.btn_generate_insights.setText("Analyzing Data... 🤔")
        
        # Gather context
        now = datetime.now(timezone.utc)
        stats = self.analytics_service.get_summary_stats()
        comps = self.analytics_service.get_period_comparisons(now)
        dist = self.analytics_service.get_topic_distribution()
        
        # Build context string
        context = []
        context.append(f"Total Lifetime Sessions: {stats['total_sessions']}")
        context.append(f"Total Lifetime Focus Time (seconds): {stats['total_seconds']}")
        context.append(f"This Week Focus Time (seconds): {comps['this_week']} (Last Week: {comps['last_week']})")
        context.append(f"This Month Focus Time (seconds): {comps['this_month']} (Last Month: {comps['last_month']})")
        
        context.append("\nTime Spent per Subject (seconds):")
        for subj, t in dist.items():
            context.append(f"- {subj}: {t}")
            
        context_str = "\n".join(context)
        
        self.ai_worker = AIInsightsWorker(context_str)
        self.ai_worker.chunk_received.connect(self._on_chunk_received)
        self.ai_worker.finished.connect(self._on_insights_finished)
        self.ai_worker.error.connect(self._on_insights_error)
        
        self.current_insights_text = ""
        self.lbl_ai_insights.setText("")
        self.ai_worker.start()
        
    def _on_chunk_received(self, chunk: str):
        self.current_insights_text += chunk
        self.lbl_ai_insights.setText(self.current_insights_text)
        
    def _on_insights_finished(self):
        self.btn_generate_insights.setEnabled(True)
        self.btn_generate_insights.setText("Regenerate AI Insights")
        
    def _on_insights_error(self, err: str):
        self.btn_generate_insights.setEnabled(True)
        self.btn_generate_insights.setText("Generate AI Insights")
        self.lbl_ai_insights.setText(f"**Error generating insights:** {err}")

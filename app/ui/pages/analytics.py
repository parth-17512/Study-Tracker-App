from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea
from PySide6.QtCore import Qt, QThread, Signal
from datetime import datetime, timezone
from app.ui.theme import Theme
from app.ui.components.card import Card
from app.ui.components.button import PrimaryButton
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
            from app.config.config_manager import ConfigManager
            config = ConfigManager()
            api_key = config.get("gemini_api_key", "").strip()
            
            if not api_key:
                self.error.emit("Gemini API Key is not configured. Please add it in Settings.")
                return
                
            from google import genai
            
            client = genai.Client(api_key=api_key)
            prompt = (
                "You are an Advanced Analytical AI for a student's study tracker app. "
                "Based on the following stats, provide a daily summary with key insights, "
                "identify strengths and weaknesses, suggest areas to improve, and offer "
                "actionable advice on how to sustainably increase focus time.\n\n"
                f"Data Context:\n{self.stats_context}\n\n"
                "Format your response elegantly in Markdown using headers, bold text, and lists."
            )
            
            response_stream = client.models.generate_content_stream(
                model="gemini-3.6-flash",
                contents=prompt
            )
            
            for chunk in response_stream:
                if chunk.text:
                    self.chunk_received.emit(chunk.text)
            
            self.finished.emit()
        except Exception as e:
            # Fallback to older model if available
            self.error.emit(str(e))

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
        lbl_dist_title = QLabel("Subject Distribution")
        lbl_dist_title.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-weight: bold; margin-bottom: 8px;")
        dist_layout.addWidget(lbl_dist_title)
        
        self.dist_chart = DistributionChartWidget()
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
        
        dist_data = self.analytics_service.get_topic_distribution()
        self.dist_chart.set_data(dist_data)

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

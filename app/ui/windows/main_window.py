from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget, QLabel, QSizePolicy
from PySide6.QtCore import Qt
from app.ui.widgets.sidebar import Sidebar
from app.ui.widgets.topbar import Topbar
from app.ui.pages.dashboard import DashboardPage
from app.ui.theme import Theme

from app.ui.pages.timer import TimerPage
from app.ui.pages.coach import CoachPage
from app.services.timer_service import TimerService
from app.services.session_service import SessionService
from app.services.notification_service import NotificationService

class MainWindow(QMainWindow):
    """The main application window containing the sidebar and page stack."""
    
    def __init__(self, timer_service: TimerService):
        super().__init__()
        self.timer_service = timer_service
        self.session_service = SessionService()
        self.notification_service = NotificationService(self)
        self.setWindowTitle("StudyTrack")
        self.setMinimumSize(1000, 700)
        
        # Central Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main Layout (Horizontal: Sidebar + Right Content)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # 1. Sidebar
        self.sidebar = Sidebar()
        self.main_layout.addWidget(self.sidebar)
        
        # 2. Right Content Area
        self.right_widget = QWidget()
        self.right_layout = QVBoxLayout(self.right_widget)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_layout.setSpacing(0)
        
        # 2a. Topbar
        self.topbar = Topbar()
        self.right_layout.addWidget(self.topbar)
        
        # 2b. Pages Stack
        self.pages_stack = QStackedWidget()
        self.pages_stack.setStyleSheet(f"background-color: {Theme.BACKGROUND_DARK};")
        self.pages_stack.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.right_layout.addWidget(self.pages_stack, stretch=1)
        
        self.right_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.main_layout.addWidget(self.right_widget, stretch=1)
        
        # Initialize Pages
        self.setup_pages()
        
        # Connect Navigation
        self.sidebar.navigation_requested.connect(self.navigate_to)
        
    def setup_pages(self):
        """Initialize and add pages to the stack."""
        self.pages = {}
        
        # Dashboard
        self.pages["dashboard"] = DashboardPage()
        self.pages_stack.addWidget(self.pages["dashboard"])
        
        # Timer
        self.pages["timer"] = TimerPage(self.timer_service, self.notification_service)
        self.pages_stack.addWidget(self.pages["timer"])
        
        # Sessions
        from app.ui.pages.sessions import SessionsPage
        self.pages["sessions"] = SessionsPage()
        self.pages_stack.addWidget(self.pages["sessions"])
        
        # Calendar
        from app.ui.pages.calendar import CalendarPage
        self.pages["calendar"] = CalendarPage()
        self.pages_stack.addWidget(self.pages["calendar"])
        
        # Analytics
        from app.ui.pages.analytics import AnalyticsPage
        self.pages["analytics"] = AnalyticsPage()
        self.pages_stack.addWidget(self.pages["analytics"])
        
        # Settings
        from app.ui.pages.settings import SettingsPage
        self.pages["settings"] = SettingsPage()
        self.pages_stack.addWidget(self.pages["settings"])
        
        # Coach
        self.pages["coach"] = CoachPage()
        self.pages_stack.addWidget(self.pages["coach"])
        
        # Placeholders for other pages
        for page_name in ["goals", "subjects"]:
            placeholder = QWidget()
            layout = QVBoxLayout(placeholder)
            label = QLabel(f"{page_name.capitalize()} Page (Coming Soon)")
            label.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-size: {Theme.FONT_SIZE_XLARGE};")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label)
            self.pages[page_name] = placeholder
            self.pages_stack.addWidget(placeholder)
            
        # Set default page
        self.navigate_to("dashboard")
        
    def navigate_to(self, page_name: str):
        """Navigate to a specific page."""
        if page_name in self.pages:
            target_page = self.pages[page_name]
            self.pages_stack.setCurrentWidget(target_page)
            self.topbar.set_title(page_name.capitalize())
            
            # Auto-refresh data if the page supports it
            if hasattr(target_page, 'load_data'):
                target_page.load_data()
            # Bind Ctrl+K for Global Search
        from PySide6.QtGui import QShortcut, QKeySequence
        self.search_shortcut = QShortcut(QKeySequence("Ctrl+K"), self)
        self.search_shortcut.activated.connect(self.show_search_dialog)

    def show_search_dialog(self):
        from app.ui.components.search_dialog import SearchDialog
        from app.ui.components.dialogs import EditSessionDialog
        
        dialog = SearchDialog(self.session_service, self)
        
        def on_session_selected(session_id):
            session = self.session_service.get_session(session_id)
            if session:
                edit_dialog = EditSessionDialog(session, self)
                if edit_dialog.exec():
                    data = edit_dialog.get_data()
                    self.session_service.update_session(session_id, **data)
                    # Refresh pages if needed
                    self.navigate_to(self.sidebar.current_nav)
                    
        dialog.session_selected.connect(on_session_selected)
        dialog.show()
        # Ensure it receives focus
        dialog.search_input.setFocus()

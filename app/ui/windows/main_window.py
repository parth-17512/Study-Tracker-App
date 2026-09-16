from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget, QLabel
from PySide6.QtCore import Qt
from app.ui.widgets.sidebar import Sidebar
from app.ui.widgets.topbar import Topbar
from app.ui.pages.dashboard import DashboardPage
from app.ui.theme import Theme

from app.ui.pages.timer import TimerPage
from app.services.timer_service import TimerService

class MainWindow(QMainWindow):
    """The main application window."""
    
    def __init__(self, timer_service: TimerService):
        super().__init__()
        self.timer_service = timer_service
        self.setWindowTitle("StudyTrack - Build a Better You")
        self.setMinimumSize(1280, 720)
        
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
        self.right_layout.addWidget(self.pages_stack)
        
        self.main_layout.addWidget(self.right_widget)
        
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
        self.pages["timer"] = TimerPage(self.timer_service)
        self.pages_stack.addWidget(self.pages["timer"])
        
        # Placeholders for other pages
        for page_name in ["sessions", "goals", "analytics", "calendar", "subjects", "settings"]:
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
            self.pages_stack.setCurrentWidget(self.pages[page_name])
            self.topbar.set_title(page_name.capitalize())

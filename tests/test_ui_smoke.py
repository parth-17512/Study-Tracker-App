import pytest
import sys
from PySide6.QtWidgets import QApplication

# Initialize a dummy QApplication for UI tests
@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app

def test_ui_imports():
    """Smoke test to ensure all pages and components can be imported without syntax/attribute errors."""
    try:
        from app.ui.pages.dashboard import DashboardPage
        from app.ui.pages.timer import TimerPage
        from app.ui.pages.sessions import SessionsPage
        from app.ui.pages.analytics import AnalyticsPage
        from app.ui.pages.settings import SettingsPage
        
        from app.ui.components.dialogs import AlarmDialog, DailySessionsDialog
        from app.ui.components.search_dialog import SearchDialog
    except Exception as e:
        pytest.fail(f"UI import failed with error: {e}")

def test_ui_instantiation(qapp):
    """Smoke test to ensure pages can be instantiated without crashing."""
    try:
        from app.ui.pages.settings import SettingsPage
        from app.ui.pages.analytics import AnalyticsPage
        from app.ui.pages.sessions import SessionsPage
        
        # Instantiate to ensure __init__ doesn't raise errors like missing Theme colors
        page1 = SettingsPage()
        page2 = AnalyticsPage()
        page3 = SessionsPage()
        
        assert page1 is not None
        assert page2 is not None
        assert page3 is not None
    except Exception as e:
        pytest.fail(f"UI instantiation failed with error: {e}")

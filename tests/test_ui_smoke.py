import pytest
import sys
from PySide6.QtWidgets import QApplication, QLabel

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

def test_dashboard_replaces_recent_activity_with_full_width_graph(qapp):
    from PySide6.QtWidgets import QLabel
    from app.ui.pages.dashboard import DashboardPage

    dashboard = DashboardPage()
    labels = [label.text() for label in dashboard.findChildren(QLabel)]

    assert not any("RECENT ACTIVITY" in text for text in labels)
    assert hasattr(dashboard, "heatmap")
    assert not hasattr(dashboard, "recent_list_layout")


def test_subject_distribution_only_displays_top_ten_in_both_views(qapp):
    from app.ui.pages.analytics import AnalyticsPage

    page = AnalyticsPage()
    chart = page.dist_chart
    distribution = {f"Subject {index}": index * 3600 for index in range(1, 13)}

    chart.set_data(distribution)
    original_labels = [
        label.text()
        for label in chart.findChildren(QLabel)
        if label.text().startswith("Subject ")
    ]
    assert len(original_labels) == 10
    assert "Subject 12" in original_labels
    assert "Subject 1" not in original_labels

    grouped_data = {
        "total_seconds": sum(distribution.values()),
        "groups": [
            {
                "label": f"Area {index}",
                "total_seconds": index * 3600,
                "formatted_duration": f"{index}h 0m",
                "percentage": index / 78 * 100,
                "topics": [{"name": f"Original {index}", "formatted": f"{index}h 0m"}],
            }
            for index in range(1, 13)
        ],
    }
    chart.set_grouped_data(grouped_data)
    qapp.processEvents()

    group_labels = [
        label.text()
        for label in chart.findChildren(QLabel)
        if label.text().startswith("Area ")
    ]
    original_detail_labels = [
        label.text()
        for label in chart.findChildren(QLabel)
        if label.text().startswith("• Original ")
    ]
    assert len(group_labels) == 10
    assert "Area 12" in group_labels
    assert "Area 1" not in group_labels
    assert original_detail_labels == []
    assert chart.minimumHeight() == 340
    assert chart.maximumHeight() == 340

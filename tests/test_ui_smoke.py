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

def test_main_window_defers_pages_until_navigation(qapp, monkeypatch):
    from PySide6.QtWidgets import QWidget
    from app.ui.windows import main_window

    monkeypatch.setattr(main_window, "DashboardPage", lambda: QWidget())
    monkeypatch.setattr(main_window, "SessionService", lambda: object())
    monkeypatch.setattr(main_window, "NotificationService", lambda parent: object())

    window = main_window.MainWindow(timer_service=object())
    assert set(window.pages) == {"dashboard"}
    assert window.pages_stack.count() == 1

    notes_page = QWidget()
    window.page_factories["notes"] = lambda: notes_page
    window.navigate_to("notes")

    assert window.pages["notes"] is notes_page
    assert window.pages_stack.count() == 2
    window.close()

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


def test_timestamp_page_renders_summary_and_activity_rows(qapp, monkeypatch):
    from app.ui.pages import timestamp

    segments = [
        {
            "category": "unallocated",
            "name": "Unallocated time",
            "notes": "",
            "start_seconds": 0,
            "end_seconds": 9 * 3600,
            "duration_seconds": 9 * 3600,
            "block_id": None,
            "session_id": None,
        },
        {
            "category": "study",
            "name": "Math",
            "notes": "",
            "start_seconds": 9 * 3600,
            "end_seconds": 10 * 3600,
            "duration_seconds": 3600,
            "block_id": None,
            "session_id": 1,
        },
        {
            "category": "unallocated",
            "name": "Unallocated time",
            "notes": "",
            "start_seconds": 10 * 3600,
            "end_seconds": 86400,
            "duration_seconds": 14 * 3600,
            "block_id": None,
            "session_id": None,
        },
    ]

    class FakeTimelineService:
        def get_day_timeline(self, target_date):
            return {
                "date": target_date,
                "entries": [],
                "segments": segments,
                "summary": {
                    "study": 3600,
                    "rest": 0,
                    "other": 0,
                    "unallocated": 82800,
                    "categorized_total": 3600,
                    "total_seconds": 86400,
                },
            }

    monkeypatch.setattr(timestamp, "TimelineService", FakeTimelineService)
    page = timestamp.TimestampPage()
    page.resize(1000, 700)
    page.show()
    qapp.processEvents()

    assert page.summary_values["study"].text() == "1h"
    assert page.summary_values["categorized_total"].text() == "1h"
    assert page.summary_values["unallocated"].text() == "23h"
    assert len(page.timeline_bar.segments) == 3
    assert page.date_picker.calendarPopup()
    page.close()


def test_activity_dialog_validates_same_day_times(qapp):
    from datetime import date
    from PySide6.QtCore import QTime
    from PySide6.QtWidgets import QDialog
    from app.ui.components.activity_dialog import ActivityDialog

    target_date = date(2026, 11, 15)
    dialog = ActivityDialog(target_date)
    dialog.name_input.setText("Walk")
    dialog.start_input.setTime(QTime(14, 0))
    dialog.end_input.setTime(QTime(14, 0))
    dialog._validate_and_accept()

    assert dialog.result() != QDialog.DialogCode.Accepted
    assert "later than start time" in dialog.feedback.text()

    dialog.end_input.setTime(QTime(15, 0))
    dialog._validate_and_accept()
    assert dialog.result() == QDialog.DialogCode.Accepted

    activity = dialog.get_data()
    assert activity["start_time"].date() == target_date
    assert activity["end_time"].hour == 15


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

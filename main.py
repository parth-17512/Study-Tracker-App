import sys
import logging
from PySide6.QtWidgets import QApplication
from app.ui.windows.main_window import MainWindow
from app.ui.theme import GLOBAL_STYLESHEET
from app.database.database import db

def main():
    logger = logging.getLogger(__name__)
    
    # 1. Initialize Database
    try:
        db.init_db()
    except Exception as e:
        logger.critical(f"Failed to initialize database: {e}")
        sys.exit(1)
        
    # 2. Start Application
    app = QApplication(sys.argv)
    
    # Check for active timers (Phase 2 foundation)
    from app.services.timer_service import TimerService
    from app.ui.components.dialogs import ResumeTimerDialog
    
    timer_service = TimerService()
    
    # Apply global stylesheet
    app.setStyleSheet(GLOBAL_STYLESHEET)
    
    # Check for active timer and prompt BEFORE building UI so TimerPage syncs perfectly
    if timer_service.check_active_timer():
        # We need a hidden root widget for the dialog to center properly, but None is fine too
        dialog = ResumeTimerDialog()
        if dialog.exec():
            # User chose Resume -> state is loaded, do nothing
            pass
        else:
            # User chose Discard
            timer_service.cancel()
    
    # Launch main window
    window = MainWindow(timer_service)
    window.show()
    
    logger.info("StudyTrack started successfully.")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

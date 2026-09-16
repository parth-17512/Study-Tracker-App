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
    timer_service = TimerService()
    if timer_service.check_active_timer():
        logger.info("Found an active abandoned timer in the database!")
    
    # Apply global stylesheet
    app.setStyleSheet(GLOBAL_STYLESHEET)
    
    # Launch main window
    window = MainWindow()
    window.show()
    
    logger.info("StudyTrack started successfully.")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

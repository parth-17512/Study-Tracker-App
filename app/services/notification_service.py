import logging
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QStyle
from PySide6.QtGui import QIcon

logger = logging.getLogger(__name__)

class NotificationService:
    """Manages cross-platform desktop notifications and audio alarms."""
    
    def __init__(self, parent_widget=None):
        self.parent = parent_widget
        
        # We need a system tray icon to show native notifications
        self.tray_icon = QSystemTrayIcon(self.parent)
        
        # Use a default system icon for the tray (Information icon)
        icon = QApplication.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation)
        self.tray_icon.setIcon(icon)
        self.tray_icon.show()
        
        # Config (Hardcoded for now, will be moved to Settings in Phase 11)
        self.sound_enabled = True
        self.notifications_enabled = True

    def notify_session_complete(self):
        """Triggers the alarm and notification sequence."""
        if self.sound_enabled:
            self.play_alarm()
            
        if self.notifications_enabled:
            self.show_notification(
                "Study Session Complete!", 
                "Great job! Your countdown has finished."
            )
            
    def play_alarm(self):
        """Plays the configured alarm sound."""
        try:
            # Fallback to system beep since we don't have a custom .wav yet
            QApplication.beep()
            logger.debug("Played system beep for alarm.")
        except Exception as e:
            logger.error(f"Failed to play alarm: {e}")
            
    def show_notification(self, title: str, message: str):
        """Displays a native OS desktop notification."""
        if self.tray_icon.isSystemTrayAvailable():
            self.tray_icon.showMessage(
                title,
                message,
                QSystemTrayIcon.MessageIcon.Information,
                5000 # Duration in ms
            )
            logger.debug(f"Showed desktop notification: {title}")
        else:
            logger.warning("System tray not available for notifications.")

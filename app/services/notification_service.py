import logging
import platform
import threading
import time

logger = logging.getLogger(__name__)

class NotificationService:
    """Manages cross-platform desktop notifications and audio alarms."""
    
    def __init__(self, parent_widget=None):
        self.parent = parent_widget
        
        # Use ConfigManager
        from app.config.config_manager import ConfigManager
        self.config = ConfigManager()
        
        self.is_windows = platform.system() == 'Windows'
        self._alarm_running = False
        self._alarm_thread = None
        
        if self.is_windows:
            import winsound
            self.winsound = winsound

    def play_alarm(self):
        """Plays a looping alarm sound."""
        if not self.config.get("sound_enabled", True):
            return
            
        try:
            if self.is_windows:
                self._alarm_running = True
                self._alarm_thread = threading.Thread(target=self._beep_loop, daemon=True)
                self._alarm_thread.start()
                logger.debug("Started threading beep alarm.")
            else:
                from PySide6.QtWidgets import QApplication
                QApplication.beep()
        except Exception as e:
            logger.error(f"Failed to play alarm: {e}")
            
    def _beep_loop(self):
        """Internal loop to trigger PC speaker beeps."""
        while self._alarm_running:
            try:
                # 800Hz for 400ms is a standard alarm tone
                self.winsound.Beep(800, 400)
                time.sleep(0.4)
            except Exception:
                break
            
    def stop_alarm(self):
        """Stops the looping alarm sound."""
        self._alarm_running = False
        logger.debug("Stopped system alarm.")

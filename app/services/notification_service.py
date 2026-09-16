import logging
import platform

logger = logging.getLogger(__name__)

class NotificationService:
    """Manages cross-platform desktop notifications and audio alarms."""
    
    def __init__(self, parent_widget=None):
        self.parent = parent_widget
        
        # Config (Hardcoded for now, will be moved to Settings in Phase 11)
        self.sound_enabled = True
        self.notifications_enabled = True
        
        self.is_windows = platform.system() == 'Windows'
        if self.is_windows:
            import winsound
            self.winsound = winsound

    def play_alarm(self):
        """Plays a looping alarm sound."""
        if not self.sound_enabled:
            return
            
        try:
            if self.is_windows:
                # SND_ASYNC = return immediately, SND_LOOP = loop indefinitely, SND_ALIAS = system sound
                self.winsound.PlaySound("SystemExclamation", self.winsound.SND_ALIAS | self.winsound.SND_LOOP | self.winsound.SND_ASYNC)
                logger.debug("Started looping system alarm.")
            else:
                from PySide6.QtWidgets import QApplication
                QApplication.beep()
        except Exception as e:
            logger.error(f"Failed to play alarm: {e}")
            
    def stop_alarm(self):
        """Stops the looping alarm sound."""
        try:
            if self.is_windows:
                # SND_PURGE stops the currently playing waveform
                self.winsound.PlaySound(None, self.winsound.SND_PURGE)
                logger.debug("Stopped system alarm.")
        except Exception as e:
            logger.error(f"Failed to stop alarm: {e}")

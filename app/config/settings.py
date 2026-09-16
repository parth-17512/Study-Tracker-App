import logging
import os
import sys
from pathlib import Path

if getattr(sys, 'frozen', False):
    # Packaged environment
    # Use %LOCALAPPDATA%\StudyTrack
    local_app_data = os.environ.get('LOCALAPPDATA')
    if local_app_data:
        APP_DATA_DIR = Path(local_app_data) / "StudyTrack"
    else:
        APP_DATA_DIR = Path.home() / 'AppData' / 'Local' / "StudyTrack"
    
    BASE_DIR = Path(sys._MEIPASS)
else:
    # Development environment
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    APP_DATA_DIR = BASE_DIR / "user_data"

DATA_DIR = APP_DATA_DIR
LOG_DIR = APP_DATA_DIR / "logs"
EXPORT_DIR = APP_DATA_DIR / "exports"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

# Database path
DATABASE_URL = f"sqlite:///{DATA_DIR / 'studytrack.db'}"

# Logging configuration
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(LOG_DIR / "studytrack.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )

setup_logging()
logger = logging.getLogger(__name__)
logger.info(f"StudyTrack configuration initialized. App Data Dir: {APP_DATA_DIR}")

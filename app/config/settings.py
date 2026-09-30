import logging
import os
import sys
from pathlib import Path

if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).resolve().parent.parent.parent

# V2 Preferred Data Location: %APPDATA%\StudyTrack
app_data = os.environ.get('APPDATA')
if app_data:
    APP_DATA_DIR = Path(app_data) / "StudyTrack"
else:
    APP_DATA_DIR = Path.home() / 'AppData' / 'Roaming' / "StudyTrack"

# Migrate V1 data if V2 data dir doesn't exist but V1 does
import shutil
if not APP_DATA_DIR.exists():
    # Check old packaged location
    local_app_data = os.environ.get('LOCALAPPDATA')
    old_packaged_dir = Path(local_app_data) / "StudyTrack" if local_app_data else None
    
    # Check old dev location
    old_dev_dir = BASE_DIR / "user_data"
    
    if old_packaged_dir and old_packaged_dir.exists() and (old_packaged_dir / "studytrack.db").exists():
        shutil.copytree(old_packaged_dir, APP_DATA_DIR)
    elif old_dev_dir.exists() and (old_dev_dir / "studytrack.db").exists():
        shutil.copytree(old_dev_dir, APP_DATA_DIR)

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

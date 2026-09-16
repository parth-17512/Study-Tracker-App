import logging
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "user_data"
LOG_DIR = BASE_DIR / "logs"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

# Database path
DATABASE_URL = f"sqlite:///{DATA_DIR / 'studytrack.db'}"

# Logging configuration
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(LOG_DIR / "studytrack.log"),
            logging.StreamHandler()
        ]
    )

setup_logging()
logger = logging.getLogger(__name__)
logger.info("StudyTrack configuration initialized.")

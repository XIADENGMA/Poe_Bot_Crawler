import datetime
import json
import os
import shutil
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get cookies from environment variables
P_B = os.getenv("P_B")
P_LAT = os.getenv("P_LAT")

# Ensure cookies are available
if not P_B or not P_LAT:
    raise ValueError("P_B and P_LAT environment variables must be set in .env file")

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"
JSON_DIR = OUTPUT_DIR / "json"
BOTS_DIR = OUTPUT_DIR / "bots"
RESULT_DIR = OUTPUT_DIR / "result"
HISTORY_DIR = RESULT_DIR / "history"

# Ensure all directories exist
for directory in [OUTPUT_DIR, JSON_DIR, BOTS_DIR, RESULT_DIR, HISTORY_DIR]:
    directory.mkdir(exist_ok=True)

# Current date formatted as YYYY-MM-DD
CURRENT_DATE = datetime.datetime.now().strftime("%Y-%m-%d")

# HTTP headers for API requests
HEADERS = {
    "content-type": "application/json",
    "poegraphql": "1",
}

# Cookie string for requests
COOKIES = f"p-b={P_B}; p-lat={P_LAT}"


def get_cookie_dict():
    """
    Convert cookie string to dictionary format for requests library
    """
    return {"p-b": P_B, "p-lat": P_LAT}


def save_json(data, directory, filename):
    """
    Save data as JSON file

    Args:
        data: Data to save
        directory: Directory to save to
        filename: Filename to save as

    Returns:
        Path to saved file
    """
    filepath = directory / filename
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return filepath


def load_json(filepath):
    """
    Load data from JSON file

    Args:
        filepath: Path to JSON file

    Returns:
        Loaded data
    """
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def clean_old_files(directory, days=7):
    """
    Delete files in directory that are older than specified days

    Args:
        directory: Directory to clean
        days: Number of days to keep files for (default 7)
    """
    now = datetime.datetime.now()
    cutoff = now - datetime.timedelta(days=days)

    for file_path in directory.glob("*"):
        if file_path.is_file():
            try:
                # Get file modification time
                mtime = datetime.datetime.fromtimestamp(file_path.stat().st_mtime)

                # Check if file is older than cutoff
                if mtime < cutoff:
                    file_path.unlink()
                    print(f"Deleted old file: {file_path}")
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")


def update_index_html():
    """
    Update index.html with the most recent HTML file from history directory

    Returns:
        Path to the updated index.html file
    """
    import logging
    import shutil

    logger = logging.getLogger(__name__)

    try:
        # Find most recent HTML file in history directory
        html_files = list(HISTORY_DIR.glob("*.html"))

        if not html_files:
            logger.warning("No HTML files found in history directory")
            return None

        # Sort by modification time (newest first)
        most_recent_file = max(html_files, key=lambda f: f.stat().st_mtime)

        # Copy to index.html
        index_path = RESULT_DIR / "index.html"
        shutil.copy2(most_recent_file, index_path)

        logger.info(f"Updated index.html with content from {most_recent_file}")
        return index_path
    except Exception as e:
        logger.error(f"Error updating index.html: {e}")
        return None

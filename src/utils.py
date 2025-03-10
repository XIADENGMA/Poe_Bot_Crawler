import datetime
import json
import os
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

# Ensure all directories exist
for directory in [OUTPUT_DIR, JSON_DIR, BOTS_DIR, RESULT_DIR]:
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

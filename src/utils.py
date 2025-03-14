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
BOT_INFO_DIR = RESULT_DIR / "bot_info"
TIMELINE_DIR = RESULT_DIR / "timeline"

# Ensure all directories exist
for directory in [OUTPUT_DIR, JSON_DIR, BOTS_DIR, RESULT_DIR, BOT_INFO_DIR, TIMELINE_DIR]:
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
    import os
    from pathlib import Path

    # If directory is empty and filename already has a path, use it directly
    if not directory and os.path.dirname(filename):
        filepath = filename
    else:
        # Convert to Path objects for proper path handling
        dir_path = Path(directory)
        file_path = Path(filename)

        # Combine directory and filename
        filepath = dir_path / file_path

    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

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
    Update index.html with the most recent HTML file from bot_info directory

    Returns:
        Path to the updated index.html file
    """
    import logging
    import shutil

    logger = logging.getLogger(__name__)

    try:
        # Find most recent HTML file in bot_info directory
        html_files = list(BOT_INFO_DIR.glob("*.html"))

        if not html_files:
            logger.warning("No HTML files found in bot_info directory")
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

def get_previous_data():
    """
    Find and load the most recent bot data JSON file before today

    Returns:
        Dictionary containing previous bot data, or None if no previous data found
    """
    import logging
    logger = logging.getLogger(__name__)

    try:
        # Find all JSON files with the pattern "official_bots_with_prices_*.json"
        json_files = list(JSON_DIR.glob("official_bots_with_prices_*.json"))

        if not json_files:
            logger.warning("No previous bot data files found")
            return None

        # Filter out today's file
        today_pattern = f"official_bots_with_prices_{CURRENT_DATE}.json"
        previous_files = [f for f in json_files if f.name != today_pattern]

        if not previous_files:
            logger.warning("No previous bot data files found (only today's file exists)")
            return None

        # Sort by modification time (newest first)
        most_recent_file = max(previous_files, key=lambda f: f.stat().st_mtime)

        # Load the data
        previous_data = load_json(most_recent_file)
        logger.info(f"Loaded previous bot data from {most_recent_file}")

        return previous_data
    except Exception as e:
        logger.error(f"Error getting previous data: {e}")
        return None

def compare_bot_data(today_data, previous_data):
    """
    Compare today's bot data with previous data to identify changes

    Args:
        today_data: List or dictionary of bot data from today
        previous_data: List or dictionary of bot data from previous run

    Returns:
        Dictionary containing changes:
        {
            "new_bots": [
                {"id": "bot_id", "name": "Bot Name", "price": 0}
            ],
            "price_changes": [
                {"id": "bot_id", "name": "Bot Name", "old_price": 0, "new_price": 10}
            ]
        }
    """
    import logging
    logger = logging.getLogger(__name__)

    changes = {
        "new_bots": [],
        "price_changes": []
    }

    # Make sure today_data is in the right format (list of dictionaries)
    if isinstance(today_data, dict) and not isinstance(today_data, list):
        logger.info("Converting today_data from dictionary to list")
        today_data_list = []
        for key, bot in today_data.items():
            if isinstance(bot, dict):
                today_data_list.append(bot)
        today_data = today_data_list

    # If no previous data, all bots are considered new
    if not previous_data:
        for bot in today_data:
            if isinstance(bot, dict):
                changes["new_bots"].append({
                    "id": bot.get("botId", ""),
                    "name": bot.get("displayName", ""),
                    "price": bot.get("price", 0)
                })
        logger.info(f"No previous data found, all {len(changes['new_bots'])} bots considered new")
        return changes

    # Create dictionary of previous bots for easy lookup
    previous_bots = {}

    # Handle different data formats
    if isinstance(previous_data, dict) and not isinstance(previous_data, list):
        # If previous_data is a dictionary with numeric keys
        logger.info("Previous data is in dictionary format")

        for key, bot in previous_data.items():
            if isinstance(bot, dict):
                # Extract bot_id, looking for either botId or bot_ID
                bot_id = bot.get("botId", bot.get("bot_ID", ""))

                if not bot_id and "bot_ID" in bot:
                    bot_id = str(bot["bot_ID"])

                if bot_id:
                    # Make sure we're consistent with field names
                    if "displayName" not in bot and "display_name" in bot:
                        bot["displayName"] = bot["display_name"]

                    if "price" not in bot:
                        # Try to extract price from nested structure
                        if "points_price" in bot and "standard_message" in bot["points_price"]:
                            try:
                                bot["price"] = int(bot["points_price"]["standard_message"]["value"])
                            except (ValueError, TypeError):
                                bot["price"] = 0

                    previous_bots[str(bot_id)] = bot

    elif isinstance(previous_data, list):
        # If previous_data is already a list
        logger.info("Previous data is in list format")

        for bot in previous_data:
            if isinstance(bot, dict):
                # Extract bot_id, looking for either botId or bot_ID
                bot_id = bot.get("botId", bot.get("bot_ID", ""))

                if not bot_id and "bot_ID" in bot:
                    bot_id = str(bot["bot_ID"])

                if bot_id:
                    # Make sure we're consistent with field names
                    if "displayName" not in bot and "display_name" in bot:
                        bot["displayName"] = bot["display_name"]

                    if "price" not in bot:
                        # Try to extract price from nested structure
                        if "points_price" in bot and "standard_message" in bot["points_price"]:
                            try:
                                bot["price"] = int(bot["points_price"]["standard_message"]["value"])
                            except (ValueError, TypeError):
                                bot["price"] = 0

                    previous_bots[str(bot_id)] = bot

    else:
        # If we can't process the previous data, all bots are considered new
        logger.warning(f"Unable to process previous data format (type: {type(previous_data)})")
        for bot in today_data:
            if isinstance(bot, dict):
                changes["new_bots"].append({
                    "id": bot.get("botId", ""),
                    "name": bot.get("displayName", ""),
                    "price": bot.get("price", 0)
                })
        logger.info(f"Unable to process previous data format, all {len(changes['new_bots'])} bots considered new")
        return changes

    # Check each bot in today's data
    for bot in today_data:
        # Skip if bot is not a dictionary
        if not isinstance(bot, dict):
            logger.warning(f"Skipping non-dictionary item in today_data: {type(bot)}")
            continue

        bot_id = bot.get("botId", "")

        if not bot_id:
            continue

        # Convert to string for consistent comparison
        bot_id = str(bot_id)

        # If bot not in previous data, it's new
        if bot_id not in previous_bots:
            changes["new_bots"].append({
                "id": bot_id,
                "name": bot.get("displayName", ""),
                "price": bot.get("price", 0)
            })
            continue

        # Check for price changes
        previous_price = previous_bots[bot_id].get("price", 0)
        current_price = bot.get("price", 0)

        if previous_price != current_price:
            changes["price_changes"].append({
                "id": bot_id,
                "name": bot.get("displayName", ""),
                "old_price": previous_price,
                "new_price": current_price
            })

    return changes

def save_timeline_data(changes):
    """
    Save changes to timeline data file

    Args:
        changes: Dictionary containing changes for today

    Returns:
        Path to saved timeline data file
    """
    import logging
    logger = logging.getLogger(__name__)

    timeline_data = {}
    timeline_file = JSON_DIR / "timeline_data.json"

    # Load existing timeline data if available
    if timeline_file.exists():
        try:
            timeline_data = load_json(timeline_file)
        except Exception as e:
            logger.error(f"Error loading existing timeline data: {e}")

    # Add today's changes if there are any
    if changes["new_bots"] or changes["price_changes"]:
        timeline_data[CURRENT_DATE] = changes

        # Save updated timeline data
        save_json(timeline_data, JSON_DIR, "timeline_data.json")
        logger.info(f"Saved timeline data to {timeline_file}")

        # Also save a dated copy for history
        dated_filename = f"timeline_data_{CURRENT_DATE}.json"
        dated_file = save_json(timeline_data, JSON_DIR, dated_filename)
        logger.info(f"Saved dated timeline data to {dated_file}")

        return timeline_file
    else:
        logger.info("No changes detected, timeline data not updated")
        return None

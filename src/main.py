import logging
import os
import sys
from pathlib import Path
from datetime import datetime
import traceback

# Add the src directory to the Python path
script_dir = Path(__file__).resolve().parent
if str(script_dir) not in sys.path:
    sys.path.append(str(script_dir))

from bot_list import get_official_bots
from bot_details import get_bot_details
from utils import (
    save_json, load_json, JSON_DIR, CURRENT_DATE, BASE_DIR,
    BOT_INFO_DIR, RESULT_DIR, TIMELINE_DIR,
    clean_old_files, get_previous_data, compare_bot_data, save_timeline_data
)
from bot_info_generator import generate_html
# Try to import timeline_generator functions, if the module exists
try:
    from timeline_generator import generate_timeline_html, update_timeline_index
    has_timeline_generator = True
except ImportError:
    has_timeline_generator = False
    print("Warning: timeline_generator module not found. Timeline HTML will not be generated.")

# Ensure logs directory exists
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Configure logging - Fix the logging configuration to ensure logs are written
log_file_path = LOGS_DIR / f"poe_crawler_{CURRENT_DATE}.log"

# Remove all existing handlers to avoid duplicates
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Configure the root logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_file_path, mode='w', encoding='utf-8')
    ]
)

# Get the logger for this module
logger = logging.getLogger(__name__)

def main():
    """Main function to run the crawler."""
    logger.info("Starting Poe crawler...")

    try:
        # Fetch the official bot list
        logger.info("Fetching official bot list...")
        bots_data, bots_filepath = get_official_bots()
        logger.info(f"Retrieved {len(bots_data)} bots")

        # Get detailed information for each bot
        updated_bots_data = get_bot_details(bots_data)

        # Save updated bot data to file
        today = datetime.now().date().strftime("%Y-%m-%d")
        output_file = f"official_bots_with_prices_{today}.json"
        updated_filepath = save_json(updated_bots_data, JSON_DIR, output_file)
        logger.info(f"Saved updated bot list to {updated_filepath}")

        # Get previous data
        previous_data = get_previous_data()

        # Debug print to check data types
        logger.info(f"Type of updated_bots_data: {type(updated_bots_data)}")
        if isinstance(updated_bots_data, list) and updated_bots_data:
            logger.info(f"Type of first item in updated_bots_data: {type(updated_bots_data[0])}")
        else:
            logger.info(f"updated_bots_data is not a list or is empty")

        logger.info(f"Type of previous_data: {type(previous_data)}")
        if isinstance(previous_data, dict) and previous_data:
            logger.info(f"Type of first item in previous_data: {type(list(previous_data.values())[0])}")

        # Compare today's data with previous data
        changes = compare_bot_data(updated_bots_data, previous_data)

        # Log the changes found
        logger.info(f"Found {len(changes['new_bots'])} new bots and {len(changes['price_changes'])} price changes")

        # Save timeline data
        timeline_filepath = save_timeline_data(changes)
        logger.info(f"Timeline data filepath: {timeline_filepath}")

        # Load timeline data for HTML generation
        timeline_data = None
        if timeline_filepath:
            try:
                timeline_data = load_json(timeline_filepath)
                logger.info(f"Loaded timeline data with {len(timeline_data)} entries")
            except Exception as e:
                logger.error(f"Error loading timeline data: {e}")

        # Generate HTML using html_generator
        has_updates = (len(changes['new_bots']) > 0 or len(changes['price_changes']) > 0)
        html_path = generate_html(updated_bots_data, has_updates)
        logger.info(f"Generated HTML at {html_path}")

        # Generate timeline HTML if the module is available
        if has_timeline_generator and timeline_data:
            timeline_html_path = generate_timeline_html(timeline_data)
            logger.info(f"Generated timeline HTML at {timeline_html_path}")

            # Update timeline.html with latest timeline content
            timeline_index_path = update_timeline_index()
            logger.info(f"Updated timeline.html at {timeline_index_path}")

        # Clean old files (keeping the last 7 days by default)
        for directory in [JSON_DIR, BOT_INFO_DIR, TIMELINE_DIR]:
            clean_old_files(directory)
            logger.info(f"Cleaned old files in {directory}")

        logger.info("Process completed successfully!")
        print(f"\nTimeline data saved to: {timeline_filepath}")
        print(f"Bot list saved to: {updated_filepath}")
        print(f"HTML generated at: {html_path}")
        if has_timeline_generator and timeline_data:
            print(f"Timeline HTML generated at: {timeline_html_path}")

    except Exception as e:
        logger.error(f"Error in main function: {e}")
        logger.error(traceback.format_exc())
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())

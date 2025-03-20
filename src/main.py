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
    from timeline_generator import generate_timeline_html, update_timeline_index, generate_timeline_data
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

        # Generate HTML using html_generator
        html_path = generate_html(updated_bots_data)
        logger.info(f"Generated HTML at {html_path}")

        # Generate timeline HTML if the module is available
        if has_timeline_generator:
            # Generate timeline data and HTML directly with our new function
            logger.info("Generating timeline data and HTML...")
            timeline_data = generate_timeline_data()
            # Always generate timeline HTML, even if there are no changes
            timeline_html_path = generate_timeline_html(timeline_data)
            if timeline_html_path:
                logger.info(f"Generated timeline HTML at {timeline_html_path}")

                # Always update timeline.html with latest timeline content
                timeline_index_path = update_timeline_index()
                logger.info(f"Updated timeline.html at {timeline_index_path}")
            else:
                # If no timeline_html_path was returned, force creation of a new one
                logger.info("No timeline data generated, creating empty timeline...")
                empty_timeline_data = {CURRENT_DATE: {"new_bots": [], "price_changes": []}}
                timeline_html_path = generate_timeline_html(empty_timeline_data)
                timeline_index_path = update_timeline_index()
                logger.info(f"Generated empty timeline HTML at {timeline_html_path}")

        # Clean old files (keeping the last 7 days by default)
        for directory in [JSON_DIR, BOT_INFO_DIR, TIMELINE_DIR]:
            clean_old_files(directory)
            logger.info(f"Cleaned old files in {directory}")

        # Clean old files in output/bots directory
        BOTS_DIR = BASE_DIR / "output" / "bots"
        if BOTS_DIR.exists():
            clean_old_files(BOTS_DIR)
            logger.info(f"Cleaned old files in {BOTS_DIR}")

        logger.info("Process completed successfully!")
        print(f"\nBot list saved to: {updated_filepath}")
        print(f"HTML generated at: {html_path}")
        if has_timeline_generator and 'timeline_html_path' in locals() and timeline_html_path:
            print(f"Timeline HTML generated at: {timeline_html_path}")

    except Exception as e:
        logger.error(f"Error in main function: {e}")
        logger.error(traceback.format_exc())
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())

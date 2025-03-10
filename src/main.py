import logging
import os
import sys
from pathlib import Path

# Add the src directory to the Python path
script_dir = Path(__file__).resolve().parent
if str(script_dir) not in sys.path:
    sys.path.append(str(script_dir))

from bot_list import get_official_bots
from bot_details import get_bot_details, save_bot_details
from html_generator import generate_html
from utils import save_json, JSON_DIR, CURRENT_DATE, BASE_DIR

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
    """
    Main entry point for the application
    """
    try:
        logger.info("Starting Poe crawler...")

        # Step 1: Get official bot list
        bots_data, bots_filepath = get_official_bots()
        logger.info(f"Retrieved {len(bots_data)} bots")

        # Step 2: Get bot details
        updated_bots_data = get_bot_details(bots_data)

        # Step 3: Save updated bot list
        updated_filename = f"official_bots_with_prices_{CURRENT_DATE}.json"
        updated_filepath = save_json(updated_bots_data, JSON_DIR, updated_filename)
        logger.info(f"Saved updated bot list to {updated_filepath}")

        # Step 4: Generate HTML display
        html_filepath = generate_html(updated_bots_data)
        logger.info(f"Generated HTML display at {html_filepath}")

        logger.info("Poe crawler completed successfully")
        print(f"\nResults saved to:")
        print(f"- Bot list: {updated_filepath}")
        print(f"- HTML display: {html_filepath}")
        print(f"- Log file: {log_file_path}")

        return 0
    except Exception as e:
        logger.error(f"Error in main function: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())

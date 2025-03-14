#!/usr/bin/env python3
"""
Maintenance utilities for Poe Crawler
- Update index.html with most recent HTML file
- Clean up old files

Usage:
    python maintenance.py --update-index
    python maintenance.py --clean-old-files [--days 7]
    python maintenance.py --all
"""

import argparse
import logging
import os
import sys
from pathlib import Path

# Add the src directory to the Python path
script_dir = Path(__file__).resolve().parent
if str(script_dir) not in sys.path:
    sys.path.append(str(script_dir))

# Import maintenance-specific utilities without requiring Poe cookies
# Define paths manually instead of importing them from utils
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"
JSON_DIR = OUTPUT_DIR / "json"
RESULT_DIR = OUTPUT_DIR / "result"
HISTORY_DIR = RESULT_DIR / "history"
LOGS_DIR = BASE_DIR / "logs"

# Ensure all directories exist
for directory in [OUTPUT_DIR, JSON_DIR, RESULT_DIR, HISTORY_DIR, LOGS_DIR]:
    directory.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOGS_DIR / "maintenance.log", mode='a', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

# Import clean_old_files function from utils
def clean_old_files(directory, days=7):
    """
    Delete files in directory that are older than specified days

    Args:
        directory: Directory to clean
        days: Number of days to keep files for (default 7)
    """
    import datetime

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
                    logger.info(f"Deleted old file: {file_path}")
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {e}")

def update_index_html():
    """
    Update index.html with the most recent HTML file from history directory

    Returns:
        Path to the updated index.html file
    """
    import shutil

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

def main():
    parser = argparse.ArgumentParser(description="Poe Crawler maintenance utilities")

    parser.add_argument("--update-index", action="store_true",
                        help="Update index.html with most recent HTML file")
    parser.add_argument("--clean-old-files", action="store_true",
                        help="Clean up old files")
    parser.add_argument("--days", type=int, default=7,
                        help="Number of days to keep files (default: 7)")
    parser.add_argument("--all", action="store_true",
                        help="Run all maintenance tasks")

    args = parser.parse_args()

    # Default to --all if no arguments provided
    if not (args.update_index or args.clean_old_files or args.all):
        args.all = True

    # Update index.html
    if args.update_index or args.all:
        logger.info("Updating index.html...")
        index_path = update_index_html()
        if index_path:
            logger.info(f"index.html updated successfully: {index_path}")
        else:
            logger.warning("Failed to update index.html")

    # Clean old files
    if args.clean_old_files or args.all:
        logger.info(f"Cleaning old files (older than {args.days} days)...")
        clean_old_files(HISTORY_DIR, days=args.days)
        clean_old_files(JSON_DIR, days=args.days)
        clean_old_files(LOGS_DIR, days=args.days)
        logger.info("Cleanup complete")

    return 0

if __name__ == "__main__":
    sys.exit(main())

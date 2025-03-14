#!/usr/bin/env python3
"""
Test script for bot_info_generator.py
"""
import sys
from pathlib import Path

# Add the src directory to the Python path
script_dir = Path(__file__).resolve().parent
if str(script_dir) not in sys.path:
    sys.path.append(str(script_dir))

from bot_info_generator import generate_html, BOT_INFO_DIR

# Simple test data
test_data = {
    "bot1": {
        "display_name": "Test Bot 1",
        "handle": "testbot1",
        "description": "This is a test bot",
        "picture_url": "https://example.com/image.jpg",
        "points_price": {
            "pricing_type": "flat",
            "standard_message": {"value": 10}
        },
        "creator": {"full_name": "Test Creator"}
    }
}

def main():
    print(f"Current BOT_INFO_DIR: {BOT_INFO_DIR}")
    try:
        result_path = generate_html(test_data)
        print(f"HTML generated successfully and saved to {result_path}")
        print(f"BOT_INFO_DIR after generation: {BOT_INFO_DIR}")
        # Check if the files were created
        files = list(BOT_INFO_DIR.glob("*"))
        print(f"Files in BOT_INFO_DIR: {files}")
    except Exception as e:
        print(f"Error generating HTML: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

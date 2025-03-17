import logging
import requests
import time
from tqdm import tqdm

from utils import CURRENT_DATE, HEADERS, JSON_DIR, get_cookie_dict, save_json

# Configure logging - use the logger from the main module
logger = logging.getLogger("src.bot_list")

# API endpoint
POE_API_URL = "https://poe.com/api/gql_POST"


def fetch_official_bots(max_retries=5, retry_delay=1):
    """
    Fetch the official bot list from Poe API

    Args:
        max_retries: Maximum number of retries on failure
        retry_delay: Delay between retries in seconds

    Returns:
        Dict containing the official bot list
    """
    logger.info("Fetching official bot list...")

    # Request payload
    payload = {
        "queryName": "ExploreBotsListPaginationQuery",
        "variables": {
            "categoryName": "defaultCategory",
            "count": 25535,  # Set to a large number to get all bots
            "cursor": None,
        },
        "extensions": {"hash": "b24b2f2f6da147b3345eec1a433ed17b6e1332df97dea47622868f41078a40cc"},
    }

    for attempt in range(max_retries):
        try:
            response = requests.post(
                POE_API_URL, headers=HEADERS, cookies=get_cookie_dict(), json=payload
            )
            response.raise_for_status()
            data = response.json()
            logger.info("Successfully fetched official bot list")
            return data
        except requests.exceptions.RequestException as e:
            logger.warning(f"Attempt {attempt+1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} second(s)...")
                time.sleep(retry_delay)
            else:
                logger.error(f"Error fetching official bot list after {max_retries} attempts: {e}")
                raise


def process_bots_data(data):
    """
    Process the raw API response and extract relevant bot information

    Args:
        data: Raw API response

    Returns:
        Dict containing processed bot information
    """
    processed_data = {}

    try:
        edges = data.get("data", {}).get("exploreBotsConnection", {}).get("edges", [])

        # Set up progress bar
        with tqdm(total=len(edges), desc="Processing bots data") as pbar:
            for index, edge in enumerate(edges):
                node = edge.get("node", {})

                # Extract basic bot information
                bot_id = node.get("botId")
                display_name = node.get("displayName", "")
                handle = node.get("handle", "")
                description = node.get("description", "")
                picture_url = node.get("picture", {}).get("url", "")

                processed_data[str(index)] = {
                    "display_name": display_name,
                    "description": description,
                    "bot_ID": bot_id,
                    "handle": handle,
                    "picture_url": picture_url,
                    # Creator and points_price will be populated later
                    "creator": {},
                    "points_price": {},
                }

                # Update progress bar
                pbar.update(1)

        logger.info(f"Processed {len(processed_data)} bots")
        return processed_data
    except Exception as e:
        logger.error(f"Error processing bot data: {e}")
        raise


def save_official_bots(processed_data):
    """
    Save the processed official bot list to a JSON file

    Args:
        processed_data: Processed bot information

    Returns:
        Path to the saved file
    """
    filename = f"official_bots_list_{CURRENT_DATE}.json"
    filepath = save_json(processed_data, JSON_DIR, filename)
    logger.info(f"Saved official bot list to {filepath}")
    return filepath


def get_official_bots():
    """
    Main function to fetch, process, and save the official bot list

    Returns:
        Tuple of (processed_data, filepath)
    """
    raw_data = fetch_official_bots()
    processed_data = process_bots_data(raw_data)
    filepath = save_official_bots(processed_data)
    return processed_data, filepath

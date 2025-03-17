import logging
import re
import json
import time

import markdown
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from utils import BOTS_DIR, CURRENT_DATE, HEADERS, get_cookie_dict, load_json, save_json

# Configure logging - use the logger from the main module
logger = logging.getLogger("src.bot_details")

# API endpoint
POE_API_URL = "https://poe.com/api/gql_POST"


def fetch_bot_details(bot_id, max_retries=5, retry_delay=1):
    """
    Fetch details for a specific bot by ID

    Args:
        bot_id: ID of the bot
        max_retries: Maximum number of retries on failure
        retry_delay: Delay between retries in seconds

    Returns:
        Dict containing the bot details
    """
    logger.info(f"Fetching details for bot ID: {bot_id}")

    # Request payload
    payload = {
        "queryName": "MessagePointsOverviewModalQuery",
        "variables": {"botId": int(bot_id)},
        "extensions": {"hash": "6fd0395447f45865f1ef2bb029eb99aafb1a865d91d8634d1c7103cd7bc08009"},
    }

    for attempt in range(max_retries):
        try:
            response = requests.post(
                POE_API_URL, headers=HEADERS, cookies=get_cookie_dict(), json=payload
            )
            response.raise_for_status()
            data = response.json()
            logger.info(f"Successfully fetched details for bot ID: {bot_id}")
            return data
        except requests.exceptions.RequestException as e:
            logger.warning(f"Attempt {attempt+1}/{max_retries} failed for bot ID {bot_id}: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} second(s)...")
                time.sleep(retry_delay)
            else:
                logger.error(f"Error fetching bot details for ID {bot_id} after {max_retries} attempts: {e}")
                raise


def save_bot_details(bot_id, data):
    """
    Save raw bot details to a JSON file

    Args:
        bot_id: ID of the bot
        data: Raw bot details data

    Returns:
        Path to the saved file
    """
    filename = f"bot_{bot_id}_{CURRENT_DATE}.json"
    filepath = save_json(data, BOTS_DIR, filename)
    logger.info(f"Saved details for bot ID {bot_id} to {filepath}")
    return filepath


def extract_price_from_text(text, pattern):
    """
    Extracts price values from text based on regex pattern

    Args:
        text: The text to search in
        pattern: Regex pattern to match

    Returns:
        Match object if found, None otherwise
    """
    return re.search(pattern, text)


def parse_rate_menu_markdown(markdown_text, pricing_type=None, standard_price=None):
    """
    Parse the rate menu markdown text to extract pricing information

    Args:
        markdown_text: Rate menu markdown text
        pricing_type: Pricing type from the bot details
        standard_price: Standard price from the bot details

    Returns:
        Dict containing pricing information
    """
    if not markdown_text:
        return {}

    result = {}

    # Check for character-based pricing first
    character_match = re.search(r"\|\s*(?:text\s+)?input\s*\|\s*(\d+)\s*points?\s*\/\s*(?:(\d+)k\s*)?(characters?)\s*\|",
                               markdown_text, re.IGNORECASE)
    if character_match:
        multiplier = character_match.group(2) or "1"  # If group 2 exists (like "1k"), use it, otherwise use "1"
        per_value = multiplier + "k" if character_match.group(2) else "1"
        result["text_input"] = {
            "value": character_match.group(1),
            "unit": "points",
            "per": {
                "value": per_value,
                "unit": "characters"
            }
        }
        # Add standard_message for template compatibility
        result["standard_message"] = {
            "value": character_match.group(1),
            "unit": "points",
            "per": (multiplier + "k " if character_match.group(2) else "") + "characters"
        }
        return result

    # For single character pricing
    single_char_match = re.search(r"\|\s*(?:text\s+)?input\s*\(?.*?\)?\s*\|\s*(\d+)\s*points?\s*\/\s*character\s*\|",
                                 markdown_text, re.IGNORECASE)
    if single_char_match:
        result["text_input"] = {
            "value": single_char_match.group(1),
            "unit": "points",
            "per": {
                "value": "1",
                "unit": "characters"
            }
        }
        # Add standard_message for template compatibility
        result["standard_message"] = {
            "value": single_char_match.group(1),
            "unit": "points",
            "per": "character"
        }
        return result

    # Determine if this is a mixed pricing (subscriber/non-subscriber)
    has_subscriber_section = "subscriber" in markdown_text.lower() or "subscribers" in markdown_text.lower()
    has_non_subscriber_section = "non-subscriber" in markdown_text.lower() or "non-subscribers" in markdown_text.lower()

    if has_subscriber_section and has_non_subscriber_section:
        result["pricing_type"] = "mixed"
        result["non_subscriber"] = {}
        result["subscriber"] = {}

        # Extract non-subscriber section
        non_sub_section = ""
        if "non-subscriber" in markdown_text.lower():
            non_sub_match = re.search(r"\*\*non-subscribers?\*\*(.*?)(?=\*\*subscribers?\*\*|\Z)",
                                      markdown_text, re.DOTALL | re.IGNORECASE)
            if non_sub_match:
                non_sub_section = non_sub_match.group(1)

        # Extract subscriber section
        sub_section = ""
        if "subscriber" in markdown_text.lower():
            sub_match = re.search(r"\*\*subscribers?\*\*(.*?)(?=\Z)", markdown_text, re.DOTALL | re.IGNORECASE)
            if sub_match:
                sub_section = sub_match.group(1)

        # Parse non-subscriber section
        if non_sub_section:
            # Extract text output
            text_output_match = re.search(r"\|\s*text output\s*\|\s*(\d+)\s*points\/message\s*\|",
                                         non_sub_section, re.IGNORECASE)
            if text_output_match:
                result["non_subscriber"]["text_output"] = {
                    "value": text_output_match.group(1),
                    "unit": "points",
                    "per": "message"
                }

            # Extract image output
            image_output_match = re.search(r"\|\s*image output\s*\|\s*(\d+)\s*points\/message\s*\|",
                                          non_sub_section, re.IGNORECASE)
            if image_output_match:
                result["non_subscriber"]["image_output"] = {
                    "value": image_output_match.group(1),
                    "unit": "points",
                    "per": "message"
                }

            # Extract input rates if present
            input_match = re.search(r"\|\s*input\s*\|\s*(?:up to\s*)?(\d+)\s*points\/(\d+)k\s*(tokens|characters)\s*\|",
                                   non_sub_section, re.IGNORECASE)
            if input_match:
                is_max = "up to" in input_match.group(0).lower()
                result["non_subscriber"]["input"] = {
                    "value": input_match.group(1),
                    "unit": "points",
                    "per": {
                        "value": input_match.group(2) + "k",
                        "unit": input_match.group(3).lower()  # Use the actual unit from the text
                    },
                    "is_max": is_max
                }

        # Parse subscriber section
        if sub_section:
            # Extract text output
            text_output_match = re.search(r"\|\s*text output\s*\|\s*(\d+)\s*points\/message\s*\|",
                                         sub_section, re.IGNORECASE)
            if text_output_match:
                result["subscriber"]["text_output"] = {
                    "value": text_output_match.group(1),
                    "unit": "points",
                    "per": "message"
                }

            # Extract image output
            image_output_match = re.search(r"\|\s*image output\s*\|\s*(\d+)\s*points\/message\s*\|",
                                          sub_section, re.IGNORECASE)
            if image_output_match:
                result["subscriber"]["image_output"] = {
                    "value": image_output_match.group(1),
                    "unit": "points",
                    "per": "message"
                }

            # Extract input rates if present
            input_match = re.search(r"\|\s*input\s*\|\s*(?:up to\s*)?(\d+)\s*points\/(\d+)k\s*(tokens|characters)\s*\|",
                                   sub_section, re.IGNORECASE)
            if input_match:
                is_max = "up to" in input_match.group(0).lower()
                result["subscriber"]["input"] = {
                    "value": input_match.group(1),
                    "unit": "points",
                    "per": {
                        "value": input_match.group(2) + "k",
                        "unit": input_match.group(3).lower()  # Use the actual unit from the text
                    },
                    "is_max": is_max
                }

        # Add standard_message field for template compatibility
        # Use text_output from non_subscriber as the standard message value
        if result.get("non_subscriber", {}).get("text_output"):
            result["standard_message"] = {
                "value": result["non_subscriber"]["text_output"]["value"],
                "unit": "points",
                "per": "message"
            }

        return result

    # For other pricing types (flat or variable)
    if pricing_type == "flat":
        result["pricing_type"] = "flat"

        # Extract the flat rate (total cost)
        total_cost_match = re.search(r"\|\s*total cost\s*\|\s*(\d+)\s*points\/message\s*\|",
                                   markdown_text, re.IGNORECASE)
        if total_cost_match:
            result["standard_message"] = {
                "value": total_cost_match.group(1),
                "unit": "points",
                "per": "message"
            }
        elif standard_price:
            result["standard_message"] = {
                "value": str(standard_price),
                "unit": "points",
                "per": "message"
            }

        return result

    # For undefined pricing with only text input (like Cartesia)
    text_input_pattern = re.search(r"\|\s*text input\s*\|\s*(\d+)\s*points\s*\/\s*(\d+)k\s*(tokens|characters)\s*\|",
                                 markdown_text, re.IGNORECASE)

    if pricing_type == "undefined" and text_input_pattern:
        result["pricing_type"] = "text_input_only"

        # Determine if the unit is tokens or characters
        unit = "tokens"
        if text_input_pattern.group(3) and "characters" in text_input_pattern.group(3).lower():
            unit = "characters"

        result["text_input"] = {
            "value": text_input_pattern.group(1),
            "unit": "points",
            "per": {
                "value": text_input_pattern.group(2) + "k",
                "unit": unit
            }
        }

        # Add standard_message for template compatibility
        result["standard_message"] = {
            "value": text_input_pattern.group(1),
            "unit": "points",
            "per": "message"
        }

    # For variable pricing
    result["pricing_type"] = pricing_type or "variable"

    # Extract standard message price
    if standard_price:
        result["standard_message"] = {
            "value": str(standard_price),
            "unit": "points",
            "per": "message"
        }

    # Extract text input price
    text_input_match = re.search(r"\|\s*input\s*\(text\)\s*\|\s*(\d+)\s*points\/(\d+)k\s*(tokens|characters)\s*\|",
                               markdown_text, re.IGNORECASE)
    if not text_input_match:
        text_input_match = re.search(r"\|\s*text input\s*\|\s*(\d+)\s*points\/(\d+)k\s*(tokens|characters)\s*\|",
                                   markdown_text, re.IGNORECASE)
    if not text_input_match:
        text_input_match = re.search(r"\|\s*input\s*\|\s*(\d+)\s*points\/(\d+)k\s*(tokens|characters)\s*\|",
                                   markdown_text, re.IGNORECASE)

    if text_input_match:
        unit = text_input_match.group(3).lower()  # Use the actual unit from the text
        result["text_input"] = {
            "value": text_input_match.group(1),
            "unit": "points",
            "per": {
                "value": text_input_match.group(2) + "k",
                "unit": unit
            }
        }

    # Extract image input price
    image_input_match = re.search(r"\|\s*input\s*\(image\)\s*\|\s*(\d+)\s*points\/(\d+)k\s*tokens\s*\|",
                                markdown_text, re.IGNORECASE)
    if not image_input_match:
        image_input_match = re.search(r"\|\s*image input\s*\|\s*(\d+)\s*points\/(\d+)k\s*tokens\s*\|",
                                   markdown_text, re.IGNORECASE)

    if image_input_match:
        result["image_input"] = {
            "value": image_input_match.group(1),
            "unit": "points",
            "per": {
                "value": image_input_match.group(2) + "k",
                "unit": "tokens"
            }
        }

    # Extract cached input price
    cached_input_match = re.search(r"\|\s*chat history(?:\s*cache)?\s*\|\s*input rates are applied\s*\|",
                                 markdown_text, re.IGNORECASE)
    chat_history_discount_match = re.search(r"\|\s*chat history(?:\s*cache)?\s*discount\s*\|\s*(\d+)%\s*discount",
                                          markdown_text, re.IGNORECASE)

    if cached_input_match and chat_history_discount_match and result.get("text_input"):
        discount = int(chat_history_discount_match.group(1))
        discount_factor = discount / 100
        original_value = int(result["text_input"]["value"])
        discounted_value = str(int(original_value * discount_factor + 0.5))

        result["cached_input"] = {
            "value": discounted_value,
            "unit": "points",
            "per": {
                "value": result["text_input"]["per"]["value"],
                "unit": result["text_input"]["per"]["unit"]
            }
        }

    # Extract bot message/output price
    bot_message_match = re.search(r"\|\s*bot message\s*\|\s*(\d+)\s*points\/message\s*\|",
                                markdown_text, re.IGNORECASE)
    if not bot_message_match:
        bot_message_match = re.search(r"\|\s*output\s*\|\s*(\d+)\s*points\/message\s*\|",
                                    markdown_text, re.IGNORECASE)

    if bot_message_match:
        result["output"] = {
            "value": bot_message_match.group(1),
            "unit": "points",
            "per": "message"
        }

    # For variable pricing, if we don't have standard_message but have output, use that
    if not result.get("standard_message") and result.get("output"):
        result["standard_message"] = result["output"].copy()

    # If we have chat history discount but not as a percentage
    chat_history_discount_percent = None
    if chat_history_discount_match:
        chat_history_discount_percent = int(chat_history_discount_match.group(1))

    if chat_history_discount_percent:
        result["chat_history_discount"] = chat_history_discount_percent

    return result


def extract_bot_pricing(bot_details):
    """
    Extract bot pricing information from bot details

    Args:
        bot_details: Bot details data

    Returns:
        Dict containing pricing information
    """
    try:
        bot_pricing = bot_details.get("data", {}).get("botById", {}).get("botPricing", {})
        bot_id = bot_details.get("data", {}).get("botById", {}).get("botId")
        bot_name = bot_details.get("data", {}).get("botById", {}).get("displayName", "")

        if not bot_pricing:
            logger.warning("No bot pricing information found")
            return {}

        rate_menu_markdown = bot_pricing.get("rateMenuMarkdown", "")
        pricing_type = bot_pricing.get("botPricingType", "")
        standard_price = bot_pricing.get("standardMessagePrice")

        # Special handling for known character-based bots
        if bot_name == "ElevenLabs":
            # ElevenLabs charges per character
            character_match = re.search(r"Input \(text\) \| (\d+) point(?:s)? \/ character", rate_menu_markdown, re.IGNORECASE)
            if character_match:
                points_per_char = character_match.group(1)
                return {
                    "pricing_type": "per_character",
                    "standard_message": {
                        "value": points_per_char,
                        "unit": "points",
                        "per": "character"
                    },
                    "text_input": {
                        "value": points_per_char,
                        "unit": "points",
                        "per": {
                            "value": "1",
                            "unit": "characters"
                        }
                    }
                }

        if bot_name == "Cartesia":
            # Cartesia charges per 1k characters
            character_match = re.search(r"Text input \| (\d+) points \/ 1k characters", rate_menu_markdown, re.IGNORECASE)
            if character_match:
                points_per_1k_chars = character_match.group(1)
                return {
                    "pricing_type": "per_character",
                    "standard_message": {
                        "value": points_per_1k_chars,
                        "unit": "points",
                        "per": "1k characters"
                    },
                    "text_input": {
                        "value": points_per_1k_chars,
                        "unit": "points",
                        "per": {
                            "value": "1k",
                            "unit": "characters"
                        }
                    }
                }

        # If pricing_type is undefined but contains subscriber/non-subscriber sections, treat it as mixed
        if pricing_type == "undefined" and rate_menu_markdown and (
            "subscriber" in rate_menu_markdown.lower() or
            "non-subscriber" in rate_menu_markdown.lower()):
            pricing_type = "mixed"

        # Parse the rate menu markdown to extract pricing information
        pricing_info = parse_rate_menu_markdown(rate_menu_markdown, pricing_type, standard_price)

        # Ensure every pricing structure has a standard_message field
        if "standard_message" not in pricing_info:
            # For flat pricing, use standard_price or message price
            if pricing_type == "flat" and standard_price:
                pricing_info["standard_message"] = {
                    "value": str(standard_price),
                    "unit": "points",
                    "per": "message"
                }
            # For variable pricing, try to use output or standard_price
            elif pricing_type == "variable":
                if "output" in pricing_info:
                    pricing_info["standard_message"] = pricing_info["output"].copy()
                elif standard_price:
                    pricing_info["standard_message"] = {
                        "value": str(standard_price),
                        "unit": "points",
                        "per": "message"
                    }
            # For mixed pricing, try to use non_subscriber text_output
            elif pricing_type == "mixed" and "non_subscriber" in pricing_info:
                if "text_output" in pricing_info["non_subscriber"]:
                    pricing_info["standard_message"] = {
                        "value": pricing_info["non_subscriber"]["text_output"]["value"],
                        "unit": "points",
                        "per": "message"
                    }
            # For undefined or any other type, use a default placeholder
            if "standard_message" not in pricing_info:
                # Try to find any price info we can use as a placeholder
                if "text_input" in pricing_info:
                    pricing_info["standard_message"] = {
                        "value": pricing_info["text_input"]["value"],
                        "unit": "points",
                        "per": "message"
                    }
                else:
                    # Last resort: provide a placeholder value
                    pricing_info["standard_message"] = {
                        "value": "N/A",
                        "unit": "points",
                        "per": "message"
                    }

        return pricing_info
    except Exception as e:
        logger.error(f"Error extracting bot pricing: {e}")
        return {"standard_message": {"value": "N/A", "unit": "points", "per": "message"}}


def extract_creator_info(bot_details):
    """
    Extract creator information from bot details

    Args:
        bot_details: Raw bot details data

    Returns:
        Dict containing creator information
    """
    try:
        logger.debug(f"Bot details structure: {json.dumps(bot_details, indent=2)}")
        creator = bot_details.get("data", {}).get("botById", {}).get("creator", {})
        logger.debug(f"Creator data: {json.dumps(creator, indent=2)}")
        result = {
            "full_name": creator.get("fullName", ""),
            "profile_photo_url": creator.get("profilePhotoUrl", "")
        }
        logger.debug(f"Extracted creator info: {json.dumps(result, indent=2)}")
        return result
    except Exception as e:
        logger.error(f"Error extracting creator info: {e}")
        return {}


def update_bot_with_details(bots_data, bot_index, bot_details):
    """
    Update a bot in the bots data with details information

    Args:
        bots_data: Dict containing all bots data
        bot_index: Index of the bot to update
        bot_details: Details data for the bot

    Returns:
        Updated bots data
    """
    try:
        # Extract pricing and creator information
        pricing_info = extract_bot_pricing(bot_details)
        creator_info = extract_creator_info(bot_details)

        logger.debug(f"Bot ID: {bots_data[bot_index].get('bot_ID')}")
        logger.debug(f"Original creator info: {json.dumps(bots_data[bot_index].get('creator', {}), indent=2)}")
        logger.debug(f"New creator info: {json.dumps(creator_info, indent=2)}")

        # Update bot data
        bots_data[bot_index]["points_price"] = pricing_info
        bots_data[bot_index]["creator"] = creator_info

        logger.debug(f"Final creator info: {json.dumps(bots_data[bot_index].get('creator', {}), indent=2)}")

        return bots_data
    except Exception as e:
        logger.error(f"Error updating bot with details: {e}")
        return bots_data


def get_bot_details(bots_data):
    """
    Get details for all bots in the list

    Args:
        bots_data: Dict containing all bots data

    Returns:
        Updated bots data with details
    """
    logger.info(f"Retrieved {len(bots_data)} bots")

    updated_bots_data = bots_data.copy()
    total_bots = len(updated_bots_data)
    processed_count = 0

    # Manually set pricing for Assistant bot (ID 3002)
    for index, bot in updated_bots_data.items():
        bot_id = bot.get("bot_ID")
        if bot_id == 3002:
            # Create a fake bot details object for Assistant
            bot_details = {
                "data": {
                    "botById": {
                        "botPricing": {
                            "rateMenuMarkdown": "**Non-Subscribers**\n\n| Service | Rate |\n|---------|------|\n| Text Output | 15 points/message |\n| Image Output | 62 points/message |\n\n**Subscribers**\n\n| Service | Rate |\n|---------|------|\n| Input | 90 points/1k tokens (max) |\n| Text Output | 267 points/message |\n| Image Output | 1334 points/message |",
                            "botPricingType": "mixed",
                            "standardMessagePrice": None,
                            "creator": {
                                "isDeleted": False,
                                "profilePhotoUrl": "https://qph.cf2.poecdn.net/main-thumb-2187163946-50-eexyawnwrihdoupubqqzwkbjvasbkqhd.jpeg",
                                "fullName": "Poe",
                                "nullableHandle": "poe",
                                "__isNode": "PoeUser",
                                "id": "UG9lVXNlcjoyMTg3MTYzOTQ2"
                            }
                        }
                    }
                }
            }
            updated_bots_data = update_bot_with_details(updated_bots_data, index, bot_details)

            # 确保creator信息正确设置
            updated_bots_data[index]["creator"] = {
                "full_name": "Poe",
                "profile_photo_url": "https://qph.cf2.poecdn.net/main-thumb-2187163946-50-eexyawnwrihdoupubqqzwkbjvasbkqhd.jpeg"
            }

            logger.info(f"Manually set pricing information for Assistant bot (ID 3002)")
            logger.info(f"Successfully processed details for bot ID 3002 (1/{total_bots})")
            processed_count += 1
            break

    # Process all other bots
    for index, bot in updated_bots_data.items():
        bot_id = bot.get("bot_ID")
        if not bot_id or bot_id == 3002:
            continue

        processed_count += 1
        logger.info(f"Fetching details for bot ID: {bot_id} ({processed_count}/{total_bots})")

        try:
            # First, check if we have cached details
            cache_path = BOTS_DIR / f"bot_{bot_id}_{CURRENT_DATE}.json"
            if cache_path.exists():
                with open(cache_path, "r", encoding="utf-8") as f:
                    bot_details = json.load(f)
            else:
                # Fetch details from Poe API
                bot_details = fetch_bot_details(bot_id)

                # Save details to cache file
                save_bot_details(bot_id, bot_details)

            # Update bot with details
            updated_bots_data = update_bot_with_details(updated_bots_data, index, bot_details)

            logger.info(f"Successfully processed details for bot ID {bot_id} ({processed_count}/{total_bots})")
        except Exception as e:
            logger.error(f"Error processing details for bot ID {bot_id}: {e}")

    return updated_bots_data

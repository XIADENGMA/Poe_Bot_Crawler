import logging
from pathlib import Path
import shutil
import json
from datetime import datetime

from jinja2 import Template

from utils import CURRENT_DATE, RESULT_DIR, load_json

# Configure logging - use the logger from the main module
logger = logging.getLogger("src.timeline_generator")

# Directory for timeline HTML files
TIMELINE_DIR = RESULT_DIR / "timeline"
TIMELINE_DIR.mkdir(exist_ok=True)

# HTML template for the timeline page
TIMELINE_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Poe 机器人更新时间线 - {{ date }}</title>
    <link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
    <style>
        :root {
            /* Light mode (default) */
            --primary-color: #4361ee;
            --secondary-color: #3f37c9;
            --accent-color: #4895ef;
            --text-color: #333;
            --light-text: #6c757d;
            --bg-color: #f8f9fa;
            --card-bg: #fff;
            --card-hover-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
            --card-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
            --header-bg: linear-gradient(135deg, #4361ee 0%, #3a0ca3 100%);
            --border-color: #e9ecef;
            --info-bg: #e7f5ff;
            --timeline-line: #4361ee;
            --timeline-dot: #4361ee;
            --timeline-dot-border: #fff;
            --timeline-card-bg: #fff;
            --timeline-date: #4361ee;
            --toggle-bg: #f1f1f1;
            --toggle-dot: #4361ee;
            --toggle-icon: #333;
            --button-hover: #edf2ff;
            --separator-color: #e9ecef;
            --new-bot-bg: #e7f5ff;
            --price-change-bg: #fff3cd;
            --price-increase: #dc3545;
            --price-decrease: #28a745;
        }

        /* Dark mode color scheme */
        [data-theme="dark"] {
            --primary-color: #4cc9f0;
            --secondary-color: #4895ef;
            --accent-color: #4361ee;
            --text-color: #e9ecef;
            --light-text: #adb5bd;
            --bg-color: #121212;
            --card-bg: #1e1e1e;
            --card-hover-shadow: 0 15px 30px rgba(0, 0, 0, 0.3);
            --card-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
            --header-bg: linear-gradient(135deg, #4cc9f0 0%, #3a0ca3 100%);
            --border-color: #2d3748;
            --info-bg: #1a365d;
            --timeline-line: #4cc9f0;
            --timeline-dot: #4cc9f0;
            --timeline-dot-border: #121212;
            --timeline-card-bg: #1e1e1e;
            --timeline-date: #4cc9f0;
            --toggle-bg: #2d3748;
            --toggle-dot: #4cc9f0;
            --toggle-icon: #e9ecef;
            --button-hover: #2d3748;
            --separator-color: #2d3748;
            --new-bot-bg: #1a365d;
            --price-change-bg: #332701;
            --price-increase: #e74c3c;
            --price-decrease: #2ecc71;
        }

        @media (prefers-color-scheme: dark) {
            :root:not([data-theme="light"]) {
                --primary-color: #4cc9f0;
                --secondary-color: #4895ef;
                --accent-color: #4361ee;
                --text-color: #e9ecef;
                --light-text: #adb5bd;
                --bg-color: #121212;
                --card-bg: #1e1e1e;
                --card-hover-shadow: 0 15px 30px rgba(0, 0, 0, 0.3);
                --card-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
                --header-bg: linear-gradient(135deg, #4cc9f0 0%, #3a0ca3 100%);
                --border-color: #2d3748;
                --info-bg: #1a365d;
                --timeline-line: #4cc9f0;
                --timeline-dot: #4cc9f0;
                --timeline-dot-border: #121212;
                --timeline-card-bg: #1e1e1e;
                --timeline-date: #4cc9f0;
                --toggle-bg: #2d3748;
                --toggle-dot: #4cc9f0;
                --toggle-icon: #e9ecef;
                --button-hover: #2d3748;
                --separator-color: #2d3748;
                --new-bot-bg: #1a365d;
                --price-change-bg: #332701;
                --price-increase: #e74c3c;
                --price-decrease: #2ecc71;
            }
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background-color: var(--bg-color);
            color: var(--text-color);
            transition: all 0.3s ease;
            line-height: 1.6;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }

        header {
            background: var(--header-bg);
            color: white;
            padding: 40px 0;
            text-align: center;
            margin-bottom: 40px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            border-bottom: 1px solid var(--border-color);
        }

        header h1 {
            margin: 0;
            font-size: 2.5rem;
            font-weight: 700;
            letter-spacing: 0.5px;
        }

        .info {
            background-color: var(--info-bg);
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
            border: 1px solid var(--border-color);
            text-align: center;
            max-width: 900px;
            margin-left: auto;
            margin-right: auto;
        }

        .info p {
            margin: 0;
            font-size: 1.05rem;
            line-height: 1.7;
        }

        .header-links {
            display: flex;
            justify-content: center;
            margin-top: 20px;
        }

        .back-link {
            display: inline-block;
            background-color: var(--primary-color);
            color: white !important;
            padding: 6px 12px;
            border-radius: 20px;
            text-decoration: none;
            margin-left: 10px;
            font-size: 0.9rem;
            transition: all 0.3s ease;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }

        .back-link:hover {
            background-color: var(--secondary-color);
            text-decoration: none !important;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
        }

        /* Theme toggle style */
        #theme-toggle {
            position: fixed;
            top: 15px;
            right: 15px;
            z-index: 1000;
            display: flex;
            align-items: center;
            justify-content: space-between;
            width: 65px;
            height: 30px;
            background: var(--toggle-bg);
            border-radius: 30px;
            padding: 5px;
            cursor: pointer;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }

        #theme-toggle:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
        }

        .theme-toggle-track {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            border-radius: 30px;
            transition: 0.3s;
        }

        .theme-toggle-thumb {
            position: absolute;
            top: 2.5px;
            left: 2.5px;
            width: 25px;
            height: 25px;
            background: var(--toggle-dot);
            border-radius: 50%;
            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--toggle-icon);
        }

        [data-theme="dark"] .theme-toggle-thumb {
            transform: translateX(35px);
        }

        .light-icon, .dark-icon {
            width: 18px;
            height: 18px;
            position: absolute;
            transition: opacity 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--toggle-icon);
            font-size: 14px;
        }

        .light-icon {
            left: 8px;
            opacity: 1;
        }

        .dark-icon {
            right: 8px;
            opacity: 0.5;
        }

        [data-theme="dark"] .light-icon {
            opacity: 0.5;
        }

        [data-theme="dark"] .dark-icon {
            opacity: 1;
        }

        /* Timeline specific styles */
        .timeline {
            position: relative;
            max-width: 800px;
            margin: 0 auto;
            padding: 60px 0;
        }

        .timeline::after {
            content: '';
            position: absolute;
            width: 4px;
            background-color: var(--timeline-line);
            top: 0;
            bottom: 0;
            left: 50%;
            margin-left: -2px;
            border-radius: 2px;
            z-index: 0;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }

        .timeline-item {
            padding: 10px 40px;
            position: relative;
            width: 50%;
            box-sizing: border-box;
            animation: fadeIn 0.6s ease-out both;
        }

        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .timeline-item::after {
            content: '';
            position: absolute;
            width: 20px;
            height: 20px;
            background-color: var(--timeline-dot);
            border: 4px solid var(--timeline-dot-border);
            border-radius: 50%;
            top: 15px;
            z-index: 1;
            box-sizing: content-box;
            box-shadow: 0 0 8px rgba(0, 0, 0, 0.2);
            transition: all 0.3s ease;
        }

        .timeline-item:hover::after {
            /* Remove transform and shadow hover effects */
            transform: none;
            box-shadow: 0 0 8px rgba(0, 0, 0, 0.2);
        }

        .timeline-left {
            left: 0;
        }

        .timeline-right {
            left: 50%;
        }

        .timeline-left::after {
            right: -14px;
        }

        .timeline-right::after {
            left: -14px;
        }

        .timeline-content {
            padding: 25px;
            background-color: var(--timeline-card-bg);
            border-radius: 12px;
            box-shadow: var(--card-shadow);
            position: relative;
            transition: all 0.3s ease;
            border: 1px solid var(--border-color);
            overflow: hidden;
        }

        .timeline-content::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background: linear-gradient(to bottom, var(--primary-color), var(--secondary-color));
            opacity: 0.7;
        }

        .timeline-content:hover {
            /* Remove transform and shadow hover effects */
            transform: none;
            box-shadow: var(--card-shadow);
        }

        .timeline-date {
            font-weight: 600;
            color: var(--timeline-date);
            margin-bottom: 15px;
            font-size: 1.2rem;
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 8px;
            display: inline-block;
        }

        .timeline-changes {
            margin: 0;
            padding: 0;
            list-style-type: none;
        }

        .timeline-changes li {
            margin-bottom: 15px;
            padding: 12px 15px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            transition: all 0.2s ease;
        }

        .timeline-changes li:hover {
            /* Remove shadow and transform hover effects */
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            transform: none;
        }

        .timeline-changes li:last-child {
            margin-bottom: 0;
        }

        .new-bot {
            background-color: var(--new-bot-bg);
        }

        .price-change {
            background-color: var(--price-change-bg);
        }

        .bot-link {
            color: var(--primary-color);
            text-decoration: none;
            font-weight: 600;
            transition: all 0.2s ease;
            border-bottom: 1px dotted transparent;
        }

        .bot-link:hover {
            text-decoration: none;
            border-bottom: 1px dotted var(--primary-color);
        }

        .price-increase {
            color: var(--price-increase);
            font-weight: 600;
            background-color: rgba(220, 53, 69, 0.1);
            padding: 2px 6px;
            border-radius: 4px;
        }

        .price-decrease {
            color: var(--price-decrease);
            font-weight: 600;
            background-color: rgba(40, 167, 69, 0.1);
            padding: 2px 6px;
            border-radius: 4px;
        }

        .no-changes {
            text-align: center;
            padding: 40px;
            background-color: var(--card-bg);
            border-radius: 12px;
            box-shadow: var(--card-shadow);
            margin: 40px 0;
        }

        .no-changes h3 {
            margin: 0 0 10px;
            font-size: 1.3rem;
        }

        .no-changes p {
            margin: 0;
            color: var(--light-text);
        }

        footer {
            text-align: center;
            padding: 30px 0;
            margin-top: 30px;
            color: var(--light-text);
            font-size: 0.9rem;
        }

        footer a {
            color: var(--primary-color);
            text-decoration: none;
        }

        footer a:hover {
            text-decoration: underline;
        }

        @media (max-width: 768px) {
            header {
                padding: 30px 0;
            }

            header h1 {
                font-size: 2rem;
            }

            .timeline::after {
                left: 31px;
            }

            .timeline-item {
                width: 100%;
                padding-left: 70px;
                padding-right: 25px;
            }

            .timeline-left::after, .timeline-right::after {
                left: 21px;
            }

            .timeline-right {
                left: 0;
            }
        }

        @media (max-width: 480px) {
            .container {
                padding: 0 15px;
            }

            header h1 {
                font-size: 1.8rem;
            }

            #theme-toggle {
                top: 10px;
                right: 10px;
            }

            .timeline-item {
                padding-left: 60px;
                padding-right: 15px;
            }
        }
    </style>
</head>
<body>
    <div id="theme-toggle">
        <span class="light-icon">☀️</span>
        <span class="dark-icon">🌙</span>
        <span class="theme-toggle-thumb"></span>
    </div>

    <header>
        <div class="container">
            <h1>Poe 机器人更新时间线</h1>
            <div class="info">
                <p>数据更新时间: {{ date }}
                    <a href="index.html" class="back-link">返回机器人列表</a>
                </p>
            </div>
        </div>
    </header>

    <div class="container">
        {% if timeline_data %}
        <div class="timeline">
            {% for date, changes in timeline_data.items() %}
            <div class="timeline-item {% if loop.index is even %}timeline-right{% else %}timeline-left{% endif %}">
                <div class="timeline-content">
                    <div class="timeline-date">{{ date }}</div>
                    <ul class="timeline-changes">
                        {% if changes.new_bots %}
                        {% for bot in changes.new_bots %}
                        <li class="new-bot">
                            新增机器人: <a href="https://poe.com/{{ bot.handle }}" target="_blank" class="bot-link">{{ bot.name }}</a>
                            {% if bot.price > 0 %}
                            ({{ bot.price }} 积分/条)
                            {% else %}
                            (免费)
                            {% endif %}
                        </li>
                        {% endfor %}
                        {% endif %}

                        {% if changes.price_changes %}
                        {% for change in changes.price_changes %}
                        <li class="price-change">
                            价格变化: <a href="https://poe.com/{{ change.handle }}" target="_blank" class="bot-link">{{ change.name }}</a>
                            <span class="{% if change.old_price < change.new_price %}price-increase{% else %}price-decrease{% endif %}">
                                {{ change.old_price }} → {{ change.new_price }} 积分
                            </span>
                        </li>
                        {% endfor %}
                        {% endif %}
                    </ul>
                </div>
            </div>
            {% endfor %}
        </div>
        {% else %}
        <div class="no-changes">
            <h3>暂无更新记录</h3>
            <p>目前还没有收集到任何机器人的更新记录</p>
        </div>
        {% endif %}
    </div>

    <footer>
        <div class="container">
            <p>© 2023-2024 <a href="https://github.com/Yidadaa/Poe-Bot-Crawler" target="_blank">Poe Bot Crawler</a>. 数据来源于 <a href="https://poe.com" target="_blank">Poe.com</a>.</p>
        </div>
    </footer>

    <script>
        // Theme toggle functionality
        const themeToggle = document.getElementById('theme-toggle');
        const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');

        // Check for saved theme preference or use the system preference
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {
            document.documentElement.setAttribute('data-theme', savedTheme);
        } else if (prefersDarkScheme.matches) {
            document.documentElement.setAttribute('data-theme', 'dark');
        }

        // Toggle theme when the button is clicked
        themeToggle.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            if (currentTheme === 'dark') {
                document.documentElement.setAttribute('data-theme', 'light');
                localStorage.setItem('theme', 'light');
            } else {
                document.documentElement.setAttribute('data-theme', 'dark');
                localStorage.setItem('theme', 'dark');
            }
        });
    </script>
</body>
</html>"""

def generate_timeline_data():
    """
    Generate timeline data by comparing current and previous bot data

    Returns:
        Dictionary with timeline data or None if no changes
    """
    from utils import JSON_DIR, load_json, CURRENT_DATE

    # Path to today's and previous day's data files
    today_file = JSON_DIR / f"official_bots_with_prices_{CURRENT_DATE}.json"

    # Find the previous day's file
    json_files = list(JSON_DIR.glob("official_bots_with_prices_*.json"))
    previous_files = [f for f in json_files if CURRENT_DATE not in f.name]

    if not previous_files:
        logger.warning("No previous data files found")
        return None

    # Sort by modification time (newest first)
    previous_file = max(previous_files, key=lambda f: f.stat().st_mtime)

    # Load data
    today_data = load_json(today_file)
    previous_data = load_json(previous_file)

    # Initialize timeline data
    timeline_data = {}

    # Find new bots and price changes
    new_bots = []
    price_changes = []

    # Create sets of bot IDs for quick comparison
    today_bot_ids = set(today_data.keys())
    previous_bot_ids = set(previous_data.keys())

    # Find new bots (in today's data but not in previous data)
    for bot_id in today_bot_ids - previous_bot_ids:
        bot = today_data[bot_id]
        new_bots.append({
            "id": bot.get("bot_ID", ""),
            "handle": bot.get("handle", ""),
            "name": bot.get("display_name", "Unknown Bot"),
            "price": get_bot_price(bot)
        })

    # Check price changes for existing bots
    for bot_id in today_bot_ids.intersection(previous_bot_ids):
        today_bot = today_data[bot_id]
        previous_bot = previous_data[bot_id]

        today_price = get_bot_price(today_bot)
        previous_price = get_bot_price(previous_bot)

        if today_price != previous_price:
            price_changes.append({
                "id": today_bot.get("bot_ID", ""),
                "handle": today_bot.get("handle", ""),
                "name": today_bot.get("display_name", "Unknown Bot"),
                "old_price": previous_price,
                "new_price": today_price
            })

    # Add to timeline data if there are changes
    if new_bots or price_changes:
        timeline_data[CURRENT_DATE] = {
            "new_bots": new_bots,
            "price_changes": price_changes
        }

        # Try to load existing timeline data and merge
        timeline_file = JSON_DIR / "timeline_data.json"
        if timeline_file.exists():
            existing_timeline = load_json(timeline_file)
            timeline_data.update(existing_timeline)

        # Save the timeline data
        with open(timeline_file, 'w', encoding='utf-8') as f:
            json.dump(timeline_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Created timeline data with {len(new_bots)} new bots and {len(price_changes)} price changes")
    else:
        logger.info("No changes detected for timeline")

    return timeline_data

def get_bot_price(bot):
    """Extract price from bot data in any format"""
    try:
        # Try direct price field
        if "price" in bot and isinstance(bot["price"], (int, float)):
            return bot["price"]

        # Try points_price structure
        if "points_price" in bot:
            if isinstance(bot["points_price"], dict):
                # Try standard_message
                if "standard_message" in bot["points_price"]:
                    value = bot["points_price"]["standard_message"].get("value", 0)
                    if isinstance(value, (int, float, str)):
                        try:
                            return float(value)
                        except (ValueError, TypeError):
                            return 0

                # Try different format
                if "pricing_type" in bot["points_price"]:
                    # Mixed pricing with non_subscriber field
                    if "non_subscriber" in bot["points_price"]:
                        text_output = bot["points_price"]["non_subscriber"].get("text_output", {})
                        value = text_output.get("value", 0)
                        try:
                            return float(value)
                        except (ValueError, TypeError):
                            return 0

        return 0
    except Exception:
        return 0

def generate_timeline_html(timeline_data=None):
    """
    Generate HTML display for timeline

    Args:
        timeline_data: Dictionary containing timeline data (optional)

    Returns:
        Path to generated HTML file
    """
    # If no timeline data provided, try to generate it
    if timeline_data is None:
        timeline_data = generate_timeline_data()

    # If still no data, try to load from file
    if timeline_data is None:
        timeline_file = Path("output/json/timeline_data.json")
        if timeline_file.exists():
            try:
                timeline_data = load_json(timeline_file)
            except Exception as e:
                logger.error(f"Error loading timeline data: {e}")
                timeline_data = {}

    # Render HTML template
    template = Template(TIMELINE_HTML_TEMPLATE)
    html_content = template.render(
        timeline_data=timeline_data,
        date=CURRENT_DATE
    )

    # Save HTML to file
    filename = f"timeline_{CURRENT_DATE}.html"
    filepath = TIMELINE_DIR / filename

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_content)

    logger.info(f"Generated timeline HTML at {filepath}")

    # Update timeline.html in result directory
    timeline_path = RESULT_DIR / "timeline.html"
    shutil.copy2(filepath, timeline_path)

    return filepath

def update_timeline_index():
    """
    Update timeline.html with the most recent timeline HTML file

    Returns:
        Path to the updated timeline.html file
    """
    try:
        # Find most recent HTML file in timeline directory
        html_files = list(TIMELINE_DIR.glob("*.html"))

        if not html_files:
            logger.warning("No HTML files found in timeline directory")
            return None

        # Sort by modification time (newest first)
        most_recent_file = max(html_files, key=lambda f: f.stat().st_mtime)

        # Copy to timeline.html
        timeline_path = RESULT_DIR / "timeline.html"
        shutil.copy2(most_recent_file, timeline_path)

        logger.info(f"Updated timeline.html with content from {most_recent_file}")
        return timeline_path
    except Exception as e:
        logger.error(f"Error updating timeline.html: {e}")
        return None

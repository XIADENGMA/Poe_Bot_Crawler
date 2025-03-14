import logging
from pathlib import Path
import shutil

from jinja2 import Template

from utils import CURRENT_DATE, RESULT_DIR

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

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background-color: var(--bg-color);
            color: var(--text-color);
            transition: all 0.3s ease;
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
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        header h1 {
            margin: 0;
            font-size: 2.5rem;
            font-weight: 700;
        }

        header p {
            margin: 10px 0 0;
            font-size: 1.1rem;
            opacity: 0.9;
        }

        .theme-toggle {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000;
            background-color: var(--toggle-bg);
            border-radius: 30px;
            padding: 5px;
            display: flex;
            align-items: center;
            cursor: pointer;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }

        .theme-toggle:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
        }

        .theme-toggle-dot {
            width: 24px;
            height: 24px;
            background-color: var(--toggle-dot);
            border-radius: 50%;
            position: relative;
            transition: transform 0.3s ease;
        }

        [data-theme="dark"] .theme-toggle-dot {
            transform: translateX(24px);
        }

        .theme-icon {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: var(--toggle-icon);
            font-size: 14px;
        }

        .info-bar {
            background-color: var(--info-bg);
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            box-shadow: var(--card-shadow);
        }

        .info-bar p {
            margin: 5px 0;
            font-size: 0.95rem;
        }

        .info-bar a {
            color: var(--primary-color);
            text-decoration: none;
            transition: color 0.3s ease;
        }

        .info-bar a:hover {
            text-decoration: underline;
        }

        .back-link {
            margin-right: 15px;
            padding: 5px 10px;
            background-color: var(--primary-color);
            color: white !important;
            border-radius: 4px;
            text-decoration: none;
            transition: background-color 0.3s ease;
        }

        .back-link:hover {
            background-color: var(--secondary-color);
            text-decoration: none !important;
        }

        /* Timeline specific styles */
        .timeline {
            position: relative;
            max-width: 800px;
            margin: 0 auto;
            padding: 40px 0;
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
        }

        .timeline-item {
            padding: 10px 40px;
            position: relative;
            width: 50%;
            box-sizing: border-box;
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
        }

        .timeline-left {
            left: 0;
        }

        .timeline-right {
            left: 50%;
        }

        .timeline-left::after {
            right: -10px;
        }

        .timeline-right::after {
            left: -10px;
        }

        .timeline-content {
            padding: 20px;
            background-color: var(--timeline-card-bg);
            border-radius: 8px;
            box-shadow: var(--card-shadow);
            position: relative;
            transition: all 0.3s ease;
        }

        .timeline-content:hover {
            transform: translateY(-5px);
            box-shadow: var(--card-hover-shadow);
        }

        .timeline-date {
            font-weight: 600;
            color: var(--timeline-date);
            margin-bottom: 10px;
            font-size: 1.1rem;
        }

        .timeline-changes {
            margin: 0;
            padding: 0;
            list-style-type: none;
        }

        .timeline-changes li {
            margin-bottom: 10px;
            padding: 10px;
            border-radius: 6px;
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
        }

        .bot-link:hover {
            text-decoration: underline;
        }

        .price-increase {
            color: var(--price-increase);
        }

        .price-decrease {
            color: var(--price-decrease);
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

            .theme-toggle {
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
    <div class="theme-toggle" id="themeToggle">
        <div class="theme-toggle-dot">
            <span class="theme-icon">☀️</span>
        </div>
    </div>

    <header>
        <div class="container">
            <h1>Poe 机器人更新时间线</h1>
            <p>查看 Poe 机器人的更新历史</p>
        </div>
    </header>

    <div class="container">
        <div class="info-bar">
            <div>
                <p>数据更新时间: {{ date }}</p>
                <p>
                    <a href="index.html" class="back-link">返回机器人列表</a>
                </p>
            </div>
            <div>
                <p>
                    <a href="https://github.com/Yidadaa/Poe-Bot-Crawler" target="_blank">GitHub</a> |
                    <a href="https://poe.com" target="_blank">Poe 官网</a>
                </p>
            </div>
        </div>

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
                            新增机器人: <a href="https://poe.com/{{ bot.id }}" target="_blank" class="bot-link">{{ bot.name }}</a>
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
                            价格变化: <a href="https://poe.com/{{ change.id }}" target="_blank" class="bot-link">{{ change.name }}</a>
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
        const themeToggle = document.getElementById('themeToggle');
        const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');

        // Check for saved theme preference or use the system preference
        const currentTheme = localStorage.getItem('theme') || (prefersDarkScheme.matches ? 'dark' : 'light');

        // Apply the current theme
        if (currentTheme === 'dark') {
            document.body.setAttribute('data-theme', 'dark');
            themeToggle.querySelector('.theme-icon').textContent = '🌙';
        } else {
            document.body.removeAttribute('data-theme');
            themeToggle.querySelector('.theme-icon').textContent = '☀️';
        }

        // Toggle theme when the button is clicked
        themeToggle.addEventListener('click', () => {
            let theme;
            if (document.body.getAttribute('data-theme') === 'dark') {
                document.body.removeAttribute('data-theme');
                theme = 'light';
                themeToggle.querySelector('.theme-icon').textContent = '☀️';
            } else {
                document.body.setAttribute('data-theme', 'dark');
                theme = 'dark';
                themeToggle.querySelector('.theme-icon').textContent = '🌙';
            }
            localStorage.setItem('theme', theme);
        });
    </script>
</body>
</html>"""

def generate_timeline_html(timeline_data):
    """
    Generate HTML display for timeline

    Args:
        timeline_data: Dictionary containing timeline data

    Returns:
        Path to generated HTML file
    """
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

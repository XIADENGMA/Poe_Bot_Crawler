import logging
from pathlib import Path
import shutil
import sys
import os

from jinja2 import Template

# Try different import methods to be compatible with different ways of running
try:
    from src.utils import CURRENT_DATE, RESULT_DIR
except ModuleNotFoundError:
    try:
        from utils import CURRENT_DATE, RESULT_DIR
    except ModuleNotFoundError:
        # Add parent directory to path if needed
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from src.utils import CURRENT_DATE, RESULT_DIR

# Define a custom BOT_INFO_DIR path
BOT_INFO_DIR = Path('output/result/bot_info')
BOT_INFO_DIR.mkdir(exist_ok=True, parents=True)

# Configure logging - use the logger from the main module
logger = logging.getLogger("src.html_generator")

# HTML template for the result page
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Poe 机器人积分价格 - {{ date }}</title>
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
            --pricing-bg: #f8f9fa;
            --standard-msg-bg: #e7f5ff;
            --price-text: #2c3e50;
            --toggle-bg: #f1f1f1;
            --toggle-dot: #4361ee;
            --toggle-icon: #333;
            --button-hover: #edf2ff;
            --price-tag-bg: #4361ee;
            --price-tag-text: white;
            --separator-color: #e9ecef;
        }

        /* Dark mode color scheme */
        [data-theme="dark"] {
            --primary-color: #4cc9f0;
            --secondary-color: #4895ef;
            --accent-color: #3f37c9;
            --text-color: #f8f9fa;
            --light-text: #ced4da;
            --bg-color: #121212;
            --card-bg: #1e1e1e;
            --card-hover-shadow: 0 15px 30px rgba(0, 0, 0, 0.5);
            --card-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
            --header-bg: linear-gradient(135deg, #3a0ca3 0%, #4361ee 100%);
            --border-color: #2d3748;
            --info-bg: #1a365d;
            --pricing-bg: #1a1d21;
            --standard-msg-bg: #1a365d;
            --price-text: #f8f9fa;
            --toggle-bg: #2d3748;
            --toggle-dot: #4cc9f0;
            --toggle-icon: #f8f9fa;
            --button-hover: #2d3748;
            --price-tag-bg: #4cc9f0;
            --price-tag-text: #1a1d21;
            --separator-color: #2d3748;
        }

        @media (prefers-color-scheme: dark) {
            :root:not([data-theme="light"]) {
                --primary-color: #4cc9f0;
                --secondary-color: #4895ef;
                --accent-color: #3f37c9;
                --text-color: #f8f9fa;
                --light-text: #ced4da;
                --bg-color: #121212;
                --card-bg: #1e1e1e;
                --card-hover-shadow: 0 15px 30px rgba(0, 0, 0, 0.5);
                --card-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
                --header-bg: linear-gradient(135deg, #3a0ca3 0%, #4361ee 100%);
                --border-color: #2d3748;
                --info-bg: #1a365d;
                --pricing-bg: #1a1d21;
                --standard-msg-bg: #1a365d;
                --price-text: #f8f9fa;
                --toggle-bg: #2d3748;
                --toggle-dot: #4cc9f0;
                --toggle-icon: #f8f9fa;
                --button-hover: #2d3748;
                --price-tag-bg: #4cc9f0;
                --price-tag-text: #1a1d21;
                --separator-color: #2d3748;
            }
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        /* Add transition to elements that will change colors */
        .bot-card, .bot-header, .bot-name, .bot-description, .creator-name,
        .price-info, .standard-message, .price-title, .price-heading,
        .subscriber-label, .info, .character-pricing, .mixed-pricing,
        .text-input, .image-input, .cached-input, .output,
        .non-subscriber-section, .subscriber-section, .theme-toggle,
        .theme-toggle-track {
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            margin: 0;
            padding: 0;
            background-color: var(--bg-color);
            color: var(--text-color);
            line-height: 1.6;
            transition: background-color 0.3s ease, color 0.3s ease;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }

        header {
            background: var(--header-bg);
            color: white;
            padding: 40px 0;
            text-align: center;
            margin-bottom: 40px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
            border-radius: 0 0 15px 15px;
            position: relative;
            overflow: hidden;
        }

        header::before {
            content: "";
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 70%);
            pointer-events: none;
        }

        header h1 {
            font-size: 2.8rem;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        header p {
            font-size: 1.1rem;
            opacity: 0.95;
            max-width: 800px;
            margin: 0 auto;
        }

        .poe-logo {
            width: 48px;
            height: 48px;
            margin-right: 15px;
            vertical-align: middle;
            filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
        }

        /* Theme toggle styling */
        .theme-toggle-wrapper {
            position: absolute;
            top: 20px;
            right: 20px;
            z-index: 10;
        }

        .theme-toggle {
            background-color: var(--toggle-bg);
            border-radius: 24px;
            padding: 4px;
            width: 70px;
            height: 36px;
            display: flex;
            align-items: center;
            cursor: pointer;
            position: relative;
            border: 2px solid rgba(255,255,255,0.2);
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
            transition: all 0.3s ease;
        }

        .theme-toggle:hover {
            transform: scale(1.05);
            box-shadow: 0 6px 15px rgba(0, 0, 0, 0.25);
        }

        .theme-toggle-track {
            position: absolute;
            width: 28px;
            height: 28px;
            border-radius: 50%;
            background-color: var(--toggle-dot);
            left: 4px;
            transition: transform 0.4s cubic-bezier(0.68, -0.55, 0.27, 1.55);
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
        }

        .theme-toggle[data-active="dark"] .theme-toggle-track {
            transform: translateX(34px);
        }

        .theme-toggle-icon {
            position: absolute;
            font-size: 16px;
            transition: opacity 0.3s ease;
        }

        .theme-toggle-icon.sun {
            left: 8px;
            opacity: 1;
        }

        .theme-toggle-icon.moon {
            right: 8px;
            opacity: 0.5;
        }

        .theme-toggle[data-active="dark"] .theme-toggle-icon.sun {
            opacity: 0.5;
        }

        .theme-toggle[data-active="dark"] .theme-toggle-icon.moon {
            opacity: 1;
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

        .search-filter-container {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: center;
            gap: 15px;
            margin-bottom: 30px;
            background-color: var(--card-bg);
            padding: 20px;
            border-radius: 12px;
            box-shadow: var(--card-shadow);
            border: 1px solid var(--border-color);
            animation: fadeIn 0.5s ease-out 0.7s backwards;
        }

        .search-box {
            position: relative;
            flex: 1;
            min-width: 250px;
        }

        .search-input {
            width: 100%;
            padding: 10px 40px 10px 15px;
            border-radius: 8px;
            border: 1px solid var(--border-color);
            background-color: var(--bg-color);
            color: var(--text-color);
            font-size: 1rem;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }

        .search-input:focus {
            outline: none;
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px rgba(67, 97, 238, 0.2);
        }

        .search-clear {
            position: absolute;
            right: 10px;
            top: 50%;
            transform: translateY(-50%);
            background: none;
            border: none;
            color: var(--light-text);
            cursor: pointer;
            font-size: 14px;
            padding: 4px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0.7;
            transition: all 0.2s ease;
            visibility: hidden;
        }

        .search-clear:hover {
            opacity: 1;
            background-color: rgba(0,0,0,0.05);
        }

        .search-input:not(:placeholder-shown) + .search-clear {
            visibility: visible;
        }

        .filter-options {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }

        .filter-select {
            padding: 10px 15px;
            border-radius: 8px;
            border: 1px solid var(--border-color);
            background-color: var(--bg-color);
            color: var(--text-color);
            font-size: 0.95rem;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            -webkit-appearance: none;
            -moz-appearance: none;
            appearance: none;
            background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
            background-repeat: no-repeat;
            background-position: right 10px center;
            background-size: 16px;
            padding-right: 35px;
        }

        .filter-select:focus {
            outline: none;
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px rgba(67, 97, 238, 0.2);
        }

        .no-results {
            grid-column: 1 / -1;
            text-align: center;
            padding: 40px;
            background-color: var(--card-bg);
            border-radius: 12px;
            border: 1px solid var(--border-color);
            color: var(--light-text);
            font-size: 1.1rem;
            box-shadow: var(--card-shadow);
            display: none;
        }

        .bot-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 25px;
            margin-top: 30px;
        }

        .bot-card {
            background-color: var(--card-bg);
            border-radius: 12px;
            box-shadow: var(--card-shadow);
            padding: 20px;
            display: flex;
            flex-direction: column;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            position: relative;
            overflow: hidden;
            cursor: pointer;
        }

        .bot-card:hover {
            transform: translateY(-5px);
            box-shadow: var(--card-hover-shadow);
        }

        .bot-header {
            padding: 20px;
            display: flex;
            align-items: center;
            border-bottom: 1px solid var(--border-color);
            position: relative;
        }

        .bot-avatar {
            width: 70px;
            height: 70px;
            border-radius: 50%;
            object-fit: cover;
            margin-right: 15px;
            border: 3px solid var(--primary-color);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
        }

        .bot-card:hover .bot-avatar {
            transform: scale(1.05);
        }

        .bot-name {
            font-size: 1.4rem;
            margin: 0 0 5px;
            color: var(--text-color);
            font-weight: 600;
        }

        .bot-handle-container {
            display: flex;
            align-items: center;
            width: 100%;
            margin-bottom: 4px;
        }

        .bot-handle {
            font-size: 0.85rem;
            color: var(--light-text);
            margin-top: -2px;
        }

        .bot-name a, .bot-handle a {
            text-decoration: none;
            color: inherit;
            transition: color 0.2s ease;
        }

        .bot-name a:hover, .bot-handle a:hover {
            color: var(--primary-color);
            text-decoration: underline;
        }

        /* Make the whole card not clickable by default */
        .bot-card a {
            text-decoration: none;
            color: inherit;
            pointer-events: none;
        }

        /* But enable clicks specifically on the avatar and name elements */
        .bot-avatar, .bot-name a, .bot-handle a {
            pointer-events: auto;
        }

        /* Style for the creator info in the header */
        .header-creator-info {
            margin-left: auto;
            padding: 0;
            background-color: transparent;
            border: none;
            display: flex;
            align-items: center;
        }

        .header-creator-info .creator-avatar {
            width: 24px;
            height: 24px;
            margin-right: 8px;
        }

        .header-creator-info .creator-name {
            font-size: 0.85rem;
            color: var(--light-text);
        }

        /* Style for the inline creator info */
        .inline-creator-info {
            display: inline-flex;
            align-items: center;
            padding: 3px 8px;
            background-color: rgba(0, 0, 0, 0.2);
            border-radius: 8px;
            font-size: 0.75rem;
            margin-top: 8px;
            max-width: 100%;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .inline-creator-info .creator-avatar {
            width: 14px;
            height: 14px;
            border-radius: 50%;
            margin-right: 4px;
        }

        .inline-creator-info .creator-name {
            font-size: 0.75rem;
            color: var(--light-text);
            font-weight: normal;
        }

        .bot-content {
            padding: 20px;
            flex-grow: 1;
            display: flex;
            flex-direction: column;
        }

        .bot-description {
            margin-bottom: 20px;
            font-size: 0.95rem;
            line-height: 1.6;
            color: var(--text-color);
            max-height: 120px;
            overflow-y: auto;
            scrollbar-width: thin;
            scrollbar-color: var(--primary-color) var(--card-bg);
        }

        .bot-description::-webkit-scrollbar {
            width: 6px;
        }

        .bot-description::-webkit-scrollbar-track {
            background: var(--card-bg);
        }

        .bot-description::-webkit-scrollbar-thumb {
            background-color: var(--primary-color);
            border-radius: 10px;
        }

        .creator-info {
            display: flex;
            align-items: center;
            background-color: var(--pricing-bg);
            border-radius: 6px;
            margin-top: 4px;
            padding: 5px 8px;
            font-size: 0.8rem;
            width: fit-content;
            border: 1px solid var(--border-color);
        }

        .creator-avatar {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            margin-right: 10px;
            object-fit: cover;
        }

        .creator-name {
            font-size: 0.95rem;
            color: var(--text-color);
            font-weight: 500;
        }

        .price-info {
            background-color: var(--pricing-bg);
            border-radius: 12px;
            padding: 15px;
            flex-grow: 1;
            border: 1px solid var(--border-color);
        }

        .price-title {
            font-size: 1.15rem;
            margin: 0 0 15px;
            color: var(--text-color);
            text-align: center;
            font-weight: 600;
            padding-bottom: 10px;
            border-bottom: 1px solid var(--separator-color);
            position: relative;
        }

        .price-title::after {
            content: "";
            position: absolute;
            bottom: -1px;
            left: 50%;
            transform: translateX(-50%);
            width: 60px;
            height: 3px;
            background-color: var(--primary-color);
            border-radius: 3px;
        }

        .price-separator {
            border: 0;
            height: 1px;
            background-color: var(--separator-color);
            margin: 15px 0;
        }

        .standard-message, .text-input, .image-input, .cached-input, .output,
        .non-subscriber-section, .subscriber-section {
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 12px;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
            position: relative;
        }

        .standard-message {
            background-color: var(--standard-msg-bg);
            border: 1px solid var(--border-color);
        }

        .text-input, .image-input, .cached-input, .output {
            background-color: var(--pricing-bg);
            border: 1px solid var(--border-color);
        }

        .price-heading {
            font-size: 1rem;
            font-weight: 600;
            margin-bottom: 8px;
            color: var(--price-text);
            display: inline-block;
            background-color: var(--price-tag-bg);
            color: var(--price-tag-text);
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 0.9rem;
            margin-right: 8px;
        }

        .subscriber-label {
            display: inline-block;
            padding: 4px 10px;
            background-color: var(--primary-color);
            color: white;
            border-radius: 12px;
            font-size: 0.85rem;
            font-weight: 600;
            margin-bottom: 10px;
        }

        .footer {
            margin-top: 50px;
            text-align: center;
            color: var(--light-text);
            font-size: 0.95rem;
            padding: 30px 0;
            border-top: 1px solid var(--border-color);
            background-color: var(--card-bg);
            border-radius: 15px 15px 0 0;
            box-shadow: 0 -4px 10px rgba(0, 0, 0, 0.05);
        }

        @media (max-width: 768px) {
            .bot-grid {
                grid-template-columns: repeat(2, 1fr);
                gap: 20px;
            }

            .container {
                padding: 10px;
            }

            header {
                padding: 30px 0;
            }

            header h1 {
                font-size: 2.2rem;
            }

            .bot-description {
                max-height: 100px;
            }

            .theme-toggle-wrapper {
                top: 15px;
                right: 15px;
            }

            .bot-avatar {
                width: 60px;
                height: 60px;
            }

            .price-title {
                font-size: 1.1rem;
            }

            .header-creator-info .creator-name {
                font-size: 0.8rem;
            }

            .header-creator-info .creator-avatar {
                width: 20px;
                height: 20px;
            }

            .inline-creator-info .creator-name {
                font-size: 0.8rem;
            }

            .inline-creator-info .creator-avatar {
                width: 16px;
                height: 16px;
            }
        }

        @media (max-width: 480px) {
            .bot-grid {
                grid-template-columns: 1fr;
            }

            header h1 {
                font-size: 1.8rem;
            }

            .poe-logo {
                width: 36px;
                height: 36px;
            }

            .bot-card {
                max-width: 100%;
            }

            .header-creator-info {
                margin-left: 0;
                margin-top: 10px;
                position: absolute;
                top: 70px;
                right: 20px;
            }

            .bot-header {
                flex-wrap: wrap;
                padding-bottom: 40px;
            }

            .bot-handle-container {
                flex-wrap: wrap;
            }

            .inline-creator-info {
                margin-left: 0;
                margin-top: 5px;
            }
        }

        .timeline-button {
            display: inline-block;
            background-color: var(--primary-color);
            color: white;
            padding: 6px 12px;
            border-radius: 20px;
            text-decoration: none;
            margin-left: 10px;
            font-size: 0.9rem;
            transition: all 0.3s ease;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }

        .timeline-button:hover {
            background-color: var(--secondary-color);
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
        }

        .update-sparkle {
            display: inline-block;
            margin-left: 5px;
            animation: sparkle 1.5s infinite;
        }

        .update-notice {
            color: var(--primary-color);
            font-weight: 600;
            margin-top: 10px;
            animation: sparkle 1.5s infinite;
        }

        @keyframes sparkle {
            0% { opacity: 0.4; }
            50% { opacity: 1; }
            100% { opacity: 0.4; }
        }

        @media (max-width: 992px) {
            .bot-card {
                opacity: 0;
                transform: translateY(20px);
                transition: opacity 0.5s ease, transform 0.5s ease;
            }

            .bot-card.animate-in {
                opacity: 1;
                transform: translateY(0);
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="theme-toggle-wrapper">
                <div class="theme-toggle" id="theme-toggle" data-active="light">
                    <div class="theme-toggle-track"></div>
                    <span class="theme-toggle-icon sun">☀️</span>
                    <span class="theme-toggle-icon moon">🌙</span>
                </div>
            </div>
            <div class="header-content">
                <h1><img src="assets/favicon.svg" alt="Poe Logo" class="poe-logo">Poe 机器人积分价格</h1>
                <div class="info">
                    <p>数据更新时间: {{ date }}
                        <a href="timeline.html" class="timeline-button">
                            查看更新时间线 {% if has_updates %}<span class="update-sparkle">✨</span>{% endif %}
                        </a>
                    </p>
                    {% if has_updates %}
                    <p class="update-notice">今日有更新!</p>
                    {% endif %}
                </div>
            </div>
        </header>

        <div class="search-filter-container">
            <div class="search-box">
                <input type="text" id="search-input" placeholder="搜索机器人名称或描述..." class="search-input">
                <button id="search-clear" class="search-clear" title="清除搜索">✕</button>
            </div>
            <div class="filter-options">
                <select id="price-filter" class="filter-select">
                    <option value="all">所有价格类型</option>
                    <option value="flat">固定价格</option>
                    <option value="variable">变量价格</option>
                    <option value="mixed">混合价格</option>
                </select>
                <select id="sort-options" class="filter-select">
                    <option value="name-asc">名称 (A-Z)</option>
                    <option value="name-desc">名称 (Z-A)</option>
                    <option value="price-asc">价格 (低到高)</option>
                    <option value="price-desc">价格 (高到低)</option>
                </select>
            </div>
        </div>

        <div class="bot-grid" id="bot-grid">
            {% for bot_id, bot in bots.items() %}
            <div class="bot-card"
                 data-name="{{ bot.display_name }}"
                 data-handle="{{ bot.handle }}"
                 data-description="{{ bot.description }}"
                 data-pricing-type="{{ bot.points_price.pricing_type if bot.points_price else 'unknown' }}"
                 data-standard-price="{{ bot.points_price.standard_message.value if bot.points_price and bot.points_price.standard_message else '0' }}">
                <div class="bot-header">
                    <a href="https://poe.com/{{ bot.handle }}" target="_blank"><img class="bot-avatar" src="{{ bot.picture_url }}" alt="{{ bot.display_name }}"></a>
                    <div>
                        <h3 class="bot-name"><a href="https://poe.com/{{ bot.handle }}" target="_blank">{{ bot.display_name }}</a></h3>
                        <div class="bot-handle-container">
                            <div class="bot-handle"><a href="https://poe.com/{{ bot.handle }}" target="_blank">@{{ bot.handle }}</a></div>
                        </div>
                        {% if bot.creator %}
                        <div class="creator-info inline-creator-info">
                            {% if bot.creator.profile_photo_url %}
                            <img class="creator-avatar" src="{{ bot.creator.profile_photo_url }}" alt="{{ bot.creator.full_name }}">
                            {% endif %}
                            <div class="creator-name">{{ bot.creator.full_name }}</div>
                        </div>
                        {% else %}
                        <div class="creator-info inline-creator-info">
                            <div class="creator-name">Unknown Creator</div>
                        </div>
                        {% endif %}
                    </div>
                </div>
                <div class="bot-content">
                    <div class="bot-description">{{ bot.description }}</div>

                    <div class="price-info">
                        <h3 class="price-title">积分价格</h3>
                        {% if bot.points_price %}
                            {% if bot.points_price.pricing_type == "flat" %}
                                <div class="standard-message">
                                    <p class="price-heading">标准消息</p>
                                    <p>{{ bot.points_price.standard_message.value }} 积分/信息</p>
                                </div>

                                {% if bot.points_price.text_input or bot.points_price.image_input or bot.points_price.cached_input or bot.points_price.output %}
                                <hr class="price-separator">
                                {% endif %}

                                {% if bot.points_price.text_input %}
                                <div class="text-input">
                                    <p>文本输入: {{ bot.points_price.text_input.value }}
                                    {% if bot.points_price.text_input.per is mapping %}
                                        {% if bot.points_price.text_input.per.unit == "tokens" %}
                                            积分/{{ bot.points_price.text_input.per.value }} Tokens
                                        {% elif bot.points_price.text_input.per.unit == "characters" %}
                                            积分/{{ bot.points_price.text_input.per.value }} Tokens
                                        {% else %}
                                            {{ bot.points_price.text_input.unit }}/{{ bot.points_price.text_input.per.value }} {{ bot.points_price.text_input.per.unit }}
                                        {% endif %}
                                    {% else %}
                                        {% if bot.points_price.text_input.per == "1k tokens" %}
                                            积分/1k Tokens
                                        {% elif bot.points_price.text_input.per == "token" %}
                                            积分/Token
                                        {% elif bot.points_price.text_input.per == "character" %}
                                            积分/Token
                                        {% elif bot.points_price.text_input.per == "1k characters" or bot.points_price.text_input.per == "1k character" %}
                                            积分/1k Tokens
                                        {% elif bot.points_price.text_input.per == "message" %}
                                            积分/信息
                                        {% else %}
                                            {{ bot.points_price.text_input.unit }}/{{ bot.points_price.text_input.per }}
                                        {% endif %}
                                    {% endif %}
                                    </p>
                                </div>
                                {% endif %}

                                {% if bot.points_price.image_input %}
                                <div class="image-input">
                                    <p>图片输入: {{ bot.points_price.image_input.value }}
                                    {% if bot.points_price.image_input.per is mapping %}
                                        {% if bot.points_price.image_input.per.unit == "tokens" %}
                                            积分/{{ bot.points_price.image_input.per.value }} Tokens
                                        {% elif bot.points_price.image_input.per.unit == "characters" %}
                                            积分/{{ bot.points_price.image_input.per.value }} Tokens
                                        {% else %}
                                            {{ bot.points_price.image_input.unit }}/{{ bot.points_price.image_input.per.value }} {{ bot.points_price.image_input.per.unit }}
                                        {% endif %}
                                    {% else %}
                                        {% if bot.points_price.image_input.per == "1k tokens" %}
                                            积分/1k Tokens
                                        {% elif bot.points_price.image_input.per == "token" %}
                                            积分/Token
                                        {% elif bot.points_price.image_input.per == "character" %}
                                            积分/Token
                                        {% elif bot.points_price.image_input.per == "1k characters" or bot.points_price.image_input.per == "1k character" %}
                                            积分/1k Tokens
                                        {% elif bot.points_price.image_input.per == "message" %}
                                            积分/信息
                                        {% elif bot.points_price.image_input.per == "image" %}
                                            积分/图片
                                        {% else %}
                                            {{ bot.points_price.image_input.unit }}/{{ bot.points_price.image_input.per }}
                                        {% endif %}
                                    {% endif %}
                                    </p>
                                </div>
                                {% endif %}

                                {% if bot.points_price.cached_input %}
                                <div class="cached-input">
                                    <p>缓存输入: {{ bot.points_price.cached_input.value }}
                                    {% if bot.points_price.cached_input.per is mapping %}
                                        {% if bot.points_price.cached_input.per.unit == "tokens" %}
                                            积分/{{ bot.points_price.cached_input.per.value }} Tokens
                                        {% elif bot.points_price.cached_input.per.unit == "characters" %}
                                            积分/{{ bot.points_price.cached_input.per.value }} Tokens
                                        {% else %}
                                            {{ bot.points_price.cached_input.unit }}/{{ bot.points_price.cached_input.per.value }} {{ bot.points_price.cached_input.per.unit }}
                                        {% endif %}
                                    {% else %}
                                        {% if bot.points_price.cached_input.per == "1k tokens" %}
                                            积分/1k Tokens
                                        {% elif bot.points_price.cached_input.per == "token" %}
                                            积分/Token
                                        {% elif bot.points_price.cached_input.per == "character" %}
                                            积分/Token
                                        {% elif bot.points_price.cached_input.per == "1k characters" or bot.points_price.cached_input.per == "1k character" %}
                                            积分/1k Tokens
                                        {% elif bot.points_price.cached_input.per == "message" %}
                                            积分/信息
                                        {% else %}
                                            {{ bot.points_price.cached_input.unit }}/{{ bot.points_price.cached_input.per }}
                                        {% endif %}
                                    {% endif %}
                                    </p>
                                </div>
                                {% endif %}

                                {% if bot.points_price.output %}
                                <div class="output">
                                    <p>输出: {{ bot.points_price.output.value }}
                                    {% if bot.points_price.output.per is mapping %}
                                        {% if bot.points_price.output.per.unit == "tokens" %}
                                            积分/{{ bot.points_price.output.per.value }} Tokens
                                        {% elif bot.points_price.output.per.unit == "characters" %}
                                            积分/{{ bot.points_price.output.per.value }} Tokens
                                        {% else %}
                                            {{ bot.points_price.output.unit }}/{{ bot.points_price.output.per.value }} {{ bot.points_price.output.per.unit }}
                                        {% endif %}
                                    {% else %}
                                        {% if bot.points_price.output.per == "1k tokens" %}
                                            积分/1k Tokens
                                        {% elif bot.points_price.output.per == "token" %}
                                            积分/Token
                                        {% elif bot.points_price.output.per == "character" %}
                                            积分/Token
                                        {% elif bot.points_price.output.per == "1k characters" or bot.points_price.output.per == "1k character" %}
                                            积分/1k Tokens
                                        {% elif bot.points_price.output.per == "message" %}
                                            积分/信息
                                        {% else %}
                                            {{ bot.points_price.output.unit }}/{{ bot.points_price.output.per }}
                                        {% endif %}
                                    {% endif %}
                                    </p>
                                </div>
                                {% endif %}

                            {% elif bot.points_price.pricing_type == "variable" %}
                                <div class="standard-message">
                                    <p class="price-heading">标准消息</p>
                                    <p>{{ bot.points_price.standard_message.value }} 积分/信息</p>
                                </div>

                                {% if bot.points_price.text_input or bot.points_price.image_input or bot.points_price.cached_input or bot.points_price.output %}
                                <hr class="price-separator">
                                {% endif %}

                                {% if bot.points_price.text_input %}
                                <div class="text-input">
                                    <p>文本输入: {{ bot.points_price.text_input.value }}
                                    {% if bot.points_price.text_input.per is mapping %}
                                        {% if bot.points_price.text_input.per.unit == "tokens" %}
                                            积分/{{ bot.points_price.text_input.per.value }} Tokens
                                        {% elif bot.points_price.text_input.per.unit == "characters" %}
                                            积分/{{ bot.points_price.text_input.per.value }} Tokens
                                        {% else %}
                                            {{ bot.points_price.text_input.unit }}/{{ bot.points_price.text_input.per.value }} {{ bot.points_price.text_input.per.unit }}
                                        {% endif %}
                                    {% else %}
                                        {% if bot.points_price.text_input.per == "1k tokens" %}
                                            积分/1k Tokens
                                        {% elif bot.points_price.text_input.per == "token" %}
                                            积分/Token
                                        {% elif bot.points_price.text_input.per == "character" %}
                                            积分/Token
                                        {% elif bot.points_price.text_input.per == "1k characters" or bot.points_price.text_input.per == "1k character" %}
                                            积分/1k Tokens
                                        {% elif bot.points_price.text_input.per == "message" %}
                                            积分/信息
                                        {% else %}
                                            {{ bot.points_price.text_input.unit }}/{{ bot.points_price.text_input.per }}
                                        {% endif %}
                                    {% endif %}
                                    </p>
                                </div>
                                {% endif %}

                                {% if bot.points_price.image_input %}
                                <div class="image-input">
                                    <p>图片输入: {{ bot.points_price.image_input.value }}
                                    {% if bot.points_price.image_input.per is mapping %}
                                        {% if bot.points_price.image_input.per.unit == "tokens" %}
                                            积分/{{ bot.points_price.image_input.per.value }} Tokens
                                        {% elif bot.points_price.image_input.per.unit == "characters" %}
                                            积分/{{ bot.points_price.image_input.per.value }} Tokens
                                        {% else %}
                                            {{ bot.points_price.image_input.unit }}/{{ bot.points_price.image_input.per.value }} {{ bot.points_price.image_input.per.unit }}
                                        {% endif %}
                                    {% else %}
                                        {% if bot.points_price.image_input.per == "1k tokens" %}
                                            积分/1k Tokens
                                        {% elif bot.points_price.image_input.per == "token" %}
                                            积分/Token
                                        {% elif bot.points_price.image_input.per == "character" %}
                                            积分/Token
                                        {% elif bot.points_price.image_input.per == "1k characters" or bot.points_price.image_input.per == "1k character" %}
                                            积分/1k Tokens
                                        {% elif bot.points_price.image_input.per == "message" %}
                                            积分/信息
                                        {% elif bot.points_price.image_input.per == "image" %}
                                            积分/图片
                                        {% else %}
                                            {{ bot.points_price.image_input.unit }}/{{ bot.points_price.image_input.per }}
                                        {% endif %}
                                    {% endif %}
                                    </p>
                                </div>
                                {% endif %}

                                {% if bot.points_price.cached_input %}
                                <div class="cached-input">
                                    <p>缓存输入: {{ bot.points_price.cached_input.value }}
                                    {% if bot.points_price.cached_input.per is mapping %}
                                        {% if bot.points_price.cached_input.per.unit == "tokens" %}
                                            积分/{{ bot.points_price.cached_input.per.value }} Tokens
                                        {% elif bot.points_price.cached_input.per.unit == "characters" %}
                                            积分/{{ bot.points_price.cached_input.per.value }} Tokens
                                        {% else %}
                                            {{ bot.points_price.cached_input.unit }}/{{ bot.points_price.cached_input.per.value }} {{ bot.points_price.cached_input.per.unit }}
                                        {% endif %}
                                    {% else %}
                                        {% if bot.points_price.cached_input.per == "1k tokens" %}
                                            积分/1k Tokens
                                        {% elif bot.points_price.cached_input.per == "token" %}
                                            积分/Token
                                        {% elif bot.points_price.cached_input.per == "character" %}
                                            积分/Token
                                        {% elif bot.points_price.cached_input.per == "1k characters" or bot.points_price.cached_input.per == "1k character" %}
                                            积分/1k Tokens
                                        {% elif bot.points_price.cached_input.per == "message" %}
                                            积分/信息
                                        {% else %}
                                            {{ bot.points_price.cached_input.unit }}/{{ bot.points_price.cached_input.per }}
                                        {% endif %}
                                    {% endif %}
                                    </p>
                                </div>
                                {% endif %}

                                {% if bot.points_price.output %}
                                <div class="output">
                                    <p>输出: {{ bot.points_price.output.value }}
                                    {% if bot.points_price.output.per is mapping %}
                                        {% if bot.points_price.output.per.unit == "tokens" %}
                                            积分/{{ bot.points_price.output.per.value }} Tokens
                                        {% elif bot.points_price.output.per.unit == "characters" %}
                                            积分/{{ bot.points_price.output.per.value }} Tokens
                                        {% else %}
                                            {{ bot.points_price.output.unit }}/{{ bot.points_price.output.per.value }} {{ bot.points_price.output.per.unit }}
                                        {% endif %}
                                    {% else %}
                                        {% if bot.points_price.output.per == "1k tokens" %}
                                            积分/1k Tokens
                                        {% elif bot.points_price.output.per == "token" %}
                                            积分/Token
                                        {% elif bot.points_price.output.per == "character" %}
                                            积分/Token
                                        {% elif bot.points_price.output.per == "1k characters" or bot.points_price.output.per == "1k character" %}
                                            积分/1k Tokens
                                        {% elif bot.points_price.output.per == "message" %}
                                            积分/信息
                                        {% else %}
                                            {{ bot.points_price.output.unit }}/{{ bot.points_price.output.per }}
                                        {% endif %}
                                    {% endif %}
                                    </p>
                                </div>
                                {% endif %}
                            {% elif bot.points_price.pricing_type == "text_input_only" %}
                                <div class="standard-message">
                                    <p class="price-heading">标准消息</p>
                                    <p>{{ bot.points_price.standard_message.value }} 积分/信息</p>
                                </div>

                                <hr class="price-separator">

                                <div class="text-input">
                                    <p>文本输入: {{ bot.points_price.text_input.value }}
                                    {% if bot.points_price.text_input.per is mapping %}
                                        {% if bot.points_price.text_input.per.unit == "tokens" %}
                                            积分/{{ bot.points_price.text_input.per.value }} Tokens
                                        {% elif bot.points_price.text_input.per.unit == "characters" %}
                                            积分/{{ bot.points_price.text_input.per.value }} Tokens
                                        {% else %}
                                            {{ bot.points_price.text_input.unit }}/{{ bot.points_price.text_input.per.value }} {{ bot.points_price.text_input.per.unit }}
                                        {% endif %}
                                    {% else %}
                                        {% if bot.points_price.text_input.per == "1k tokens" %}
                                            积分/1k Tokens
                                        {% elif bot.points_price.text_input.per == "token" %}
                                            积分/Token
                                        {% elif bot.points_price.text_input.per == "character" %}
                                            积分/Token
                                        {% elif bot.points_price.text_input.per == "1k characters" or bot.points_price.text_input.per == "1k character" %}
                                            积分/1k Tokens
                                        {% elif bot.points_price.text_input.per == "message" %}
                                            积分/信息
                                        {% else %}
                                            {{ bot.points_price.text_input.unit }}/{{ bot.points_price.text_input.per }}
                                        {% endif %}
                                    {% endif %}
                                    </p>
                                </div>
                            {% elif bot.points_price.pricing_type == "per_character" %}
                                <div class="character-pricing">
                                    <div class="standard-message">
                                        <p class="price-heading">标准消息</p>
                                        <p>{{ bot.points_price.standard_message.value }}
                                        {% if bot.points_price.standard_message.per == "character" %}
                                            积分/Token
                                        {% elif bot.points_price.standard_message.per == "1k characters" or bot.points_price.standard_message.per == "1k character" %}
                                            积分/1k Tokens
                                        {% elif bot.points_price.standard_message.per == "message" %}
                                            积分/信息
                                        {% else %}
                                            {{ bot.points_price.standard_message.unit }}/{{ bot.points_price.standard_message.per }}
                                        {% endif %}
                                        </p>
                                    </div>

                                    {% if bot.points_price.text_input %}
                                    <hr class="price-separator">
                                    <div class="text-input">
                                        <p>文本输入: {{ bot.points_price.text_input.value }}
                                        {% if bot.points_price.text_input.per is mapping %}
                                            {% if bot.points_price.text_input.per.unit == "tokens" %}
                                                积分/{{ bot.points_price.text_input.per.value }} Tokens
                                            {% elif bot.points_price.text_input.per.unit == "characters" %}
                                                积分/{{ bot.points_price.text_input.per.value }} Tokens
                                            {% else %}
                                                {{ bot.points_price.text_input.unit }}/{{ bot.points_price.text_input.per.value }} {{ bot.points_price.text_input.per.unit }}
                                            {% endif %}
                                        {% else %}
                                            {% if bot.points_price.text_input.per == "1k tokens" %}
                                                积分/1k Tokens
                                            {% elif bot.points_price.text_input.per == "token" %}
                                                积分/Token
                                            {% elif bot.points_price.text_input.per == "character" %}
                                                积分/Token
                                            {% elif bot.points_price.text_input.per == "1k characters" or bot.points_price.text_input.per == "1k character" %}
                                                积分/1k Tokens
                                            {% elif bot.points_price.text_input.per == "message" %}
                                                积分/信息
                                            {% else %}
                                                {{ bot.points_price.text_input.unit }}/{{ bot.points_price.text_input.per }}
                                            {% endif %}
                                        {% endif %}
                                        </p>
                                    </div>
                                    {% endif %}
                                </div>
                            {% elif bot.points_price.pricing_type == "mixed" %}
                                <div class="mixed-pricing">
                                    {% if bot.points_price.non_subscriber %}
                                    <div class="non-subscriber-section">
                                        <p class="price-heading">非订阅用户</p>

                                        {% if bot.points_price.non_subscriber.text_output %}
                                        <div class="text-output">
                                            <p>文本输出: {{ bot.points_price.non_subscriber.text_output.value }}
                                            {% if bot.points_price.non_subscriber.text_output.per == "message" %}
                                                积分/信息
                                            {% else %}
                                                {{ bot.points_price.non_subscriber.text_output.unit }}/{{ bot.points_price.non_subscriber.text_output.per }}
                                            {% endif %}
                                            </p>
                                        </div>
                                        {% endif %}

                                        {% if bot.points_price.non_subscriber.image_output %}
                                        <div class="image-output">
                                            <p>图片输出: {{ bot.points_price.non_subscriber.image_output.value }}
                                            {% if bot.points_price.non_subscriber.image_output.per == "message" %}
                                                积分/信息
                                            {% else %}
                                                {{ bot.points_price.non_subscriber.image_output.unit }}/{{ bot.points_price.non_subscriber.image_output.per }}
                                            {% endif %}
                                            </p>
                                        </div>
                                        {% endif %}
                                    </div>
                                    {% endif %}

                                    {% if bot.points_price.subscriber %}
                                    <div class="subscriber-section">
                                        <p class="price-heading">订阅用户</p>

                                        {% if bot.points_price.subscriber.input %}
                                        <div class="input">
                                            <p>输入: {{ bot.points_price.subscriber.input.value }}
                                            {% if bot.points_price.subscriber.input.per is mapping %}
                                                {% if bot.points_price.subscriber.input.per.unit == "tokens" %}
                                                    积分/{{ bot.points_price.subscriber.input.per.value }} Tokens
                                                {% elif bot.points_price.subscriber.input.per.unit == "characters" %}
                                                    积分/{{ bot.points_price.subscriber.input.per.value }} Tokens
                                                {% else %}
                                                    {{ bot.points_price.subscriber.input.unit }}/{{ bot.points_price.subscriber.input.per.value }} {{ bot.points_price.subscriber.input.per.unit }}
                                                {% endif %}
                                            {% else %}
                                                {% if bot.points_price.subscriber.input.per == "1k tokens" %}
                                                    积分/1k Tokens
                                                {% elif bot.points_price.subscriber.input.per == "token" %}
                                                    积分/Token
                                                {% elif bot.points_price.subscriber.input.per == "character" %}
                                                    积分/Token
                                                {% elif bot.points_price.subscriber.input.per == "1k characters" or bot.points_price.subscriber.input.per == "1k character" %}
                                                    积分/1k Tokens
                                                {% elif bot.points_price.subscriber.input.per == "message" %}
                                                    积分/信息
                                                {% else %}
                                                    {{ bot.points_price.subscriber.input.unit }}/{{ bot.points_price.subscriber.input.per }}
                                                {% endif %}
                                            {% endif %}
                                            {% if bot.points_price.subscriber.input.is_max %} (最大){% endif %}
                                            </p>
                                        </div>
                                        {% endif %}

                                        {% if bot.points_price.subscriber.text_output %}
                                        <div class="text-output">
                                            <p>文本输出: {{ bot.points_price.subscriber.text_output.value }}
                                            {% if bot.points_price.subscriber.text_output.per == "message" %}
                                                积分/信息
                                            {% else %}
                                                {{ bot.points_price.subscriber.text_output.unit }}/{{ bot.points_price.subscriber.text_output.per }}
                                            {% endif %}
                                            </p>
                                        </div>
                                        {% endif %}

                                        {% if bot.points_price.subscriber.image_output %}
                                        <div class="image-output">
                                            <p>图片输出: {{ bot.points_price.subscriber.image_output.value }}
                                            {% if bot.points_price.subscriber.image_output.per == "message" %}
                                                积分/信息
                                            {% else %}
                                                {{ bot.points_price.subscriber.image_output.unit }}/{{ bot.points_price.subscriber.image_output.per }}
                                            {% endif %}
                                            </p>
                                        </div>
                                        {% endif %}
                                    </div>
                                    {% endif %}
                                </div>
                            {% else %}
                                <p>无价格信息</p>
                            {% endif %}
                        {% else %}
                            <p>无价格信息</p>
                        {% endif %}
                    </div>
                </div>
            </div>
            {% endfor %}
            <div id="no-results" class="no-results">
                <p>未找到匹配的机器人。请尝试其他搜索条件。</p>
            </div>
        </div>

        <div class="footer">
            <p>© {{ current_year }} Poe 机器人积分价格爬虫 | 数据仅供参考</p>
        </div>
    </div>

    <script>
        // 获取页面元素
        const themeToggle = document.getElementById('theme-toggle');
        const botCards = document.querySelectorAll('.bot-card');
        const searchInput = document.getElementById('search-input');
        const searchClear = document.getElementById('search-clear');
        const priceFilter = document.getElementById('price-filter');
        const sortOptions = document.getElementById('sort-options');
        const botGrid = document.getElementById('bot-grid');
        const noResults = document.getElementById('no-results');

        // 搜索、筛选和排序功能
        function filterAndSortBots() {
            const searchTerm = searchInput.value.toLowerCase();
            const priceType = priceFilter.value;
            const sortOption = sortOptions.value;

            let visibleCount = 0;

            // 转换为数组以便于排序
            const cardsArray = Array.from(botCards);

            // 根据选项排序
            cardsArray.sort((a, b) => {
                if (sortOption === 'name-asc') {
                    return a.dataset.name.localeCompare(b.dataset.name);
                } else if (sortOption === 'name-desc') {
                    return b.dataset.name.localeCompare(a.dataset.name);
                } else if (sortOption === 'price-asc') {
                    const priceA = parseFloat(a.dataset.standardPrice) || 0;
                    const priceB = parseFloat(b.dataset.standardPrice) || 0;
                    return priceA - priceB;
                } else if (sortOption === 'price-desc') {
                    const priceA = parseFloat(a.dataset.standardPrice) || 0;
                    const priceB = parseFloat(b.dataset.standardPrice) || 0;
                    return priceB - priceA;
                }
                return 0;
            });

            // 重新添加到grid中保持排序顺序
            cardsArray.forEach(card => {
                botGrid.appendChild(card);

                // 应用筛选
                const name = card.dataset.name.toLowerCase();
                const handle = card.dataset.handle.toLowerCase();
                const description = card.dataset.description.toLowerCase();
                const pricingType = card.dataset.pricingType;

                const matchesSearch = name.includes(searchTerm) ||
                                     handle.includes(searchTerm) ||
                                     description.includes(searchTerm);

                const matchesPrice = priceType === 'all' || pricingType === priceType;

                if (matchesSearch && matchesPrice) {
                    card.style.display = 'flex';
                    visibleCount++;
                } else {
                    card.style.display = 'none';
                }
            });

            // 显示"无结果"提示
            if (visibleCount === 0) {
                noResults.style.display = 'block';
            } else {
                noResults.style.display = 'none';
            }
        }

        // 添加事件监听器
        searchInput.addEventListener('input', filterAndSortBots);
        priceFilter.addEventListener('change', filterAndSortBots);
        sortOptions.addEventListener('change', filterAndSortBots);

        // 清除搜索
        searchClear.addEventListener('click', () => {
            searchInput.value = '';
            filterAndSortBots();
        });

        // 初始筛选和排序
        filterAndSortBots();

        // 卡片动画效果
        const animateOnScroll = (entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                    observer.unobserve(entry.target);
                }
            });
        };

        // 设置Intersection Observer
        const cardObserver = new IntersectionObserver(animateOnScroll, {
            root: null,
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });

        // 添加动画CSS
        const style = document.createElement('style');
        style.textContent = `
            .bot-card {
                opacity: 0;
                transform: translateY(20px);
                transition: opacity 0.5s ease, transform 0.5s ease;
            }

            .bot-card.animate-in {
                opacity: 1;
                transform: translateY(0);
            }
        `;
        document.head.appendChild(style);

        // 观察每个卡片
        botCards.forEach(card => {
            cardObserver.observe(card);
        });

        // 主题切换
        themeToggle.addEventListener('click', () => {
            const currentTheme = themeToggle.getAttribute('data-active');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';

            themeToggle.setAttribute('data-active', newTheme);
            document.documentElement.setAttribute('data-theme', newTheme);

            // 存储主题偏好
            localStorage.setItem('theme', newTheme);
        });

        // 加载保存的主题设置
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {
            themeToggle.setAttribute('data-active', savedTheme);
            document.documentElement.setAttribute('data-theme', savedTheme);
        } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            // 如果用户系统偏好深色模式
            themeToggle.setAttribute('data-active', 'dark');
            document.documentElement.setAttribute('data-theme', 'dark');
        }
    </script>
</body>
</html>

"""

def generate_html(bots_data, has_updates=False):
    """
    Generate HTML display from bot data

    Args:
        bots_data: Dict or List containing bot data
        has_updates: Whether updates are available

    Returns:
        Path to the generated HTML file
    """
    logger.info("Generating HTML display...")

    try:
        # Convert bots_data to the format expected by the template if needed
        if isinstance(bots_data, list):
            logger.info("Converting bots_data from list to dictionary for HTML generation")
            bots_dict = {}
            for idx, bot in enumerate(bots_data):
                if isinstance(bot, dict):
                    # Use bot_id as key if available, otherwise use index
                    key = str(bot.get('bot_id', bot.get('botId', idx)))

                    # Create a new bot dictionary with standardized field names
                    new_bot = {}

                    # Map display name
                    if 'displayName' in bot:
                        new_bot['display_name'] = bot['displayName']
                    elif 'display_name' in bot:
                        new_bot['display_name'] = bot['display_name']
                    else:
                        new_bot['display_name'] = "Unknown Bot"

                    # Map handle/bot ID
                    if 'botId' in bot:
                        new_bot['handle'] = bot['botId']
                    elif 'bot_id' in bot:
                        new_bot['handle'] = bot['bot_id']
                    elif 'handle' in bot:
                        new_bot['handle'] = bot['handle']
                    else:
                        new_bot['handle'] = ""

                    # Map description
                    if 'description' in bot:
                        new_bot['description'] = bot['description']
                    else:
                        new_bot['description'] = ""

                    # Map profile picture
                    if 'profilePicture' in bot:
                        new_bot['picture_url'] = bot['profilePicture']
                    elif 'picture_url' in bot:
                        new_bot['picture_url'] = bot['picture_url']
                    else:
                        new_bot['picture_url'] = ""

                    # Map pricing information
                    pricing_info = {}
                    if 'price' in bot and bot['price'] > 0:
                        pricing_info['pricing_type'] = 'flat'
                        pricing_info['standard_message'] = {'value': bot['price']}
                    elif 'points_price' in bot:
                        pricing_info = bot['points_price']

                    new_bot['points_price'] = pricing_info

                    # Map creator information
                    if 'creator' in bot:
                        new_bot['creator'] = bot['creator']
                    else:
                        new_bot['creator'] = {}

                    bots_dict[key] = new_bot
            bots_data = bots_dict

        # Count total and paid bots
        total_bots = len(bots_data)

        # Count paid bots (those with standard_message price > 0)
        paid_bots = 0
        for bot_id, bot in bots_data.items():
            try:
                if bot.get('points_price') and bot['points_price'].get('standard_message'):
                    value = bot['points_price']['standard_message'].get('value', 0)
                    if value == 'N/A':
                        continue
                    if float(str(value)) > 0:
                        paid_bots += 1
            except (ValueError, TypeError):
                continue

        # Create template
        template = Template(HTML_TEMPLATE)

        # Render template with data
        import datetime

        html_content = template.render(
            bots=bots_data,
            date=CURRENT_DATE,
            current_year=datetime.datetime.now().year,
            has_updates=has_updates,
            total_bots=total_bots,
            paid_bots=paid_bots,
            free_bots=total_bots - paid_bots
        )

        # Save HTML files

        # Ensure directories exist
        BOT_INFO_DIR.mkdir(exist_ok=True, parents=True)

        # Save to bot_info directory
        bot_info_filename = f"bot_info_{CURRENT_DATE}.html"
        bot_info_filepath = BOT_INFO_DIR / bot_info_filename

        with open(bot_info_filepath, "w", encoding="utf-8") as f:
            f.write(html_content)

        # Save index.html to result directory only
        result_index_filepath = RESULT_DIR / "index.html"
        shutil.copy2(bot_info_filepath, result_index_filepath)

        logger.info(f"HTML display saved to {bot_info_filepath}")
        logger.info(f"Latest HTML copy saved as {result_index_filepath}")

        return bot_info_filepath
    except Exception as e:
        logger.error(f"Error generating HTML display: {e}")
        raise

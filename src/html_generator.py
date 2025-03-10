import logging
from pathlib import Path

from jinja2 import Template

from utils import CURRENT_DATE, RESULT_DIR

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
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
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
            margin-bottom: 20px;
            padding: 8px 12px;
            background-color: var(--pricing-bg);
            border-radius: 8px;
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
                grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
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
                <p>数据更新时间: {{ date }}</p>
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
                    <img class="bot-avatar" src="{{ bot.picture_url }}" alt="{{ bot.display_name }}">
                    <div>
                        <h3 class="bot-name"><a href="https://poe.com/{{ bot.handle }}" target="_blank">{{ bot.display_name }}</a></h3>
                        <div class="bot-handle"><a href="https://poe.com/{{ bot.handle }}" target="_blank">@{{ bot.handle }}</a></div>
                    </div>
                </div>
                <div class="bot-content">
                    <div class="bot-description">{{ bot.description }}</div>

                    <div class="creator-info">
                        {% if bot.creator %}
                            {% if bot.creator.profile_photo_url %}
                            <img class="creator-avatar" src="{{ bot.creator.profile_photo_url }}" alt="{{ bot.creator.full_name }}">
                            {% endif %}
                            <div class="creator-name">{{ bot.creator.full_name }}</div>
                        {% else %}
                            <div class="creator-name">Unknown Creator</div>
                        {% endif %}
                    </div>

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
        // Get theme toggle element
        const themeToggle = document.getElementById('theme-toggle');
        const botCards = document.querySelectorAll('.bot-card');

        // Add animation class to cards when they appear in viewport
        const animateOnScroll = (entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                    observer.unobserve(entry.target);
                }
            });
        };

        // Set up Intersection Observer
        const cardObserver = new IntersectionObserver(animateOnScroll, {
            root: null,
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });

        // Add animation CSS
        const style = document.createElement('style');
        style.textContent = `
            .bot-card {
                opacity: 0;
                transform: translateY(20px);
                transition: opacity 0.5s ease, transform 0.5s ease, box-shadow 0.3s ease;
            }

            .bot-card.animate-in {
                opacity: 1;
                transform: translateY(0);
            }

            .bot-card:hover .bot-avatar {
                transform: scale(1.05);
            }

            .bot-description {
                position: relative;
                overflow: hidden;
                max-height: 120px;
                transition: max-height 0.3s ease;
            }

            .bot-description.expanded {
                max-height: 300px;
            }

            .bot-description::after {
                content: "";
                position: absolute;
                bottom: 0;
                left: 0;
                width: 100%;
                height: 30px;
                background: linear-gradient(to bottom, transparent, var(--card-bg));
                pointer-events: none;
                opacity: 1;
                transition: opacity 0.3s ease;
            }

            .bot-description.expanded::after {
                opacity: 0;
            }

            .expand-btn {
                background: var(--primary-color);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 3px 10px;
                font-size: 0.8rem;
                cursor: pointer;
                margin-top: -10px;
                margin-bottom: 15px;
                align-self: center;
                opacity: 0.9;
                transition: all 0.2s ease;
            }

            .expand-btn:hover {
                opacity: 1;
                transform: scale(1.05);
            }

            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }

            .header-content {
                animation: fadeIn 0.8s ease-out;
            }

            .theme-toggle {
                animation: fadeIn 0.5s ease-out 0.3s backwards;
            }

            .info {
                animation: fadeIn 0.5s ease-out 0.5s backwards;
            }
        `;
        document.head.appendChild(style);

        // Function to set theme
        function setTheme(theme) {
            document.documentElement.setAttribute('data-theme', theme);
            themeToggle.setAttribute('data-active', theme);
            localStorage.setItem('poe-theme', theme);

            // Add transition animation to body after theme changes
            document.body.classList.add('theme-transition');
            setTimeout(() => {
                document.body.classList.remove('theme-transition');
            }, 1000);
        }

        // Initialize theme based on localStorage or system preference
        function initTheme() {
            const savedTheme = localStorage.getItem('poe-theme');

            if (savedTheme) {
                // If user has previously set a theme preference
                setTheme(savedTheme);
            } else {
                // Check system preference
                const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
                setTheme(prefersDark ? 'dark' : 'light');
            }
        }

        // Toggle theme when button is clicked
        themeToggle.addEventListener('click', function() {
            const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            setTheme(newTheme);

            // Add a small bounce animation to the toggle
            this.classList.add('toggle-bounce');
            setTimeout(() => {
                this.classList.remove('toggle-bounce');
            }, 300);
        });

        // Listen for system preference changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
            // Only automatically change if user hasn't manually set a preference
            if (!localStorage.getItem('poe-theme')) {
                setTheme(e.matches ? 'dark' : 'light');
            }
        });

        // Initialize animation effects
        function initAnimations() {
            // Observe each bot card for scroll animation
            botCards.forEach(card => {
                cardObserver.observe(card);

                // Make bot cards clickable
                card.addEventListener('click', function(e) {
                    // Only navigate if the click was not on an anchor tag or its children
                    if (!e.target.closest('a') && !e.target.closest('button')) {
                        const handle = this.getAttribute('data-handle');
                        if (handle) {
                            window.open(`https://poe.com/${handle}`, '_blank');
                        }
                    }
                });

                // Add description expand functionality
                const description = card.querySelector('.bot-description');
                if (description && description.scrollHeight > description.clientHeight) {
                    const expandBtn = document.createElement('button');
                    expandBtn.className = 'expand-btn';
                    expandBtn.textContent = '展开描述';

                    expandBtn.addEventListener('click', () => {
                        if (description.classList.contains('expanded')) {
                            description.classList.remove('expanded');
                            expandBtn.textContent = '展开描述';
                            // Scroll back to the card top when collapsing
                            card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                        } else {
                            description.classList.add('expanded');
                            expandBtn.textContent = '收起描述';
                        }
                    });

                    // Insert the button after the description
                    description.parentNode.insertBefore(expandBtn, description.nextSibling);
                }
            });
        }

        // Initialize theme on page load
        initTheme();

        // Initialize animations when DOM is fully loaded
        document.addEventListener('DOMContentLoaded', initAnimations);

        // Search and filter functionality
        const searchInput = document.getElementById('search-input');
        const searchClear = document.getElementById('search-clear');
        const priceFilter = document.getElementById('price-filter');
        const sortOptions = document.getElementById('sort-options');
        const noResults = document.getElementById('no-results');

        // Handle search input
        function handleSearch() {
            const searchTerm = searchInput.value.toLowerCase().trim();
            const priceFilterValue = priceFilter.value;
            const sortValue = sortOptions.value;

            // Filter cards based on search term and filter options
            filterAndSortCards(searchTerm, priceFilterValue, sortValue);
        }

        // Filter and sort cards
        function filterAndSortCards(searchTerm, priceType, sortOption) {
            let visibleCount = 0;
            const cards = [...document.querySelectorAll('.bot-card:not(.no-results)')];

            // First, reset all cards to visible for the filter process
            cards.forEach(card => {
                card.style.display = 'flex';
                // Remove animation class to re-apply it later
                card.classList.remove('animate-in');
            });

            // Apply filters
            cards.forEach(card => {
                const name = card.getAttribute('data-name').toLowerCase();
                const handle = card.getAttribute('data-handle').toLowerCase();
                const description = card.getAttribute('data-description').toLowerCase();
                const cardPriceType = card.getAttribute('data-pricing-type');

                const searchMatch = searchTerm === '' ||
                                   name.includes(searchTerm) ||
                                   handle.includes(searchTerm) ||
                                   description.includes(searchTerm);

                const priceMatch = priceType === 'all' || cardPriceType === priceType;

                if (searchMatch && priceMatch) {
                    visibleCount++;
                } else {
                    card.style.display = 'none';
                }
            });

            // Apply sorting
            if (sortOption !== 'name-asc') {
                const sortedCards = [...cards].filter(card => card.style.display !== 'none').sort((a, b) => {
                    if (sortOption === 'name-desc') {
                        return b.getAttribute('data-name').localeCompare(a.getAttribute('data-name'));
                    } else if (sortOption === 'price-asc') {
                        return parseFloat(a.getAttribute('data-standard-price')) - parseFloat(b.getAttribute('data-standard-price'));
                    } else if (sortOption === 'price-desc') {
                        return parseFloat(b.getAttribute('data-standard-price')) - parseFloat(a.getAttribute('data-standard-price'));
                    }
                    return 0;
                });

                // Reappend cards in the new order
                const grid = document.getElementById('bot-grid');
                sortedCards.forEach(card => {
                    grid.appendChild(card);
                });
            }

            // Show no results message if needed
            if (visibleCount === 0) {
                noResults.style.display = 'block';
            } else {
                noResults.style.display = 'none';

                // Re-observe visible cards for animation
                setTimeout(() => {
                    const visibleCards = document.querySelectorAll('.bot-card:not([style*="display: none"])');
                    visibleCards.forEach(card => {
                        cardObserver.observe(card);
                    });
                }, 100);
            }
        }

        // Clear search
        searchClear.addEventListener('click', () => {
            searchInput.value = '';
            handleSearch();
            searchInput.focus();
        });

        // Event listeners for search and filter controls
        searchInput.addEventListener('input', handleSearch);
        priceFilter.addEventListener('change', handleSearch);
        sortOptions.addEventListener('change', handleSearch);

        // Reset filters button
        function addResetButton() {
            const resetBtn = document.createElement('button');
            resetBtn.textContent = '重置筛选';
            resetBtn.className = 'filter-reset';
            resetBtn.addEventListener('click', () => {
                searchInput.value = '';
                priceFilter.value = 'all';
                sortOptions.value = 'name-asc';
                handleSearch();
            });

            // Add to filter options
            document.querySelector('.filter-options').appendChild(resetBtn);

            // Add CSS
            const resetStyle = document.createElement('style');
            resetStyle.textContent = `
                .filter-reset {
                    padding: 10px 15px;
                    border-radius: 8px;
                    border: 1px solid var(--primary-color);
                    background-color: var(--primary-color);
                    color: white;
                    font-size: 0.95rem;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }

                .filter-reset:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
                }

                @media (max-width: 768px) {
                    .search-filter-container {
                        flex-direction: column;
                        align-items: stretch;
                    }

                    .filter-options {
                        justify-content: space-between;
                    }

                    .filter-select, .filter-reset {
                        flex: 1;
                    }
                }
            `;
            document.head.appendChild(resetStyle);
        }

        addResetButton();

        // Add additional animation styles
        const additionalStyles = document.createElement('style');
        additionalStyles.textContent = `
            .theme-transition {
                transition: background-color 0.5s ease, color 0.5s ease;
            }

            .toggle-bounce {
                animation: bounce 0.3s ease;
            }

            @keyframes bounce {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.1); }
            }

            .price-title::after {
                animation: slideIn 1s ease-out;
            }

            @keyframes slideIn {
                from { width: 0; }
                to { width: 60px; }
            }
        `;
        document.head.appendChild(additionalStyles);
    </script>
</body>
</html>
"""


def generate_html(bots_data):
    """
    Generate HTML display from bot data

    Args:
        bots_data: Dict containing bot data

    Returns:
        Path to the generated HTML file
    """
    logger.info("Generating HTML display...")

    try:
        # Create template
        template = Template(HTML_TEMPLATE)

        # Render template with data
        import datetime

        html_content = template.render(
            bots=bots_data, date=CURRENT_DATE, current_year=datetime.datetime.now().year
        )

        # Save HTML file
        filename = f"bots_{CURRENT_DATE}.html"
        filepath = RESULT_DIR / filename

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)

        logger.info(f"HTML display generated and saved to {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"Error generating HTML display: {e}")
        raise

import logging
from pathlib import Path
import shutil
import json
from datetime import datetime

from jinja2 import Template

from src.utils import CURRENT_DATE, RESULT_DIR, load_json

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
            --primary-color-rgb: 67, 97, 238;
            --secondary-color: #3f37c9;
            --secondary-color-rgb: 63, 55, 201;
            --accent-color: #4895ef;
            --accent-color-rgb: 72, 149, 239;
            --text-color: #2d3748;
            --text-color-rgb: 45, 55, 72;
            --light-text: #4a5568;
            --bg-color: #f8f9fa;
            --bg-color-rgb: 248, 249, 250;
            --card-bg: #fff;
            --card-hover-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
            --card-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
            --header-bg: linear-gradient(135deg, #4361ee 0%, #3a0ca3 100%);
            --border-color: #e9ecef;
            --border-color-rgb: 233, 236, 239;
            --info-bg: #e7f5ff;
            --timeline-line: #4361ee;
            --timeline-dot: #4361ee;
            --timeline-dot-border: #fff;
            --timeline-card-bg: #fff;
            --timeline-date: #3a0ca3;
            --toggle-bg: #f1f1f1;
            --toggle-dot: #4361ee;
            --toggle-icon: #333;
            --button-hover: #edf2ff;
            --separator-color: #e9ecef;
            --new-bot-bg: #e7f5ff;
            --price-change-bg: rgba(230, 230, 250, 0.3);
            --price-increase: #dc3545;
            --price-increase-rgb: 220, 53, 69;
            --price-decrease: #28a745;
            --price-decrease-rgb: 40, 167, 69;
            --detail-label-color: #4a5568;
            --detail-value-color: #2d3748;
        }

        /* Dark mode color scheme */
        :root[data-theme="dark"] {
            /* Dark mode */
            --primary-color: #6c8aff;
            --primary-color-rgb: 108, 138, 255;
            --secondary-color: #5e60ce;
            --secondary-color-rgb: 94, 96, 206;
            --accent-color: #64dfdf;
            --accent-color-rgb: 100, 223, 223;
            --text-color: #e9ecef;
            --text-color-rgb: 233, 236, 239;
            --light-text: #adb5bd;
            --bg-color: #121212;
            --bg-color-rgb: 18, 18, 18;
            --card-bg: #1e1e1e;
            --card-hover-shadow: 0 15px 30px rgba(0, 0, 0, 0.3);
            --card-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
            --header-bg: linear-gradient(135deg, #5e60ce 0%, #6930c3 100%);
            --border-color: #333;
            --border-color-rgb: 51, 51, 51;
            --info-bg: #1a365d;
            --timeline-line: #5e60ce;
            --timeline-dot: #5e60ce;
            --timeline-dot-border: #121212;
            --timeline-card-bg: #1e1e1e;
            --timeline-date: #6c8aff;
            --toggle-bg: #333;
            --toggle-dot: #6c8aff;
            --toggle-icon: #e9ecef;
            --button-hover: #2d3748;
            --separator-color: #333;
            --new-bot-bg: #1a365d;
            --price-change-bg: rgba(230, 230, 250, 0.08);
            --price-increase: #ff4d6a;
            --price-increase-rgb: 255, 77, 106;
            --price-decrease: #48bb78;
            --price-decrease-rgb: 72, 187, 120;
            --detail-label-color: #cbd5e0;
            --detail-value-color: #f7fafc;
        }

        @media (prefers-color-scheme: dark) {
            :root:not([data-theme="light"]) {
                --primary-color: #4cc9f0;
                --secondary-color: #4895ef;
                --accent-color: #4361ee;
                --text-color: #e9ecef;
                --light-text: #adb5bd;
                --bg-color: #121212;
                --bg-color-rgb: 18, 18, 18;
                --card-bg: #1e1e1e;
                --card-hover-shadow: 0 15px 30px rgba(0, 0, 0, 0.3);
                --card-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
                --header-bg: linear-gradient(135deg, #4cc9f0 0%, #3a0ca3 100%);
                --border-color: #2d3748;
                --border-color-rgb: 45, 55, 72;
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
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 20px;
        }

        header {
            background: var(--header-bg);
            color: white;
            padding: 40px 0;
            text-align: center;
            margin-bottom: 40px;
            box-shadow: 0 4px 25px rgba(0, 0, 0, 0.2);
            border-bottom: 1px solid var(--border-color);
            position: relative;
            overflow: hidden;
        }

        header:before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: radial-gradient(circle at 20% 150%, rgba(67, 97, 238, 0.15) 0%, transparent 70%),
                        radial-gradient(circle at 80% -20%, rgba(58, 12, 163, 0.2) 0%, transparent 70%);
            pointer-events: none;
        }

        header h1 {
            margin: 0;
            font-size: 2.8rem;
            font-weight: 800;
            letter-spacing: 0.5px;
            text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
            position: relative;
        }

        .info {
            background-color: var(--info-bg);
            padding: 25px;
            border-radius: 16px;
            margin-bottom: 30px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
            border: 1px solid var(--border-color);
            text-align: center;
            max-width: 900px;
            margin-left: auto;
            margin-right: auto;
            position: relative;
            overflow: hidden;
        }

        .info:before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: radial-gradient(circle at 10% 50%, rgba(67, 97, 238, 0.08) 0%, transparent 70%);
            pointer-events: none;
        }

        .info p {
            margin: 0;
            font-size: 1.05rem;
            line-height: 1.7;
            color: var(--text-color);
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
            padding: 10px 20px;
            border-radius: 30px;
            text-decoration: none;
            margin-left: 10px;
            font-size: 0.95rem;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }

        .back-link:hover {
            background-color: var(--secondary-color);
            text-decoration: none !important;
            transform: translateY(-3px);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
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
            max-width: 1000px;
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
            left: 98px;
            border-radius: 2px;
            z-index: 0;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }

        .timeline-item {
            padding: 10px 40px 10px 140px;
            position: relative;
            width: 100%;
            box-sizing: border-box;
            margin-bottom: 30px;
        }

        .timeline-item::after {
            content: '';
            position: absolute;
            width: 20px;
            height: 20px;
            background-color: var(--timeline-dot);
            border: 4px solid var(--timeline-dot-border);
            border-radius: 50%;
            top: 25px;
            left: 86px;
            z-index: 1;
            box-sizing: content-box;
            box-shadow: 0 0 12px rgba(0, 0, 0, 0.3);
            transition: all 0.3s ease;
        }

        .timeline-item:hover::after {
            transform: scale(1.1);
            box-shadow: 0 0 16px rgba(0, 0, 0, 0.4);
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
            padding: 25px 30px;
            background-color: var(--timeline-card-bg);
            border-radius: 16px;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
            position: relative;
            transition: all 0.3s ease;
            border: 1px solid var(--border-color);
            overflow: hidden;
        }

        .timeline-content::before {
            display: none;
        }

        .timeline-content:hover {
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
        }

        .timeline-date {
            font-weight: 700;
            color: var(--timeline-date);
            margin-bottom: 20px;
            font-size: 1.4rem;
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 10px;
            display: inline-block;
            letter-spacing: 0.5px;
        }

        .timeline-changes {
            margin: 0;
            padding: 0;
            list-style-type: none;
        }

        .timeline-changes li {
            margin-bottom: 18px;
            padding: 0;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
            transition: all 0.3s ease;
            overflow: hidden;
        }

        .timeline-changes li:hover {
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
            transform: translateY(-3px);
        }

        .timeline-changes li:last-child {
            margin-bottom: 0;
        }

        .new-bot {
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
        }

        .price-change {
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            margin-bottom: 15px;
        }

        .price-change-summary {
            display: flex;
            align-items: center;
            padding: 15px;
            border-radius: 0;
            border: none;
            border-bottom: 1px solid var(--border-color);
            transition: all 0.2s ease;
            position: relative;
            overflow: hidden;
        }

        .new-bot .price-change-summary {
            border-left: 4px solid var(--accent-color);
        }

        .price-change .price-change-summary {
            border-left: 4px solid var(--primary-color);
        }

        .price-change-summary::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            height: 100%;
            width: 4px;
            opacity: 0.6;
            transition: all 0.3s ease;
        }

        .price-change-summary:hover {
            background-color: rgba(var(--primary-color-rgb), 0.05);
        }

        .price-change-text {
            margin: 0 10px;
            flex-grow: 1;
            font-size: 0.95rem;
            color: var(--text-color);
        }

        .price-change-details {
            padding: 20px;
            background-color: rgba(var(--bg-color-rgb), 0.5);
            margin-top: 0;
            border-top: none;
            animation: slideDown 0.3s ease-out;
        }

        @keyframes slideDown {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .price-comparison-summary {
            background-color: var(--card-bg);
            border-radius: 8px;
            padding: 12px 15px;
            margin-bottom: 15px;
            border: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-weight: 500;
        }

        .price-change-percentage {
            font-size: 0.85rem;
            padding: 3px 8px;
            border-radius: 12px;
            margin-left: 10px;
        }

        .price-increase-percentage {
            background-color: rgba(220, 53, 69, 0.1);
            color: var(--price-increase);
        }

        .price-decrease-percentage {
            background-color: rgba(40, 167, 69, 0.1);
            color: var(--price-decrease);
        }

        .details-card-title {
            display: flex;
            align-items: center;
            margin-bottom: 15px;
        }

        .details-card-title h4 {
            margin-top: 0;
            padding-bottom: 10px;
            border-bottom: 1px solid var(--border-color);
            font-size: 1.1rem;
            color: var(--primary-color);
        }

        .details-card-title .price-badge {
            margin-left: auto;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
        }

        .old-price-badge {
            background-color: rgba(220, 53, 69, 0.1);
            color: var(--price-increase);
        }

        .new-price-badge {
            background-color: rgba(40, 167, 69, 0.1);
            color: var(--price-decrease);
        }

        .diff-highlight {
            font-weight: 600;
            padding: 2px 8px;
            border-radius: 4px;
            position: relative;
        }

        .diff-highlight.increase {
            background-color: rgba(220, 53, 69, 0.15);
            color: var(--price-increase);
            border-left: 3px solid var(--price-increase);
        }

        .diff-highlight.decrease {
            background-color: rgba(40, 167, 69, 0.15);
            color: var(--price-decrease);
            border-left: 3px solid var(--price-decrease);
        }

        .diff-highlight.old {
            background-color: rgba(220, 53, 69, 0.15);
            color: var(--price-increase);
            border-left: 3px solid var(--price-increase);
        }

        .diff-highlight.new {
            background-color: rgba(40, 167, 69, 0.15);
            color: var(--price-decrease);
            border-left: 3px solid var(--price-decrease);
        }

        .diff-highlight.added {
            background-color: rgba(255, 193, 7, 0.15);
            color: #ff9800;
            border-left: 3px solid #ff9800;
        }

        .hidden {
            display: none;
        }

        .details-cards {
            display: flex;
            gap: 25px;
            margin-top: 15px;
        }

        .details-card {
            flex: 1;
            background-color: var(--card-bg);
            border-radius: 10px;
            padding: 20px;
            border: 1px solid var(--border-color);
            position: relative;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.06);
            transition: all 0.3s ease;
            overflow: hidden;
        }

        .details-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
        }

        .details-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            height: 100%;
            width: 4px;
            opacity: 0.8;
            border-radius: 0;
        }

        .details-card-old {
            border-left: none;
        }

        .details-card-new {
            border-left: none;
        }

        .details-card-old::before {
            background-color: var(--price-increase);
        }

        .details-card-new::before {
            background-color: var(--price-decrease);
        }

        .pricing-header {
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid var(--border-color);
        }

        .details-card h4 {
            margin-top: 0;
            padding-bottom: 10px;
            border-bottom: 1px solid var(--border-color);
            font-size: 1.1rem;
            color: var(--primary-color);
        }

        .bot-details-list {
            list-style: none;
            padding: 0;
            margin: 0;
        }

        .bot-details-list li {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid rgba(var(--border-color-rgb), 0.5);
        }

        /* 确保内部列表项不受父级悬停效果影响 */
        .bot-details-list li:hover {
            box-shadow: none;
            transform: none;
        }

        .bot-details-list li:last-child {
            border-bottom: none;
        }

        .detail-label {
            font-weight: 600;
            color: var(--detail-label-color);
            font-size: 0.95rem;
        }

        .detail-value {
            font-weight: 600;
            font-size: 0.95rem;
            color: var(--detail-value-color);
        }

        .toggle-details {
            margin-left: auto;
            background: none;
            border: none;
            color: var(--primary-color);
            cursor: pointer;
            padding: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            width: 32px;
            height: 32px;
            transition: all 0.2s ease;
            background-color: rgba(var(--primary-color-rgb), 0.05);
        }

        .toggle-details:hover {
            background-color: var(--button-hover);
            transform: scale(1.1);
        }

        .expand-icon {
            font-size: 14px;
            transition: transform 0.3s ease;
        }

        .toggle-details.expanded .expand-icon {
            transform: rotate(180deg);
        }

        .bot-link {
            color: var(--primary-color);
            text-decoration: none;
            font-weight: 600;
            transition: all 0.2s ease;
            border-bottom: 1px dotted transparent;
            font-size: 1.05rem;
            padding: 2px 0;
        }

        .bot-link:hover {
            text-decoration: none;
            border-bottom: 1px dotted var(--primary-color);
            color: var(--secondary-color);
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
                font-size: 2.2rem;
            }

            .timeline::after {
                left: 31px;
            }

            .timeline-item {
                width: 100%;
                padding-left: 70px;
                padding-right: 15px;
            }

            .timeline-item::after {
                left: 21px;
                width: 20px;
                height: 20px;
            }

            .timeline-content {
                padding: 20px;
            }

            .timeline-date {
                font-size: 1.2rem;
                margin-bottom: 15px;
            }

            .details-cards {
                flex-direction: column;
                gap: 15px;
            }

            .price-change-summary {
                flex-wrap: wrap;
                padding: 12px;
            }

            .price-comparison-summary {
                flex-direction: column;
                align-items: flex-start;
            }

            .price-comparison-summary div:last-child {
                margin-top: 8px;
            }

            .price-change-summary .bot-link {
                width: 100%;
                margin-bottom: 8px;
            }

            .price-change-text {
                margin: 0 0 8px 0;
                width: 100%;
            }

            .toggle-details {
                margin-left: auto;
                margin-right: 0;
            }

            .details-card-title {
                flex-direction: column;
                align-items: flex-start;
            }

            .details-card-title .price-badge {
                margin-left: 0;
                margin-top: 8px;
            }

            .details-card {
                padding: 15px;
            }

            .bot-meta {
                flex-direction: column;
                gap: 8px;
            }

            .bot-info-card {
                padding: 12px;
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
                padding-right: 10px;
            }

            .timeline-content {
                padding: 15px;
            }

            .price-change-details {
                padding: 15px;
            }

            .details-card {
                padding: 12px;
            }

            .bot-info-card {
                padding: 10px;
            }

            .timeline-date {
                font-size: 1.1rem;
                margin-bottom: 12px;
            }
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

        .bot-info-card {
            background-color: var(--card-bg);
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
            border: 1px solid var(--border-color);
            border-left: 4px solid var(--primary-color);
        }

        .bot-description {
            margin-bottom: 10px;
            line-height: 1.5;
            font-size: 0.95rem;
            color: var(--text-color);
        }

        .bot-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            font-size: 0.9rem;
            color: var(--light-text);
        }

        .bot-creator, .bot-model {
            padding: 3px 8px;
            background-color: var(--bg-color);
            border-radius: 4px;
            display: inline-block;
        }

        /* Enhanced scrolling animation */
        html {
            scroll-behavior: smooth;
        }

        /* Scrollbar styling */
        ::-webkit-scrollbar {
            width: 12px;
        }

        ::-webkit-scrollbar-track {
            background: var(--bg-color);
        }

        ::-webkit-scrollbar-thumb {
            background: var(--primary-color);
            border-radius: 6px;
            border: 3px solid var(--bg-color);
        }

        ::-webkit-scrollbar-thumb:hover {
            background: var(--secondary-color);
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
            {% for date, changes in timeline_data.items()|sort(reverse=true) %}
            <div class="timeline-item">
                <div class="timeline-content">
                    <div class="timeline-date">{{ date }}</div>
                    <ul class="timeline-changes">
                        {% if changes.new_bots %}
                        {% for bot in changes.new_bots %}
                        <li class="new-bot">
                            <div class="price-change-summary">
                                <a href="https://poe.com/{{ bot.handle }}" target="_blank" class="bot-link">{{ bot.name }}</a>
                                <span class="price-change-text">
                                    ✨ 新增机器人{% if bot.price|float > 0 %}（标准信息：{{ bot.price }} {{ bot.unit }}）{% else %}（免费）{% endif %}
                                </span>
                                <button class="toggle-details" onclick="toggleDetails(this)">
                                    <span class="expand-icon">▼</span>
                                </button>
                            </div>
                            <div class="price-change-details hidden">
                                <div class="details-cards">
                                    <div class="details-card details-card-new">
                                        <div class="details-card-title">
                                            <h4>机器人详情</h4>
                                        </div>
                                        <ul class="bot-details-list">
                                            <li>
                                                <span class="detail-label">标准消息价格:</span>
                                                <span class="detail-value">{{ bot.price or 0 }} {{ bot.unit }}/{{ bot.per }}</span>
                                            </li>
                                            {% if (bot.text_input|float or 0) > 0 %}
                                            <li>
                                                <span class="detail-label">文本输入:</span>
                                                <span class="detail-value">
                                                    {{ bot.text_input }} {{ bot.text_input_unit }}/{{ bot.text_input_per }}
                                                </span>
                                            </li>
                                            {% endif %}
                                            {% if (bot.image_input|float or 0) > 0 %}
                                            <li>
                                                <span class="detail-label">图片输入:</span>
                                                <span class="detail-value">
                                                    {{ bot.image_input }} {{ bot.image_input_unit }}/{{ bot.image_input_per }}
                                                </span>
                                            </li>
                                            {% endif %}
                                            {% if (bot.cache_input|float or 0) > 0 %}
                                            <li>
                                                <span class="detail-label">缓存输入:</span>
                                                <span class="detail-value">
                                                    {{ bot.cache_input }} {{ bot.cache_input_unit }}/{{ bot.cache_input_per }}
                                                </span>
                                            </li>
                                            {% endif %}
                                            {% if (bot.output|float or 0) > 0 %}
                                            <li>
                                                <span class="detail-label">输出:</span>
                                                <span class="detail-value">
                                                    {{ bot.output }} {{ bot.output_unit }}/{{ bot.output_per }}
                                                </span>
                                            </li>
                                            {% endif %}
                                        </ul>
                                    </div>
                                </div>
                            </div>
                        </li>
                        {% endfor %}
                        {% endif %}

                        {% if changes.price_changes %}
                        {% for change in changes.price_changes %}
                        <li class="price-change">
                            <div class="price-change-summary">
                                <a href="https://poe.com/{{ change.handle }}" target="_blank" class="bot-link">{{ change.name }}</a>
                                <span class="price-change-text">
                                    标准消息: <span class="{% if (change.old_price|float or 0) < (change.new_price|float or 0) %}price-increase{% else %}price-decrease{% endif %}">
                                        {{ change.old_price or 0 }} {{ change.old_unit }}/{{ change.old_per }} → {{ change.new_price or 0 }} {{ change.new_unit }}/{{ change.new_per }}
                                    </span>
                                </span>
                                <button class="toggle-details" onclick="toggleDetails(this)">
                                    <span class="expand-icon">▼</span>
                                </button>
                            </div>
                            <div class="price-change-details hidden">
                                <div class="details-cards">
                                    <div class="details-card details-card-old">
                                        <div class="details-card-title">
                                            <h4>之前价格</h4>
                                        </div>
                                        <ul class="bot-details-list">
                                            <li>
                                                <span class="detail-label">标准消息:</span>
                                                <span class="detail-value {% if (change.old_price|float or 0) != (change.new_price|float or 0) %}diff-highlight old{% endif %}">
                                                    {{ change.old_price or 0 }} {{ change.old_unit }}/{{ change.old_per }}
                                                </span>
                                            </li>
                                            {% if (change.old_text_input|float or 0) > 0 %}
                                            <li>
                                                <span class="detail-label">文本输入:</span>
                                                <span class="detail-value {% if (change.old_text_input|float or 0) != (change.new_text_input|float or 0) %}diff-highlight old{% endif %}">
                                                    {{ change.old_text_input }} {{ change.old_text_input_unit }}/{{ change.old_text_input_per }}
                                                </span>
                                            </li>
                                            {% endif %}
                                            {% if (change.old_image_input|float or 0) > 0 %}
                                            <li>
                                                <span class="detail-label">图片输入:</span>
                                                <span class="detail-value {% if (change.old_image_input|float or 0) != (change.new_image_input|float or 0) %}diff-highlight old{% endif %}">
                                                    {{ change.old_image_input }} {{ change.old_image_input_unit }}/{{ change.old_image_input_per }}
                                                </span>
                                            </li>
                                            {% endif %}
                                            {% if (change.old_cache_input|float or 0) > 0 %}
                                            <li>
                                                <span class="detail-label">缓存输入:</span>
                                                <span class="detail-value {% if (change.old_cache_input|float or 0) != (change.new_cache_input|float or 0) %}diff-highlight old{% endif %}">
                                                    {{ change.old_cache_input }} {{ change.old_cache_input_unit }}/{{ change.old_cache_input_per }}
                                                </span>
                                            </li>
                                            {% endif %}
                                            {% if (change.old_output|float or 0) > 0 %}
                                            <li>
                                                <span class="detail-label">输出:</span>
                                                <span class="detail-value {% if (change.old_output|float or 0) != (change.new_output|float or 0) %}diff-highlight old{% endif %}">
                                                    {{ change.old_output }} {{ change.old_output_unit }}/{{ change.old_output_per }}
                                                </span>
                                            </li>
                                            {% endif %}
                                        </ul>
                                    </div>
                                    <div class="details-card details-card-new">
                                        <div class="details-card-title">
                                            <h4>当前价格</h4>
                                        </div>
                                        <ul class="bot-details-list">
                                            <li>
                                                <span class="detail-label">标准消息:</span>
                                                <span class="detail-value {% if (change.old_price|float or 0) != (change.new_price|float or 0) %}diff-highlight new{% endif %}">
                                                    {{ change.new_price or 0 }} {{ change.new_unit }}/{{ change.new_per }}
                                                </span>
                                            </li>
                                            {% if (change.new_text_input|float or 0) > 0 %}
                                            <li>
                                                <span class="detail-label">文本输入:</span>
                                                <span class="detail-value {% if (change.old_text_input|float or 0) > 0 %}{% if (change.old_text_input|float or 0) != (change.new_text_input|float or 0) %}diff-highlight new{% endif %}{% else %}diff-highlight added{% endif %}">
                                                    {{ change.new_text_input }} {{ change.new_text_input_unit }}/{{ change.new_text_input_per }}
                                                </span>
                                            </li>
                                            {% endif %}
                                            {% if (change.new_image_input|float or 0) > 0 %}
                                            <li>
                                                <span class="detail-label">图片输入:</span>
                                                <span class="detail-value {% if (change.old_image_input|float or 0) > 0 %}{% if (change.old_image_input|float or 0) != (change.new_image_input|float or 0) %}diff-highlight new{% endif %}{% else %}diff-highlight added{% endif %}">
                                                    {{ change.new_image_input }} {{ change.new_image_input_unit }}/{{ change.new_image_input_per }}
                                                </span>
                                            </li>
                                            {% endif %}
                                            {% if (change.new_cache_input|float or 0) > 0 %}
                                            <li>
                                                <span class="detail-label">缓存输入:</span>
                                                <span class="detail-value {% if (change.old_cache_input|float or 0) > 0 %}{% if (change.old_cache_input|float or 0) != (change.new_cache_input|float or 0) %}diff-highlight new{% endif %}{% else %}diff-highlight added{% endif %}">
                                                    {{ change.new_cache_input }} {{ change.new_cache_input_unit }}/{{ change.new_cache_input_per }}
                                                </span>
                                            </li>
                                            {% endif %}
                                            {% if (change.new_output|float or 0) > 0 %}
                                            <li>
                                                <span class="detail-label">输出:</span>
                                                <span class="detail-value {% if (change.old_output|float or 0) > 0 %}{% if (change.old_output|float or 0) != (change.new_output|float or 0) %}diff-highlight new{% endif %}{% else %}diff-highlight added{% endif %}">
                                                    {{ change.new_output }} {{ change.new_output_unit }}/{{ change.new_output_per }}
                                                </span>
                                            </li>
                                            {% endif %}
                                        </ul>
                                    </div>
                                </div>
                            </div>
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
            <p>© 2025 <a href="https://github.com/Yidadaa/Poe-Bot-Crawler" target="_blank">Poe Bot Crawler</a>. 数据来源于 <a href="https://poe.com" target="_blank">Poe.com</a>.</p>
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

        // Toggle details for price changes
        function toggleDetails(button) {
            button.classList.toggle('expanded');
            const parent = button.closest('.price-change') || button.closest('.new-bot');
            const detailsSection = parent.querySelector('.price-change-details');
            detailsSection.classList.toggle('hidden');
        }
    </script>
</body>
</html>"""

def generate_timeline_data():
    """
    Generate timeline data by comparing all historical bot data files

    Returns:
        Dictionary with complete timeline data
    """
    from src.utils import JSON_DIR, load_json, CURRENT_DATE
    import re

    # Initialize timeline data
    timeline_data = {}

    # Find all bot data files
    json_files = list(JSON_DIR.glob("official_bots_with_prices_*.json"))

    if not json_files:
        logger.warning("No bot data files found")
        return None

    # Sort files by date in filename (newest first)
    pattern = re.compile(r'official_bots_with_prices_(\d{4}-\d{2}-\d{2})\.json')

    def extract_date(filepath):
        match = pattern.search(filepath.name)
        if match:
            return match.group(1)
        return ""

    json_files.sort(key=extract_date, reverse=True)

    # Get the list of dates from filenames
    dates = [extract_date(f) for f in json_files]
    dates = [d for d in dates if d]  # Remove empty strings

    if not dates:
        logger.warning("No valid date patterns found in filenames")
        return None

    # Load all data files into a dictionary keyed by date
    all_data = {}
    for file in json_files:
        date = extract_date(file)
        if date:
            try:
                all_data[date] = load_json(file)
                logger.info(f"Loaded data for {date}")
            except Exception as e:
                logger.error(f"Error loading data for {date}: {e}")

    # Process each date in chronological order (oldest to newest)
    sorted_dates = sorted(all_data.keys())

    # Skip adding the first day's bots as "new" since we have no previous day to compare with
    # This prevents incorrectly marking all bots as new on the first day
    first_date = sorted_dates[0]

    # Initialize timeline_data with empty first day to maintain chronological structure
    timeline_data[first_date] = {
        "new_bots": [],
        "price_changes": []
    }

    logger.info(f"Skipping first day ({first_date}) bot comparison as there's no previous data to compare with")

    # For each subsequent date, compare with the previous date
    for i in range(1, len(sorted_dates)):
        current_date = sorted_dates[i]
        previous_date = sorted_dates[i-1]

        current_data = all_data[current_date]
        previous_data = all_data[previous_date]

        # Find new bots and price changes
        new_bots = []
        price_changes = []

        # Create bot ID dictionaries for more precise comparison
        current_bot_ids = {}
        previous_bot_ids = {}

        # Build dictionaries with bot_ID as keys for precise tracking
        for key, bot in current_data.items():
            if "bot_ID" in bot:
                current_bot_ids[str(bot["bot_ID"])] = bot
            else:
                current_bot_ids[key] = bot

        for key, bot in previous_data.items():
            if "bot_ID" in bot:
                previous_bot_ids[str(bot["bot_ID"])] = bot
            else:
                previous_bot_ids[key] = bot

        # Find new bots (in current date but not in previous date)
        for bot_id, bot in current_bot_ids.items():
            if bot_id not in previous_bot_ids:
                price_info = get_price_info(bot)

                # Get component-specific price information
                components = ["text_input", "image_input", "cache_input", "output", "standard_message"]
                component_price_info = {}

                for component in components:
                    component_info = get_component_price_info(bot, component)
                    component_price_info[component] = component_info["value"]
                    component_price_info[f"{component}_unit"] = component_info["unit"]
                    component_price_info[f"{component}_per"] = component_info["per"]

                new_bot_data = {
                    "id": bot.get("bot_ID", ""),
                    "handle": bot.get("handle", ""),
                    "name": bot.get("display_name", "Unknown Bot"),
                    "price": price_info["value"],
                    "unit": price_info["unit"],
                    "per": price_info["per"]
                }

                # Add component-specific price information
                new_bot_data.update(component_price_info)

                new_bots.append(new_bot_data)
                logger.info(f"New bot on {current_date}: {bot.get('handle', 'Unknown')}")

        # Check price changes for existing bots
        for bot_id in set(current_bot_ids.keys()) & set(previous_bot_ids.keys()):
            current_bot = current_bot_ids[bot_id]
            previous_bot = previous_bot_ids[bot_id]

            current_price_info = get_price_info(current_bot)
            previous_price_info = get_price_info(previous_bot)

            current_price = current_price_info["value"]
            previous_price = previous_price_info["value"]

            # If price or pricing terms changed
            if (current_price != previous_price or
                current_price_info["unit"] != previous_price_info["unit"] or
                current_price_info["per"] != previous_price_info["per"]):

                # Get component-specific price information
                components = ["text_input", "image_input", "cache_input", "output", "standard_message"]
                component_price_info = {}

                for component in components:
                    current_component = get_component_price_info(current_bot, component)
                    previous_component = get_component_price_info(previous_bot, component)

                    component_price_info[f"new_{component}"] = current_component["value"]
                    component_price_info[f"new_{component}_unit"] = current_component["unit"]
                    component_price_info[f"new_{component}_per"] = current_component["per"]

                    component_price_info[f"old_{component}"] = previous_component["value"]
                    component_price_info[f"old_{component}_unit"] = previous_component["unit"]
                    component_price_info[f"old_{component}_per"] = previous_component["per"]

                price_changes.append({
                    "id": current_bot.get("bot_ID", ""),
                    "handle": current_bot.get("handle", ""),
                    "name": current_bot.get("display_name", "Unknown Bot"),
                    "old_price": previous_price_info["value"],
                    "old_unit": previous_price_info["unit"],
                    "old_per": previous_price_info["per"],
                    "new_price": current_price_info["value"],
                    "new_unit": current_price_info["unit"],
                    "new_per": current_price_info["per"],
                    **component_price_info
                })
                logger.info(f"Price change on {current_date}: {current_bot.get('handle', 'Unknown')}")

        # Add to timeline data if there are changes
        if new_bots or price_changes:
            timeline_data[current_date] = {
                "new_bots": new_bots,
                "price_changes": price_changes
            }

    # Save the timeline data
    timeline_file = JSON_DIR / "timeline_data.json"
    with open(timeline_file, 'w', encoding='utf-8') as f:
        json.dump(timeline_data, f, indent=2, ensure_ascii=False)

    logger.info(f"Generated complete timeline data with {len(timeline_data)-1} days of actual comparison data (skipping first day)")

    # Also save a dated copy for history
    dated_filename = f"timeline_data_{CURRENT_DATE}.json"
    dated_file = JSON_DIR / dated_filename
    with open(dated_file, 'w', encoding='utf-8') as f:
        json.dump(timeline_data, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved dated timeline data to {dated_file}")

    return timeline_data

def get_price_info(bot):
    """Get price value, unit and per information from bot data"""
    try:
        # Default values - 使用完整的字符串作为默认值
        price_info = {"value": 0, "unit": "积分", "per": "1k Tokens"}

        # Try direct price field
        if "price" in bot and isinstance(bot["price"], (int, float)):
            price_info["value"] = bot["price"]

        # Try points_price structure
        elif "points_price" in bot and isinstance(bot["points_price"], dict):
            # Try standard_message
            if "standard_message" in bot["points_price"]:
                standard_msg = bot["points_price"]["standard_message"]
                if isinstance(standard_msg, dict):
                    if "value" in standard_msg:
                        price_info["value"] = standard_msg["value"]
                    if "unit" in standard_msg:
                        # 翻译单位
                        if standard_msg["unit"] == "points":
                            price_info["unit"] = "积分"
                        else:
                            price_info["unit"] = standard_msg["unit"] or "积分"
                    if "per" in standard_msg:
                        if isinstance(standard_msg["per"], dict) and "unit" in standard_msg["per"]:
                            if standard_msg["per"]["unit"]:
                                # 尝试翻译单位单位
                                per_unit = standard_msg["per"]["unit"]
                                if per_unit.lower() == "tokens":
                                    per_unit = "Tokens"
                                elif per_unit.lower() == "message":
                                    per_unit = "信息"
                                price_info["per"] = f"{standard_msg['per'].get('value', '1k')} {per_unit}"
                        elif standard_msg["per"]:
                            # 尝试翻译单位单位
                            per_info = standard_msg["per"]
                            if per_info.lower() == "message":
                                price_info["per"] = "信息"
                            elif "tokens" in per_info.lower():
                                price_info["per"] = per_info.replace("tokens", "Tokens")
                            else:
                                price_info["per"] = per_info

            # If pricing_type exists with non_subscriber field
            elif "pricing_type" in bot["points_price"] and "non_subscriber" in bot["points_price"]:
                text_output = bot["points_price"]["non_subscriber"].get("text_output", {})
                if isinstance(text_output, dict):
                    if "value" in text_output:
                        price_info["value"] = text_output["value"]
                    if "unit" in text_output:
                        # 翻译单位
                        if text_output["unit"] == "points":
                            price_info["unit"] = "积分"
                        else:
                            price_info["unit"] = text_output["unit"] or "积分"
                    if "per" in text_output:
                        if isinstance(text_output["per"], dict) and "unit" in text_output["per"]:
                            if text_output["per"]["unit"]:
                                # 尝试翻译单位单位
                                per_unit = text_output["per"]["unit"]
                                if per_unit.lower() == "tokens":
                                    per_unit = "Tokens"
                                elif per_unit.lower() == "message":
                                    per_unit = "信息"
                                price_info["per"] = f"{text_output['per'].get('value', '1k')} {per_unit}"
                        elif text_output["per"]:
                            # 尝试翻译单位单位
                            per_info = text_output["per"]
                            if per_info.lower() == "message":
                                price_info["per"] = "信息"
                            elif "tokens" in per_info.lower():
                                price_info["per"] = per_info.replace("tokens", "Tokens")
                            else:
                                price_info["per"] = per_info

        # 确保单位和单位单位有值
        if not price_info["unit"]:
            price_info["unit"] = "积分"
        if not price_info["per"]:
            price_info["per"] = "1k Tokens"

        return price_info
    except Exception as e:
        logger.warning(f"Error getting price info: {e}")
        return {"value": 0, "unit": "积分", "per": "1k Tokens"}

def get_component_price_info(bot, component_name):
    """Get price information for a specific component"""
    try:
        # Default values
        price_info = {"value": 0, "unit": "积分", "per": "1k Tokens"}

        # If standard_message is requested and no points_price, use the bot price
        if component_name == "standard_message" and ("points_price" not in bot or "standard_message" not in bot.get("points_price", {})):
            return get_price_info(bot)

        # Try points_price structure
        if "points_price" in bot and isinstance(bot["points_price"], dict):
            component = None

            # Direct component
            if component_name in bot["points_price"]:
                component = bot["points_price"][component_name]

            # Try inputs array for input components
            elif "inputs" in bot["points_price"] and component_name.endswith("_input"):
                input_type = component_name.replace("_input", "")
                for input_item in bot["points_price"]["inputs"]:
                    if input_item.get("type") == input_type:
                        component = input_item
                        break

            # If component found, extract values
            if component and isinstance(component, dict):
                if "value" in component:
                    price_info["value"] = component["value"]
                if "unit" in component:
                    # 翻译单位
                    if component["unit"] == "points":
                        price_info["unit"] = "积分"
                    else:
                        price_info["unit"] = component["unit"] or "积分"
                if "per" in component:
                    if isinstance(component["per"], dict) and "unit" in component["per"]:
                        if component["per"].get("unit"):
                            # 尝试翻译单位单位
                            per_unit = component["per"]["unit"]
                            if per_unit.lower() == "tokens":
                                per_unit = "Tokens"
                            elif per_unit.lower() == "message":
                                per_unit = "信息"
                            price_info["per"] = f"{component['per'].get('value', '1k')} {per_unit}"
                    elif component["per"]:
                        # 尝试翻译单位单位
                        per_info = component["per"]
                        if per_info.lower() == "message":
                            price_info["per"] = "信息"
                        elif "tokens" in per_info.lower():
                            price_info["per"] = per_info.replace("tokens", "Tokens")
                        else:
                            price_info["per"] = per_info

        # 确保单位和单位单位有值
        if not price_info["unit"]:
            price_info["unit"] = "积分"
        if not price_info["per"]:
            price_info["per"] = "1k Tokens"

        return price_info
    except Exception as e:
        logger.warning(f"Error getting component price info: {e}")
        return {"value": 0, "unit": "积分", "per": "1k Tokens"}

def get_bot_price_component(bot, component_name):
    """Extract specific pricing component from bot data"""
    try:
        # Try points_price structure
        if "points_price" in bot:
            if isinstance(bot["points_price"], dict):
                # Direct component in points_price
                if component_name in bot["points_price"]:
                    value = bot["points_price"][component_name].get("value", 0)
                    if isinstance(value, (int, float, str)):
                        try:
                            return float(value)
                        except (ValueError, TypeError):
                            return 0

                # Special case for "standard_message" which is what most bots use
                if component_name == "standard_message" and "standard_message" in bot["points_price"]:
                    value = bot["points_price"]["standard_message"].get("value", 0)
                    if isinstance(value, (int, float, str)):
                        try:
                            return float(value)
                        except (ValueError, TypeError):
                            return 0

                # Special case for input/output components
                if "input_" in component_name and "inputs" in bot["points_price"]:
                    input_type = component_name.replace("input_", "")
                    for input_item in bot["points_price"]["inputs"]:
                        if input_item.get("type") == input_type:
                            value = input_item.get("value", 0)
                            if isinstance(value, (int, float, str)):
                                try:
                                    return float(value)
                                except (ValueError, TypeError):
                                    return 0

        # If we get here, use standard price if this is standard_message
        if component_name == "standard_message":
            return get_bot_price(bot)

        # Default value for any component
        return 0
    except Exception:
        # Return 0 instead of None
        return 0

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

def get_bot_model(bot):
    """Extract the model information from bot data"""
    try:
        if "model" in bot:
            return bot["model"]
        elif "settings" in bot and "model" in bot["settings"]:
            return bot["settings"]["model"]
        return "Unknown"
    except Exception:
        return "Unknown"

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
    if timeline_data is None or not timeline_data:
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
        timeline_data=timeline_data,  # 传递完整的时间线数据
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

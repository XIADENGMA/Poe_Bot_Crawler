# Poe Bot Crawler

A tool for crawling and collecting data about AI bots on the Poe platform, including their details and credit pricing information.

[中文文档](README_CN.md)

## TODO

- [ ] Add various bot price parsing (image generation, video generation, etc.)

## Features

1. Retrieves the official bot list from Poe and saves it in JSON format
2. Collects detailed information for each bot
3. Parses credit pricing information
4. Generates an HTML dashboard to visualize the results
5. Creates timeline visualizations to track changes in bot pricing and availability
6. Supports automated daily updates via GitHub Actions
7. Automatically archives HTML files to a history directory
8. Maintains the most recent HTML files as index.html and timeline.html
9. Performs data management by cleaning up files older than 7 days

## Requirements

- Python 3.10 or higher
- `uv` package manager (recommended) or pip

## Installation

This project uses `uv` for package management:

```bash
# Create a virtual environment
uv venv

# Activate the virtual environment
source .venv/bin/activate  # Linux/macOS
# or
# .venv\Scripts\activate  # Windows

# Install dependencies
uv pip install -e .
```

## Configuration

1. Create a `.env` file in the project root with the following content:

```
P_B=your_p-b_cookie
P_LAT=your_p-lat_cookie
```

> **Note**: You need to get these cookies from your Poe account by logging in through a web browser and examining the cookies.

## Usage

### Complete Workflow

A typical workflow for this project consists of three main steps:

1. **Data Crawling**: Run the main crawler to fetch bot data from Poe
2. **HTML Generation**: The crawler automatically generates HTML dashboards
3. **Maintenance**: Run maintenance tasks to manage files and keep the dashboards updated

#### Step 1: Run the crawler

```bash
# Run the crawler script directly
python src/main.py
```

This will:

- Fetch the official bot list from Poe
- Collect detailed information for each bot
- Parse pricing information
- Generate HTML dashboards in the `output/result/history/` directory
- Create timeline visualization for tracking changes in bots and pricing
- Copy the dashboards to `output/result/index.html` and `output/result/timeline.html`
- Clean up files older than 7 days
- Output file paths for the generated files

#### Step 2: View the results

Navigate to the output directory and open the HTML files in your browser:

```bash
# Linux/macOS
open output/result/index.html
open output/result/timeline.html

# Windows
start output/result/index.html
start output/result/timeline.html
```

Alternatively, you can directly open the files in your preferred web browser.

#### Step 3: Manual maintenance (if needed)

If you need to update the index.html file or clean up old files manually:

```bash
# Run all maintenance tasks
python src/maintenance.py

# Or run specific tasks
python src/maintenance.py --update-index
python src/maintenance.py --clean-old-files
python src/maintenance.py --clean-old-files --days 14
```

### View the results

- Bot list is saved in the `output/json/` directory
- Bot details are saved in the `output/bots/` directory
- HTML dashboard is saved in the `output/result/history/` directory
- Timeline visualization is saved in the `output/result/timeline/` directory
- Most recent HTML dashboard is available as `output/result/index.html`
- Most recent timeline visualization is available as `output/result/timeline.html`

## Automated Updates

This project includes a GitHub Actions workflow that automatically runs the crawler daily at 4:00 AM UTC. The workflow:

1. Sets up the Python environment
2. Installs dependencies
3. Runs the crawler with your stored credentials
4. Commits and pushes any changes to the repository
5. Uploads build artifacts for each run, which can be downloaded from the GitHub Actions interface

To set up automated updates:

1. Push this repository to GitHub
2. Go to your repository settings → Secrets and variables → Actions
3. Add the following repository secrets:
   - `P_B`: Your Poe p-b cookie value
   - `P_LAT`: Your Poe p-lat cookie value

The GitHub Actions workflow will use these secrets to authenticate with Poe and run the crawler without exposing your credentials. Each workflow run will also produce downloadable artifacts containing the output files and logs, which are retained for 30 days.

## Project Structure

```
Poe_crawler/
├── README.md             # Project documentation
├── README_CN.md          # Project documentation (Chinese)
├── pyproject.toml        # Project configuration and dependencies
├── .env                  # Environment variables (not in version control)
├── src/                  # Source code directory
│   ├── __init__.py       # Package initialization file
│   ├── main.py           # Main program entry point
│   ├── bot_list.py       # Functions to retrieve bot list
│   ├── bot_details.py    # Functions to get bot details
│   ├── bot_info_generator.py # Functions to generate HTML dashboard
│   ├── timeline_generator.py # Functions to generate timeline visualization
│   ├── maintenance.py    # Maintenance utilities
│   └── utils.py          # Utility functions
└── output/               # Output directory
    ├── json/             # JSON files with bot lists
    ├── bots/             # JSON files with bot details
    └── result/           # Generated HTML dashboards
        ├── index.html    # Most recent HTML dashboard
        ├── timeline.html # Most recent timeline visualization
        ├── timeline/     # Archive of historical timeline files
        └── history/      # Archive of historical HTML files
```

## Development

Install development dependencies:

```bash
uv pip install -e ".[dev]"
```

Code formatting and checking:

```bash
# Format code
black src/

# Sort imports
isort src/

# Type checking
mypy src/
```

## Logs

Logs are saved in the `logs/` directory with timestamps, providing detailed information about the crawler's execution.

## Output Files

The crawler generates several output files:

1. `output/json/official_bots_list_YYYY-MM-DD.json` - Initial bot list
2. `output/json/official_bots_with_prices_YYYY-MM-DD.json` - Bot list with pricing details
3. `output/result/history/bots_YYYY-MM-DD.html` - HTML dashboard displaying all bots with their details
4. `output/result/timeline/timeline_YYYY-MM-DD.html` - Timeline visualization showing changes in bots and pricing
5. `output/result/index.html` - Copy of the most recent HTML dashboard
6. `output/result/timeline.html` - Copy of the most recent timeline visualization

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Data Management

The crawler automatically manages historical data:

1. HTML files are saved to `output/result/history/` directory
2. Timeline files are saved to `output/result/timeline/` directory
3. The most recent HTML file is copied to `output/result/index.html`
4. The most recent timeline file is copied to `output/result/timeline.html`
5. Files older than 7 days are automatically cleaned up from:
   - `output/json/`
   - `output/result/history/`
   - `output/result/timeline/`
   - `output/bots/`
   - `logs/`

You can manually manage data using the maintenance script:

```bash
python src/maintenance.py
```

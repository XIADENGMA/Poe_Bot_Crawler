# Poe Bot Crawler

A tool for crawling and collecting data about AI bots on the Poe platform, including their details and credit pricing information.

[中文文档](README_CN.md)

## Features

1. Retrieves the official bot list from Poe and saves it in JSON format
2. Collects detailed information for each bot
3. Parses credit pricing information
4. Generates an HTML dashboard to visualize the results
5. Supports automated daily updates via GitHub Actions

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

1. Run the main program:

```bash
# If installed as a package
poe-crawler

# Or run the script directly
python src/main.py
```

2. View the results:

   - Bot list is saved in the `output/json/` directory
   - Bot details are saved in the `output/bots/` directory
   - HTML dashboard is saved in the `output/result/` directory

3. View the HTML dashboard in a browser:

```bash
# If installed as a package
view-html

# Or run the script directly
python view_html.py
```

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
├── pyproject.toml        # Project configuration and dependencies
├── .env                  # Environment variables (not in version control)
├── src/                  # Source code directory
│   ├── __init__.py       # Package initialization file
│   ├── main.py           # Main program entry point
│   ├── bot_list.py       # Functions to retrieve bot list
│   ├── bot_details.py    # Functions to get bot details
│   ├── html_generator.py # Functions to generate HTML dashboard
│   └── utils.py          # Utility functions
├── beautify_html.py      # Script to beautify HTML output
├── view_html.py          # Script to view results in browser
└── output/               # Output directory
    ├── json/             # JSON files with bot lists
    ├── bots/             # JSON files with bot details
    └── result/           # Generated HTML dashboards
```

## Development

Install development dependencies:

```bash
uv pip install -e ".[dev]"
```

Code formatting and checking:

```bash
# Format code
black src/ view_html.py

# Sort imports
isort src/ view_html.py

# Type checking
mypy src/ view_html.py
```

## Logs

Logs are saved in the `logs/` directory with timestamps, providing detailed information about the crawler's execution.

## Output Files

The crawler generates several output files:

1. `output/json/official_bots_list_YYYY-MM-DD.json` - Initial bot list
2. `output/json/official_bots_with_prices_YYYY-MM-DD.json` - Bot list with pricing details
3. `output/result/bots_YYYY-MM-DD.html` - HTML dashboard displaying all bots with their details

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

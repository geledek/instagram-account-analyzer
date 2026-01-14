# Instagram Account Analyzer

Download and analyze public Instagram accounts. Generate analytics reports and visual posters with engagement metrics, posting patterns, and content insights.

## Features

- **Download** images and metadata from public Instagram profiles
- **Analyze** engagement metrics, posting patterns, and content themes
- **Generate** visual analytics posters with key insights
- **Export** data as JSON for further analysis

## Installation

Requires Python 3.10+ and [uv](https://github.com/astral-sh/uv) package manager.

```bash
# Clone the repository
git clone https://github.com/geledek/instagram-account-analyzer.git
cd instagram-account-analyzer

# Install dependencies
uv sync
```

## Quick Start

```bash
# Download posts from a public account
uv run python download_profile.py USERNAME --max 50

# Generate analysis and poster
uv run python instagram_analyzer.py -m downloads/metadata.json --poster --account USERNAME

# Generate premium poster (enhanced design)
uv run python poster_designer.py -m downloads/metadata.json --account USERNAME
```

## Usage

### Download Profile

```bash
uv run python download_profile.py USERNAME [OPTIONS]

Options:
  --max, -m INT       Maximum posts to download (default: all)
  --output, -o DIR    Output directory (default: downloads)
  --login, -l USER    Your Instagram username for authenticated access
```

### Analyze & Generate Poster

```bash
uv run python instagram_analyzer.py [OPTIONS]

Options:
  --from-metadata, -m FILE    Load from metadata.json
  --poster, -p                Generate visual poster
  --account, -n NAME          Account name for poster header
  --output, -o DIR            Output directory
```

### Premium Poster Designer

```bash
uv run python poster_designer.py [OPTIONS]

Options:
  --metadata, -m FILE    Path to metadata.json
  --account, -n NAME     Account name
  --output, -o DIR       Output directory
```

## Output Structure

```
output/
└── YYYY-MM-DD_username/
    ├── metadata.json           # Post data (likes, comments, captions, timestamps)
    ├── analytics_report.json   # Computed metrics
    ├── analytics_charts.png    # Statistical charts
    ├── analytics_poster.png    # Visual poster
    ├── analytics_poster_v2.png # Premium poster design
    └── *.jpg                   # Downloaded images
```

## Analytics Insights

The analyzer provides:

- **Engagement Metrics**: Total/average likes and comments
- **Posting Patterns**: Activity by day of week and time
- **Content Analysis**: Caption length, hashtag usage
- **Account Profile**: Auto-detected themes and content type
- **Top Posts**: Highest performing content

## Rate Limiting

Instagram may rate-limit requests. To avoid issues:

```bash
# Login once to save session (recommended)
uv run instaloader --login YOUR_USERNAME

# Use saved session for downloads
uv run python download_profile.py USERNAME --login YOUR_USERNAME
```

## Project Structure

```
├── download_profile.py     # Instagram downloader using instaloader
├── instagram_analyzer.py   # Analysis and basic poster generation
├── poster_designer.py      # Premium poster design
├── pyproject.toml          # Dependencies
├── CLAUDE.md               # AI assistant context
└── output/                 # Generated reports (gitignored)
```

## License

MIT License - See [LICENSE](LICENSE) for details.

## Disclaimer

This tool is for educational purposes only. Respect Instagram's Terms of Service and rate limits. Only use on public accounts with proper authorization.

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Objective

Analyze public Instagram accounts by downloading images with metadata and generating visual analytics reports.

## Architecture

```
├── download_profile.py     # Downloads posts using instaloader
├── instagram_analyzer.py   # Analyzes data and generates basic poster
├── poster_designer.py      # Generates premium visual poster
└── output/                 # Timestamped output folders
    └── YYYY-MM-DD_username/
        ├── metadata.json
        ├── analytics_report.json
        ├── analytics_poster.png
        ├── analytics_poster_v2.png
        └── *.jpg
```

## Commands

```bash
# Install dependencies
uv sync

# Download posts (auto-creates output/YYYY-MM-DD_username/)
uv run python download_profile.py USERNAME --max 50

# Run analysis and generate poster
uv run python instagram_analyzer.py -m output/YYYY-MM-DD_username/metadata.json --poster --account USERNAME

# Generate premium poster
uv run python poster_designer.py -m output/YYYY-MM-DD_username/metadata.json --account USERNAME

# Login to avoid rate limits (recommended)
uv run instaloader --login YOUR_USERNAME
uv run python download_profile.py USERNAME --login YOUR_USERNAME --max 50
```

## Key Technical Details

- Uses `instaloader` library for Instagram API access
- Outputs organized in timestamped folders: `output/YYYY-MM-DD_username/`
- Poster designer uses matplotlib with custom dark theme
- Account content analysis detects themes from captions

## Rate Limiting

- Instagram rate-limits unauthenticated requests
- Login with `--login` flag to avoid 403 errors
- Add delays between large downloads

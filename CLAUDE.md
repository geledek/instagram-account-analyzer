# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Objective

Analyze a public Instagram account (https://www.instagram.com/thedankoe/) by downloading all images with metadata and generating insights.

## Technical Context

Instagram employs anti-bot measures and serves dynamic HTML content, making traditional scraping difficult. This project uses browser developer tools to intercept API calls, extract data, and perform analytics.

## Approach

1. **API Interception**: Use browser Network tab to capture Instagram's internal GraphQL API requests when scrolling through the profile
2. **URL Extraction**: Parse API responses to compile image URLs and metadata (timestamps, captions, engagement data)
3. **Automated Download**: Download all images with their associated metadata to a local directory
4. **Analyze**: Generate insights and reports from the collected data

## Expected Outcome

- All photos downloaded with metadata (timestamps, captions, likes/comments if available)
- Analytics report with insights

## Analytics Insights

- **Posting Patterns**: Days/times of posts, posting frequency trends over time
- **Engagement Metrics**: Likes, comments per post (if accessible from API)
- **Content Analysis**: Image types, dimensions, color schemes
- **Caption Analysis**: Word frequency, hashtag usage, caption length trends
- **Growth Trends**: How engagement changes over time
- **Visual Themes**: Dominant colors, branding consistency

## Key Technical Details

- Instagram's GraphQL endpoint: `https://www.instagram.com/graphql/query/`
- Image URLs are in the `display_url` field within edge nodes
- Metadata includes `taken_at_timestamp`, `edge_media_to_caption`, `edge_liked_by`, `edge_media_to_comment`
- Pagination uses `end_cursor` for loading more posts
- Requests require session cookies and appropriate headers

## Commands

```bash
# Install dependencies
uv sync

# Option 1: Download using instaloader (recommended)
uv run python download_profile.py thedankoe              # Download all posts
uv run python download_profile.py thedankoe --max 50    # Limit to 50 posts
uv run python download_profile.py thedankoe --login YOUR_USERNAME  # With login

# Option 2: Manual API capture (browser dev tools)
uv run python instagram_analyzer.py response.json

# Run analysis on downloaded data
uv run python instagram_analyzer.py --from-metadata downloads/metadata.json

# Generate visual poster with metrics and images
uv run python instagram_analyzer.py -m downloads/metadata.json --poster --account thedankoe

# Login to Instagram (saves session for future use - avoids rate limits)
uv run instaloader --login YOUR_USERNAME
```

## Rate Limiting Considerations

- Add delays between requests (1-3 seconds recommended)
- Respect Instagram's robots.txt and terms of service
- This is for educational purposes on a public account only

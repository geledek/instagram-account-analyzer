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

## Rate Limiting Considerations

- Add delays between requests (1-3 seconds recommended)
- Respect Instagram's robots.txt and terms of service
- This is for educational purposes on a public account only

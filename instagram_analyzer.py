"""
Instagram Account Analyzer

Four-step process:
1. API Interception - Manual capture via browser dev tools
2. URL Extraction - Parse API responses for image URLs and metadata
3. Automated Download - Download images with metadata
4. Analyze - Generate insights from collected data
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from collections import Counter

import requests
from PIL import Image
import pandas as pd
import matplotlib.pyplot as plt


class InstagramAnalyzer:
    def __init__(self, download_dir="downloads"):
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)
        self.posts_data = []

    # Step 2: URL Extraction
    def extract_from_response(self, json_file_path):
        """Extract image URLs and metadata from saved API response JSON."""
        with open(json_file_path, 'r') as f:
            data = json.load(f)

        edges = self._find_edges(data)

        for edge in edges:
            node = edge.get('node', {})
            post = {
                'id': node.get('id'),
                'shortcode': node.get('shortcode'),
                'display_url': node.get('display_url'),
                'timestamp': node.get('taken_at_timestamp'),
                'likes': node.get('edge_liked_by', {}).get('count', 0),
                'comments': node.get('edge_media_to_comment', {}).get('count', 0),
                'caption': self._extract_caption(node),
                'is_video': node.get('is_video', False),
                'dimensions': node.get('dimensions', {}),
            }
            if post['display_url'] and not post['is_video']:
                self.posts_data.append(post)

        print(f"Extracted {len(self.posts_data)} image posts")
        return self.posts_data

    def _find_edges(self, data):
        """Recursively find edge arrays in the JSON response."""
        if isinstance(data, dict):
            if 'edges' in data:
                return data['edges']
            for value in data.values():
                result = self._find_edges(value)
                if result:
                    return result
        elif isinstance(data, list):
            for item in data:
                result = self._find_edges(item)
                if result:
                    return result
        return []

    def _extract_caption(self, node):
        """Extract caption text from post node."""
        edges = node.get('edge_media_to_caption', {}).get('edges', [])
        if edges:
            return edges[0].get('node', {}).get('text', '')
        return ''

    # Step 3: Automated Download
    def download_images(self, delay=1.5):
        """Download all extracted images with metadata."""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

        for i, post in enumerate(self.posts_data):
            url = post['display_url']
            filename = f"{post['shortcode']}.jpg"
            filepath = self.download_dir / filename

            if filepath.exists():
                print(f"[{i+1}/{len(self.posts_data)}] Skipping {filename} (exists)")
                continue

            try:
                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()

                with open(filepath, 'wb') as f:
                    f.write(response.content)

                print(f"[{i+1}/{len(self.posts_data)}] Downloaded {filename}")
                time.sleep(delay)

            except Exception as e:
                print(f"[{i+1}/{len(self.posts_data)}] Failed {filename}: {e}")

        # Save metadata
        self._save_metadata()

    def _save_metadata(self):
        """Save posts metadata to JSON file."""
        metadata_file = self.download_dir / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(self.posts_data, f, indent=2)
        print(f"Metadata saved to {metadata_file}")

    # Step 4: Analyze
    def analyze(self):
        """Generate analytics report from collected data."""
        if not self.posts_data:
            print("No data to analyze. Run extract_from_response first.")
            return

        df = pd.DataFrame(self.posts_data)
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
        df['day_of_week'] = df['datetime'].dt.day_name()
        df['hour'] = df['datetime'].dt.hour
        df['month'] = df['datetime'].dt.to_period('M')

        report = {
            'total_posts': len(df),
            'date_range': {
                'first_post': df['datetime'].min().isoformat(),
                'last_post': df['datetime'].max().isoformat(),
            },
            'engagement': {
                'total_likes': int(df['likes'].sum()),
                'total_comments': int(df['comments'].sum()),
                'avg_likes': float(df['likes'].mean()),
                'avg_comments': float(df['comments'].mean()),
                'top_post_likes': int(df['likes'].max()),
            },
            'posting_patterns': {
                'posts_by_day': df['day_of_week'].value_counts().to_dict(),
                'most_active_day': df['day_of_week'].value_counts().idxmax(),
                'posts_by_hour': df['hour'].value_counts().sort_index().to_dict(),
            },
            'captions': {
                'avg_length': float(df['caption'].str.len().mean()),
                'hashtag_count': int(df['caption'].str.count('#').sum()),
            }
        }

        # Save report
        report_file = self.download_dir / "analytics_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        self._print_report(report)
        self._generate_charts(df)

        return report

    def _print_report(self, report):
        """Print analytics report to console."""
        print("\n" + "="*50)
        print("INSTAGRAM ANALYTICS REPORT")
        print("="*50)
        print(f"\nTotal Posts: {report['total_posts']}")
        print(f"Date Range: {report['date_range']['first_post'][:10]} to {report['date_range']['last_post'][:10]}")
        print(f"\nEngagement:")
        print(f"  Total Likes: {report['engagement']['total_likes']:,}")
        print(f"  Total Comments: {report['engagement']['total_comments']:,}")
        print(f"  Avg Likes/Post: {report['engagement']['avg_likes']:.1f}")
        print(f"  Avg Comments/Post: {report['engagement']['avg_comments']:.1f}")
        print(f"\nPosting Patterns:")
        print(f"  Most Active Day: {report['posting_patterns']['most_active_day']}")
        print(f"\nCaptions:")
        print(f"  Avg Length: {report['captions']['avg_length']:.0f} chars")
        print(f"  Total Hashtags: {report['captions']['hashtag_count']}")
        print("="*50 + "\n")

    def _generate_charts(self, df):
        """Generate visualization charts."""
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))

        # Posts by day of week
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_counts = df['day_of_week'].value_counts().reindex(day_order, fill_value=0)
        axes[0, 0].bar(day_counts.index, day_counts.values, color='steelblue')
        axes[0, 0].set_title('Posts by Day of Week')
        axes[0, 0].tick_params(axis='x', rotation=45)

        # Posts by hour
        hour_counts = df['hour'].value_counts().sort_index()
        axes[0, 1].bar(hour_counts.index, hour_counts.values, color='coral')
        axes[0, 1].set_title('Posts by Hour of Day')
        axes[0, 1].set_xlabel('Hour')

        # Engagement over time
        monthly = df.groupby('month')['likes'].mean()
        axes[1, 0].plot(monthly.index.astype(str), monthly.values, marker='o', color='green')
        axes[1, 0].set_title('Average Likes Over Time')
        axes[1, 0].tick_params(axis='x', rotation=45)

        # Likes distribution
        axes[1, 1].hist(df['likes'], bins=20, color='purple', alpha=0.7)
        axes[1, 1].set_title('Likes Distribution')
        axes[1, 1].set_xlabel('Likes')

        plt.tight_layout()
        chart_file = self.download_dir / "analytics_charts.png"
        plt.savefig(chart_file, dpi=150)
        plt.close()
        print(f"Charts saved to {chart_file}")


def main():
    """
    Usage:
    1. Open Instagram profile in browser
    2. Open Developer Tools (F12) > Network tab
    3. Scroll through the profile to trigger API calls
    4. Find requests to graphql/query and save response as JSON
    5. Run this script with the JSON file path
    """
    import sys

    if len(sys.argv) < 2:
        print("Usage: python instagram_analyzer.py <response.json>")
        print("\nSee CLAUDE.md for instructions on capturing API responses.")
        sys.exit(1)

    json_file = sys.argv[1]

    analyzer = InstagramAnalyzer()
    analyzer.extract_from_response(json_file)
    analyzer.download_images()
    analyzer.analyze()


if __name__ == "__main__":
    main()

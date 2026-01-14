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
import glob

import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import numpy as np


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

    def generate_poster(self, account_name="Instagram Account", profile_info=None):
        """Generate a visual poster with key metrics and images from the account."""
        if not self.posts_data:
            print("No data for poster. Run analysis first.")
            return

        df = pd.DataFrame(self.posts_data)
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')

        # Find images in download directory
        image_files = self._find_post_images()

        # Generate account insights from content analysis
        account_insights = self._analyze_account_content(df)

        # Create figure with custom layout (increased height for new section)
        fig = plt.figure(figsize=(16, 24), facecolor='#1a1a2e')

        # Define grid layout (6 rows now)
        gs = fig.add_gridspec(6, 4, hspace=0.25, wspace=0.2,
                              left=0.05, right=0.95, top=0.96, bottom=0.04,
                              height_ratios=[0.8, 1.2, 1.2, 1.5, 1.5, 1.2])

        # === HEADER SECTION ===
        ax_header = fig.add_subplot(gs[0, :])
        ax_header.set_facecolor('#1a1a2e')
        ax_header.axis('off')

        # Account name
        ax_header.text(0.5, 0.75, f"@{account_name}", fontsize=42, fontweight='bold',
                       color='white', ha='center', va='center',
                       transform=ax_header.transAxes)
        ax_header.text(0.5, 0.25, "Instagram Analytics Report", fontsize=16,
                       color='#888888', ha='center', va='center',
                       transform=ax_header.transAxes)

        # === ACCOUNT INSIGHTS DESCRIPTION ===
        ax_desc = fig.add_subplot(gs[1, :])
        ax_desc.set_facecolor('#1a1a2e')
        ax_desc.axis('off')

        # Add insight box
        rect = mpatches.FancyBboxPatch((0.02, 0.1), 0.96, 0.8,
                                        boxstyle="round,pad=0.02,rounding_size=0.02",
                                        facecolor='#16213e', edgecolor='#e94560',
                                        linewidth=2, transform=ax_desc.transAxes)
        ax_desc.add_patch(rect)

        ax_desc.text(0.5, 0.85, "ACCOUNT PROFILE", fontsize=14, fontweight='bold',
                     color='#e94560', ha='center', va='center',
                     transform=ax_desc.transAxes)
        ax_desc.text(0.5, 0.45, account_insights, fontsize=12, color='white',
                     ha='center', va='center', transform=ax_desc.transAxes,
                     wrap=True, linespacing=1.5)

        # === KEY METRICS SECTION ===
        metrics = [
            ("Total Posts", f"{len(df):,}", "#e94560"),
            ("Total Likes", f"{df['likes'].sum():,}", "#0f3460"),
            ("Avg Likes", f"{df['likes'].mean():,.0f}", "#16213e"),
            ("Total Comments", f"{df['comments'].sum():,}", "#533483"),
        ]

        for i, (label, value, color) in enumerate(metrics):
            ax = fig.add_subplot(gs[2, i])
            ax.set_facecolor(color)
            ax.axis('off')

            # Add rounded rectangle effect
            rect = mpatches.FancyBboxPatch((0.05, 0.05), 0.9, 0.9,
                                            boxstyle="round,pad=0.02,rounding_size=0.1",
                                            facecolor=color, edgecolor='white',
                                            linewidth=2, transform=ax.transAxes)
            ax.add_patch(rect)

            ax.text(0.5, 0.6, value, fontsize=36, fontweight='bold',
                    color='white', ha='center', va='center',
                    transform=ax.transAxes)
            ax.text(0.5, 0.25, label, fontsize=13,
                    color='#cccccc', ha='center', va='center',
                    transform=ax.transAxes)

        # === TOP POSTS WITH IMAGES ===
        ax_top_label = fig.add_subplot(gs[3, 0])
        ax_top_label.set_facecolor('#1a1a2e')
        ax_top_label.axis('off')
        ax_top_label.text(0.0, 0.5, "TOP\nPERFORMING\nPOSTS", fontsize=13,
                          fontweight='bold', color='white',
                          transform=ax_top_label.transAxes, linespacing=1.5)

        # Get top 3 posts by likes
        top_posts = df.nlargest(3, 'likes')

        for i, (_, post) in enumerate(top_posts.iterrows()):
            if i >= 3:
                break
            ax = fig.add_subplot(gs[3, i + 1])
            ax.set_facecolor('#16213e')

            # Try to find and display the image
            img_path = self._find_image_for_post(post['shortcode'], image_files)
            if img_path:
                try:
                    img = Image.open(img_path)
                    img.thumbnail((400, 400))
                    ax.imshow(img)
                except Exception:
                    ax.text(0.5, 0.5, "IMG", fontsize=20, color='gray',
                            ha='center', va='center', transform=ax.transAxes)
            else:
                ax.text(0.5, 0.5, "IMG", fontsize=20, color='gray',
                        ha='center', va='center', transform=ax.transAxes)

            ax.axis('off')
            # Format date
            post_date = pd.to_datetime(post['timestamp'], unit='s').strftime('%b %d, %Y')
            ax.set_title(f"{post['likes']:,} likes  |  {post_date}", fontsize=10, color='white', pad=8)

        # === RECENT POSTS ===
        ax_collage_label = fig.add_subplot(gs[4, 0])
        ax_collage_label.set_facecolor('#1a1a2e')
        ax_collage_label.axis('off')
        ax_collage_label.text(0.0, 0.5, "RECENT\nPOSTS", fontsize=13,
                              fontweight='bold', color='white',
                              transform=ax_collage_label.transAxes, linespacing=1.5)

        # Get recent posts sorted by date
        recent_posts = df.nlargest(3, 'timestamp')

        for i, (_, post) in enumerate(recent_posts.iterrows()):
            if i >= 3:
                break
            ax = fig.add_subplot(gs[4, i + 1])

            img_path = self._find_image_for_post(post['shortcode'], image_files)
            if img_path:
                try:
                    img = Image.open(img_path)
                    img.thumbnail((400, 400))
                    ax.imshow(img)
                except Exception:
                    ax.set_facecolor('#16213e')
            else:
                ax.set_facecolor('#16213e')
            ax.axis('off')
            # Format date
            post_date = pd.to_datetime(post['timestamp'], unit='s').strftime('%b %d, %Y')
            ax.set_title(post_date, fontsize=10, color='#888888', pad=8)

        # === POSTING PATTERN CHART ===
        ax_pattern = fig.add_subplot(gs[5, :2])
        ax_pattern.set_facecolor('#16213e')

        day_order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        df['day_short'] = df['datetime'].dt.day_name().str[:3]
        day_counts = df['day_short'].value_counts().reindex(day_order, fill_value=0)

        bars = ax_pattern.bar(day_counts.index, day_counts.values, color='#e94560', edgecolor='white')
        ax_pattern.set_title('Posting by Day of Week', fontsize=12, color='white', pad=10)
        ax_pattern.tick_params(colors='white', labelsize=9)
        ax_pattern.set_facecolor('#16213e')
        for spine in ax_pattern.spines.values():
            spine.set_color('#333333')

        # === INSIGHTS TEXT ===
        ax_insights = fig.add_subplot(gs[5, 2:])
        ax_insights.set_facecolor('#16213e')
        ax_insights.axis('off')

        # Calculate insights
        most_active_day = df['datetime'].dt.day_name().value_counts().idxmax()
        date_range = f"{df['datetime'].min().strftime('%b %Y')} - {df['datetime'].max().strftime('%b %Y')}"
        avg_caption_len = df['caption'].str.len().mean()
        hashtag_count = df['caption'].str.count('#').sum()

        insights_text = f"""KEY INSIGHTS

Most Active Day: {most_active_day}
Date Range: {date_range}
Avg Caption Length: {avg_caption_len:.0f} chars
Total Hashtags Used: {hashtag_count}
Engagement Rate: {((df['likes'].sum() + df['comments'].sum()) / len(df)):,.0f} per post"""

        ax_insights.text(0.1, 0.9, insights_text, fontsize=11, color='white',
                         transform=ax_insights.transAxes, verticalalignment='top',
                         family='monospace', linespacing=1.8)

        # Add border to insights
        rect = mpatches.FancyBboxPatch((0.02, 0.02), 0.96, 0.96,
                                        boxstyle="round,pad=0.02,rounding_size=0.05",
                                        facecolor='#16213e', edgecolor='#e94560',
                                        linewidth=2, transform=ax_insights.transAxes)
        ax_insights.add_patch(rect)

        # Save poster
        poster_file = self.download_dir / "analytics_poster.png"
        plt.savefig(poster_file, dpi=150, facecolor='#1a1a2e', edgecolor='none')
        plt.close()
        print(f"Poster saved to {poster_file}")
        return poster_file

    def _analyze_account_content(self, df):
        """Analyze captions and content to generate account insights."""
        all_captions = ' '.join(df['caption'].fillna('').tolist()).lower()

        # Common theme keywords to detect
        themes = {
            'entrepreneurship': ['entrepreneur', 'business', 'startup', 'hustle', 'wealth', 'money', 'income', 'profit'],
            'personal development': ['mindset', 'growth', 'self', 'improve', 'discipline', 'habits', 'success', 'goals'],
            'productivity': ['productivity', 'focus', 'time', 'efficient', 'routine', 'morning', 'schedule'],
            'motivation': ['motivation', 'inspire', 'believe', 'dream', 'achieve', 'passion', 'purpose'],
            'education': ['learn', 'knowledge', 'skill', 'read', 'book', 'study', 'course'],
            'lifestyle': ['life', 'lifestyle', 'travel', 'freedom', 'experience', 'adventure'],
            'health & fitness': ['health', 'fitness', 'workout', 'gym', 'diet', 'exercise', 'body'],
            'creativity': ['create', 'creative', 'art', 'design', 'content', 'write', 'build'],
        }

        detected_themes = []
        for theme, keywords in themes.items():
            if any(kw in all_captions for kw in keywords):
                detected_themes.append(theme)

        # Determine account type
        avg_likes = df['likes'].mean()
        total_posts = len(df)

        if avg_likes > 10000:
            influence_level = "High-influence creator"
        elif avg_likes > 1000:
            influence_level = "Growing creator"
        else:
            influence_level = "Emerging creator"

        # Build insight text
        if detected_themes:
            themes_str = ', '.join(detected_themes[:3])
            insight = f"{influence_level} focused on {themes_str}. "
        else:
            insight = f"{influence_level} sharing visual content. "

        # Add engagement observation
        engagement_rate = (df['likes'].sum() + df['comments'].sum()) / len(df)
        if engagement_rate > 5000:
            insight += "Strong audience engagement with high interaction rates. "
        elif engagement_rate > 1000:
            insight += "Consistent engagement from an active community. "

        # Add posting pattern observation
        if total_posts >= 3:
            posting_freq = (df['datetime'].max() - df['datetime'].min()).days / total_posts
            if posting_freq < 2:
                insight += "Frequent posting schedule maintains audience connection."
            elif posting_freq < 7:
                insight += "Regular posting cadence keeps content fresh."
            else:
                insight += "Measured posting approach focuses on quality over quantity."

        return insight

    def _find_post_images(self):
        """Find all downloaded post images."""
        image_files = []
        for ext in ['*.jpg', '*.jpeg', '*.png']:
            image_files.extend(glob.glob(str(self.download_dir / ext)))
        # Filter out analytics images
        image_files = [f for f in image_files if 'analytics' not in f and 'poster' not in f]
        return sorted(image_files, key=os.path.getmtime, reverse=True)

    def _find_image_for_post(self, shortcode, image_files):
        """Find the image file for a specific post shortcode."""
        for img_path in image_files:
            if shortcode in img_path:
                return img_path
        return None

    def load_from_metadata(self, metadata_file):
        """Load posts data from existing metadata.json (e.g., from instaloader)."""
        with open(metadata_file, 'r') as f:
            self.posts_data = json.load(f)
        print(f"Loaded {len(self.posts_data)} posts from metadata")
        return self.posts_data


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Instagram Account Analyzer")
    parser.add_argument("json_file", nargs="?", help="API response JSON file")
    parser.add_argument("--from-metadata", "-m", help="Load from metadata.json (from instaloader)")
    parser.add_argument("--analyze-only", "-a", action="store_true", help="Only run analysis (skip download)")
    parser.add_argument("--output", "-o", default="downloads", help="Output directory")
    parser.add_argument("--account", "-n", default="Instagram Account", help="Account name for poster")
    parser.add_argument("--poster", "-p", action="store_true", help="Generate visual poster")

    args = parser.parse_args()

    analyzer = InstagramAnalyzer(download_dir=args.output)

    if args.from_metadata:
        # Load from existing metadata (e.g., from instaloader)
        analyzer.load_from_metadata(args.from_metadata)
        analyzer.analyze()
        if args.poster:
            analyzer.generate_poster(account_name=args.account)
    elif args.json_file:
        # Extract from API response JSON
        analyzer.extract_from_response(args.json_file)
        if not args.analyze_only:
            analyzer.download_images()
        analyzer.analyze()
        if args.poster:
            analyzer.generate_poster(account_name=args.account)
    else:
        parser.print_help()
        print("\nExamples:")
        print("  uv run python instagram_analyzer.py response.json")
        print("  uv run python instagram_analyzer.py --from-metadata downloads/metadata.json")
        print("  uv run python instagram_analyzer.py -m downloads/metadata.json --poster --account thedankoe")


if __name__ == "__main__":
    main()

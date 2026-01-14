"""
Instagram Analytics Poster - Premium Design Edition

A refined, editorial-style poster with sophisticated aesthetics.
"""

import json
import glob
import os
from pathlib import Path
from datetime import datetime

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle
from matplotlib.collections import PatchCollection
import matplotlib.patheffects as path_effects
from PIL import Image
import numpy as np


class PosterDesigner:
    """Creates beautifully designed Instagram analytics posters."""

    # Color palette - Sophisticated dark theme with warm accents
    COLORS = {
        'bg_primary': '#0A0A0A',      # Deep black
        'bg_secondary': '#151515',    # Soft black
        'bg_card': '#1A1A1A',         # Card background
        'accent_coral': '#FF6B6B',    # Warm coral (primary accent)
        'accent_gold': '#F4D03F',     # Warm gold
        'accent_teal': '#58D68D',     # Fresh teal
        'accent_blue': '#5DADE2',     # Sky blue
        'text_primary': '#FFFFFF',    # White
        'text_secondary': '#A0A0A0',  # Light gray
        'text_muted': '#606060',      # Dark gray
        'border': '#2D2D2D',          # Subtle border
        'gradient_start': '#FF6B6B',
        'gradient_end': '#F4D03F',
    }

    def __init__(self, download_dir="downloads"):
        self.download_dir = Path(download_dir)

    def create_poster(self, metadata_file, account_name="Instagram Account"):
        """Generate a premium analytics poster."""

        # Load data
        with open(metadata_file, 'r') as f:
            posts_data = json.load(f)

        df = pd.DataFrame(posts_data)
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')

        # Find images
        image_files = self._find_post_images()

        # Create figure with elegant proportions
        fig = plt.figure(figsize=(14, 20), facecolor=self.COLORS['bg_primary'], dpi=150)

        # Use a clean grid
        gs = fig.add_gridspec(
            12, 12,
            hspace=0.4, wspace=0.3,
            left=0.06, right=0.94,
            top=0.95, bottom=0.03
        )

        # === HEADER ===
        self._draw_header(fig, gs, account_name)

        # === ACCOUNT PROFILE ===
        self._draw_profile_section(fig, gs, df)

        # === METRICS CARDS ===
        self._draw_metrics(fig, gs, df)

        # === TOP POSTS ===
        self._draw_top_posts(fig, gs, df, image_files)

        # === RECENT POSTS ===
        self._draw_recent_posts(fig, gs, df, image_files)

        # === BOTTOM SECTION: Chart + Insights ===
        self._draw_chart(fig, gs, df)
        self._draw_insights(fig, gs, df)

        # Save
        poster_file = self.download_dir / "analytics_poster_v2.png"
        plt.savefig(poster_file, facecolor=self.COLORS['bg_primary'],
                    edgecolor='none', bbox_inches='tight', pad_inches=0.3)
        plt.close()
        print(f"Premium poster saved to {poster_file}")
        return poster_file

    def _draw_header(self, fig, gs, account_name):
        """Draw elegant header with account name."""
        ax = fig.add_subplot(gs[0:1, :])
        ax.set_facecolor(self.COLORS['bg_primary'])
        ax.axis('off')

        # Account name with gradient effect (simulated)
        ax.text(0.5, 0.6, f"@{account_name}",
                fontsize=48, fontweight='bold',
                color=self.COLORS['text_primary'],
                ha='center', va='center',
                transform=ax.transAxes,
                fontfamily='sans-serif')

        # Subtle tagline with letter spacing effect
        ax.text(0.5, 0.1, "A N A L Y T I C S   R E P O R T",
                fontsize=10, fontweight='normal',
                color=self.COLORS['text_muted'],
                ha='center', va='center',
                transform=ax.transAxes,
                fontfamily='sans-serif')

        # Decorative line
        line = plt.Line2D([0.3, 0.7], [0.0, 0.0],
                         color=self.COLORS['accent_coral'],
                         linewidth=2, alpha=0.6,
                         transform=ax.transAxes)
        ax.add_line(line)

    def _draw_profile_section(self, fig, gs, df):
        """Draw account profile insight section."""
        ax = fig.add_subplot(gs[1:2, 0:12])
        ax.set_facecolor(self.COLORS['bg_primary'])
        ax.axis('off')

        # Generate insight
        insight = self._analyze_account(df)

        # Draw subtle card background
        card = FancyBboxPatch(
            (0.05, 0.15), 0.9, 0.7,
            boxstyle="round,pad=0.02,rounding_size=0.02",
            facecolor=self.COLORS['bg_card'],
            edgecolor=self.COLORS['border'],
            linewidth=1,
            transform=ax.transAxes,
            zorder=1
        )
        ax.add_patch(card)

        # Accent bar on left
        accent_bar = Rectangle(
            (0.05, 0.2), 0.006, 0.6,
            facecolor=self.COLORS['accent_coral'],
            transform=ax.transAxes,
            zorder=2
        )
        ax.add_patch(accent_bar)

        # Profile text - larger and more prominent
        ax.text(0.5, 0.5, insight,
                fontsize=14, color=self.COLORS['text_secondary'],
                ha='center', va='center',
                transform=ax.transAxes,
                fontfamily='sans-serif',
                fontweight='normal',
                zorder=3)

    def _draw_metrics(self, fig, gs, df):
        """Draw elegant metric cards."""
        metrics = [
            ("POSTS", f"{len(df)}", self.COLORS['accent_coral']),
            ("TOTAL LIKES", f"{df['likes'].sum():,}", self.COLORS['accent_gold']),
            ("AVG LIKES", f"{df['likes'].mean():,.0f}", self.COLORS['accent_teal']),
            ("COMMENTS", f"{df['comments'].sum():,}", self.COLORS['accent_blue']),
        ]

        for i, (label, value, accent) in enumerate(metrics):
            ax = fig.add_subplot(gs[2:4, i*3:(i+1)*3])
            ax.set_facecolor(self.COLORS['bg_primary'])
            ax.axis('off')

            # Card background with subtle gradient effect
            card = FancyBboxPatch(
                (0.08, 0.08), 0.84, 0.84,
                boxstyle="round,pad=0.02,rounding_size=0.08",
                facecolor=self.COLORS['bg_card'],
                edgecolor=self.COLORS['border'],
                linewidth=1,
                transform=ax.transAxes
            )
            ax.add_patch(card)

            # Accent dot
            dot = Circle(
                (0.18, 0.75), 0.04,
                facecolor=accent,
                transform=ax.transAxes,
                alpha=0.9
            )
            ax.add_patch(dot)

            # Value - large and bold
            ax.text(0.5, 0.48, value,
                    fontsize=38, fontweight='bold',
                    color=self.COLORS['text_primary'],
                    ha='center', va='center',
                    transform=ax.transAxes,
                    fontfamily='sans-serif')

            # Label - small and clean
            ax.text(0.5, 0.18, label,
                    fontsize=8, fontweight='bold',
                    color=self.COLORS['text_muted'],
                    ha='center', va='center',
                    transform=ax.transAxes,
                    fontfamily='sans-serif')

    def _draw_top_posts(self, fig, gs, df, image_files):
        """Draw top performing posts section."""
        # Section label
        ax_label = fig.add_subplot(gs[4:5, 0:3])
        ax_label.set_facecolor(self.COLORS['bg_primary'])
        ax_label.axis('off')
        ax_label.text(0.15, 0.5, "TOP POSTS",
                      fontsize=12, fontweight='bold',
                      color=self.COLORS['accent_coral'],
                      ha='left', va='center',
                      transform=ax_label.transAxes)

        # Top 3 posts
        top_posts = df.nlargest(3, 'likes')

        for i, (_, post) in enumerate(top_posts.iterrows()):
            ax = fig.add_subplot(gs[4:7, 3+i*3:6+i*3])
            ax.set_facecolor(self.COLORS['bg_card'])
            ax.axis('off')

            # Find and display image
            img_path = self._find_image_for_post(post['shortcode'], image_files)
            if img_path:
                try:
                    img = Image.open(img_path)
                    # Crop to square
                    img = self._crop_to_square(img)
                    img.thumbnail((500, 500))
                    ax.imshow(img, aspect='equal')
                except Exception:
                    self._draw_placeholder(ax)
            else:
                self._draw_placeholder(ax)

            ax.axis('off')

            # Stats overlay at bottom - likes emphasized
            post_date = pd.to_datetime(post['timestamp'], unit='s').strftime('%b %d')
            title = f"{post['likes']:,}  ·  {post_date}"
            ax.set_title(title, fontsize=10, color=self.COLORS['text_secondary'],
                        pad=10, fontfamily='sans-serif', fontweight='bold')

    def _draw_recent_posts(self, fig, gs, df, image_files):
        """Draw recent posts section."""
        # Section label
        ax_label = fig.add_subplot(gs[7:8, 0:3])
        ax_label.set_facecolor(self.COLORS['bg_primary'])
        ax_label.axis('off')
        ax_label.text(0.15, 0.5, "RECENT",
                      fontsize=12, fontweight='bold',
                      color=self.COLORS['accent_teal'],
                      ha='left', va='center',
                      transform=ax_label.transAxes)

        # Recent 3 posts
        recent_posts = df.nlargest(3, 'timestamp')

        for i, (_, post) in enumerate(recent_posts.iterrows()):
            ax = fig.add_subplot(gs[7:10, 3+i*3:6+i*3])
            ax.set_facecolor(self.COLORS['bg_card'])

            img_path = self._find_image_for_post(post['shortcode'], image_files)
            if img_path:
                try:
                    img = Image.open(img_path)
                    img = self._crop_to_square(img)
                    img.thumbnail((500, 500))
                    ax.imshow(img, aspect='equal')
                except Exception:
                    self._draw_placeholder(ax)
            else:
                self._draw_placeholder(ax)

            ax.axis('off')

            post_date = pd.to_datetime(post['timestamp'], unit='s').strftime('%b %d, %Y')
            ax.set_title(post_date, fontsize=9, color=self.COLORS['text_muted'],
                        pad=8, fontfamily='sans-serif')

    def _draw_chart(self, fig, gs, df):
        """Draw elegant bar chart."""
        ax = fig.add_subplot(gs[10:12, 0:6])
        ax.set_facecolor(self.COLORS['bg_card'])

        # Prepare data
        day_order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        df['day_short'] = df['datetime'].dt.day_name().str[:3]
        day_counts = df['day_short'].value_counts().reindex(day_order, fill_value=0)

        # Draw bars with gradient-like effect
        bars = ax.bar(day_counts.index, day_counts.values,
                      color=self.COLORS['accent_coral'],
                      edgecolor='none',
                      width=0.6,
                      alpha=0.85)

        # Style
        ax.set_title('POSTING ACTIVITY', fontsize=10, color=self.COLORS['text_secondary'],
                     pad=15, fontfamily='sans-serif', fontweight='bold')
        ax.tick_params(colors=self.COLORS['text_muted'], labelsize=8)
        ax.set_facecolor(self.COLORS['bg_card'])

        # Remove spines except bottom
        for spine in ['top', 'right', 'left']:
            ax.spines[spine].set_visible(False)
        ax.spines['bottom'].set_color(self.COLORS['border'])

        # Remove y-axis ticks
        ax.set_yticks([])

        # Add value labels on bars
        for bar, val in zip(bars, day_counts.values):
            if val > 0:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                       str(int(val)), ha='center', va='bottom',
                       fontsize=9, color=self.COLORS['text_secondary'])

    def _draw_insights(self, fig, gs, df):
        """Draw key insights panel."""
        ax = fig.add_subplot(gs[10:12, 6:12])
        ax.set_facecolor(self.COLORS['bg_primary'])
        ax.axis('off')

        # Card background
        card = FancyBboxPatch(
            (0.05, 0.05), 0.9, 0.9,
            boxstyle="round,pad=0.02,rounding_size=0.05",
            facecolor=self.COLORS['bg_card'],
            edgecolor=self.COLORS['border'],
            linewidth=1,
            transform=ax.transAxes
        )
        ax.add_patch(card)

        # Calculate insights
        most_active_day = df['datetime'].dt.day_name().value_counts().idxmax()
        date_range = f"{df['datetime'].min().strftime('%b %Y')} - {df['datetime'].max().strftime('%b %Y')}"
        engagement = (df['likes'].sum() + df['comments'].sum()) / len(df)

        # Title
        ax.text(0.12, 0.85, "KEY INSIGHTS",
                fontsize=10, fontweight='bold',
                color=self.COLORS['text_secondary'],
                transform=ax.transAxes)

        # Insights with icons (using dots as bullet points)
        insights = [
            f"Most Active: {most_active_day}",
            f"Period: {date_range}",
            f"Engagement: {engagement:,.0f}/post",
            f"Hashtags: {df['caption'].str.count('#').sum()}",
        ]

        for i, insight in enumerate(insights):
            y_pos = 0.65 - (i * 0.15)
            # Bullet
            dot = Circle((0.12, y_pos), 0.012,
                        facecolor=self.COLORS['accent_coral'],
                        transform=ax.transAxes, alpha=0.7)
            ax.add_patch(dot)
            # Text
            ax.text(0.17, y_pos, insight,
                   fontsize=10, color=self.COLORS['text_secondary'],
                   va='center', transform=ax.transAxes,
                   fontfamily='sans-serif')

    def _analyze_account(self, df):
        """Generate account insight text."""
        all_captions = ' '.join(df['caption'].fillna('').tolist()).lower()

        themes = {
            'entrepreneurship': ['entrepreneur', 'business', 'startup', 'wealth', 'money'],
            'personal growth': ['mindset', 'growth', 'discipline', 'habits', 'success'],
            'productivity': ['productivity', 'focus', 'time', 'routine'],
            'creativity': ['create', 'creative', 'art', 'design', 'build'],
            'education': ['learn', 'knowledge', 'skill', 'read', 'book'],
        }

        detected = [t for t, kw in themes.items() if any(k in all_captions for k in kw)]

        avg_likes = df['likes'].mean()
        level = "High-engagement" if avg_likes > 5000 else "Growing" if avg_likes > 1000 else "Emerging"

        if detected:
            return f"{level} creator · {' · '.join(detected[:2])}"
        return f"{level} creator · Visual content"

    def _find_post_images(self):
        """Find all post images."""
        image_files = []
        for ext in ['*.jpg', '*.jpeg', '*.png']:
            image_files.extend(glob.glob(str(self.download_dir / ext)))
        image_files = [f for f in image_files if 'analytics' not in f and 'poster' not in f]
        return sorted(image_files, key=os.path.getmtime, reverse=True)

    def _find_image_for_post(self, shortcode, image_files):
        """Find image for a specific post."""
        for img_path in image_files:
            if shortcode in img_path:
                return img_path
        return None

    def _crop_to_square(self, img):
        """Crop image to square from center."""
        width, height = img.size
        size = min(width, height)
        left = (width - size) // 2
        top = (height - size) // 2
        return img.crop((left, top, left + size, top + size))

    def _draw_placeholder(self, ax):
        """Draw placeholder for missing images."""
        ax.set_facecolor(self.COLORS['bg_card'])
        ax.text(0.5, 0.5, "◻", fontsize=30, color=self.COLORS['text_muted'],
               ha='center', va='center', transform=ax.transAxes)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate premium Instagram analytics poster")
    parser.add_argument("--metadata", "-m", default="downloads/metadata.json",
                        help="Path to metadata.json")
    parser.add_argument("--account", "-n", default="Instagram Account",
                        help="Account name")
    parser.add_argument("--output", "-o", default="downloads",
                        help="Output directory")

    args = parser.parse_args()

    designer = PosterDesigner(download_dir=args.output)
    designer.create_poster(args.metadata, args.account)


if __name__ == "__main__":
    main()

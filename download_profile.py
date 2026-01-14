"""
Instagram Profile Downloader using Instaloader

Downloads all images from a public Instagram profile and prepares data for analysis.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

import instaloader


def download_profile(username: str, output_dir: str = "downloads", login_user: str = None, max_posts: int = None):
    """
    Download all images from an Instagram profile.

    Args:
        username: Instagram username to download (without @)
        output_dir: Directory to save images and metadata
        login_user: Optional - your Instagram username for login (avoids rate limits)
        max_posts: Optional - limit number of posts to download
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # Configure instaloader
    L = instaloader.Instaloader(
        download_videos=False,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=True,
        compress_json=False,
        post_metadata_txt_pattern="",
        dirname_pattern=str(output_path),
        filename_pattern="{shortcode}",
    )

    # Login if credentials provided (helps avoid rate limits)
    if login_user:
        try:
            L.load_session_from_file(login_user)
            print(f"Loaded session for {login_user}")
        except FileNotFoundError:
            print(f"No saved session found for {login_user}")
            print("Run: uv run instaloader --login YOUR_USERNAME")
            print("This will save a session file for future use.")
            return

    try:
        print(f"Loading profile: {username}")
        profile = instaloader.Profile.from_username(L.context, username)

        print(f"Profile: {profile.full_name}")
        print(f"Posts: {profile.mediacount}")
        print(f"Followers: {profile.followers}")
        print(f"Following: {profile.followees}")
        print("-" * 40)

        posts_data = []
        count = 0

        for post in profile.get_posts():
            if max_posts and count >= max_posts:
                break

            if post.is_video:
                print(f"[{count+1}] Skipping video: {post.shortcode}")
                continue

            # Download the image
            try:
                L.download_post(post, target=output_path)
                print(f"[{count+1}] Downloaded: {post.shortcode}")
            except Exception as e:
                print(f"[{count+1}] Failed {post.shortcode}: {e}")
                continue

            # Collect metadata for analysis
            post_data = {
                "id": str(post.mediaid),
                "shortcode": post.shortcode,
                "display_url": post.url,
                "timestamp": int(post.date_utc.timestamp()),
                "likes": post.likes,
                "comments": post.comments,
                "caption": post.caption or "",
                "is_video": post.is_video,
                "dimensions": {
                    "width": post.video_url and 0 or getattr(post, 'width', 0),
                    "height": post.video_url and 0 or getattr(post, 'height', 0),
                },
                "hashtags": list(post.caption_hashtags) if post.caption_hashtags else [],
                "mentions": list(post.caption_mentions) if post.caption_mentions else [],
            }
            posts_data.append(post_data)
            count += 1

        # Save consolidated metadata
        metadata_file = output_path / "metadata.json"
        with open(metadata_file, "w") as f:
            json.dump(posts_data, f, indent=2)

        print("-" * 40)
        print(f"Downloaded {count} images")
        print(f"Metadata saved to {metadata_file}")
        print(f"\nNext step: Run analyzer")
        print(f"  uv run python instagram_analyzer.py --from-metadata {metadata_file}")

        return posts_data

    except instaloader.exceptions.ProfileNotExistsException:
        print(f"Error: Profile '{username}' does not exist")
    except instaloader.exceptions.PrivateProfileNotFollowedException:
        print(f"Error: Profile '{username}' is private. Login required.")
    except instaloader.exceptions.ConnectionException as e:
        print(f"Connection error: {e}")
        print("\nTip: Instagram may be rate-limiting. Try:")
        print("  1. Wait a few minutes and try again")
        print("  2. Login to avoid rate limits:")
        print("     uv run instaloader --login YOUR_USERNAME")
    except Exception as e:
        print(f"Error: {e}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Download Instagram profile images")
    parser.add_argument("username", help="Instagram username (without @)")
    parser.add_argument("--output", "-o", help="Output directory (default: output/YYYY-MM-DD_username)")
    parser.add_argument("--login", "-l", help="Your Instagram username (for login)")
    parser.add_argument("--max", "-m", type=int, help="Maximum posts to download")

    args = parser.parse_args()

    # Generate timestamped output directory if not specified
    if args.output:
        output_dir = args.output
    else:
        timestamp = datetime.now().strftime("%Y-%m-%d")
        output_dir = f"output/{timestamp}_{args.username}"

    download_profile(
        username=args.username,
        output_dir=output_dir,
        login_user=args.login,
        max_posts=args.max,
    )


if __name__ == "__main__":
    main()

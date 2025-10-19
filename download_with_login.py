#!/usr/bin/env python3
"""
Download Instagram com Login
Usa credenciais do .env para fazer login e baixar TODAS as fotos
"""

import os
import instaloader
from pathlib import Path
from dotenv import load_dotenv
import time

# Load credentials
load_dotenv()

USERNAME = os.getenv("INSTAGRAM_USERNAME")
LOGIN = os.getenv("INSTAGRAM_LOGIN")
PASSWORD = os.getenv("INSTAGRAM_PASSWORD")

OUTPUT_DIR = Path("instagram_full_auth")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("🔐 Instagram Download with Login")
print("=" * 70)
print(f"Target: @{USERNAME}")
print(f"Login as: {LOGIN}")
print()

# Create Instaloader instance
L = instaloader.Instaloader(
    download_videos=False,
    download_video_thumbnails=False,
    download_geotags=False,
    download_comments=False,
    save_metadata=False,
    compress_json=False,
    dirname_pattern=str(OUTPUT_DIR),
    filename_pattern="{shortcode}"
)

try:
    print("🔐 Logging in...")
    
    # Try to load session
    session_file = Path("instagram_session")
    
    if session_file.exists():
        print("   📂 Loading existing session...")
        L.load_session_from_file(LOGIN, str(session_file))
        print("   ✅ Session loaded!")
    else:
        print("   🔑 Creating new session...")
        L.login(LOGIN, PASSWORD)
        L.save_session_to_file(str(session_file))
        print("   ✅ Logged in and session saved!")
    
    print()
    print(f"📥 Downloading profile: {USERNAME}")
    print("   This may take 10-15 minutes...")
    print()
    
    # Download profile
    profile = instaloader.Profile.from_username(L.context, USERNAME)
    
    print(f"   ✅ Profile found!")
    print(f"   • Posts: {profile.mediacount}")
    print(f"   • Followers: {profile.followers}")
    print()
    
    # Download all posts
    downloaded = 0
    skipped = 0
    
    for post in profile.get_posts():
        try:
            # Check if already downloaded
            filename = OUTPUT_DIR / f"{post.shortcode}.jpg"
            if filename.exists():
                skipped += 1
                continue
            
            # Download
            L.download_post(post, target=USERNAME)
            downloaded += 1
            
            print(f"   ✅ [{downloaded + skipped}/{profile.mediacount}] {post.shortcode}")
            
            # Rate limiting
            time.sleep(2)
        
        except Exception as e:
            print(f"   ⚠️  Error on {post.shortcode}: {e}")
            continue
    
    print()
    print("=" * 70)
    print("✅ DOWNLOAD COMPLETE!")
    print("=" * 70)
    print(f"📊 Statistics:")
    print(f"   • Downloaded: {downloaded}")
    print(f"   • Skipped (already exist): {skipped}")
    print(f"   • Total: {downloaded + skipped}")
    print(f"   • Output: {OUTPUT_DIR}")
    print()

except instaloader.exceptions.BadCredentialsException:
    print("❌ Login failed: Bad credentials!")
    print("   Check INSTAGRAM_LOGIN and INSTAGRAM_PASSWORD in .env")

except instaloader.exceptions.TwoFactorAuthRequiredException:
    print("❌ Two-factor authentication required!")
    print("   Please disable 2FA temporarily or use backup codes")

except instaloader.exceptions.ConnectionException as e:
    print(f"❌ Connection error: {e}")
    print("   Instagram may have rate-limited your IP")
    print("   Try again in 10-15 minutes")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

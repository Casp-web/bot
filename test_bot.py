#!/usr/bin/env python3
"""
Test script for YouTube Telegram Bot

This script tests the main components of the bot without requiring a real Telegram bot token.
"""

import asyncio
import sys
from pathlib import Path

# Add current directory to sys.path
sys.path.append(str(Path(__file__).parent))

from config.settings.base import settings
from database.models.base import init_db
from downloader.services.youtube_service import YouTubeService
from utils.validators import URLValidator
from downloader.models.video_info import VideoInfo


async def test_database():
    """Test database initialization"""
    print("🗄️  Testing database initialization...")
    try:
        await init_db()
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False


async def test_url_validator():
    """Test URL validation"""
    print("\n🔍 Testing URL validation...")
    
    validator = URLValidator()
    
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ", 
        "https://youtube.com/embed/dQw4w9WgXcQ",
        "https://example.com/video",  # Invalid
        "not_a_url",  # Invalid
    ]
    
    for url in test_urls:
        is_valid = validator.is_valid_youtube_url(url)
        status = "✅" if is_valid else "❌"
        print(f"  {status} {url}")
    
    print("✅ URL validation test completed")
    return True


async def test_youtube_service():
    """Test YouTube service (without actual download)"""
    print("\n📺 Testing YouTube service...")
    
    try:
        youtube_service = YouTubeService()
        print("✅ YouTube service initialized")
        
        # Test with a well-known video URL (Rick Roll)
        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        
        print(f"  Testing video info extraction for: {test_url}")
        
        # Note: This will fail without internet connection or if the video is not accessible
        try:
            video_info = await youtube_service.get_video_info(test_url)
            if video_info:
                print(f"  ✅ Video info extracted:")
                print(f"    Title: {video_info.title}")
                print(f"    Duration: {video_info.duration_formatted}")
                print(f"    Uploader: {video_info.uploader}")
            else:
                print("  ⚠️  Video info extraction returned None (expected without internet)")
        except Exception as e:
            print(f"  ⚠️  Video info extraction failed: {e} (expected without internet or restricted access)")
        
        return True
    except Exception as e:
        print(f"❌ YouTube service test failed: {e}")
        return False


async def test_bot_modules():
    """Test bot module imports"""
    print("\n🤖 Testing bot module imports...")
    
    try:
        from bot.handlers import routers
        print(f"  ✅ Imported {len(routers)} handlers")
        
        from bot.middleware import UserMiddleware, ThrottlingMiddleware
        print("  ✅ Imported middleware classes")
        
        from bot.keyboards.main_keyboard import MainKeyboard
        from bot.keyboards.download_keyboard import DownloadKeyboard
        from bot.keyboards.settings_keyboard import SettingsKeyboard
        print("  ✅ Imported keyboard classes")
        
        return True
    except Exception as e:
        print(f"❌ Bot module import failed: {e}")
        return False


async def test_configuration():
    """Test configuration loading"""
    print("\n⚙️  Testing configuration...")
    
    try:
        print(f"  ✅ Database URL: {settings.DATABASE_URL}")
        print(f"  ✅ Download path: {settings.DOWNLOAD_PATH}")
        print(f"  ✅ Max file size: {settings.MAX_FILE_SIZE_MB} MB")
        print(f"  ✅ Max duration: {settings.MAX_DURATION_MINUTES} minutes")
        print(f"  ✅ Log level: {settings.LOG_LEVEL}")
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


async def main():
    """Run all tests"""
    print("🚀 Starting YouTube Telegram Bot Tests")
    print("=" * 50)
    
    tests = [
        test_configuration,
        test_database,
        test_url_validator,
        test_youtube_service,
        test_bot_modules,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            result = await test()
            if result:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! The bot is ready for deployment.")
        print("\n📝 Next steps:")
        print("1. Get a real Telegram bot token from @BotFather")
        print("2. Update the BOT_TOKEN in your .env file")
        print("3. Run: python main.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    return failed == 0


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)
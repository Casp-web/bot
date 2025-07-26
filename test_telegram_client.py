#!/usr/bin/env python3
"""
Test script for Telegram Tkinter Client
This script tests the basic functionality without requiring GUI
"""

import sys
import os
import json
from datetime import datetime

def test_config_loading():
    """Test configuration loading and saving"""
    print("Testing configuration loading...")
    
    # Test config
    test_config = {
        'api_id': '123456',
        'api_hash': 'test_hash_123',
        'phone': '+380123456789'
    }
    
    # Save test config
    with open('test_config.json', 'w') as f:
        json.dump(test_config, f)
    
    # Load test config
    try:
        with open('test_config.json', 'r') as f:
            loaded_config = json.load(f)
        
        assert loaded_config == test_config
        print("✅ Configuration loading/saving works correctly")
        
        # Clean up
        os.remove('test_config.json')
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import tkinter as tk
        print("✅ Tkinter imported successfully")
    except ImportError as e:
        print(f"❌ Tkinter import failed: {e}")
        return False
    
    try:
        from telethon import TelegramClient
        print("✅ Telethon imported successfully")
    except ImportError as e:
        print(f"❌ Telethon import failed: {e}")
        return False
    
    try:
        import asyncio
        print("✅ Asyncio imported successfully")
    except ImportError as e:
        print(f"❌ Asyncio import failed: {e}")
        return False
    
    return True

def test_client_creation():
    """Test client creation without actual connection"""
    print("Testing client creation...")
    
    try:
        from telethon import TelegramClient
        
        # Create client with dummy credentials
        client = TelegramClient('test_session', 123456, 'dummy_hash')
        print("✅ Client creation successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Client creation failed: {e}")
        return False

def test_file_structure():
    """Test if all required files exist"""
    print("Testing file structure...")
    
    required_files = [
        'telegram_client.py',
        'telegram_client_advanced.py',
        'run_telegram_client.py',
        'requirements.txt',
        'TELEGRAM_CLIENT_SETUP.md',
        'README_TELEGRAM_CLIENT.md'
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")
            missing_files.append(file)
    
    if missing_files:
        print(f"Missing files: {missing_files}")
        return False
    
    return True

def test_syntax():
    """Test syntax of Python files"""
    print("Testing syntax...")
    
    python_files = [
        'telegram_client.py',
        'telegram_client_advanced.py',
        'run_telegram_client.py'
    ]
    
    for file in python_files:
        try:
            with open(file, 'r') as f:
                content = f.read()
            
            # Try to compile the code
            compile(content, file, 'exec')
            print(f"✅ {file} syntax is valid")
            
        except SyntaxError as e:
            print(f"❌ {file} syntax error: {e}")
            return False
        except Exception as e:
            print(f"❌ {file} error: {e}")
            return False
    
    return True

def main():
    """Run all tests"""
    print("=" * 50)
    print("Telegram Tkinter Client - Test Suite")
    print("=" * 50)
    print(f"Test started at: {datetime.now()}")
    print()
    
    tests = [
        ("File Structure", test_file_structure),
        ("Syntax Check", test_syntax),
        ("Imports", test_imports),
        ("Client Creation", test_client_creation),
        ("Configuration", test_config_loading)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The client should work correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
#!/usr/bin/env python3
"""
Startup script for YouTube Bot Web Developer Panel
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if all required packages are installed"""
    try:
        import flask
        import flask_login
        print("✅ Flask dependencies found")
        return True
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        return False

def install_requirements():
    """Install missing requirements"""
    print("📦 Installing web panel dependencies...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "flask>=3.0.0", "flask-login>=0.6.3"
        ])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_directories():
    """Create necessary directories for the web panel"""
    directories = [
        "web_panel/templates",
        "web_panel/static/css",
        "web_panel/static/js",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Directories created")

def start_web_panel():
    """Start the web panel application"""
    # Add web_panel to Python path
    web_panel_path = Path(__file__).parent / "web_panel"
    sys.path.insert(0, str(web_panel_path))
    
    try:
        from app import app
        print("🌐 Starting YouTube Bot Developer Panel...")
        print("📍 Access panel at: http://localhost:5000")
        print("🔑 Default login: admin / admin123")
        print("⚠️  Change default password in production!")
        print("🔧 Press Ctrl+C to stop the server")
        print("-" * 50)
        
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except KeyboardInterrupt:
        print("\n👋 Web panel stopped")
    except Exception as e:
        print(f"❌ Error starting web panel: {e}")
        return False
    
    return True

def main():
    """Main function"""
    print("🚀 YouTube Bot Web Developer Panel")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path("web_panel").exists():
        print("❌ web_panel directory not found!")
        print("Please run this script from the project root directory.")
        return 1
    
    # Create necessary directories
    create_directories()
    
    # Check requirements
    if not check_requirements():
        print("\n📦 Installing missing dependencies...")
        if not install_requirements():
            print("❌ Failed to install dependencies. Please install manually:")
            print("pip install flask>=3.0.0 flask-login>=0.6.3")
            return 1
    
    # Start the web panel
    if not start_web_panel():
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
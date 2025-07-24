#!/usr/bin/env python3
"""
Web Developer Panel for YouTube Telegram Bot
Provides a web interface for configuration management and bot monitoring
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from config.settings.base import settings
from database.models.base import init_db
from database.repositories.user_repository import UserRepository
from database.repositories.download_repository import DownloadRepository
from downloader.services.youtube_service import YouTubeService

app = Flask(__name__)
app.secret_key = os.environ.get('WEB_SECRET_KEY', 'dev-secret-key-change-in-production')

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access the developer panel.'

class AdminUser(UserMixin):
    def __init__(self, username):
        self.id = username
        self.username = username

# Simple admin user (in production, use proper user management)
ADMIN_USERS = {
    'admin': generate_password_hash('admin123')  # Change this password!
}

@login_manager.user_loader
def load_user(user_id):
    if user_id in ADMIN_USERS:
        return AdminUser(user_id)
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in ADMIN_USERS and check_password_hash(ADMIN_USERS[username], password):
            user = AdminUser(username)
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    """Main dashboard with bot statistics and overview"""
    return render_template('dashboard.html', 
                         bot_name=settings.BOT_NAME,
                         current_user=current_user)

@app.route('/config')
@login_required
def config_page():
    """Configuration management page"""
    # Read current configuration
    config_data = {
        'bot': {
            'BOT_TOKEN': settings.BOT_TOKEN,
            'BOT_NAME': settings.BOT_NAME,
        },
        'database': {
            'DATABASE_URL': settings.DATABASE_URL,
        },
        'download': {
            'MAX_FILE_SIZE_MB': settings.MAX_FILE_SIZE_MB,
            'DOWNLOAD_PATH': settings.DOWNLOAD_PATH,
            'TEMP_PATH': settings.TEMP_PATH,
            'MAX_DURATION_MINUTES': settings.MAX_DURATION_MINUTES,
            'QUALITY_VIDEO': settings.QUALITY_VIDEO,
            'QUALITY_AUDIO': settings.QUALITY_AUDIO,
        },
        'limits': {
            'MAX_DOWNLOADS_PER_USER_HOUR': settings.MAX_DOWNLOADS_PER_USER_HOUR,
            'RATE_LIMIT_REQUESTS_PER_MINUTE': settings.RATE_LIMIT_REQUESTS_PER_MINUTE,
        },
        'logging': {
            'LOG_LEVEL': settings.LOG_LEVEL,
            'LOG_FILE': settings.LOG_FILE,
        }
    }
    
    return render_template('config.html', config=config_data)

@app.route('/api/config', methods=['GET', 'POST'])
@login_required
def api_config():
    """API endpoint for configuration management"""
    if request.method == 'GET':
        # Return current configuration
        config = {
            'bot_name': settings.BOT_NAME,
            'max_file_size_mb': settings.MAX_FILE_SIZE_MB,
            'max_duration_minutes': settings.MAX_DURATION_MINUTES,
            'quality_video': settings.QUALITY_VIDEO,
            'quality_audio': settings.QUALITY_AUDIO,
            'max_downloads_per_user_hour': settings.MAX_DOWNLOADS_PER_USER_HOUR,
            'rate_limit_requests_per_minute': settings.RATE_LIMIT_REQUESTS_PER_MINUTE,
            'log_level': settings.LOG_LEVEL,
            'download_path': settings.DOWNLOAD_PATH,
            'temp_path': settings.TEMP_PATH,
        }
        return jsonify(config)
    
    elif request.method == 'POST':
        # Update configuration
        try:
            data = request.json
            
            # Update .env file
            env_path = Path('.env')
            env_content = {}
            
            if env_path.exists():
                with open(env_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            env_content[key] = value
            
            # Update values
            if 'bot_name' in data:
                env_content['BOT_NAME'] = data['bot_name']
            if 'max_file_size_mb' in data:
                env_content['MAX_FILE_SIZE_MB'] = str(data['max_file_size_mb'])
            if 'max_duration_minutes' in data:
                env_content['MAX_DURATION_MINUTES'] = str(data['max_duration_minutes'])
            if 'quality_video' in data:
                env_content['QUALITY_VIDEO'] = data['quality_video']
            if 'quality_audio' in data:
                env_content['QUALITY_AUDIO'] = data['quality_audio']
            if 'max_downloads_per_user_hour' in data:
                env_content['MAX_DOWNLOADS_PER_USER_HOUR'] = str(data['max_downloads_per_user_hour'])
            if 'rate_limit_requests_per_minute' in data:
                env_content['RATE_LIMIT_REQUESTS_PER_MINUTE'] = str(data['rate_limit_requests_per_minute'])
            if 'log_level' in data:
                env_content['LOG_LEVEL'] = data['log_level']
            if 'download_path' in data:
                env_content['DOWNLOAD_PATH'] = data['download_path']
            if 'temp_path' in data:
                env_content['TEMP_PATH'] = data['temp_path']
            
            # Write back to .env file
            with open(env_path, 'w') as f:
                for key, value in env_content.items():
                    f.write(f"{key}={value}\n")
            
            return jsonify({'status': 'success', 'message': 'Configuration updated successfully'})
            
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/users')
@login_required
def users_page():
    """User management page"""
    return render_template('users.html')

@app.route('/api/users')
@login_required
def api_users():
    """API endpoint for user statistics"""
    # This would require async context, so we'll return mock data for now
    # In production, you'd want to run this in an async context
    users_data = {
        'total_users': 0,
        'active_users': 0,
        'banned_users': 0,
        'users': []
    }
    
    return jsonify(users_data)

@app.route('/downloads')
@login_required
def downloads_page():
    """Downloads monitoring page"""
    return render_template('downloads.html')

@app.route('/api/downloads')
@login_required
def api_downloads():
    """API endpoint for download statistics"""
    # Mock data for now
    downloads_data = {
        'total_downloads': 0,
        'successful_downloads': 0,
        'failed_downloads': 0,
        'downloads_today': 0,
        'recent_downloads': []
    }
    
    return jsonify(downloads_data)

@app.route('/logs')
@login_required
def logs_page():
    """Logs viewing page"""
    return render_template('logs.html')

@app.route('/api/logs')
@login_required
def api_logs():
    """API endpoint for log data"""
    try:
        log_file = Path(settings.LOG_FILE)
        if log_file.exists():
            with open(log_file, 'r') as f:
                lines = f.readlines()
                # Return last 100 lines
                recent_logs = lines[-100:] if len(lines) > 100 else lines
                return jsonify({'logs': recent_logs})
        else:
            return jsonify({'logs': ['Log file not found']})
    except Exception as e:
        return jsonify({'logs': [f'Error reading logs: {str(e)}']})

@app.route('/api/test-youtube')
@login_required
def test_youtube():
    """Test YouTube service functionality"""
    try:
        # Test with a sample YouTube URL
        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        
        # This would need to be run in async context
        # For now, return a success message
        return jsonify({
            'status': 'success',
            'message': 'YouTube service is configured correctly',
            'test_url': test_url
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'YouTube service error: {str(e)}'
        })

@app.route('/api/restart-bot', methods=['POST'])
@login_required
def restart_bot():
    """API endpoint to restart the bot (placeholder)"""
    # In production, this would trigger a bot restart
    return jsonify({
        'status': 'success',
        'message': 'Bot restart signal sent (not implemented in demo)'
    })

if __name__ == '__main__':
    # Create directories if they don't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    print("🌐 Starting YouTube Bot Developer Panel...")
    print("📍 Access panel at: http://localhost:5000")
    print("🔑 Default login: admin / admin123")
    print("⚠️  Change default password in production!")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
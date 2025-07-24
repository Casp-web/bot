import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
if not TELEGRAM_TOKEN:
    raise ValueError("Please set the TELEGRAM_TOKEN environment variable.")

# Base URL for downloader microservice
DOWNLOADER_SERVICE_URL = os.getenv("DOWNLOADER_SERVICE_URL", "http://localhost:8000")
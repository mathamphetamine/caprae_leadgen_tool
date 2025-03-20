import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys and credentials
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')
GOOGLE_CSE_ID = os.getenv('GOOGLE_CSE_ID', '')

# Scraping settings
REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Referer': 'https://www.google.com/'
}

# Rate limiting
MAX_REQUESTS_PER_MINUTE = 10
REQUEST_TIMEOUT = 15  # seconds

# Email validation settings
EMAIL_CHECK_TIMEOUT = 5  # seconds

# LinkedIn scraping settings (use with caution due to legal considerations)
LINKEDIN_LOGIN_REQUIRED = True  # Set to False to disable LinkedIn scraping features that require login

# Default export settings
DEFAULT_EXPORT_FORMAT = 'csv'
DEFAULT_EXPORT_PATH = 'exports/'

# Patterns for regex-based extraction
EMAIL_PATTERN = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
PHONE_PATTERN = r'(\+\d{1,3}[\s.-])?(\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4})'
COMPANY_NAME_PATTERN = r'(Inc\.|LLC|Ltd\.|\bCorp\.|\bCorp\b|\bCompany\b)'

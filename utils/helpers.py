import re
import time
import csv
import json
import os
import pandas as pd
from urllib.parse import urlparse, urljoin
from datetime import datetime
import logging

from leadgen_tool.utils.config import (
    EMAIL_PATTERN, PHONE_PATTERN, COMPANY_NAME_PATTERN,
    DEFAULT_EXPORT_PATH
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def extract_emails(text):
    """Extract email addresses from text using regex."""
    if not text:
        return []
    return list(set(re.findall(EMAIL_PATTERN, text)))

def extract_phones(text):
    """Extract phone numbers from text using regex."""
    if not text:
        return []
    return list(set(re.findall(PHONE_PATTERN, text)))

def clean_text(text):
    """Clean and normalize text."""
    if not text:
        return ""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters
    text = re.sub(r'[^\w\s@.()-]', '', text)
    return text.strip()

def is_valid_url(url):
    """Check if a URL is valid."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def normalize_url(base_url, relative_url):
    """Convert relative URL to absolute URL."""
    if is_valid_url(relative_url):
        return relative_url
    return urljoin(base_url, relative_url)

def rate_limit(func):
    """Decorator for rate limiting API calls."""
    last_called = {}
    
    def wrapper(*args, **kwargs):
        handler = args[0] if args else object()
        now = time.time()
        elapsed = now - last_called.get(handler, 0)
        
        if elapsed < 1:  # Wait at least 1 second between requests
            time.sleep(1 - elapsed)
        
        result = func(*args, **kwargs)
        last_called[handler] = time.time()
        return result
    
    return wrapper

def export_to_csv(data, filename=None):
    """Export data to CSV file."""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"leads_{timestamp}.csv"
    
    # Ensure export directory exists
    os.makedirs(DEFAULT_EXPORT_PATH, exist_ok=True)
    file_path = os.path.join(DEFAULT_EXPORT_PATH, filename)
    
    # Convert data to DataFrame if it's a list of dictionaries
    if isinstance(data, list) and data and isinstance(data[0], dict):
        df = pd.DataFrame(data)
        df.to_csv(file_path, index=False)
        logger.info(f"Data exported to {file_path}")
        return file_path
    elif isinstance(data, pd.DataFrame):
        data.to_csv(file_path, index=False)
        logger.info(f"Data exported to {file_path}")
        return file_path
    else:
        raise ValueError("Data must be a list of dictionaries or a pandas DataFrame")

def export_to_excel(data, filename=None):
    """Export data to Excel file."""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"leads_{timestamp}.xlsx"
    
    # Ensure export directory exists
    os.makedirs(DEFAULT_EXPORT_PATH, exist_ok=True)
    file_path = os.path.join(DEFAULT_EXPORT_PATH, filename)
    
    # Convert data to DataFrame if it's a list of dictionaries
    if isinstance(data, list) and data and isinstance(data[0], dict):
        df = pd.DataFrame(data)
        df.to_excel(file_path, index=False)
        logger.info(f"Data exported to {file_path}")
        return file_path
    elif isinstance(data, pd.DataFrame):
        data.to_excel(file_path, index=False)
        logger.info(f"Data exported to {file_path}")
        return file_path
    else:
        raise ValueError("Data must be a list of dictionaries or a pandas DataFrame")

def extract_domain_from_url(url):
    """Extract domain name from URL."""
    if not url:
        return ""
    try:
        parsed_uri = urlparse(url)
        domain = parsed_uri.netloc
        # Remove www. if present
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain
    except:
        return ""

def extract_company_name(text, url=None):
    """
    Attempt to extract company name from text or URL.
    This is a basic implementation and might need refinement based on specific needs.
    """
    # First try to find company indicators in text
    if text:
        matches = re.findall(r'([A-Z][A-Za-z0-9\s]{0,20}\s' + COMPANY_NAME_PATTERN + ')', text)
        if matches:
            return matches[0]
    
    # If no match in text, try to extract from domain
    if url:
        domain = extract_domain_from_url(url)
        # Remove TLD
        company = domain.split('.')[0]
        return company.title()
    
    return ""

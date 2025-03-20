"""
LeadGen Tool - A comprehensive lead generation toolkit for businesses

This package provides tools for searching, scraping, validating, and enriching
business contact information to support sales and marketing efforts.

Main components:
- scraper: Web scraping modules for extracting contact information
- enricher: Data enrichment and validation tools
- utils: Helper functions and configuration

For detailed usage, see the README.md file.
"""

__version__ = '0.1.0'
__author__ = 'Caprae Capital Partners'

# Import key components for easier access
from scraper.web_scraper import scrape_website
from scraper.google_search import search_companies
from scraper.linkedin_scraper import search_linkedin_companies, get_linkedin_company_details
from enricher.email_validator import validate_email_single, validate_email_list, filter_valid_emails
from enricher.data_enricher import enrich_company_data, batch_enrich_companies, enrich_dataframe

# Define what's available through direct imports
__all__ = [
    'scrape_website',
    'search_companies',
    'search_linkedin_companies',
    'get_linkedin_company_details',
    'validate_email_single',
    'validate_email_list',
    'filter_valid_emails',
    'enrich_company_data',
    'batch_enrich_companies',
    'enrich_dataframe',
]

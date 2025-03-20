"""
Web scraping modules for the LeadGen Tool

This package provides various scraper implementations for extracting company
and contact information from different web sources:

- web_scraper: Generic website scraper for contact information
- google_search: Google search integration for company discovery
- linkedin_scraper: LinkedIn scraper for company information (educational purposes only)

Note: All scrapers implement rate limiting to respect website terms of service.
When using these tools, ensure you comply with the target website's robots.txt
and terms of service.
"""

from scraper.web_scraper import scrape_website, WebScraper
from scraper.google_search import search_companies, GoogleSearcher
from scraper.linkedin_scraper import search_linkedin_companies, get_linkedin_company_details, LinkedInScraper

__all__ = [
    'scrape_website',
    'WebScraper',
    'search_companies',
    'GoogleSearcher',
    'search_linkedin_companies',
    'get_linkedin_company_details',
    'LinkedInScraper',
]

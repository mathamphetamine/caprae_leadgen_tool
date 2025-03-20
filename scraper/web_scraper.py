import requests
from bs4 import BeautifulSoup
import logging
import time
import re
from urllib.parse import urljoin, urlparse

from leadgen_tool.utils.config import REQUEST_HEADERS, REQUEST_TIMEOUT
from leadgen_tool.utils.helpers import (
    extract_emails, extract_phones, clean_text, 
    is_valid_url, normalize_url, rate_limit,
    extract_company_name, extract_domain_from_url
)

logger = logging.getLogger(__name__)

class WebScraper:
    """Scraper to extract contact information from websites."""
    
    def __init__(self, max_pages=5, follow_links=True):
        self.max_pages = max_pages
        self.follow_links = follow_links
        self.visited_urls = set()
        self.contact_data = {
            'emails': set(),
            'phones': set(),
            'social_links': set(),
            'contact_page_url': None,
            'company_name': '',
            'address': '',
            'meta_description': '',
            'meta_keywords': '',
        }
    
    @rate_limit
    def _fetch_page(self, url):
        """Fetch a web page with rate limiting."""
        try:
            response = requests.get(url, headers=REQUEST_HEADERS, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return None
    
    def _parse_contact_page(self, html, url):
        """Extract contact information from a contact page."""
        if not html:
            return
        
        soup = BeautifulSoup(html, 'lxml')
        
        # Extract text content
        text_content = soup.get_text()
        clean_content = clean_text(text_content)
        
        # Extract emails and phones from the entire page
        emails = extract_emails(html)
        phones = extract_phones(html)
        
        if emails:
            self.contact_data['emails'].update(emails)
        
        if phones:
            self.contact_data['phones'].update(phones)
        
        # Look for company name if not already found
        if not self.contact_data['company_name']:
            company_name = extract_company_name(clean_content, url)
            if company_name:
                self.contact_data['company_name'] = company_name
        
        # Extract social media links
        social_patterns = [
            r'(https?://(www\.)?linkedin\.com/[^\s"\']+)',
            r'(https?://(www\.)?twitter\.com/[^\s"\']+)',
            r'(https?://(www\.)?facebook\.com/[^\s"\']+)',
            r'(https?://(www\.)?instagram\.com/[^\s"\']+)',
        ]
        
        for pattern in social_patterns:
            social_links = re.findall(pattern, html)
            if social_links:
                self.contact_data['social_links'].update([link[0] for link in social_links])
        
        # Try to find an address (simple implementation)
        address_patterns = [
            r'\d+\s+[A-Za-z\s]+,\s+[A-Za-z\s]+,\s+[A-Z]{2}\s+\d{5}',  # US address
            r'\d+\s+[A-Za-z\s]+,\s+[A-Za-z\s]+,\s+[A-Z]{2}\s+[0-9A-Z]{3}',  # Canadian address
            r'\d+\s+[A-Za-z\s]+,\s+[A-Za-z\s]+\s+[0-9A-Z]{2,8}',  # UK/EU style
        ]
        
        for pattern in address_patterns:
            addresses = re.findall(pattern, clean_content)
            if addresses:
                self.contact_data['address'] = addresses[0]
                break
    
    def _find_contact_links(self, soup, base_url):
        """Find links to contact pages."""
        contact_keywords = ['contact', 'about', 'about-us', 'team', 'people']
        contact_links = []
        
        for link in soup.find_all('a', href=True):
            href = link.get('href', '').lower()
            text = link.get_text().lower()
            
            # Skip empty links, anchors, or javascript
            if not href or href.startswith('#') or href.startswith('javascript:'):
                continue
            
            # Check if link text or href contains contact keywords
            if any(keyword in text or keyword in href for keyword in contact_keywords):
                full_url = normalize_url(base_url, href)
                if is_valid_url(full_url) and full_url not in self.visited_urls:
                    contact_links.append(full_url)
        
        return contact_links
    
    def _extract_meta_info(self, soup):
        """Extract metadata from the page."""
        # Get meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            self.contact_data['meta_description'] = meta_desc.get('content')
        
        # Get meta keywords
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords and meta_keywords.get('content'):
            self.contact_data['meta_keywords'] = meta_keywords.get('content')
    
    def scrape_website(self, url):
        """
        Main method to scrape a website for contact information.
        Returns a dictionary with collected contact data.
        """
        if not is_valid_url(url):
            logger.error(f"Invalid URL: {url}")
            return {}
        
        # Reset data for new website
        self.visited_urls = set()
        self.contact_data = {
            'emails': set(),
            'phones': set(),
            'social_links': set(),
            'contact_page_url': None,
            'company_name': '',
            'address': '',
            'meta_description': '',
            'meta_keywords': '',
            'domain': extract_domain_from_url(url),
            'website_url': url,
        }
        
        # Start with the homepage
        self._scrape_page(url, is_homepage=True)
        
        # Convert sets to lists for JSON serialization
        result = {
            'emails': list(self.contact_data['emails']),
            'phones': list(self.contact_data['phones']),
            'social_links': list(self.contact_data['social_links']),
            'contact_page_url': self.contact_data['contact_page_url'],
            'company_name': self.contact_data['company_name'],
            'address': self.contact_data['address'],
            'meta_description': self.contact_data['meta_description'],
            'meta_keywords': self.contact_data['meta_keywords'],
            'domain': self.contact_data['domain'],
            'website_url': self.contact_data['website_url'],
        }
        
        return result
    
    def _scrape_page(self, url, is_homepage=False):
        """Scrape a single page and follow links if needed."""
        if url in self.visited_urls or len(self.visited_urls) >= self.max_pages:
            return
        
        self.visited_urls.add(url)
        logger.info(f"Scraping {url}")
        
        html = self._fetch_page(url)
        if not html:
            return
        
        soup = BeautifulSoup(html, 'lxml')
        
        # Extract metadata from homepage
        if is_homepage:
            self._extract_meta_info(soup)
            
            # Try to find company name from title
            title = soup.find('title')
            if title and not self.contact_data['company_name']:
                company_name = extract_company_name(title.get_text(), url)
                if company_name:
                    self.contact_data['company_name'] = company_name
        
        # Parse for contact information
        self._parse_contact_page(html, url)
        
        # Find contact page links
        if self.follow_links:
            contact_links = self._find_contact_links(soup, url)
            
            for link in contact_links:
                if 'contact' in link.lower():
                    self.contact_data['contact_page_url'] = link
                    # Prioritize scraping actual contact pages
                    self._scrape_page(link)
                    break
            
            # If no explicit contact page found, follow other potential links
            if not self.contact_data['contact_page_url'] and contact_links:
                for link in contact_links[:min(3, len(contact_links))]:  # Limit to 3 additional pages
                    self._scrape_page(link)

# Functional interface for simpler usage
def scrape_website(url, max_pages=5, follow_links=True):
    """Scrape a website for contact information."""
    scraper = WebScraper(max_pages=max_pages, follow_links=follow_links)
    return scraper.scrape_website(url)

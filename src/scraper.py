import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
import random
from fake_useragent import UserAgent
import validators
from urllib.parse import urlparse, urljoin
import os
from urllib.robotparser import RobotFileParser

class LeadScraper:
    """A class for scraping and processing lead data from websites."""
    
    def __init__(self, respect_robots_txt=True):
        """
        Initialize the lead scraper with default settings.
        
        Args:
            respect_robots_txt (bool): Whether to check and respect robots.txt rules
        """
        self.user_agent = UserAgent()
        self.headers = {'User-Agent': self.user_agent.random}
        self.rate_limit = 2  # seconds between requests
        self.respect_robots_txt = respect_robots_txt
        self.robot_parsers = {}  # Cache for robot parsers
    
    def validate_url(self, url):
        """
        Validate if the provided URL is properly formatted.
        
        Args:
            url (str): URL to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        return validators.url(url)
    
    def _check_robots_txt(self, url):
        """
        Check if scraping is allowed by robots.txt.
        
        Args:
            url (str): URL to check
            
        Returns:
            bool: True if scraping is allowed, False otherwise
        """
        if not self.respect_robots_txt:
            return True
            
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        robots_url = f"{base_url}/robots.txt"
        
        # Check if we already have a parser for this domain
        if base_url in self.robot_parsers:
            rp = self.robot_parsers[base_url]
        else:
            # Create a new parser
            rp = RobotFileParser()
            rp.set_url(robots_url)
            try:
                rp.read()
                self.robot_parsers[base_url] = rp
            except Exception:
                # If we can't read robots.txt, assume scraping is allowed
                return True
        
        # Check if user agent is allowed to fetch the URL
        user_agent = self.headers['User-Agent']
        return rp.can_fetch(user_agent, url)
    
    def scrape_website(self, url, max_pages=1, depth=0):
        """
        Scrape a website for potential lead information.
        
        Args:
            url (str): The URL to scrape
            max_pages (int): Maximum number of pages to scrape
            depth (int): Current crawling depth
            
        Returns:
            list: List of scraped lead data
        """
        if not self.validate_url(url):
            return {"error": "Invalid URL format"}
        
        # Check if scraping is allowed by robots.txt
        if not self._check_robots_txt(url):
            return {"error": "Scraping not allowed by robots.txt"}
        
        leads = []
        
        try:
            # Apply rate limiting
            time.sleep(self.rate_limit)
            
            # Make request with error handling and retries
            response = None
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = requests.get(url, headers=self.headers, timeout=10)
                    response.raise_for_status()  # Raise exception for 4XX/5XX responses
                    break
                except requests.exceptions.RequestException as e:
                    if attempt < max_retries - 1:
                        # Exponential backoff
                        wait_time = 2 ** attempt
                        time.sleep(wait_time)
                    else:
                        return {"error": f"Failed to access website after {max_retries} attempts: {str(e)}"}
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract company information
            company_leads = self._extract_company_info(soup, url)
            leads.extend(company_leads)
            
            # Extract contact information for all leads
            for lead in leads:
                self._extract_contact_info(soup, lead)
            
            # Crawl additional pages if needed
            if max_pages > 1 and depth < max_pages - 1:
                # Find internal links
                internal_links = self._find_internal_links(soup, url)
                
                # Limit the number of links to process
                internal_links = internal_links[:max_pages - 1]
                
                # Recursively scrape each link
                for link in internal_links:
                    link_leads = self.scrape_website(link, max_pages, depth + 1)
                    if isinstance(link_leads, list):
                        leads.extend(link_leads)
            
            return leads
            
        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}
    
    def _find_internal_links(self, soup, base_url):
        """
        Find internal links on the page for crawling.
        
        Args:
            soup (BeautifulSoup): Parsed HTML
            base_url (str): Base URL for resolving relative links
            
        Returns:
            list: List of internal URLs
        """
        parsed_base = urlparse(base_url)
        base_domain = parsed_base.netloc
        
        internal_links = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            full_url = urljoin(base_url, href)
            
            # Check if it's an internal link
            parsed_url = urlparse(full_url)
            if parsed_url.netloc == base_domain and parsed_url.scheme in ('http', 'https'):
                # Avoid duplicates and the current page
                if full_url != base_url and full_url not in internal_links:
                    internal_links.append(full_url)
        
        return internal_links
    
    def _extract_company_info(self, soup, base_url):
        """
        Extract company information from the webpage.
        
        This method attempts to find company names, descriptions, and other
        company-specific information from various common HTML patterns.
        
        Args:
            soup (BeautifulSoup): Parsed HTML
            base_url (str): URL being scraped
            
        Returns:
            list: List of lead dictionaries
        """
        domain = urlparse(base_url).netloc
        leads = []
        
        # Company information might be in various elements
        # Try to find company name
        potential_names = []
        for tag in ['h1', 'h2', '.company-name', '.org-name', '[itemprop="name"]', '.logo alt']:
            elements = soup.select(tag)
            for element in elements:
                if element.text.strip():
                    potential_names.append(element.text.strip())
        
        # Try to find company description
        descriptions = []
        for tag in ['meta[name="description"]', 'meta[property="og:description"]', 
                   '.company-description', '.about-us', '[itemprop="description"]']:
            elements = soup.select(tag)
            for element in elements:
                if tag.startswith('meta'):
                    content = element.get('content', '')
                    if content:
                        descriptions.append(content)
                else:
                    if element.text.strip():
                        descriptions.append(element.text.strip())
        
        # Try to find industry/keywords
        keywords = []
        meta_keywords = soup.select_one('meta[name="keywords"]')
        if meta_keywords and meta_keywords.get('content'):
            keywords = [k.strip() for k in meta_keywords.get('content').split(',')]
        
        # Create a lead entry for the company
        company_name = potential_names[0] if potential_names else domain
        company_description = descriptions[0] if descriptions else ""
        
        lead = {
            'Company Name': company_name,
            'Website': base_url,
            'Domain': domain,
            'Description': company_description[:200] + "..." if len(company_description) > 200 else company_description,
            'Industry/Keywords': ", ".join(keywords[:5]) if keywords else "",
            'Contact Name': "",
            'Job Title': "",
            'Email': "",
            'Phone': "",
            'Location': "",
        }
        
        leads.append(lead)
        return leads
    
    def _extract_contact_info(self, soup, lead):
        """
        Extract contact information from the webpage and update the lead.
        
        Args:
            soup (BeautifulSoup): Parsed HTML
            lead (dict): Lead dictionary to update
        """
        # Try to find contact names (often in team/about sections)
        names = []
        for tag in ['.team-member', '.employee', '[itemprop="employee"]', '.staff', '.contact-person']:
            elements = soup.select(tag)
            for element in elements:
                name_element = element.select_one('.name') or element.select_one('h3') or element
                if name_element and name_element.text.strip():
                    names.append(name_element.text.strip())
        
        # Try to find emails using regex pattern
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, soup.text)
        
        # Try to find phone numbers with various formats
        phone_patterns = [
            r'(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}',  # US/Canada: (123) 456-7890
            r'(\+\d{1,3}\s?)?(\d{1,4}[\s.-]?){2,4}',  # International: +44 20 1234 5678
        ]
        phones = []
        for pattern in phone_patterns:
            phones.extend(re.findall(pattern, soup.text))
        
        # Try to find location
        locations = []
        for tag in ['[itemprop="address"]', '.address', '.location', '.contact-info']:
            elements = soup.select(tag)
            for element in elements:
                if element.text.strip():
                    locations.append(element.text.strip())
        
        # Update the lead with contact information
        if names:
            lead['Contact Name'] = names[0]
        if emails:
            # Filter out common no-reply emails
            valid_emails = [e for e in emails if not e.startswith(('noreply', 'no-reply', 'donotreply'))]
            if valid_emails:
                lead['Email'] = valid_emails[0]
        if phones:
            # Take first phone number and clean it
            if isinstance(phones[0], tuple):
                # Handle tuple result from regex groups
                lead['Phone'] = phones[0][0] if phones[0][0] else phones[0][-1]
            else:
                lead['Phone'] = phones[0]
        if locations:
            lead['Location'] = locations[0]
        
        # Try to find job titles near contact names
        if lead['Contact Name']:
            job_titles = []
            for tag in ['.job-title', '.title', '.position']:
                elements = soup.select(tag)
                for element in elements:
                    if element.text.strip():
                        job_titles.append(element.text.strip())
            if job_titles:
                lead['Job Title'] = job_titles[0]
    
    def filter_leads(self, leads, keywords=None, exclude_keywords=None, min_data_points=3, advanced_filters=None):
        """
        Filter leads based on keywords and data quality.
        
        Args:
            leads (list): List of lead dictionaries
            keywords (list): Keywords to include
            exclude_keywords (list): Keywords to exclude
            min_data_points (int): Minimum number of non-empty fields required
            advanced_filters (dict): Advanced filtering options (field-specific criteria)
            
        Returns:
            list: Filtered leads
        """
        if not leads:
            return []
        
        filtered_leads = []
        
        for lead in leads:
            # Skip leads with error messages
            if isinstance(lead, dict) and 'error' in lead:
                continue
                
            # Check for minimum data points
            non_empty_fields = sum(1 for v in lead.values() if v)
            if non_empty_fields < min_data_points:
                continue
            
            # Check for required keywords
            if keywords:
                text = ' '.join(str(v) for v in lead.values()).lower()
                if not any(k.lower() in text for k in keywords):
                    continue
            
            # Check for excluded keywords
            if exclude_keywords:
                text = ' '.join(str(v) for v in lead.values()).lower()
                if any(k.lower() in text for k in exclude_keywords):
                    continue
            
            # Apply advanced filters if provided
            if advanced_filters:
                skip_lead = False
                for field, criteria in advanced_filters.items():
                    if field in lead:
                        field_value = lead[field].lower()
                        if 'contains' in criteria and not any(c.lower() in field_value for c in criteria['contains']):
                            skip_lead = True
                            break
                        if 'not_contains' in criteria and any(c.lower() in field_value for c in criteria['not_contains']):
                            skip_lead = True
                            break
                        if 'regex' in criteria and not re.search(criteria['regex'], lead[field], re.IGNORECASE):
                            skip_lead = True
                            break
                if skip_lead:
                    continue
            
            filtered_leads.append(lead)
        
        return filtered_leads
    
    def validate_and_clean_data(self, leads):
        """
        Validate and clean lead data.
        
        Args:
            leads (list): List of lead dictionaries
            
        Returns:
            list: Cleaned leads
        """
        if not leads:
            return []
        
        cleaned_leads = []
        seen_emails = set()
        seen_companies = set()
        
        for lead in leads:
            # Skip leads with error messages
            if isinstance(lead, dict) and 'error' in lead:
                continue
            
            # Make a copy to avoid modifying the original
            clean_lead = lead.copy()
            
            # Validate email
            if 'Email' in clean_lead and clean_lead['Email']:
                if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', clean_lead['Email']):
                    clean_lead['Email'] = ""
                elif clean_lead['Email'] in seen_emails:
                    continue  # Skip duplicate email
                else:
                    seen_emails.add(clean_lead['Email'])
            
            # Check for duplicate company
            company_key = (clean_lead.get('Company Name', ''), clean_lead.get('Website', ''))
            if company_key in seen_companies:
                continue
            seen_companies.add(company_key)
            
            # Clean up text fields
            for key in clean_lead:
                if isinstance(clean_lead[key], str):
                    # Remove excessive whitespace
                    clean_lead[key] = re.sub(r'\s+', ' ', clean_lead[key]).strip()
                    
                    # Truncate overly long fields
                    if len(clean_lead[key]) > 500:
                        clean_lead[key] = clean_lead[key][:497] + "..."
            
            cleaned_leads.append(clean_lead)
        
        return cleaned_leads
    
    def export_to_csv(self, leads, filename="leads.csv"):
        """
        Export leads to a CSV file.
        
        Args:
            leads (list): List of lead dictionaries
            filename (str): Output filename
            
        Returns:
            str: Path to the exported file or error message
        """
        if not leads:
            return None
        
        try:
            # Ensure directory exists
            directory = os.path.dirname(filename)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            
            df = pd.DataFrame(leads)
            df.to_csv(filename, index=False)
            return filename
        except (PermissionError, OSError) as e:
            return f"Error writing to file: {str(e)}"

    def analyze_leads(self, leads):
        """
        Perform basic analysis on the lead data.
        
        Args:
            leads (list): List of lead dictionaries
            
        Returns:
            dict: Analysis results
        """
        if not leads:
            return {"total": 0}
        
        analysis = {
            "total": len(leads),
            "with_email": sum(1 for lead in leads if lead.get('Email')),
            "with_phone": sum(1 for lead in leads if lead.get('Phone')),
            "with_contact_name": sum(1 for lead in leads if lead.get('Contact Name')),
            "with_job_title": sum(1 for lead in leads if lead.get('Job Title')),
            "industries": {},
            "domains": {},
        }
        
        # Count industries
        for lead in leads:
            # Process industries
            industries = lead.get('Industry/Keywords', '').split(',')
            for industry in industries:
                industry = industry.strip()
                if industry:
                    analysis["industries"][industry] = analysis["industries"].get(industry, 0) + 1
            
            # Process domains
            domain = lead.get('Domain', '')
            if domain:
                analysis["domains"][domain] = analysis["domains"].get(domain, 0) + 1
        
        # Sort industries by count
        analysis["top_industries"] = sorted(
            analysis["industries"].items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]
        
        # Sort domains by count
        analysis["top_domains"] = sorted(
            analysis["domains"].items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]
        
        return analysis

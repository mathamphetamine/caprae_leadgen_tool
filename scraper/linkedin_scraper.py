import logging
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

from utils.config import REQUEST_HEADERS, LINKEDIN_LOGIN_REQUIRED
from utils.helpers import rate_limit

logger = logging.getLogger(__name__)

class LinkedInScraper:
    """
    LinkedIn scraper for educational purposes only.
    
    WARNING: Using this scraper may violate LinkedIn's Terms of Service.
    This is provided for educational purposes only, and users should ensure
    they comply with LinkedIn's robots.txt and Terms of Service.
    """
    
    def __init__(self, headless=True):
        self.headless = headless
        self.driver = None
        self.logged_in = False
        
        # Print warning about LinkedIn ToS
        logger.warning(
            "WARNING: Using the LinkedIn scraper may violate LinkedIn's Terms of Service. "
            "This is provided for educational purposes only. "
            "Users should ensure they comply with LinkedIn's robots.txt and Terms of Service."
        )
    
    def _initialize_driver(self):
        """Initialize Selenium WebDriver for Chrome."""
        if self.driver:
            return
            
        try:
            options = Options()
            if self.headless:
                options.add_argument('--headless')
            
            # Add user agent
            options.add_argument(f"user-agent={REQUEST_HEADERS['User-Agent']}")
            
            # Disable images for faster loading
            options.add_argument('--blink-settings=imagesEnabled=false')
            
            # Initialize Chrome WebDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            
            # Set window size
            self.driver.set_window_size(1920, 1080)
            
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {str(e)}")
            raise
    
    def login(self, username, password):
        """
        Login to LinkedIn with credentials.
        
        Note: This method is for educational purposes only.
        Using automated tools to access LinkedIn may violate their Terms of Service.
        """
        if not LINKEDIN_LOGIN_REQUIRED:
            logger.warning("LinkedIn login functionality is disabled in config")
            return False
            
        if not username or not password:
            logger.error("LinkedIn credentials not provided")
            return False
            
        try:
            self._initialize_driver()
            
            # Navigate to LinkedIn login page
            self.driver.get('https://www.linkedin.com/login')
            
            # Wait for login form to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'username'))
            )
            
            # Fill in credentials
            self.driver.find_element(By.ID, 'username').send_keys(username)
            self.driver.find_element(By.ID, 'password').send_keys(password)
            
            # Submit form
            self.driver.find_element(By.XPATH, '//button[@type="submit"]').click()
            
            # Wait for login to complete
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.url_contains('linkedin.com/feed')
                )
                self.logged_in = True
                logger.info("Successfully logged in to LinkedIn")
                return True
            except TimeoutException:
                logger.error("Failed to login to LinkedIn - timeout waiting for feed page")
                return False
                
        except Exception as e:
            logger.error(f"LinkedIn login failed: {str(e)}")
            return False
    
    def close(self):
        """Close the WebDriver."""
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.logged_in = False
    
    @rate_limit
    def search_companies(self, query, max_results=5):
        """
        Search for companies on LinkedIn.
        
        Note: This method is for educational purposes only.
        """
        if not LINKEDIN_LOGIN_REQUIRED:
            logger.warning("LinkedIn functionality is disabled in config")
            return []
            
        results = []
        try:
            self._initialize_driver()
            
            # Check if logged in
            if not self.logged_in:
                logger.warning("Not logged in to LinkedIn. Some features may be limited.")
            
            # Navigate to LinkedIn search page
            search_url = f"https://www.linkedin.com/search/results/companies/?keywords={query.replace(' ', '%20')}"
            self.driver.get(search_url)
            
            # Wait for search results to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'search-results__list'))
            )
            
            # Extract company cards
            company_cards = self.driver.find_elements(By.XPATH, "//li[contains(@class, 'reusable-search__result-container')]")
            
            for i, card in enumerate(company_cards[:max_results]):
                try:
                    company_data = {}
                    
                    # Extract company name
                    name_elem = card.find_element(By.XPATH, ".//span[@dir='ltr']")
                    company_data['company_name'] = name_elem.text.strip()
                    
                    # Extract LinkedIn URL
                    link_elem = card.find_element(By.XPATH, ".//a[contains(@class, 'app-aware-link')]")
                    company_data['linkedin_url'] = link_elem.get_attribute('href')
                    
                    # Extract description if available
                    try:
                        desc_elem = card.find_element(By.XPATH, ".//p[contains(@class, 'entity-result__summary')]")
                        company_data['description'] = desc_elem.text.strip()
                    except NoSuchElementException:
                        company_data['description'] = ""
                    
                    results.append(company_data)
                    
                except Exception as e:
                    logger.debug(f"Error extracting company data: {str(e)}")
                    continue
            
            return results
            
        except Exception as e:
            logger.error(f"LinkedIn company search failed: {str(e)}")
            return results
    
    @rate_limit
    def get_company_details(self, linkedin_url):
        """
        Get detailed information about a company from its LinkedIn page.
        
        Note: This method is for educational purposes only.
        """
        if not LINKEDIN_LOGIN_REQUIRED:
            logger.warning("LinkedIn functionality is disabled in config")
            return {}
            
        if not linkedin_url or 'linkedin.com/company/' not in linkedin_url:
            logger.error(f"Invalid LinkedIn company URL: {linkedin_url}")
            return {}
            
        company_data = {'linkedin_url': linkedin_url}
        
        try:
            self._initialize_driver()
            
            # Navigate to the company page
            self.driver.get(linkedin_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//h1[contains(@class, 'org-top-card-summary__title')]"))
            )
            
            # Extract company name
            try:
                name_elem = self.driver.find_element(By.XPATH, "//h1[contains(@class, 'org-top-card-summary__title')]")
                company_data['company_name'] = name_elem.text.strip()
            except NoSuchElementException:
                pass
            
            # Extract company website
            try:
                website_elem = self.driver.find_element(By.XPATH, "//a[contains(@class, 'org-top-card-primary-actions__action') and contains(@href, 'http')]")
                company_data['website_url'] = website_elem.get_attribute('href')
            except NoSuchElementException:
                pass
            
            # Extract company description
            try:
                about_section = self.driver.find_element(By.XPATH, "//p[contains(@class, 'org-about-us-organization-description__text')]")
                company_data['description'] = about_section.text.strip()
            except NoSuchElementException:
                pass
            
            # Extract company size, industry, etc.
            try:
                info_sections = self.driver.find_elements(By.XPATH, "//dd[contains(@class, 'org-about-company-module__company-size-definition-text')]")
                
                # Extract company size
                if len(info_sections) > 0:
                    company_data['company_size'] = info_sections[0].text.strip()
                
                # Extract industry
                if len(info_sections) > 2:
                    company_data['industry'] = info_sections[2].text.strip()
            except NoSuchElementException:
                pass
            
            return company_data
            
        except Exception as e:
            logger.error(f"Error getting LinkedIn company details: {str(e)}")
            return company_data
    
    def __del__(self):
        """Ensure driver is closed when object is destroyed."""
        self.close()

# Functional interface for simpler usage
def search_linkedin_companies(query, max_results=5):
    """
    Search for companies on LinkedIn.
    
    Note: This function is for educational purposes only.
    Using automated tools to access LinkedIn may violate their Terms of Service.
    """
    if not LINKEDIN_LOGIN_REQUIRED:
        logger.warning("LinkedIn functionality is disabled in config")
        return []
        
    scraper = LinkedInScraper()
    try:
        return scraper.search_companies(query, max_results)
    finally:
        scraper.close()

def get_linkedin_company_details(linkedin_url):
    """
    Get detailed information about a company from its LinkedIn page.
    
    Note: This function is for educational purposes only.
    Using automated tools to access LinkedIn may violate their Terms of Service.
    """
    if not LINKEDIN_LOGIN_REQUIRED:
        logger.warning("LinkedIn functionality is disabled in config")
        return {}
        
    scraper = LinkedInScraper()
    try:
        return scraper.get_company_details(linkedin_url)
    finally:
        scraper.close()

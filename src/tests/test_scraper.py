import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from scraper import LeadScraper

class TestLeadScraper(unittest.TestCase):
    """Test cases for the LeadScraper class."""
    
    def setUp(self):
        """Set up the test environment."""
        self.scraper = LeadScraper()
    
    def test_url_validation(self):
        """Test URL validation functionality."""
        # Valid URLs
        self.assertTrue(self.scraper.validate_url("https://example.com"))
        self.assertTrue(self.scraper.validate_url("http://test.com/about"))
        
        # Invalid URLs
        self.assertFalse(self.scraper.validate_url("example"))
        self.assertFalse(self.scraper.validate_url("www.example"))
        self.assertFalse(self.scraper.validate_url(""))
    
    def test_robots_txt_checking(self):
        """Test robots.txt checking functionality."""
        # Create a scraper that respects robots.txt
        scraper_with_robots = LeadScraper(respect_robots_txt=True)
        # Create a scraper that ignores robots.txt
        scraper_without_robots = LeadScraper(respect_robots_txt=False)
        
        # Test when robots.txt check is disabled
        self.assertTrue(scraper_without_robots._check_robots_txt("https://example.com"))
        
        # Mock the RobotFileParser
        with patch('scraper.RobotFileParser') as mock_rp:
            # Configure mock to disallow scraping
            mock_instance = MagicMock()
            mock_instance.can_fetch.return_value = False
            mock_rp.return_value = mock_instance
            
            # Test when robots.txt disallows scraping
            self.assertFalse(scraper_with_robots._check_robots_txt("https://example.com/disallowed"))
            
            # Configure mock to allow scraping
            mock_instance.can_fetch.return_value = True
            
            # Test when robots.txt allows scraping
            self.assertTrue(scraper_with_robots._check_robots_txt("https://example.com/allowed"))
    
    def test_filter_leads(self):
        """Test lead filtering functionality."""
        test_leads = [
            {
                'Company Name': 'Tech Solutions',
                'Industry/Keywords': 'software, technology',
                'Description': 'A software company',
                'Email': 'contact@techsolutions.com',
                'Phone': '123-456-7890'
            },
            {
                'Company Name': 'Marketing Agency',
                'Industry/Keywords': 'marketing, advertising',
                'Description': 'A marketing firm',
                'Email': '',
                'Phone': ''
            }
        ]
        
        # Test filtering with keywords
        filtered = self.scraper.filter_leads(test_leads, keywords=["software"])
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]['Company Name'], 'Tech Solutions')
        
        # Test filtering with exclude keywords
        filtered = self.scraper.filter_leads(test_leads, exclude_keywords=["marketing"])
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]['Company Name'], 'Tech Solutions')
        
        # Test filtering with minimum data points
        filtered = self.scraper.filter_leads(test_leads, min_data_points=5)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]['Company Name'], 'Tech Solutions')
        
        # Test with advanced filters
        advanced_filters = {
            'Industry/Keywords': {
                'contains': ['technology']
            }
        }
        filtered = self.scraper.filter_leads(test_leads, advanced_filters=advanced_filters)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]['Company Name'], 'Tech Solutions')
        
        # Test with advanced filters - multiple conditions
        advanced_filters = {
            'Company Name': {
                'contains': ['Agency'],
                'not_contains': ['Tech']
            }
        }
        filtered = self.scraper.filter_leads(test_leads, advanced_filters=advanced_filters)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]['Company Name'], 'Marketing Agency')
    
    def test_validate_and_clean_data(self):
        """Test data validation and cleaning functionality."""
        test_leads = [
            {
                'Company Name': 'Tech Solutions',
                'Website': 'example.com',
                'Email': 'contact@techsolutions.com',
                'Description': 'A  company  with  extra  spaces'
            },
            {
                'Company Name': 'Invalid Email Corp',
                'Website': 'different.com',
                'Email': 'not-an-email',
                'Description': 'Company with invalid email'
            },
            {
                'Company Name': 'Tech Solutions',  # Duplicate company
                'Website': 'example.com',  # Same website as first one
                'Email': 'another@techsolutions.com',
                'Description': 'Duplicate company'
            }
        ]
        
        cleaned = self.scraper.validate_and_clean_data(test_leads)
        
        # Should have 2 leads: the first one, and the second one with a blank email
        # The third one should be removed as a duplicate
        self.assertEqual(len(cleaned), 2)
        
        # Check if spaces were normalized
        self.assertEqual(cleaned[0]['Description'], 'A company with extra spaces')
        
        # Check that the invalid email was blanked out
        self.assertEqual(cleaned[1]['Email'], '')
        
        # Verify the duplicate company was removed by checking the remaining companies
        company_names = [lead['Company Name'] for lead in cleaned]
        self.assertIn('Tech Solutions', company_names)
        self.assertIn('Invalid Email Corp', company_names)
        self.assertEqual(company_names.count('Tech Solutions'), 1, "Duplicate company not removed")
    
    def test_export_to_csv(self):
        """Test CSV export functionality."""
        test_leads = [
            {
                'Company Name': 'Test Company',
                'Email': 'test@example.com'
            }
        ]
        
        # Create a temporary directory for testing
        test_dir = 'test_export'
        test_file = os.path.join(test_dir, 'test_leads.csv')
        
        try:
            # Test successful export
            result = self.scraper.export_to_csv(test_leads, test_file)
            self.assertEqual(result, test_file)
            self.assertTrue(os.path.exists(test_file))
            
            # Test with empty leads
            result = self.scraper.export_to_csv([], test_file)
            self.assertIsNone(result)
            
        finally:
            # Clean up test files
            if os.path.exists(test_file):
                os.remove(test_file)
            if os.path.exists(test_dir):
                os.rmdir(test_dir)
    
    def test_find_internal_links(self):
        """Test finding internal links for crawling."""
        # Create a sample HTML with various links
        html = """
        <html>
        <body>
            <a href="https://example.com/page1">Internal Link 1</a>
            <a href="/page2">Relative Link</a>
            <a href="https://different-domain.com">External Link</a>
            <a href="https://example.com">Same as base URL</a>
        </body>
        </html>
        """
        
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        base_url = "https://example.com"
        
        links = self.scraper._find_internal_links(soup, base_url)
        
        # Should find 1 internal link (the first one)
        # The second one should be resolved to example.com/page2
        # The third one should be filtered out (external)
        # The fourth one should be filtered out (same as base URL)
        self.assertEqual(len(links), 2)
        self.assertIn("https://example.com/page1", links)
        self.assertIn("https://example.com/page2", links)
        self.assertNotIn("https://different-domain.com", links)
        self.assertNotIn(base_url, links)
    
    def test_analyze_leads(self):
        """Test lead analysis functionality."""
        test_leads = [
            {
                'Company Name': 'Tech Company',
                'Domain': 'tech.com',
                'Industry/Keywords': 'software, technology',
                'Email': 'contact@tech.com',
                'Phone': '123-456-7890',
                'Contact Name': 'John Doe',
                'Job Title': 'CEO'
            },
            {
                'Company Name': 'Marketing Agency',
                'Domain': 'marketing.com',
                'Industry/Keywords': 'marketing, advertising',
                'Email': 'info@marketing.com',
                'Phone': '',
                'Contact Name': '',
                'Job Title': ''
            }
        ]
        
        analysis = self.scraper.analyze_leads(test_leads)
        
        # Check basic counts
        self.assertEqual(analysis['total'], 2)
        self.assertEqual(analysis['with_email'], 2)
        self.assertEqual(analysis['with_phone'], 1)
        self.assertEqual(analysis['with_contact_name'], 1)
        self.assertEqual(analysis['with_job_title'], 1)
        
        # Check industry analysis
        self.assertIn('software', analysis['industries'])
        self.assertIn('technology', analysis['industries'])
        self.assertIn('marketing', analysis['industries'])
        self.assertIn('advertising', analysis['industries'])
        
        # Check domain analysis
        self.assertIn('tech.com', analysis['domains'])
        self.assertIn('marketing.com', analysis['domains'])
        
        # Check top lists
        self.assertEqual(len(analysis['top_industries']), min(4, 5))  # 4 industries or max 5
        self.assertEqual(len(analysis['top_domains']), 2)  # 2 domains

if __name__ == '__main__':
    unittest.main() 
import re
import logging
import pandas as pd

from leadgen_tool.utils.helpers import extract_domain_from_url
from leadgen_tool.scraper.web_scraper import scrape_website
from leadgen_tool.enricher.email_validator import filter_valid_emails

logger = logging.getLogger(__name__)

class DataEnricher:
    """Enrich contact data with additional information."""
    
    def __init__(self):
        pass
    
    def generate_company_email_patterns(self, domain, name=None):
        """Generate potential email patterns for a company domain."""
        if not domain:
            return []
            
        # Common email patterns
        patterns = []
        
        # General patterns
        patterns.extend([
            f"info@{domain}",
            f"contact@{domain}",
            f"sales@{domain}",
            f"support@{domain}",
            f"hello@{domain}",
        ])
        
        # Person-specific patterns if name is provided
        if name:
            first, last = self._split_name(name)
            if first and last:
                patterns.extend([
                    f"{first}@{domain}",
                    f"{last}@{domain}",
                    f"{first}.{last}@{domain}",
                    f"{first[0]}{last}@{domain}",
                    f"{first}{last[0]}@{domain}",
                    f"{first}_{last}@{domain}",
                ])
        
        return patterns
    
    def _split_name(self, name):
        """Split a full name into first and last name."""
        if not name:
            return None, None
            
        parts = name.strip().split()
        if len(parts) == 1:
            return parts[0].lower(), ""
        elif len(parts) >= 2:
            return parts[0].lower(), parts[-1].lower()
        return None, None
    
    def enrich_company_data(self, company_data):
        """
        Enrich company data with additional information.
        Input should be a dictionary with at least 'website_url' or 'domain'.
        """
        if not company_data:
            return company_data
            
        # Ensure we have a domain
        if not company_data.get('domain') and company_data.get('website_url'):
            company_data['domain'] = extract_domain_from_url(company_data['website_url'])
        
        # If we don't have website data yet, scrape it
        if company_data.get('website_url') and not company_data.get('emails'):
            scraped_data = scrape_website(company_data['website_url'])
            # Merge scraped data with existing data
            for key, value in scraped_data.items():
                if key not in company_data or not company_data[key]:
                    company_data[key] = value
        
        # Generate potential email patterns if we have a domain but no emails
        if company_data.get('domain') and not company_data.get('emails'):
            patterns = self.generate_company_email_patterns(company_data['domain'])
            # Validate these email patterns
            valid_patterns = filter_valid_emails(patterns)
            if valid_patterns:
                company_data['potential_emails'] = valid_patterns
        
        # Try to improve company name extraction if not already present
        if not company_data.get('company_name') and company_data.get('domain'):
            domain_parts = company_data['domain'].split('.')
            if domain_parts:
                # Use the first part of the domain as company name
                company_data['company_name'] = domain_parts[0].title()
        
        return company_data
    
    def batch_enrich(self, company_list):
        """Enrich a list of company data dictionaries."""
        enriched_data = []
        for company in company_list:
            enriched_data.append(self.enrich_company_data(company))
        return enriched_data
    
    def enrich_from_dataframe(self, df, website_col='website', name_col=None, domain_col=None):
        """
        Enrich data from a pandas DataFrame.
        Returns a new DataFrame with enriched information.
        """
        if df.empty:
            return df
            
        # Create a list of company data dictionaries
        company_list = []
        for _, row in df.iterrows():
            company = {}
            
            # Extract required fields
            if website_col in df.columns and pd.notna(row[website_col]):
                company['website_url'] = row[website_col]
            
            if domain_col in df.columns and pd.notna(row[domain_col]):
                company['domain'] = row[domain_col]
            elif 'website_url' in company:
                company['domain'] = extract_domain_from_url(company['website_url'])
            
            if name_col in df.columns and pd.notna(row[name_col]):
                company['company_name'] = row[name_col]
                
            # Include all other columns as is
            for col in df.columns:
                if col not in company and pd.notna(row[col]):
                    company[col] = row[col]
                    
            company_list.append(company)
        
        # Enrich the company data
        enriched_list = self.batch_enrich(company_list)
        
        # Convert back to DataFrame
        return pd.DataFrame(enriched_list)

# Functional interface for simpler usage
def enrich_company_data(company_data):
    """Enrich a single company's data."""
    enricher = DataEnricher()
    return enricher.enrich_company_data(company_data)

def batch_enrich_companies(company_list):
    """Enrich multiple companies' data."""
    enricher = DataEnricher()
    return enricher.batch_enrich(company_list)

def enrich_dataframe(df, website_col='website', name_col=None, domain_col=None):
    """Enrich data from a pandas DataFrame."""
    enricher = DataEnricher()
    return enricher.enrich_from_dataframe(df, website_col, name_col, domain_col)

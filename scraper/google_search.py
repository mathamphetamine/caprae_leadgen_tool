import requests
import logging
import json
import time
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from leadgen_tool.utils.config import GOOGLE_API_KEY, GOOGLE_CSE_ID, REQUEST_HEADERS, REQUEST_TIMEOUT
from leadgen_tool.utils.helpers import rate_limit, extract_domain_from_url

logger = logging.getLogger(__name__)

class GoogleSearcher:
    """Class to handle Google search queries."""
    
    def __init__(self, api_key=None, cse_id=None):
        self.api_key = api_key or GOOGLE_API_KEY
        self.cse_id = cse_id or GOOGLE_CSE_ID
        self.service = None
        
        if self.api_key and self.cse_id:
            try:
                self.service = build("customsearch", "v1", developerKey=self.api_key)
            except Exception as e:
                logger.error(f"Error initializing Google Custom Search API: {str(e)}")
                self.service = None
    
    @rate_limit
    def _search_with_api(self, query, num_results=10):
        """Search using Google Custom Search API."""
        if not self.service:
            logger.warning("Google Custom Search API not initialized")
            return self._fallback_search(query, num_results)
        
        try:
            # Execute search
            result = self.service.cse().list(
                q=query,
                cx=self.cse_id,
                num=num_results
            ).execute()
            
            items = result.get('items', [])
            return [
                {
                    'title': item.get('title', ''),
                    'link': item.get('link', ''),
                    'snippet': item.get('snippet', ''),
                    'domain': extract_domain_from_url(item.get('link', ''))
                }
                for item in items
            ]
        except HttpError as e:
            logger.error(f"Google Custom Search API error: {str(e)}")
            return self._fallback_search(query, num_results)
    
    @rate_limit
    def _fallback_search(self, query, num_results=10):
        """Fallback to scraping search results (use with caution, may violate ToS)."""
        logger.warning("Using fallback search method")
        try:
            # Format query for URL
            formatted_query = query.replace(' ', '+')
            url = f"https://www.googleapis.com/customsearch/v1?key={self.api_key}&cx={self.cse_id}&q={formatted_query}"
            
            response = requests.get(url, headers=REQUEST_HEADERS, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            
            result = response.json()
            items = result.get('items', [])
            
            return [
                {
                    'title': item.get('title', ''),
                    'link': item.get('link', ''),
                    'snippet': item.get('snippet', ''),
                    'domain': extract_domain_from_url(item.get('link', ''))
                }
                for item in items
            ]
        except Exception as e:
            logger.error(f"Fallback search error: {str(e)}")
            return []
    
    def search_companies(self, query, num_results=10, filter_domains=None):
        """
        Search for companies based on the query.
        Optionally filter results by domain extensions.
        """
        if not query:
            return []
        
        # Add "company" to the query if not already present
        if "company" not in query.lower() and "business" not in query.lower():
            query = f"{query} company"
        
        results = self._search_with_api(query, num_results)
        
        # Filter by domain extensions if specified
        if filter_domains:
            filtered_results = []
            for result in results:
                domain = result.get('domain', '')
                if any(domain.endswith(ext) for ext in filter_domains):
                    filtered_results.append(result)
            return filtered_results
        
        return results

# Functional interface for simpler usage
def search_companies(query, num_results=10, filter_domains=None, api_key=None, cse_id=None):
    """Search for companies based on the query."""
    searcher = GoogleSearcher(api_key, cse_id)
    return searcher.search_companies(query, num_results, filter_domains)

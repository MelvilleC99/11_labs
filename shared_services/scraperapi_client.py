"""
ScraperAPI client setup and configuration
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

class ScraperAPIClient:
    def __init__(self):
        self.api_key = os.getenv('SCRAPERAPI_KEY')
        self._initialized = False
        
        if not self.api_key:
            print("⚠️  Warning: SCRAPERAPI_KEY not found in environment variables")
            print("⚠️  Scraping functionality will be disabled")
            return
        
        self.base_url = 'http://api.scraperapi.com/'
        self.default_params = {
            'api_key': self.api_key,
            'render': True,
            'country_code': 'us',
            'device_type': 'desktop',
            'timeout': 30000
        }
        self._initialized = True
    
    def is_available(self):
        """Check if the client is properly initialized"""
        return self._initialized and self.api_key is not None
    
    def scrape_url(self, url, custom_params=None):
        """
        Scrape a single URL using ScraperAPI
        
        Args:
            url (str): URL to scrape
            custom_params (dict): Additional parameters to override defaults
            
        Returns:
            dict: Response with success status, html content, and metadata
        """
        if not self.is_available():
            return {
                'success': False,
                'status_code': None,
                'html': None,
                'url': url,
                'error': 'ScraperAPI not configured - missing API key'
            }
        
        params = self.default_params.copy()
        params['url'] = url
        
        if custom_params:
            params.update(custom_params)
        
        try:
            response = requests.get(self.base_url, params=params)
            
            return {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'html': response.text if response.status_code == 200 else None,
                'url': url,
                'error': None if response.status_code == 200 else f"HTTP {response.status_code}"
            }
            
        except Exception as e:
            return {
                'success': False,
                'status_code': None,
                'html': None,
                'url': url,
                'error': str(e)
            }

# Global instance - will be initialized when first accessed
_scraper_client = None

def get_scraper_client():
    """Lazy initialization of scraper client"""
    global _scraper_client
    if _scraper_client is None:
        _scraper_client = ScraperAPIClient()
    return _scraper_client

# For backward compatibility - but don't initialize yet
def scraper_client():
    return get_scraper_client()

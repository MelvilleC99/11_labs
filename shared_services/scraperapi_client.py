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
        
        if not self.api_key:
            raise ValueError("Missing SCRAPERAPI_KEY in environment variables")
        
        self.base_url = 'http://api.scraperapi.com/'
        self.default_params = {
            'api_key': self.api_key,
            'render': True,
            'country_code': 'us',
            'device_type': 'desktop',
            'timeout': 30000
        }
    
    def scrape_url(self, url, custom_params=None):
        """
        Scrape a single URL using ScraperAPI
        
        Args:
            url (str): URL to scrape
            custom_params (dict): Additional parameters to override defaults
            
        Returns:
            dict: Response with success status, html content, and metadata
        """
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

# Global instance
scraper_client = ScraperAPIClient()

"""
Web scraping tool using ScraperAPI
Handles URL scraping and internal link discovery
"""
import re
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from shared_services.scraperapi_client import scraper_client
from knowledge.scraping_config import load_scraping_config

class WebScraper:
    def __init__(self):
        self.client = scraper_client
        self.config = load_scraping_config()
    
    def discover_internal_links(self, html, base_url):
        """Extract relevant internal links from homepage HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Priority page patterns from config
        priority_patterns = [
            'about', 'about-us', 'company', 'who-we-are', 'our-story', 'our-team',
            'services', 'products', 'solutions', 'what-we-do', 'offerings',
            'team', 'leadership', 'management', 'founders', 'executives',
            'contact', 'contact-us', 'get-in-touch',
            'careers', 'jobs', 'culture', 'values',
            'testimonials', 'case-studies', 'clients', 'customers'
        ]
        
        internal_links = set()
        
        # Extract all links
        for link in soup.find_all('a', href=True):
            href = link['href'].strip()
            
            # Skip empty, mailto, tel, javascript links
            if not href or href.startswith(('mailto:', 'tel:', 'javascript:', '#')):
                continue
            
            # Convert relative URLs to absolute
            if href.startswith('/'):
                full_url = urljoin(base_url, href)
            elif href.startswith(('http://', 'https://')):
                # Check if it's an internal link
                if urlparse(href).netloc != urlparse(base_url).netloc:
                    continue
                full_url = href
            else:
                full_url = urljoin(base_url, href)
            
            # Check if URL matches priority patterns
            url_path = urlparse(full_url).path.lower().strip('/')
            if any(pattern in url_path for pattern in priority_patterns):
                internal_links.add(full_url)
        
        return list(internal_links)[:10]  # Limit to 10 most relevant pages
    
    def scrape_single_page(self, url):
        """Scrape a single page and return structured data"""
        print(f"Scraping: {url}")
        
        result = self.client.scrape_url(url)
        
        if result['success']:
            print(f"Success! Content length: {len(result['html']):,} chars")
        else:
            print(f"Failed: {result['error']}")
        
        return result
    
    def scrape_website(self, base_url):
        """
        Scrape a website starting from base URL, discovering and scraping relevant pages
        
        Args:
            base_url (str): The main website URL to start scraping
            
        Returns:
            dict: Complete scraping results with all pages
        """
        scraped_pages = {}
        
        print(f"Starting website scraping for: {base_url}")
        print("=" * 60)
        
        # Step 1: Scrape homepage
        homepage_result = self.scrape_single_page(base_url)
        scraped_pages['homepage'] = homepage_result
        
        if not homepage_result['success']:
            return {
                'success': False,
                'base_url': base_url,
                'pages_scraped': scraped_pages,
                'error': f"Failed to scrape homepage: {homepage_result['error']}"
            }
        
        # Step 2: Discover internal links
        print(f"\nDiscovering internal links...")
        internal_links = self.discover_internal_links(homepage_result['html'], base_url)
        print(f"Found {len(internal_links)} relevant internal pages")
        
        for link in internal_links:
            print(f"   • {link}")
        
        # Step 3: Scrape internal pages
        print(f"\nScraping internal pages...")
        for i, link in enumerate(internal_links, 1):
            page_key = f"page_{i}"
            scraped_pages[page_key] = self.scrape_single_page(link)
        
        # Calculate success rate
        successful_pages = sum(1 for page in scraped_pages.values() if page['success'])
        total_pages = len(scraped_pages)
        
        print(f"\nScraping completed: {successful_pages}/{total_pages} pages successful")
        
        return {
            'success': successful_pages > 0,
            'base_url': base_url,
            'pages_scraped': scraped_pages,
            'internal_links_found': internal_links,
            'success_rate': successful_pages / total_pages if total_pages > 0 else 0,
            'total_pages': total_pages,
            'successful_pages': successful_pages
        }

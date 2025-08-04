"""
HTML cleaning and text extraction tool
Converts raw HTML to clean, structured text for LLM processing
"""
import re
from bs4 import BeautifulSoup

class HTMLCleaner:
    def __init__(self):
        # Tags to completely remove (along with their content)
        self.remove_tags = ['script', 'style', 'nav', 'footer', 'header', 'aside']
        
        # Tags to keep but extract text from
        self.content_tags = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div', 'span', 'li', 'td', 'th']
    
    def clean_single_page(self, html, url):
        """
        Clean HTML from a single page and extract meaningful text
        
        Args:
            html (str): Raw HTML content
            url (str): URL of the page for context
            
        Returns:
            dict: Cleaned content with metadata
        """
        if not html:
            return {
                'url': url,
                'title': '',
                'meta_description': '',
                'cleaned_text': '',
                'word_count': 0
            }
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract metadata
        title = soup.find('title')
        title_text = title.get_text().strip() if title else ''
        
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        meta_description = meta_desc.get('content', '').strip() if meta_desc else ''
        
        # Remove unwanted elements
        for tag in self.remove_tags:
            for element in soup.find_all(tag):
                element.decompose()
        
        # Extract clean text
        text_content = soup.get_text()
        
        # Clean up the text
        cleaned_text = self._clean_text(text_content)
        
        return {
            'url': url,
            'title': title_text,
            'meta_description': meta_description,
            'cleaned_text': cleaned_text,
            'word_count': len(cleaned_text.split())
        }
    
    def _clean_text(self, text):
        """Clean and normalize extracted text"""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common navigation/footer text patterns
        patterns_to_remove = [
            r'Cookie Policy',
            r'Privacy Policy',
            r'Terms of Service',
            r'All Rights Reserved',
            r'Copyright.*?\d{4}',
            r'Follow us on',
            r'Subscribe to.*?newsletter'
        ]
        
        for pattern in patterns_to_remove:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Clean up extra spaces again
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def combine_page_content(self, scraped_pages):
        """
        Combine content from multiple scraped pages into one coherent text
        
        Args:
            scraped_pages (dict): Dictionary of scraped page results
            
        Returns:
            str: Combined cleaned content from all pages
        """
        combined_sections = []
        
        # Process homepage first
        if 'homepage' in scraped_pages and scraped_pages['homepage']['success']:
            homepage_data = self.clean_single_page(
                scraped_pages['homepage']['html'], 
                scraped_pages['homepage']['url']
            )
            
            if homepage_data['cleaned_text']:
                combined_sections.append(f"=== HOMEPAGE ===\n{homepage_data['cleaned_text']}")
        
        # Process other pages
        for page_key, page_data in scraped_pages.items():
            if page_key == 'homepage' or not page_data['success']:
                continue
            
            cleaned_data = self.clean_single_page(page_data['html'], page_data['url'])
            
            if cleaned_data['cleaned_text']:
                page_title = cleaned_data['title'] or page_data['url']
                combined_sections.append(f"=== {page_title.upper()} ===\n{cleaned_data['cleaned_text']}")
        
        return "\n\n".join(combined_sections)
    
    def get_content_summary(self, scraped_pages):
        """Get a summary of the content extraction results"""
        total_pages = len(scraped_pages)
        successful_pages = sum(1 for page in scraped_pages.values() if page['success'])
        
        page_summaries = []
        total_words = 0
        
        for page_key, page_data in scraped_pages.items():
            if page_data['success']:
                cleaned_data = self.clean_single_page(page_data['html'], page_data['url'])
                total_words += cleaned_data['word_count']
                
                page_summaries.append({
                    'page': page_key,
                    'url': page_data['url'],
                    'title': cleaned_data['title'],
                    'word_count': cleaned_data['word_count']
                })
        
        return {
            'total_pages': total_pages,
            'successful_pages': successful_pages,
            'total_words': total_words,
            'page_summaries': page_summaries
        }

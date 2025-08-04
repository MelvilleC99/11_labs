#!/usr/bin/env python3
"""
Debug test for scraping workflow components
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    print("Testing imports...")
    try:
        from tools.web_scraper import WebScraper
        print("WebScraper imported")
        
        from tools.html_cleaner import HTMLCleaner
        print("HTMLCleaner imported")
        
        from agents.scraper_agent import ScraperAgent
        print("ScraperAgent imported")
        
        from workflows.scrape_workflow import ScrapeWorkflow
        print("ScrapeWorkflow imported")
        
        return True
    except Exception as e:
        print(f"Import error: {e}")
        return False

def test_scraper_only():
    print("\nTesting web scraper only...")
    try:
        from tools.web_scraper import WebScraper
        scraper = WebScraper()
        
        # Test with a simple page
        result = scraper.scrape_single_page("https://www.civitas.network/")
        
        if result['success']:
            print(f"Scraping successful: {len(result['html'])} chars")
            return True
        else:
            print(f"Scraping failed: {result['error']}")
            return False
            
    except Exception as e:
        print(f"Scraping error: {e}")
        return False

def main():
    print("Component Testing")
    print("=" * 40)
    
    if not test_imports():
        return
        
    if not test_scraper_only():
        return
        
    print("\nAll tests passed! Ready for full workflow.")

if __name__ == "__main__":
    main()

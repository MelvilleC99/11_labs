#!/usr/bin/env python3
"""
Simple test script for website scraping
Usage: python scripts/test_scrape.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workflows.scrape_workflow import ScrapeWorkflow

def main():
    print("Website Scraper Test")
    print("=" * 40)
    
    # Get URL from user
    url = input("Enter website URL to scrape: ").strip()
    
    if not url:
        print("No URL provided")
        return
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
        print(f"Using URL: {url}")
    
    print(f"\nStarting scraping workflow for: {url}")
    print("-" * 60)
    
    try:
        # Initialize workflow
        workflow = ScrapeWorkflow()
        
        # Run the complete workflow
        result = workflow.run(url)
        
        # Display results
        print("\n" + "=" * 60)
        print("SCRAPING RESULTS")
        print("=" * 60)
        
        if result.get('success'):
            print(f"Status: {result.get('status', 'completed')}")
            print(f"Pages scraped: {len(result.get('pages_scraped', []))}")
            print(f"Content length: {len(result.get('cleaned_content', ''))}")
            
            extracted_data = result.get('extracted_data')
            if extracted_data:
                print(f"Company data extracted: {len(extracted_data)} sections")
                
                # Show some key extracted data
                if 'company_snapshot' in extracted_data:
                    snapshot = extracted_data['company_snapshot']
                    if snapshot.get('company_name'):
                        print(f"   Company: {snapshot['company_name']}")
                    if snapshot.get('headquarters'):
                        print(f"   Location: {snapshot['headquarters']}")
            else:
                print("No structured data extracted")
        else:
            print(f"Status: {result.get('status', 'failed')}")
            if result.get('error'):
                print(f"Error: {result['error']}")
                
    except Exception as e:
        print(f"Error running workflow: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Test email extraction improvements
"""

import sys
sys.path.append('/Users/melville/Documents/11 labs webhook')

from scrapetest import scrape_company_website, combine_page_content, extract_company_data_with_gpt, load_extraction_template
import json

def test_email_extraction(url):
    print(f"🧪 Testing EMAIL EXTRACTION for: {url}")
    print("=" * 60)
    
    template = load_extraction_template()
    
    # Scrape
    scraped_pages = scrape_company_website(url, max_pages=3)
    successful_pages = sum(1 for p in scraped_pages.values() if p['success'])
    print(f"✅ Scraped {successful_pages}/{len(scraped_pages)} pages")
    
    if successful_pages == 0:
        print("❌ No pages scraped successfully")
        return None
    
    # Process content
    combined_content = combine_page_content(scraped_pages)
    print(f"📄 Content length: {len(combined_content):,} chars")
    
    # Check if emails were extracted in preprocessing
    if "EXTRACTED_EMAILS:" in combined_content:
        emails_section = combined_content.split("EXTRACTED_EMAILS:")[1].split("\n")[0]
        print(f"🔍 PRE-EXTRACTED EMAILS: {emails_section}")
    else:
        print("⚠️  No emails found in preprocessing")
    
    # Extract with GPT
    print("\n🤖 Running GPT extraction...")
    extracted_data = extract_company_data_with_gpt(combined_content, template)
    
    if extracted_data:
        contact = extracted_data.get('contact_info', {})
        
        print(f"\n📊 EMAIL EXTRACTION RESULTS:")
        print(f"✅ Email found: {contact.get('email', 'NOT FOUND')}")
        print(f"📞 Phone found: {contact.get('phone', 'NOT FOUND')}")
        print(f"📍 Address found: {contact.get('address', 'NOT FOUND')}")
        
        # Save results
        with open(f"email_test_{url.replace('://', '_').replace('/', '_')}.json", 'w') as f:
            json.dump({
                'url': url,
                'email_extraction': {
                    'email_found': contact.get('email'),
                    'phone_found': contact.get('phone'),
                    'address_found': contact.get('address'),
                    'social_media_found': contact.get('social_media')
                },
                'full_contact_info': contact
            }, f, indent=2)
        
        return extracted_data
    else:
        print("❌ GPT extraction failed")
        return None

if __name__ == "__main__":
    # Test websites that should have clear contact info
    test_sites = [
        "https://postmarkapp.com",  # Email service - should definitely have contact email
        "https://basecamp.com",     # Popular SaaS - should have contact info  
        "https://mailchimp.com"     # Email marketing - must have contact email
    ]
    
    print("Choose a test:")
    for i, site in enumerate(test_sites, 1):
        print(f"{i}. {site}")
    print("4. Enter custom URL")
    
    choice = input("Enter choice (1-4): ").strip()
    
    if choice == "4":
        url = input("Enter URL: ").strip()
        if not url.startswith('http'):
            url = 'https://' + url
    elif choice in ['1', '2', '3']:
        url = test_sites[int(choice) - 1]
    else:
        url = test_sites[0]  # Default
    
    test_email_extraction(url)

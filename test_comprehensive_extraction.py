#!/usr/bin/env python3
"""
Test the enhanced comprehensive scraper against Civitas
"""

import sys
sys.path.append('/Users/melville/Documents/11 labs webhook')

from scrapetest import scrape_company_website, combine_page_content, extract_company_data_with_gpt, load_extraction_template
import json
from datetime import datetime

def test_comprehensive_extraction():
    print("🧪 Testing COMPREHENSIVE extraction on Civitas")
    print("=" * 60)
    
    url = "https://www.civitas.network/"
    
    # Load the new comprehensive template
    template = load_extraction_template()
    print(f"📋 Loaded comprehensive template with {len(template)} sections")
    
    # Scrape with increased page limit
    print("\n🕷️ Scraping with enhanced coverage...")
    scraped_pages = scrape_company_website(url, max_pages=8)
    successful_pages = sum(1 for p in scraped_pages.values() if p['success'])
    print(f"✅ Scraped {successful_pages}/{len(scraped_pages)} pages successfully")
    
    # Show which pages were scraped
    print("\n📄 Pages scraped:")
    for url_scraped, data in scraped_pages.items():
        status = "✅" if data['success'] else "❌"
        print(f"  {status} {url_scraped}")
    
    if successful_pages == 0:
        print("❌ No pages scraped successfully")
        return None
    
    # Process content
    print("\n🔄 Processing content...")
    combined_content = combine_page_content(scraped_pages)
    print(f"📄 Combined content: {len(combined_content):,} characters")
    
    # Check for contact detection improvements
    if "🚨 SMART CONTACT DETECTION:" in combined_content:
        print("✅ Enhanced contact detection active")
    
    if "EXTRACTED_EMAILS:" in combined_content:
        emails_section = combined_content.split("EXTRACTED_EMAILS:")[1].split("\n")[0]
        print(f"📧 Pre-extracted emails: {emails_section}")
    
    # Extract with enhanced GPT
    print("\n🤖 Running comprehensive GPT extraction...")
    extracted_data = extract_company_data_with_gpt(combined_content, template)
    
    if extracted_data:
        print("✅ Comprehensive extraction successful!")
        
        # Analyze extraction completeness
        total_fields = 0
        filled_fields = 0
        
        for section_name, section_data in extracted_data.items():
            if isinstance(section_data, dict):
                for field_name, field_value in section_data.items():
                    total_fields += 1
                    if field_value is not None and field_value != "" and field_value != []:
                        filled_fields += 1
        
        completeness = (filled_fields / total_fields) * 100 if total_fields > 0 else 0
        print(f"📊 Data completeness: {filled_fields}/{total_fields} fields ({completeness:.1f}%)")
        
        # Save comprehensive results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"comprehensive_civitas_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'url': url,
                'extraction_timestamp': timestamp,
                'pages_scraped': len(scraped_pages),
                'successful_pages': successful_pages,
                'content_length': len(combined_content),
                'data_completeness': f"{completeness:.1f}%",
                'extracted_data': extracted_data
            }, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Results saved to: {filename}")
        
        # Show key improvements
        print(f"\n🎯 KEY SECTIONS ANALYSIS:")
        
        key_sections = [
            'leadership_governance', 'services', 'markets_customers', 
            'value_proposition', 'contact_information', 'partnerships_alliances'
        ]
        
        for section in key_sections:
            if section in extracted_data:
                section_data = extracted_data[section]
                filled_count = sum(1 for v in section_data.values() if v not in [None, "", []])
                total_count = len(section_data)
                print(f"  {section}: {filled_count}/{total_count} fields")
        
        return extracted_data
    else:
        print("❌ Comprehensive extraction failed")
        return None

def compare_with_gpt_benchmark():
    """Compare our results with the GPT benchmark provided"""
    print("\n" + "="*60)
    print("🔍 COMPARISON WITH GPT BENCHMARK")
    print("="*60)
    
    # Key areas where GPT excelled
    gpt_strengths = [
        "Leadership team (Pierre du Plessis, Paul Galatis, etc.)",
        "Detailed service breakdown (CEO Playbook, Masterclasses, Forums)",
        "Target market specifics (R5M revenue threshold, company sizes)",
        "Geographic expansion (London, Amsterdam chapters)",
        "Cultural framework (Fair Exchange, Pay-It-Forward)",
        "Operational details (2hrs/month commitment, 10-15 events)",
        "Industry breakdown (35% SaaS, 40% tech services)",
        "Advisor network (Andy Raskin, Ian Fuhr, Tendayi Viki)"
    ]
    
    print("📊 GPT Benchmark Strengths:")
    for i, strength in enumerate(gpt_strengths, 1):
        print(f"  {i}. {strength}")
    
    print(f"\n🎯 Our goal: Match or exceed this level of detail!")

if __name__ == "__main__":
    print("🚀 COMPREHENSIVE SCRAPER ENHANCEMENT TEST")
    print("Testing against GPT benchmark for Civitas")
    print("=" * 70)
    
    # Run comprehensive test
    results = test_comprehensive_extraction()
    
    # Compare with benchmark
    compare_with_gpt_benchmark()
    
    if results:
        print(f"\n✅ Test completed successfully!")
        print(f"📈 Ready to compare detailed results with GPT benchmark")
    else:
        print(f"\n❌ Test failed - need further improvements")

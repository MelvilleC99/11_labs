#!/usr/bin/env python3
"""
Complete Website Scraping & Data Extraction Agent
Tests the full flow: Scrape → Clean → Extract with GPT
"""

import os
import json
import yaml
import requests
import openai
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import re

# Load environment variables
load_dotenv()

# Configuration
SCRAPERAPI_KEY = os.getenv('SCRAPERAPI_KEY')
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY') or os.getenv('SUPABASE_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Validate environment variables
required_vars = {
    'SCRAPERAPI_KEY': SCRAPERAPI_KEY,
    'SUPABASE_URL': SUPABASE_URL,
    'SUPABASE_ANON_KEY': SUPABASE_ANON_KEY,
    'OPENAI_API_KEY': OPENAI_API_KEY
}

for var_name, var_value in required_vars.items():
    if not var_value:
        print(f"❌ {var_name} not found in environment variables")
        exit(1)

# Initialize clients
supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
openai.api_key = OPENAI_API_KEY

def load_extraction_template():
    """Load comprehensive company extraction template based on professional standards"""
    template = {
        "cover_page": {
            "company_name": "Official company name",
            "tagline_slogan": "Main tagline or slogan",
            "logo_url": "URL to company logo",
            "date_of_issue": "Date of profile creation"
        },
        "company_snapshot": {
            "founded": "Year company was founded",
            "headquarters": "Location of headquarters with full address",
            "legal_structure": "Company legal structure (LLC, Corp, etc.)",
            "number_of_employees": "Employee count or size range",
            "annual_revenue_funding": "Revenue figures or funding amounts",
            "website": "Official website URL",
            "industries_sectors": "Primary and secondary industry sectors"
        },
        "mission_vision_values": {
            "mission_statement": "What the company exists to achieve",
            "vision_statement": "Long-term aspirational goal",
            "core_values": "List of company core values with descriptions"
        },
        "history_milestones": {
            "key_milestones": "List of significant company milestones with years",
            "founding_story": "How and why the company was started",
            "major_achievements": "Notable achievements and growth markers"
        },
        "leadership_governance": {
            "executive_team": "C-level executives with roles and brief bios",
            "board_directors_advisors": "Board members and key advisors",
            "founders": "Company founders and their backgrounds"
        },
        "products_solutions": {
            "product_portfolio": "Detailed list of products with descriptions",
            "launch_years": "When key products were launched",
            "key_features": "Competitive advantages of each product",
            "pricing_models": "How products are priced",
            "product_roadmap": "Future product development plans"
        },
        "services": {
            "service_offerings": "Detailed service descriptions",
            "methodology_delivery": "How services are delivered",
            "engagement_models": "Different ways clients can engage",
            "pricing_structure": "Service pricing and engagement terms",
            "success_metrics": "KPIs and success measurements"
        },
        "markets_customers": {
            "target_segments": "Detailed customer personas and segments",
            "geographical_markets": "Countries and regions served",
            "key_clients": "Notable clients and customer logos",
            "testimonials_case_studies": "Customer success stories and testimonials"
        },
        "value_proposition": {
            "unique_selling_points": "What makes the company unique",
            "competitive_differentiators": "How they differ from competitors",
            "proof_points": "Data, awards, and validation of claims"
        },
        "operating_locations": {
            "countries_of_operation": "All countries where company operates",
            "offices_facilities": "Physical locations with addresses",
            "remote_work_policy": "Remote and hybrid work arrangements"
        },
        "key_metrics_performance": {
            "growth_metrics": "Year-over-year growth percentages",
            "market_share": "Position in the market",
            "customer_satisfaction": "NPS, CSAT, and other satisfaction metrics",
            "retention_churn": "Customer retention and churn rates",
            "other_kpis": "Business-specific key performance indicators"
        },
        "financial_highlights": {
            "revenue_trends": "Revenue growth over recent years",
            "profitability": "Profit margins and financial health",
            "funding_rounds": "Investment rounds and funding history",
            "investors": "Key investors and investment partners"
        },
        "certifications_compliance": {
            "standards_certifications": "ISO, SOC 2, PCI-DSS, and other certifications",
            "regulatory_approvals": "Industry-specific regulatory compliance",
            "security_privacy": "Security and privacy policies and measures"
        },
        "partnerships_alliances": {
            "technology_partners": "Key technology and integration partners",
            "channel_partners": "Distribution and channel partnerships",
            "strategic_alliances": "Strategic business partnerships"
        },
        "awards_recognition": {
            "industry_awards": "Awards received with years and issuers",
            "recognition": "Media recognition and industry acknowledgments",
            "rankings": "Industry rankings and analyst recognition"
        },
        "csr_sustainability": {
            "environmental_initiatives": "Environmental and sustainability programs",
            "social_impact": "Community and social impact programs",
            "esg_governance": "ESG scores and governance practices"
        },
        "technology_innovation": {
            "rd_focus": "Research and development focus areas",
            "patents_ip": "Patents and intellectual property portfolio",
            "technology_stack": "Technology platforms and infrastructure",
            "innovation_programs": "Innovation labs and development programs"
        },
        "risk_management": {
            "key_risks": "Major business risks and mitigation strategies",
            "governance_framework": "Corporate governance structure",
            "compliance_programs": "Compliance and risk management programs"
        },
        "media_public_relations": {
            "press_releases": "Recent press releases and announcements",
            "media_coverage": "Notable media coverage and mentions",
            "thought_leadership": "White papers, blogs, and thought leadership content"
        },
        "culture_career": {
            "employer_value_proposition": "What makes the company a great place to work",
            "diversity_inclusion": "D&I initiatives and commitments",
            "learning_development": "Employee development and training programs",
            "open_positions": "Current job openings and career opportunities"
        },
        "contact_information": {
            "registered_address": "Official business address",
            "phone_numbers": "Primary phone and departmental numbers",
            "email_addresses": "General and departmental email addresses",
            "social_media_handles": "Social media accounts and handles",
            "investor_media_contacts": "Specific contacts for investors and media"
        }
    }
    return template

def discover_internal_links(html, base_url):
    """Extract relevant internal links from homepage HTML with comprehensive coverage"""
    soup = BeautifulSoup(html, 'html.parser')
    
    # Comprehensive priority page patterns
    priority_patterns = [
        'about', 'about-us', 'company', 'who-we-are', 'our-story', 'our-team',
        'services', 'products', 'solutions', 'what-we-do', 'offerings',
        'team', 'leadership', 'management', 'founders', 'executives',
        'contact', 'contact-us', 'get-in-touch',
        'careers', 'jobs', 'culture', 'values',
        'testimonials', 'case-studies', 'clients', 'customers',
        'partners', 'investors', 'board',
        'news', 'press', 'media', 'blog'
    ]
    
    internal_links = set()
    
    # Find all links
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href'].strip()
        
        # Skip empty links, anchors, external links
        if not href or href.startswith('#') or href.startswith('mailto:') or href.startswith('tel:'):
            continue
            
        # Convert relative URLs to absolute
        if href.startswith('/'):
            full_url = urljoin(base_url, href)
        elif href.startswith('http') and base_url not in href:
            continue  # External link
        elif not href.startswith('http'):
            full_url = urljoin(base_url, href)
        else:
            full_url = href
            
        # Check if URL matches priority patterns
        url_path = urlparse(full_url).path.lower()
        for pattern in priority_patterns:
            if pattern in url_path:
                internal_links.add(full_url)
                break
    
    # Convert to list and prioritize key pages, increase limit
    return list(internal_links)[:8]  # Increased from 5 to 8 pages

def scrape_website_page(url):
    """Scrape a single page using ScraperAPI"""
    print(f"🕷️  Scraping: {url}")
    
    params = {
        'api_key': SCRAPERAPI_KEY,
        'url': url,
        'render': True,
        'country_code': 'us',
        'device_type': 'desktop',
        'timeout': 30000
    }
    
    try:
        response = requests.get('http://api.scraperapi.com/', params=params)
        
        if response.status_code == 200:
            print(f"✅ Success! Content length: {len(response.text):,} chars")
            return {
                'url': url,
                'html': response.text,
                'status_code': response.status_code,
                'success': True,
                'error': None
            }
        else:
            print(f"❌ Failed with status code: {response.status_code}")
            return {
                'url': url,
                'html': None,
                'status_code': response.status_code,
                'success': False,
                'error': f"HTTP {response.status_code}"
            }
            
    except Exception as e:
        print(f"❌ Error scraping {url}: {str(e)}")
        return {
            'url': url,
            'html': None,
            'status_code': None,
            'success': False,
            'error': str(e)
        }

def scrape_company_website(base_url, max_pages=8):
    """Scrape company website - homepage + key internal pages (increased coverage)"""
    print(f"🏢 Starting comprehensive scrape of: {base_url}")
    
    scraped_pages = {}
    
    # 1. Scrape homepage first
    homepage_result = scrape_website_page(base_url)
    scraped_pages[base_url] = homepage_result
    
    if not homepage_result['success']:
        print("❌ Failed to scrape homepage, aborting...")
        return scraped_pages
    
    # 2. Discover internal links from homepage
    print("🔍 Discovering internal pages...")
    internal_links = discover_internal_links(homepage_result['html'], base_url)
    print(f"📋 Found {len(internal_links)} relevant internal pages")
    
    for link in internal_links:
        print(f"   • {link}")
    
    # 3. Scrape internal pages (limit to max_pages total)
    pages_scraped = 1  # Homepage already scraped
    
    for link in internal_links:
        if pages_scraped >= max_pages:
            print(f"⏹️  Reached maximum pages limit ({max_pages})")
            break
            
        time.sleep(1)  # Rate limiting
        result = scrape_website_page(link)
        scraped_pages[link] = result
        pages_scraped += 1
    
    print(f"✅ Scraping complete! Total pages: {pages_scraped}")
    return scraped_pages

def extract_emails_from_html(html):
    """Dedicated email extraction from raw HTML before cleaning"""
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'html.parser')
    emails = set()
    
    # 1. Look for mailto links first (most reliable)
    for mailto in soup.find_all('a', href=re.compile(r'^mailto:')):
        email = mailto['href'].replace('mailto:', '').split('?')[0]
        if email:
            emails.add(email.lower())
    
    # 2. Search in contact-specific elements AND tables
    contact_selectors = [
        'footer', '[class*="contact"]', '[class*="footer"]', 
        '[id*="contact"]', '[class*="address"]', 'address',
        '[class*="info"]', '[id*="info"]', '.contact-info',
        '.footer-contact', '.contact-details', 'table', 'tbody', 'td'
    ]
    
    for selector in contact_selectors:
        elements = soup.select(selector)
        for element in elements:
            text = element.get_text()
            # More comprehensive email regex
            email_matches = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
            emails.update(email.lower() for email in email_matches)
    
    # 3. Search entire page as fallback
    full_text = soup.get_text()
    email_matches = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', full_text)
    emails.update(email.lower() for email in email_matches)
    
    # Filter out common fake/example emails
    filtered_emails = []
    exclude_patterns = [
        'example.com', 'test.com', 'domain.com', 'yoursite.com',
        'noreply', 'no-reply', 'donotreply', 'support@example',
        'admin@example', 'info@example', 'contact@example'
    ]
    
    for email in emails:
        if not any(pattern in email for pattern in exclude_patterns):
            filtered_emails.append(email)
    
    return filtered_emails

def clean_html_content(html):
    """Clean HTML and extract meaningful text content with enhanced extraction"""
    if not html:
        return ""
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # FIRST: Extract and preserve important structured data before removal
    preserved_content = []
    
    # Extract contact information from common containers
    contact_selectors = [
        'footer', '[class*="contact"]', '[class*="footer"]', 
        '[id*="contact"]', '[class*="address"]', 'address'
    ]
    
    for selector in contact_selectors:
        elements = soup.select(selector)
        for element in elements:
            text = element.get_text(separator=' ', strip=True)
            if text and len(text) > 10:
                preserved_content.append(f"CONTACT_SECTION: {text}")
    
    # Extract testimonials/reviews before cleanup
    testimonial_selectors = [
        '[class*="testimonial"]', '[class*="review"]', '[class*="quote"]',
        '[class*="client"]', '[class*="feedback"]', 'blockquote'
    ]
    
    for selector in testimonial_selectors:
        elements = soup.select(selector)
        for element in elements:
            text = element.get_text(separator=' ', strip=True)
            if text and len(text) > 20:
                preserved_content.append(f"TESTIMONIAL_SECTION: {text}")
    
    # NOW remove unwanted elements
    for element in soup(['script', 'style', 'nav', 'aside', 'iframe', 'noscript']):
        element.decompose()
    
    # Remove common noise classes/ids but preserve some footers for contact info
    noise_selectors = [
        '[class*="cookie"]', '[class*="popup"]', '[class*="modal"]',
        '[class*="menu"]', '[class*="navigation"]', '[class*="sidebar"]',
        '[class*="breadcrumb"]', '[class*="pagination"]'
    ]
    
    for selector in noise_selectors:
        for element in soup.select(selector):
            element.decompose()
    
    # Extract main text content
    text = soup.get_text(separator='\n', strip=True)
    
    # Clean up text
    lines = []
    for line in text.split('\n'):
        line = line.strip()
        if line and len(line) > 3:  # Skip very short lines
            lines.append(line)
    
    # Add preserved content at the end
    lines.extend(preserved_content)
    
    clean_text = '\n'.join(lines)
    
    # Remove excessive whitespace
    clean_text = re.sub(r'\n\s*\n', '\n\n', clean_text)
    clean_text = re.sub(r'\s+', ' ', clean_text)
    
    return clean_text

def combine_page_content(scraped_pages):
    """Combine and structure content from all scraped pages"""
    combined_content = ""
    all_emails = set()
    contact_hints = []
    
    for url, page_data in scraped_pages.items():
        if not page_data['success']:
            continue
        
        # FIRST: Extract emails from raw HTML before cleaning
        page_emails = extract_emails_from_html(page_data['html'])
        all_emails.update(page_emails)
        
        # SECOND: Smart contact pattern detection (not hardcoded)
        html_text = page_data['html'].lower()
        
        # Generic email detection in HTML
        import re
        email_pattern = r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'
        html_emails = re.findall(email_pattern, page_data['html'])
        if html_emails:
            contact_hints.append(f"🚨 CRITICAL: Emails found in HTML: {', '.join(html_emails[:2])}")
        
        # Generic location detection
        location_keywords = ['town', 'city', 'country', 'address', 'street', 'avenue', 'road']
        for keyword in location_keywords:
            if keyword in html_text:
                # Extract context around location keywords
                lines = page_data['html'].split('\n')
                for line in lines:
                    if keyword in line.lower() and len(line.strip()) > 10:
                        clean_line = re.sub(r'<[^>]+>', '', line).strip()
                        if clean_line and len(clean_line) > 5:
                            contact_hints.append(f"🚨 LOCATION CONTEXT: {clean_line[:100]}")
                            break
        
        # Identify page type from URL
        page_path = urlparse(url).path.lower()
        if page_path == '/' or page_path == '':
            page_type = "HOMEPAGE"
        elif any(x in page_path for x in ['about', 'company', 'who-we-are']):
            page_type = "ABOUT"
        elif any(x in page_path for x in ['service', 'product', 'solution', 'offering']):
            page_type = "SERVICES"
        elif any(x in page_path for x in ['team', 'leadership', 'management']):
            page_type = "TEAM"
        elif any(x in page_path for x in ['contact']):
            page_type = "CONTACT"
        else:
            page_type = "OTHER"
        
        # Clean the HTML content
        clean_text = clean_html_content(page_data['html'])
        
        if clean_text:
            combined_content += f"\n\n=== {page_type} PAGE ({url}) ===\n{clean_text[:2000]}...\n"
    
    # Add extracted emails as structured data
    if all_emails:
        combined_content += f"\n\nEXTRACTED_EMAILS: {', '.join(sorted(all_emails))}\n"
    
    # Add smart contact hints at the TOP (limit to avoid spam)
    if contact_hints:
        unique_hints = list(set(contact_hints))[:5]  # Limit to 5 unique hints
        combined_content = f"\n🚨 SMART CONTACT DETECTION:\n" + '\n'.join(unique_hints) + "\n\n" + combined_content
    
    return combined_content

def create_enhanced_extraction_prompt(combined_content, template):
    """Create a comprehensive GPT prompt matching professional company profiling standards"""
    
    # Smart pre-analysis for contact patterns
    import re
    contact_analysis = ""
    
    # Find any email patterns
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    found_emails = re.findall(email_pattern, combined_content)
    if found_emails:
        contact_analysis += f"\n🚨 EMAILS DETECTED: {', '.join(found_emails[:3])}\n"
    
    # Find location and business indicators
    business_indicators = ['headquarters', 'office', 'founded', 'ceo', 'revenue', 'employees', 'million', 'billion']
    found_indicators = [indicator for indicator in business_indicators if indicator in combined_content.lower()]
    if found_indicators:
        contact_analysis += f"🚨 BUSINESS INDICATORS: {', '.join(found_indicators[:5])}\n"

    return f"""You are an expert company profiler. You read entire websites and fill out comprehensive company profiles with maximum depth and accuracy.

CRITICAL PRE-ANALYSIS:{contact_analysis}

INSTRUCTIONS: Extract detailed information for each section below. Provide specific, factual information when available. If information is not found, return null for that field.

COMPREHENSIVE COMPANY PROFILE TEMPLATE:
{json.dumps(template, indent=2)}

WEBSITE CONTENT TO ANALYZE:
{combined_content[:20000]}

EXTRACTION RULES:
1. **BE COMPREHENSIVE**: Extract as much detail as possible for each section
2. **BE SPECIFIC**: Include exact numbers, dates, names, and details
3. **BE ACCURATE**: Only include information that is clearly stated or reasonably inferred
4. **USE STRUCTURE**: Organize information according to the template structure
5. **INCLUDE CONTEXT**: For leadership, include roles and brief descriptions
6. **EXTRACT METRICS**: Look for any performance metrics, growth numbers, revenue figures
7. **FIND DIFFERENTIATORS**: Identify what makes this company unique
8. **CAPTURE CULTURE**: Extract values, mission, and cultural elements
9. **GET CONTACT INFO**: Extract all forms of contact information thoroughly
10. **IDENTIFY PARTNERSHIPS**: Look for partners, investors, advisors, collaborators

CRITICAL FOCUS AREAS:
- Leadership team members with their roles and backgrounds
- Detailed service/product descriptions with features and benefits
- Target market specifications with criteria and thresholds
- Financial information including revenue, funding, growth metrics
- Geographic presence and operational locations
- Competitive positioning and unique value propositions
- Company culture, values, and operational philosophy
- Partnership ecosystem and strategic relationships

Return ONLY valid JSON with the complete template structure filled out. Include arrays for list items and detailed text for complex information.

JSON OUTPUT:"""

def extract_company_data_with_gpt(combined_content, template):
    """Use GPT to extract structured company data"""
    print("🤖 Processing content with GPT...")
    
    # Use the enhanced prompt
    prompt = create_enhanced_extraction_prompt(combined_content, template)


    try:
        # Increase max_tokens for better extraction
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a precise data extraction assistant. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=3000  # Increased for more complete extraction
        )
        
        response_text = response.choices[0].message.content.strip()
        
        # Clean up response (remove code blocks if present)
        if response_text.startswith('```json'):
            response_text = response_text[7:-3]
        elif response_text.startswith('```'):
            response_text = response_text[3:-3]
        
        # Parse JSON
        extracted_data = json.loads(response_text)

        # Enhanced contact information extraction with better email detection
        contact_info = extracted_data.get("contact_info", {})
        
        # Enhanced email extraction from content
        if not contact_info.get("email"):
            # First check if we have EXTRACTED_EMAILS section
            if "EXTRACTED_EMAILS:" in combined_content:
                extracted_emails_section = combined_content.split("EXTRACTED_EMAILS:")[1].split("\n")[0]
                emails_from_section = [email.strip() for email in extracted_emails_section.split(",")]
                if emails_from_section and emails_from_section[0]:
                    contact_info["email"] = emails_from_section[0]
            
            # Fallback: comprehensive email search
            if not contact_info.get("email"):
                email_patterns = [
                    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                    r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                ]
                
                all_emails = set()
                for pattern in email_patterns:
                    matches = re.findall(pattern, combined_content)
                    all_emails.update(matches)
                
                # Filter and prioritize emails
                business_emails = []
                exclude_terms = ['noreply', 'no-reply', 'donotreply', 'example.com', 'test.com']
                
                for email in all_emails:
                    email = email.lower()
                    if not any(term in email for term in exclude_terms):
                        # Prioritize common business email patterns
                        if any(term in email for term in ['info@', 'contact@', 'hello@', 'support@', 'sales@']):
                            business_emails.insert(0, email)  # Priority
                        else:
                            business_emails.append(email)
                
                if business_emails:
                    contact_info["email"] = business_emails[0]
        
        # Phone number extraction
        if not contact_info.get("phone"):
            phone_patterns = [
                r'\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}',  # US format
                r'\+?[0-9]{1,4}[-.\s]?[0-9]{1,4}[-.\s]?[0-9]{1,4}[-.\s]?[0-9]{1,9}'  # International
            ]
            for pattern in phone_patterns:
                phone_matches = re.findall(pattern, combined_content)
                if phone_matches:
                    contact_info["phone"] = phone_matches[0]
                    break
        
        # Address extraction (look for common address patterns)
        if not contact_info.get("address"):
            address_patterns = [
                r'\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Way|Place|Pl)\s*,?\s*[A-Za-z\s]+,?\s*[A-Z]{2}\s*\d{5}',
                r'\d+\s+[A-Za-z\s,]+\s+[A-Za-z\s]+,\s*[A-Za-z\s]+\s*\d{4,5}'
            ]
            for pattern in address_patterns:
                address_matches = re.findall(pattern, combined_content)
                if address_matches:
                    contact_info["address"] = address_matches[0]
                    break
        
        # Social media extraction
        if not contact_info.get("social_media"):
            social_patterns = {
                'linkedin': r'linkedin\.com/(?:company/|in/)[a-zA-Z0-9-]+',
                'twitter': r'twitter\.com/[a-zA-Z0-9_]+',
                'facebook': r'facebook\.com/[a-zA-Z0-9.]+',
                'instagram': r'instagram\.com/[a-zA-Z0-9_.]+',
                'youtube': r'youtube\.com/(?:c/|channel/|user/)[a-zA-Z0-9_-]+'
            }
            social_media = {}
            for platform, pattern in social_patterns.items():
                matches = re.findall(pattern, combined_content, re.IGNORECASE)
                if matches:
                    social_media[platform] = f"https://{matches[0]}"
            
            if social_media:
                contact_info["social_media"] = social_media
        
        extracted_data["contact_info"] = contact_info

        # Enhanced social proof detection
        social_proof = extracted_data.get("social_proof", {})
        
        # Look for testimonials, reviews, client mentions
        testimonial_indicators = [
            'testimonial', 'review', 'client says', 'customer feedback', 
            'trusted by', 'clients include', 'working with', 'case study',
            'success story', '"', 'rating', 'stars', 'recommended'
        ]
        
        testimonial_content = []
        content_lower = combined_content.lower()
        
        for indicator in testimonial_indicators:
            if indicator in content_lower:
                # Find sentences containing testimonial indicators
                sentences = re.split(r'[.!?]+', combined_content)
                for sentence in sentences:
                    if indicator in sentence.lower() and len(sentence.strip()) > 20:
                        testimonial_content.append(sentence.strip())
        
        if testimonial_content and not social_proof.get("testimonials"):
            social_proof["testimonials"] = testimonial_content[:3]  # Limit to top 3
        
        # Look for client logos/names (common patterns)
        client_patterns = [
            r'(?:clients?|customers?|partners?)\s+(?:include|such as|like):\s*([^.]+)',
            r'trusted by\s+([^.]+)',
            r'working with\s+([^.]+)'
        ]
        
        client_mentions = []
        for pattern in client_patterns:
            matches = re.findall(pattern, combined_content, re.IGNORECASE)
            client_mentions.extend(matches)
        
        if client_mentions and not social_proof.get("case_studies"):
            social_proof["case_studies"] = [f"Mentioned clients: {', '.join(client_mentions[:5])}"]
        
        extracted_data["social_proof"] = social_proof

        print("✅ GPT extraction successful!")
        return extracted_data
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        print(f"Raw response: {response_text}")
        return None
    except Exception as e:
        print(f"❌ GPT extraction error: {e}")
        return None

def save_results(base_url, scraped_pages, extracted_data):
    """Save results to JSON file and optionally to database"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    domain = urlparse(base_url).netloc.replace('www.', '')
    filename = f"company_extraction_{domain}_{timestamp}.json"
    
    # Prepare data for saving (excluding large HTML content)
    save_data = {
        'base_url': base_url,
        'extraction_timestamp': datetime.utcnow().isoformat(),
        'pages_scraped': len(scraped_pages),
        'successful_pages': sum(1 for p in scraped_pages.values() if p['success']),
        'page_urls': list(scraped_pages.keys()),
        'extracted_company_data': extracted_data,
        'scraping_summary': {
            url: {
                'success': data['success'],
                'status_code': data['status_code'],
                'content_length': len(data['html']) if data['html'] else 0,
                'error': data['error']
            }
            for url, data in scraped_pages.items()
        }
    }
    
    # Save to JSON file
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(save_data, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Results saved to: {filename}")
    return filename

def main():
    """Main function to test the complete flow"""
    print("🚀 Company Website Extraction Agent")
    print("=" * 60)
    
    # Get URL from user
    base_url = input("Enter company website URL: ").strip()
    
    if not base_url.startswith('http'):
        base_url = 'https://' + base_url
    
    print(f"🎯 Target URL: {base_url}")
    
    # Load extraction template
    template = load_extraction_template()
    print("📋 Loaded extraction template")
    
    # Step 1: Comprehensive website scraping
    print("\n" + "="*60)
    print("STEP 1: SCRAPING WEBSITE")
    print("="*60)
    scraped_pages = scrape_company_website(base_url, max_pages=4)

    # Create debug output folder and save raw homepage HTML
    from urllib.parse import urlparse
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    domain = urlparse(base_url).netloc.replace("www.", "").replace(".", "_")
    debug_dir = f"debug_output/{domain}_{timestamp}"
    os.makedirs(debug_dir, exist_ok=True)
    # Save raw HTML from homepage
    homepage_html = scraped_pages[base_url]['html']
    if homepage_html:
        with open(f"{debug_dir}/raw.html", "w", encoding="utf-8") as f:
            f.write(homepage_html)
    
    # Step 2: Content cleaning and combination
    print("\n" + "="*60)
    print("STEP 2: CLEANING & COMBINING CONTENT")
    print("="*60)
    combined_content = combine_page_content(scraped_pages)
    print(f"📄 Combined content length: {len(combined_content):,} characters")
    # Save cleaned combined content
    with open(f"{debug_dir}/cleaned.txt", "w", encoding="utf-8") as f:
        f.write(combined_content)
    
    # Step 3: GPT extraction
    print("\n" + "="*60)
    print("STEP 3: GPT DATA EXTRACTION")
    print("="*60)
    extracted_data = extract_company_data_with_gpt(combined_content, template)
    # Save summary JSON if extracted_data is present
    if extracted_data:
        with open(f"{debug_dir}/summary.json", "w", encoding="utf-8") as f:
            json.dump(extracted_data, f, indent=2, ensure_ascii=False)

    
    # Step 4: Save results
    print("\n" + "="*60)
    print("STEP 4: SAVING RESULTS")
    print("="*60)
    filename = save_results(base_url, scraped_pages, extracted_data)
    
    # Print summary
    print("\n" + "="*60)
    print("📊 EXTRACTION SUMMARY")
    print("="*60)
    print(f"Base URL: {base_url}")
    print(f"Pages scraped: {len(scraped_pages)}")
    print(f"Successful pages: {sum(1 for p in scraped_pages.values() if p['success'])}")
    print(f"Results file: {filename}")
    
    if extracted_data:
        print("\n🏢 EXTRACTED COMPANY DATA:")
        print("-" * 40)
        for category, data in extracted_data.items():
            print(f"\n{category.upper()}:")
            if isinstance(data, dict):
                for key, value in data.items():
                    if value:
                        print(f"  • {key}: {value}")
            else:
                print(f"  {data}")
    else:
        print("❌ No data extracted - check the results file for debugging info")


if __name__ == "__main__":
    main()
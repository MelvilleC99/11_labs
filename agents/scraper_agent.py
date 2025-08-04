"""
Scraper Agent - Uses LLM to extract structured company data from cleaned website content
"""
import json
import yaml
from openai import OpenAI
from knowledge.scraping_config import load_extraction_template
import os

class ScraperAgent:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.template = load_extraction_template()
        
        # Load system prompt
        with open('prompts/scraper_agent_prompt.txt', 'r') as f:
            self.system_prompt = f.read()
    
    def extract_company_data(self, cleaned_content, base_url):
        """
        Extract structured company data from cleaned website content using GPT
        
        Args:
            cleaned_content (str): Combined cleaned text from all website pages
            base_url (str): Base URL of the website for context
            
        Returns:
            dict: Extracted company data matching the template structure
        """
        print(f"Starting GPT extraction for: {base_url}")
        print(f"Content length: {len(cleaned_content):,} characters")
        
        # Build the extraction prompt
        prompt = self._build_extraction_prompt(cleaned_content, base_url)
        
        try:
            # Call OpenAI API (new format)
            response = self.client.chat.completions.create(
                model="gpt-4o",  # Use GPT-4o (GPT-4.0)
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=4000,
                temperature=0.1  # Low temperature for consistent extraction
            )
            
            # Parse the response
            extracted_text = response.choices[0].message.content
            
            # Try to parse as JSON
            try:
                extracted_data = json.loads(extracted_text)
                print("Successfully extracted structured data")
                return extracted_data
                
            except json.JSONDecodeError:
                print("Response not in JSON format, attempting to structure...")
                # If not JSON, try to structure the response
                return self._structure_text_response(extracted_text)
                
        except Exception as e:
            print(f"Error in GPT extraction: {str(e)}")
            return {
                'error': str(e),
                'extraction_failed': True
            }
    
    def _build_extraction_prompt(self, content, base_url):
        """Build the prompt for GPT extraction"""
        
        # Convert template to JSON string for the prompt
        template_json = json.dumps(self.template, indent=2)
        
        prompt = f"""
WEBSITE URL: {base_url}

EXTRACTION TEMPLATE:
{template_json}

WEBSITE CONTENT TO ANALYZE:
{content}

TASK:
Analyze the above website content and extract information according to the template structure. 
Return your response as a valid JSON object that matches the template structure exactly.

For each field in the template:
- If information is found, provide the specific details
- If information is not available, use "Not available"
- Be accurate and specific - include numbers, dates, and exact details when found
- Focus on factual information rather than marketing language

Return ONLY the JSON object, no additional text or explanation.
"""
        
        return prompt
    
    def _structure_text_response(self, text_response):
        """Attempt to structure a text response into our template format"""
        print("Attempting to structure text response...")
        
        # This is a fallback - try to extract key information from text
        structured_data = {}
        
        # Basic company info extraction patterns
        company_patterns = {
            'company_name': r'Company Name?:?\s*([^\n]+)',
            'headquarters': r'(?:Headquarters?|Location|Address):?\s*([^\n]+)',
            'founded': r'(?:Founded|Established):?\s*(\d{4})',
        }
        
        import re
        
        for key, pattern in company_patterns.items():
            match = re.search(pattern, text_response, re.IGNORECASE)
            if match:
                structured_data[key] = match.group(1).strip()
        
        # If we couldn't extract much, return the raw text with error flag
        if len(structured_data) < 2:
            return {
                'extraction_method': 'text_fallback',
                'raw_response': text_response,
                'structured_data': structured_data,
                'note': 'Could not parse into full JSON structure'
            }
        
        return structured_data
    
    def validate_extraction(self, extracted_data):
        """Validate that the extracted data meets quality standards"""
        if not extracted_data or extracted_data.get('extraction_failed'):
            return False, "Extraction failed"
        
        # Check for minimum required fields
        required_sections = ['company_snapshot', 'mission_vision_values']
        
        for section in required_sections:
            if section not in extracted_data:
                return False, f"Missing required section: {section}"
        
        # Check for some actual content (not all "Not available")
        total_fields = 0
        available_fields = 0
        
        for section_data in extracted_data.values():
            if isinstance(section_data, dict):
                for value in section_data.values():
                    total_fields += 1
                    if value and value != "Not available" and value != "Not found":
                        available_fields += 1
        
        completion_rate = available_fields / total_fields if total_fields > 0 else 0
        
        if completion_rate < 0.1:  # Less than 10% completion
            return False, f"Low completion rate: {completion_rate:.1%}"
        
        return True, f"Extraction valid with {completion_rate:.1%} completion"

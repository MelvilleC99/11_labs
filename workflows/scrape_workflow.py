"""
Scrape Workflow - Orchestrates the complete website scraping and data extraction process
Flow: scrape → clean → extract → save
"""
import uuid
from datetime import datetime
from tools.web_scraper import WebScraper
from tools.html_cleaner import HTMLCleaner
from agents.scraper_agent import ScraperAgent
from shared_services.supabase_client import supabase

class ScrapeWorkflow:
    def __init__(self):
        self.web_scraper = WebScraper()
        self.html_cleaner = HTMLCleaner()
        self.scraper_agent = ScraperAgent()
        
    def run(self, url, user_id=None):
        """
        Run the complete scraping workflow
        
        Args:
            url (str): Website URL to scrape
            user_id (str): Optional user ID for database tracking
            
        Returns:
            dict: Complete workflow results
        """
        # Generate job ID
        job_id = str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        print(f"Starting scrape workflow")
        print(f"Job ID: {job_id}")
        print(f"URL: {url}")
        print("=" * 80)
        
        # Initialize result structure
        workflow_result = {
            'job_id': job_id,
            'url': url,
            'user_id': user_id,
            'status': 'pending',
            'started_at': start_time.isoformat(),
            'success': False
        }
        
        try:
            # Step 1: Web Scraping
            workflow_result['status'] = 'scraping'
            print("\nSTEP 1: WEB SCRAPING")
            print("-" * 40)
            
            scraping_result = self.web_scraper.scrape_website(url)
            
            if not scraping_result['success']:
                workflow_result.update({
                    'status': 'failed',
                    'error': scraping_result.get('error', 'Scraping failed'),
                    'completed_at': datetime.utcnow().isoformat()
                })
                return workflow_result
            
            workflow_result['pages_scraped'] = list(scraping_result['pages_scraped'].keys())
            workflow_result['scraping_success_rate'] = scraping_result['success_rate']
            
            # Step 2: Content Cleaning
            workflow_result['status'] = 'cleaning'
            print(f"\nSTEP 2: CONTENT CLEANING")
            print("-" * 40)
            
            cleaned_content = self.html_cleaner.combine_page_content(scraping_result['pages_scraped'])
            content_summary = self.html_cleaner.get_content_summary(scraping_result['pages_scraped'])
            
            print(f"Combined content: {len(cleaned_content):,} characters")
            print(f"Total words: {content_summary['total_words']:,}")
            print(f"Successfully cleaned {content_summary['successful_pages']}/{content_summary['total_pages']} pages")
            
            workflow_result['cleaned_content_length'] = len(cleaned_content)
            workflow_result['total_words'] = content_summary['total_words']
            
            # Step 3: Data Extraction
            workflow_result['status'] = 'extracting'
            print(f"\nSTEP 3: AI DATA EXTRACTION")
            print("-" * 40)
            
            extracted_data = self.scraper_agent.extract_company_data(cleaned_content, url)
            
            # Validate extraction
            is_valid, validation_message = self.scraper_agent.validate_extraction(extracted_data)
            print(f"Extraction validation: {validation_message}")
            
            workflow_result['extracted_data'] = extracted_data
            workflow_result['extraction_valid'] = is_valid
            workflow_result['validation_message'] = validation_message
            
            # Step 4: Save to Database
            workflow_result['status'] = 'saving'
            print(f"\nSTEP 4: SAVING TO DATABASE")
            print("-" * 40)
            
            db_result = self._save_to_database(
                job_id=job_id,
                user_id=user_id,
                url=url,
                raw_pages=scraping_result['pages_scraped'],
                cleaned_content=cleaned_content,
                extracted_data=extracted_data,
                metadata={
                    'scraping_success_rate': scraping_result['success_rate'],
                    'total_words': content_summary['total_words'],
                    'extraction_valid': is_valid,
                    'validation_message': validation_message
                }
            )
            
            if db_result['success']:
                print("Successfully saved to database")
                workflow_result['database_id'] = db_result['id']
            else:
                print(f"Database save failed: {db_result['error']}")
                workflow_result['database_error'] = db_result['error']
            
            # Final status
            workflow_result.update({
                'status': 'completed',
                'success': True,
                'completed_at': datetime.utcnow().isoformat()
            })
            
            # Print summary
            print(f"\nWORKFLOW COMPLETED SUCCESSFULLY")
            print("=" * 80)
            print(f"Job ID: {job_id}")
            print(f"URL: {url}")
            print(f"Pages: {len(workflow_result['pages_scraped'])}")
            print(f"Words: {workflow_result['total_words']:,}")
            print(f"Extraction: {'Valid' if is_valid else 'Issues detected'}")
            print(f"Database: {'Saved' if db_result['success'] else 'Failed'}")
            
            return workflow_result
            
        except Exception as e:
            print(f"Workflow error: {str(e)}")
            workflow_result.update({
                'status': 'failed',
                'success': False,
                'error': str(e),
                'completed_at': datetime.utcnow().isoformat()
            })
            return workflow_result
    
    def _save_to_database(self, job_id, user_id, url, raw_pages, cleaned_content, extracted_data, metadata):
        """Save workflow results to Supabase database"""
        try:
            # Prepare data for database
            scrape_job_data = {
                'id': job_id,
                'user_id': user_id,
                'url': url,
                'status': 'completed',
                'raw_pages': raw_pages,
                'cleaned_content': cleaned_content,
                'extracted_data': extracted_data,
                'scraping_started_at': datetime.utcnow().isoformat(),
                'scraping_completed_at': datetime.utcnow().isoformat(),
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Add metadata fields
            if metadata:
                scrape_job_data.update({
                    'pages_scraped': [f"page_{i}" for i in range(len(raw_pages))],
                    'scraper_response_codes': {k: v.get('status_code') for k, v in raw_pages.items()},
                    'content_lengths': {k: len(v.get('html', '')) for k, v in raw_pages.items()},
                })
            
            # Insert into database
            result = supabase.table('scrape_jobs').insert(scrape_job_data).execute()
            
            if result.data:
                return {'success': True, 'id': job_id}
            else:
                return {'success': False, 'error': 'Database insert failed'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}

"""
Scraping configuration loader
"""
import yaml
import os

def load_scraping_config():
    """Load scraping configuration from YAML file"""
    config_path = os.path.join(os.path.dirname(__file__), 'scraping_config.yaml')
    
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"⚠️  Could not load scraping config: {e}")
        # Return default config
        return {
            'scraperapi': {
                'render': True,
                'country_code': 'us',
                'device_type': 'desktop',
                'timeout': 30000
            }
        }

def load_extraction_template():
    """Load company extraction template from YAML file"""
    template_path = os.path.join(os.path.dirname(__file__), 'company_extraction_template.yaml')
    
    try:
        with open(template_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"⚠️  Could not load extraction template: {e}")
        return {}

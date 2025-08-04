"""
Supabase client setup and configuration
"""
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

class SupabaseClient:
    def __init__(self):
        self.url = os.getenv('SUPABASE_URL')
        self.key = (
            os.getenv('SUPABASE_ANON_KEY') or 
            os.getenv('SUPABASE_KEY') or 
            os.getenv('SUPABASE_ANON') or
            os.getenv('SUPABASE_API_KEY')
        )
        
        if not self.url or not self.key:
            raise ValueError("Missing Supabase credentials in environment variables")
        
        self.client = create_client(self.url, self.key)
    
    def get_client(self):
        """Get the Supabase client instance"""
        return self.client

# Global instance
supabase_client = SupabaseClient()
supabase = supabase_client.get_client()

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
            print("⚠️  Warning: Missing Supabase credentials in environment variables")
            print("⚠️  Database functionality will be disabled")
            self.client = None
            return
        
        try:
            self.client = create_client(self.url, self.key)
            print("✅ Supabase client initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing Supabase client: {e}")
            self.client = None
    
    def get_client(self):
        """Get the Supabase client instance"""
        return self.client
    
    def is_available(self):
        """Check if the client is properly initialized"""
        return self.client is not None

# Global instance - will be initialized when first accessed
_supabase_client = None

def get_supabase_client():
    """Lazy initialization of supabase client"""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = SupabaseClient()
    return _supabase_client

# For backward compatibility - but don't initialize yet
def supabase():
    return get_supabase_client().get_client()

# Keep the old variable name for compatibility
supabase_client = get_supabase_client()

from flask import Flask, request, jsonify
import json
import os
from supabase import create_client
from datetime import datetime
import hmac
import hashlib
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Get from environment variables (try different possible names)
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_ANON_KEY = (
    os.getenv('SUPABASE_ANON_KEY') or 
    os.getenv('SUPABASE_KEY') or 
    os.getenv('SUPABASE_ANON') or
    os.getenv('SUPABASE_API_KEY')
)
HMAC_SECRET = os.getenv('HMAC_SECRET')

print(f"🔧 SUPABASE_URL: {SUPABASE_URL[:20]}..." if SUPABASE_URL else "❌ SUPABASE_URL not found")
print(f"🔧 SUPABASE_ANON_KEY: {'✅ Found' if SUPABASE_ANON_KEY else '❌ Not found'}")
print(f"🔧 HMAC_SECRET: {'✅ Found' if HMAC_SECRET else '❌ Not found'}")

# Debug: Show all environment variables that contain 'SUPABASE'
print("🔍 All SUPABASE env vars:")
for key, value in os.environ.items():
    if 'SUPABASE' in key.upper():
        print(f"  {key}: {value[:20]}..." if value else f"  {key}: (empty)")

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    print("❌ Missing required environment variables!")
    print("In Render dashboard, make sure you have:")
    print("SUPABASE_URL=https://your-project.supabase.co")
    print("SUPABASE_ANON_KEY=your-anon-key (or SUPABASE_KEY)")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def get_clean_transcript(transcript_array):
    """Convert transcript array to clean readable text"""
    if isinstance(transcript_array, list):
        clean_lines = []
        for turn in transcript_array:
            if isinstance(turn, dict):
                role = turn.get('role', 'unknown')
                message = turn.get('message', '')
                clean_lines.append(f"{role.title()}: {message}")
        return "\n".join(clean_lines)
    return str(transcript_array)

def get_user_id(conversation):
    """Handle the session ID issue you mentioned"""
    
    # Try to get user_id from dynamic variables (if you set it in ElevenLabs)
    dynamic_vars = conversation.get('dynamic_variables', {})
    if 'user_id' in dynamic_vars:
        return dynamic_vars['user_id']
    
    # Try to get from session or other fields
    session_id = conversation.get('session_id') or conversation.get('conversation_id')
    
    # For now, create a consistent user ID from session
    if session_id:
        return f"user_{session_id[:8]}"  # First 8 chars of session
    
    return "anonymous_user"

@app.route('/tools/getUserContext', methods=['POST'])
def get_user_context():
    """Tool endpoint for agent to get user's previous context"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'test_user_123')
        
        print(f"🔍 Getting context for user: {user_id}")
        
        # Get user's previous conversations from Supabase
        result = supabase.table('conversations')\
            .select('extracted_data, analysis_summary, created_at')\
            .eq('user_id', user_id)\
            .order('created_at', desc=True)\
            .limit(1)\
            .execute()
        
        if not result.data:
            return jsonify({
                "status": "new_user",
                "message": "New user - starting fresh with section 1",
                "context_summary": "No previous sessions found"
            })
        
        # Process the organized data from database
        latest_session = result.data[0]
        extracted_data = latest_session.get('extracted_data', {})
        
        # Build context summary from the clean data structure
        completed_fields = []
        missing_fields = []
        
        key_fields = [
            'broad_domain_expertise',
            'specific_niche_focus', 
            'ideal_client_definition',
            'target_customer_problems',
            'signature_outcomes'
        ]
        
        for field in key_fields:
            if field in extracted_data and extracted_data[field].get('value'):
                field_display = field.replace('_', ' ').title()
                value = extracted_data[field]['value'][:50] + "..." if len(extracted_data[field]['value']) > 50 else extracted_data[field]['value']
                completed_fields.append(f"{field_display}: {value}")
            else:
                missing_fields.append(field.replace('_', ' ').title())
        
        if completed_fields:
            recap = f"Welcome back! From our previous session, I know: {'; '.join(completed_fields[:2])}."
            if missing_fields:
                recap += f" We still need to discuss: {', '.join(missing_fields[:2])}."
        else:
            recap = "Welcome back! I see you've started before. Let's continue where we left off."
            
        return jsonify({
            "status": "returning_user",
            "message": recap,
            "context_summary": "; ".join(completed_fields) if completed_fields else "Previous session but no data extracted",
            "completed_count": len(completed_fields),
            "missing_count": len(missing_fields),
            "last_session": latest_session.get('created_at')
        })
        
    except Exception as e:
        print(f"❌ Error in getUserContext: {str(e)}")
        return jsonify({
            "status": "error", 
            "message": "I'll help you create your LinkedIn persona from scratch!",
            "context_summary": f"Error retrieving context: {str(e)}"
        }), 200  # Return 200 so agent continues

@app.route('/webhook/elevenlabs', methods=['POST'])
def handle_webhook():
    try:
        # BYPASSING HMAC CHECK FOR TESTING
        print("🚨 BYPASSING HMAC CHECK FOR TESTING")
        
        # Get raw data for logging
        raw_data = request.get_data()
        signature = request.headers.get('X-ElevenLabs-Signature')
        
        print(f"📥 Received webhook call")
        print(f"📝 Signature header: {signature}")
        print(f"📊 Data length: {len(raw_data)} bytes")
        
        # Get the JSON data from ElevenLabs
        data = request.get_json()
        
        print("=== RECEIVED WEBHOOK ===")
        print(json.dumps(data, indent=2))  # This will show you EVERYTHING
        print("=======================")
        
        # Check if it's a conversation transcript
        if data.get('type') == 'post_call_transcription':
            conversation = data.get('data', {})
            
            # Extract the CLEAN organized data from ElevenLabs analysis
            analysis = conversation.get('analysis', {})
            data_collection = analysis.get('data_collection_results', {})
            
            # Build organized extracted data
            organized_data = {}
            for field_name, field_data in data_collection.items():
                if isinstance(field_data, dict) and 'value' in field_data:
                    organized_data[field_name] = {
                        'value': field_data.get('value'),
                        'rationale': field_data.get('rationale', '')
                    }
            
            # Extract what we need
            conversation_record = {
                'conversation_id': conversation.get('conversation_id', 'unknown'),
                'transcript': get_clean_transcript(conversation.get('transcript', [])),
                'user_id': get_user_id(conversation),
                'call_duration': conversation.get('call_duration_secs', 0),
                'success': conversation.get('call_successful', False),
                'extracted_data': organized_data,  # This is clean organized JSONB data
                'analysis_summary': analysis.get('transcript_summary', ''),
                'evaluation_results': analysis.get('evaluation_criteria_results', {}),
                'created_at': datetime.utcnow().isoformat(),
                'full_data': conversation  # Complete raw data as JSONB
            }
            
            print("=== SAVING TO SUPABASE ===")
            print(f"Conversation ID: {conversation_record['conversation_id']}")
            print(f"User ID: {conversation_record['user_id']}")
            print(f"Transcript length: {len(conversation_record['transcript'])} chars")
            print(f"Extracted fields: {list(organized_data.keys())}")
            print("=== ORGANIZED EXTRACTED DATA ===")
            for field, data in organized_data.items():
                print(f"{field}: {data['value']}")
            print("=========================")
            
            # Save to Supabase
            result = supabase.table('conversations').insert(conversation_record).execute()
            
            if result.data:
                print("✅ SUCCESS: Data saved to Supabase!")
                return jsonify({'status': 'success'}), 200
            else:
                print("❌ ERROR: Failed to save to Supabase")
                return jsonify({'error': 'database_error'}), 500
                
        return jsonify({'status': 'ignored'}), 200
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/test', methods=['GET'])
def test():
    """Test if everything is working"""
    try:
        # Test Supabase connection
        result = supabase.table('conversations').select('count').limit(1).execute()
        return jsonify({
            'status': 'working',
            'supabase': 'connected',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("🚀 Starting webhook server...")
    print("📡 Webhook URL will be: https://one1-labs.onrender.com/webhook/elevenlabs")
    print("🧪 Test URL: http://localhost:5000/test")
    app.run(debug=True, host='0.0.0.0', port=5000)
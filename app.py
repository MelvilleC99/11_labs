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
    """Extract user ID with proper fallbacks for testing"""
    
    # Try to get from dynamic variables (when coming from your frontend)
    client_data = conversation.get('conversation_initiation_client_data', {})
    dynamic_vars = client_data.get('dynamic_variables', {})
    
    if 'user_id' in dynamic_vars:
        return dynamic_vars['user_id']
    
    # For testing from ElevenLabs dashboard, use user_name if available
    if 'user_name' in dynamic_vars:
        return f"test_user_{dynamic_vars['user_name']}"
    
    # Final fallback - create consistent ID from conversation
    conversation_id = conversation.get('conversation_id', 'unknown')
    return f"test_user_{conversation_id[:8]}"

@app.route('/tools/getUserContext', methods=['POST'])
def get_user_context():
    """Tool endpoint for agent to get user's previous context"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'test_user_123')
        
        print(f"🔍 Getting context for user: {user_id}")
        
        # Get user's clean data points from the new table
        result = supabase.table('user_data_points')\
            .select('data_point_key, value')\
            .eq('user_id', user_id)\
            .execute()
        
        if not result.data:
            return jsonify({
                "status": "new_user",
                "message": "New user - starting fresh. Let's build your LinkedIn persona. What's a broad topic or domain you could speak about confidently for hours?",
                "context_summary": "No previous sessions found"
            })
        
        # Process the clean data points
        user_data = {}
        for item in result.data:
            user_data[item['data_point_key']] = item['value']
        
        # Check which required fields we have
        required_fields = [
            'broad_domain_expertise',
            'specific_niche_focus', 
            'ideal_client_definition',
            'target_customer_problems',
            'signature_outcomes'
        ]
        
        completed_fields = []
        missing_fields = []
        
        for field in required_fields:
            if field in user_data and user_data[field] and user_data[field].strip():
                field_display = field.replace('_', ' ').title()
                value_preview = user_data[field][:40] + "..." if len(user_data[field]) > 40 else user_data[field]
                completed_fields.append(f"{field_display}: {value_preview}")
            else:
                missing_fields.append(field.replace('_', ' ').title())
        
        # Create context message for the agent
        if completed_fields:
            if len(missing_fields) == 0:
                context_message = f"Welcome back! We've completed your LinkedIn persona: {'; '.join(completed_fields)}. Let me summarize everything we have."
            else:
                context_message = f"Welcome back! From our previous session, I have: {'; '.join(completed_fields[:2])}{'...' if len(completed_fields) > 2 else ''}. We still need to discuss: {', '.join(missing_fields[:2])}{'...' if len(missing_fields) > 2 else ''}."
        else:
            context_message = "I see we've started before, but I don't have any complete information yet. Let's continue building your LinkedIn persona."
            
        return jsonify({
            "status": "returning_user",
            "message": context_message,
            "context_summary": f"Completed: {len(completed_fields)}/5 fields | Missing: {', '.join(missing_fields) if missing_fields else 'None'}",
            "completed_count": len(completed_fields),
            "missing_count": len(missing_fields),
            "completed_fields": completed_fields,
            "missing_fields": missing_fields
        })
        
    except Exception as e:
        print(f"❌ Error in getUserContext: {str(e)}")
        return jsonify({
            "status": "error", 
            "message": "Let's build your LinkedIn persona from scratch! What's a broad topic or domain you could speak about confidently for hours?",
            "context_summary": f"Error retrieving context: {str(e)}"
        }), 200  # Return 200 so agent continues

@app.route('/webhook/elevenlabs', methods=['POST'])
def handle_webhook():
    try:
        # BYPASSING HMAC CHECK FOR TESTING
        print("🚨 BYPASSING HMAC CHECK FOR TESTING")
        
        # Get raw data for logging
        raw_data = request.get_data()
        signature = request.headers.get('ElevenLabs-Signature')  # Fixed: Remove X- prefix
        
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
                
                # Run cleanup to extract clean data to user_data_points
                cleanup_conversation_data(conversation_record)
                
                return jsonify({'status': 'success'}), 200
            else:
                print("❌ ERROR: Failed to save to Supabase")
                return jsonify({'error': 'database_error'}), 500
                
        return jsonify({'status': 'ignored'}), 200
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return jsonify({'error': str(e)}), 500

def cleanup_conversation_data(conversation_record):
    """Extract clean values from conversation data and save to user_data_points"""
    try:
        print("🧹 Starting data cleanup...")
        
        user_id = conversation_record['user_id']
        extracted_data = conversation_record['extracted_data']
        created_at = conversation_record['created_at']
        
        if not extracted_data:
            print("⚠️  No extracted data to clean up")
            return
        
        # Clean and save each field
        cleanup_successes = 0
        cleanup_errors = []
        
        # Skip these meta fields - we only want the actual user data
        skip_fields = ['session_id', 'correction_handling', 'information_completeness_tracker']
        
        for field_name, field_data in extracted_data.items():
            # Skip meta fields
            if field_name in skip_fields:
                continue
                
            # Only save fields that have actual values
            if isinstance(field_data, dict) and field_data.get('value'):
                try:
                    clean_record = {
                        'user_id': user_id,
                        'data_point_key': field_name,
                        'value': str(field_data['value']).strip(),
                        'rationale': str(field_data.get('rationale', '')).strip(),
                        'answered_at': created_at
                    }
                    
                    # Use upsert to handle updates
                    result = supabase.table('user_data_points').upsert(
                        clean_record,
                        on_conflict='user_id,data_point_key'
                    ).execute()
                    
                    if result.data:
                        cleanup_successes += 1
                        print(f"✅ Cleaned & saved: {field_name}")
                    else:
                        cleanup_errors.append(f"No result for {field_name}")
                        
                except Exception as e:
                    cleanup_errors.append(f"Error cleaning {field_name}: {str(e)}")
                    print(f"❌ Cleanup error for {field_name}: {e}")
            else:
                print(f"⏭️  Skipping {field_name}: no value")
        
        print(f"🧹 Cleanup complete: {cleanup_successes} cleaned, {len(cleanup_errors)} errors")
        
        if cleanup_errors:
            print("❌ Cleanup errors:")
            for error in cleanup_errors:
                print(f"  - {error}")
                
    except Exception as e:
        print(f"❌ Cleanup failed: {str(e)}")
        # Don't fail the webhook - just log the error

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
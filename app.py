from flask import Flask, request, jsonify
import json
import os
from supabase import create_client
from datetime import datetime
import hmac
import hashlib

app = Flask(__name__)

# Get from environment variables
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY') 
HMAC_SECRET = os.getenv('HMAC_SECRET')

supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def verify_hmac(data, signature):
    """Verify HMAC signature from ElevenLabs"""
    if not HMAC_SECRET:
        return True  # Skip verification if no secret
    
    expected = hmac.new(
        HMAC_SECRET.encode(),
        data,
        hashlib.sha256
    ).hexdigest()
    
    received = signature.replace('sha256=', '') if signature else ''
    return hmac.compare_digest(expected, received)

@app.route('/webhook/elevenlabs', methods=['POST'])
def handle_webhook():
    try:
        # Get raw data for HMAC verification
        raw_data = request.get_data()
        signature = request.headers.get('X-ElevenLabs-Signature')
        
        # Verify HMAC (optional)
        if not verify_hmac(raw_data, signature):
            print("❌ HMAC verification failed")
            return jsonify({'error': 'unauthorized'}), 401
        
        # Get the JSON data from ElevenLabs
        data = request.get_json()
        
        print("=== RECEIVED WEBHOOK ===")
        print(json.dumps(data, indent=2))  # This will show you EVERYTHING
        print("=======================")
        
        # Check if it's a conversation transcript
        if data.get('type') == 'post_call_transcription':
            conversation = data.get('data', {})
            
            # Extract what we need
            conversation_record = {
                'conversation_id': conversation.get('conversation_id', 'unknown'),
                'transcript': conversation.get('transcript', ''),
                'user_id': get_user_id(conversation),  # Handle the session ID issue
                'call_duration': conversation.get('call_length_seconds', 0),
                'success': conversation.get('call_successful', False),
                'extracted_data': conversation.get('data_collection', {}),
                'created_at': datetime.utcnow().isoformat(),
                'full_data': conversation  # Store everything for debugging
            }
            
            print("=== SAVING TO SUPABASE ===")
            print(f"Conversation ID: {conversation_record['conversation_id']}")
            print(f"User ID: {conversation_record['user_id']}")
            print(f"Transcript length: {len(conversation_record['transcript'])} chars")
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
    print("📡 Webhook URL will be: http://your-ngrok-url.ngrok.io/webhook/elevenlabs")
    print("🧪 Test URL: http://localhost:5000/test")
    app.run(debug=True, host='0.0.0.0', port=5000)
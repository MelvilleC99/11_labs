from flask import Flask, request, jsonify
from supabase import create_client, Client
import os

app = Flask(__name__)

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Save persona section 1
@app.route('/save-persona-section1', methods=['POST'])
def save_persona_section1():
    data = request.json
    session_id = data.get('session_id')
    # extract all the section 1 variables here
    record = {
        'session_id': session_id,
        'broad_domain_expertise': data.get('broad_domain_expertise'),
        'broad_domain_expertise_quality': data.get('broad_domain_expertise_quality'),
        'specific_niche_focus': data.get('specific_niche_focus'),
        'specific_niche_focus_quality': data.get('specific_niche_focus_quality'),
        'ideal_client_definition': data.get('ideal_client_definition'),
        'ideal_client_definition_quality': data.get('ideal_client_definition_quality'),
        'target_customer_problems': data.get('target_customer_problems'),
        'target_customer_problems_quality': data.get('target_customer_problems_quality'),
        'signature_outcomes': data.get('signature_outcomes'),
        'signature_outcomes_quality': data.get('signature_outcomes_quality')
    }
    # Upsert by session_id (update if exists, insert if new)
    supabase.table('persona_section_1').upsert(record).execute()
    return jsonify({'status': 'success'})

# Optional: fetch section 1 data for session_id
@app.route('/get-persona-section1', methods=['GET'])
def get_persona_section1():
    session_id = request.args.get('session_id')
    response = supabase.table('persona_section_1').select('*').eq('session_id', session_id).execute()
    return jsonify(response.data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

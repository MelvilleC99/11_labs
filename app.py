import os
import hmac
import hashlib
from flask import Flask, request, abort, jsonify
from supabase import create_client, Client

app = Flask(__name__)

# Load Supabase credentials from environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# (Optional) For HMAC webhook security
HMAC_SECRET = os.getenv("ELEVENLABS_WEBHOOK_SECRET")

def verify_signature(request):
    signature = request.headers.get('ElevenLabs-Signature')
    if not signature:
        abort(401, description="Missing signature.")
    raw_body = request.get_data()
    computed = hmac.new(
        HMAC_SECRET.encode('utf-8'),
        raw_body,
        hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(computed, signature):
        abort(401, description="Signature verification failed.")

@app.route("/save-persona-section1", methods=["POST"])
def save_persona_section1():
    # Uncomment next line if you have HMAC security enabled!
    # verify_signature(request)

    # Log the full request for debugging
    try:
        data = request.get_json(force=True)
        print("== FULL PAYLOAD ==")
        print(data)
    except Exception as e:
        print("JSON Parse Error:", str(e))
        return jsonify({"status": "error", "msg": "Invalid JSON"}), 400

    # Try all locations for session ID
    session_id = (
        data.get("session_id") or
        data.get("conversation_id") or
        (data.get("data", {}) or {}).get("session_id") or
        (data.get("data", {}) or {}).get("conversation_id")
    )
    if not session_id:
        print("ERROR: No session_id or conversation_id in payload!")
        return jsonify({"status": "error", "msg": "Missing session_id"}), 400

    # You may also want to dig into ElevenLabs' nested "data" if you see nothing at root level
    section_data = data.get("data", {}) if "data" in data else data

    record = {
        "session_id": session_id,
        "broad_domain_expertise": section_data.get("broad_domain_expertise"),
        "broad_domain_expertise_quality": section_data.get("broad_domain_expertise_quality"),
        "specific_niche_focus": section_data.get("specific_niche_focus"),
        "specific_niche_focus_quality": section_data.get("specific_niche_focus_quality"),
        "ideal_client_definition": section_data.get("ideal_client_definition"),
        "ideal_client_definition_quality": section_data.get("ideal_client_definition_quality"),
        "target_customer_problems": section_data.get("target_customer_problems"),
        "target_customer_problems_quality": section_data.get("target_customer_problems_quality"),
        "signature_outcomes": section_data.get("signature_outcomes"),
        "signature_outcomes_quality": section_data.get("signature_outcomes_quality"),
        # Add more fields as needed for your schema
    }

    # Remove keys with None values (Supabase will ignore them)
    record = {k: v for k, v in record.items() if v is not None}

    # Save to Supabase
    try:
        resp = supabase.table("persona_section_1").upsert(record).execute()
        print("== SUPABASE RESPONSE ==")
        print(resp)
        return jsonify({"status": "ok", "msg": "Saved", "data": resp.data}), 200
    except Exception as e:
        print("Supabase insert error:", e)
        return jsonify({"status": "error", "msg": str(e)}), 500

@app.route("/", methods=["GET"])
def health_check():
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=False, host="0.0.0.0", port=port)

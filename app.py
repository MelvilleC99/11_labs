import os
from flask import Flask, request, jsonify
from supabase import create_client, Client
from datetime import datetime
import uuid

app = Flask(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route("/save-persona-call", methods=["POST"])
def save_persona_call():
    try:
        # Get full JSON payload
        payload = request.get_json(force=True)
        print("== FULL PAYLOAD ==")
        print(payload)
        
        record = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "payload": payload
        }
        # Save to Supabase
        resp = supabase.table("persona_calls").insert(record).execute()
        print("== SUPABASE RESPONSE ==")
        print(resp)
        return jsonify({"status": "ok", "msg": "Saved"}), 200
    except Exception as e:
        print("Supabase insert error:", e)
        return jsonify({"status": "error", "msg": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=10000)

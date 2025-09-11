from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
import os
import time

app = Flask(__name__)
CORS(app, origins=["*"])  # Allow all origins

# Hugging Face Space event-based endpoint
HF_SPACE_URL = "https://anaswarsi-chatbot-demo.hf.space/gradio_api/call/predict"

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Chatbot Proxy Server is running!",
        "endpoints": {
            "/chat": "POST - Send message to chatbot"
        },
        "status": "healthy"
    })

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        user_message = data.get("message", "").strip()
        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        # Step 1: Send message to HF Space and get event ID
        payload = {"data": [user_message]}
        headers = {"Content-Type": "application/json"}
        r1 = requests.post(HF_SPACE_URL, json=payload, headers=headers, timeout=30)
        
        if r1.status_code != 200:
            return jsonify({"error": f"HuggingFace API error (step1): {r1.status_code}", "details": r1.text}), 500

        res1 = r1.json()
        event_id = res1.get("id") or res1.get("hash")
        if not event_id:
            return jsonify({"error": "No event ID returned from HuggingFace", "details": str(res1)}), 500

        # Step 2: Poll the event endpoint until we get a response
        result = None
        for _ in range(10):  # try 10 times (approx 5s)
            r2 = requests.get(f"{HF_SPACE_URL}/{event_id}", headers=headers, timeout=30)
            if r2.status_code != 200:
                continue
            res2 = r2.json()
            # Check if the event contains "data"
            if "data" in res2 and len(res2["data"]) > 0:
                result = res2
                break
            time.sleep(0.5)

        if not result:
            return jsonify({"error": "No valid response from HuggingFace", "details": str(res2)}), 500

        bot_response = result["data"][0]
        return jsonify({"success": True, "response": bot_response})

    except requests.RequestException as e:
        return jsonify({"error": "Network error", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"error": "Server error", "details": str(e)}), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "hf_endpoint": HF_SPACE_URL})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

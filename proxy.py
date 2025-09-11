from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
import os
import time

app = Flask(__name__)
CORS(app, origins=["*"])  # Allow all origins for GitHub Pages

# Hugging Face Space Gradio API endpoint
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
        # Get user input from request
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        user_message = data.get("message", "")
        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        headers = {"Content-Type": "application/json"}
        payload = {"data": [user_message]}

        # Step 1: POST message to HF Gradio API to get EVENT_ID
        r1 = requests.post(HF_SPACE_URL, json=payload, headers=headers, timeout=30)
        if r1.status_code != 200:
            return jsonify({
                "error": f"HuggingFace API error (step 1): {r1.status_code}",
                "details": r1.text
            }), 500

        r1_json = r1.json()
        event_id = r1_json.get("id")
        if not event_id:
            return jsonify({
                "error": "No event ID returned from HuggingFace",
                "details": r1_json
            }), 500

        # Step 2: Poll HF API for the result using EVENT_ID
        result = None
        poll_url = f"{HF_SPACE_URL}/{event_id}"
        for _ in range(10):  # poll up to 10 times
            r2 = requests.get(poll_url, headers=headers, timeout=30)
            if r2.status_code != 200:
                continue
            r2_json = r2.json()
            # Check if data is ready
            if "data" in r2_json and len(r2_json["data"]) > 0:
                result = r2_json["data"][0]
                break
            time.sleep(1)  # wait 1 second before retry

        if result is None:
            return jsonify({
                "error": "No response received from HuggingFace after polling",
                "details": r2_json if 'r2_json' in locals() else {}
            }), 500

        return jsonify({
            "success": True,
            "response": result
        })

    except requests.RequestException as e:
        return jsonify({
            "error": "Network error connecting to HuggingFace",
            "details": str(e)
        }), 500
    except Exception as e:
        return jsonify({
            "error": "Server error",
            "details": str(e)
        }), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "hf_endpoint": HF_SPACE_URL
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

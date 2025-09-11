from flask import Flask, request, jsonify
import requests
import time
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["*"])

# Hugging Face Space base URL (CHANGE if your space name changes)
HF_SPACE = "https://anaswarsi-chatbot-demo.hf.space"
JOIN_URL = f"{HF_SPACE}/gradio_api/queue/join"
DATA_URL = f"{HF_SPACE}/gradio_api/queue/data"

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Chatbot Proxy Server (Queue) is running!",
        "endpoints": {
            "/chat": "POST - Send message to chatbot"
        },
        "status": "healthy"
    })

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        if not data or "message" not in data:
            return jsonify({"error": "No message provided"}), 400

        user_message = data["message"]

        # Step 1: Join queue
        payload = {
            "data": [user_message],
            "event_data": None,
            "fn_index": 0  # function index (0 if single interface)
        }
        headers = {"Content-Type": "application/json"}

        join_resp = requests.post(JOIN_URL, json=payload, headers=headers, timeout=30)
        if join_resp.status_code != 200:
            return jsonify({
                "error": f"HuggingFace join error {join_resp.status_code}",
                "details": join_resp.text
            }), 500

        join_data = join_resp.json()
        event_id = join_data.get("hash")
        if not event_id:
            return jsonify({
                "error": "No event ID returned from HuggingFace",
                "details": join_data
            }), 500

        # Step 2: Poll for result
        final_result = None
        for _ in range(60):  # wait up to ~60 seconds
            poll_resp = requests.get(f"{DATA_URL}?session_hash={event_id}", timeout=30)
            if poll_resp.status_code != 200:
                return jsonify({
                    "error": f"HuggingFace poll error {poll_resp.status_code}",
                    "details": poll_resp.text
                }), 500

            poll_data = poll_resp.json()
            if "data" in poll_data and poll_data["data"]:
                final_result = poll_data
                break
            time.sleep(1)

        if not final_result:
            return jsonify({"error": "No response from HuggingFace (timeout)"}), 504

        # Step 3: Extract chatbot response
        bot_reply = final_result["data"][0] if "data" in final_result else "No reply"

        return jsonify({"success": True, "response": bot_reply})

    except Exception as e:
        return jsonify({"error": "Server error", "details": str(e)}), 500


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "hf_endpoint": HF_SPACE
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

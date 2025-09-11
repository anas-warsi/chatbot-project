from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)  # Allow all origins

# Hugging Face Space queue endpoint
HF_QUEUE_URL = "https://anaswarsi-chatbot-demo.hf.space/gradio_api/queue/predict"

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
        if not data or "message" not in data:
            return jsonify({"error": "No message provided"}), 400

        user_message = data["message"]

        # Send request to Hugging Face Space queue API
        payload = {"data": [user_message]}
        headers = {"Content-Type": "application/json"}

        response = requests.post(HF_QUEUE_URL, json=payload, headers=headers, timeout=30)

        if response.status_code != 200:
            return jsonify({
                "error": f"HuggingFace API error: {response.status_code}",
                "details": response.text
            }), 500

        result = response.json()

        # Extract bot response from queue API
        if "data" in result and len(result["data"]) > 0:
            bot_response = result["data"][0]
            return jsonify({"success": True, "response": bot_response})
        else:
            return jsonify({"error": "Invalid response format", "details": str(result)}), 500

    except requests.RequestException as e:
        return jsonify({"error": "Network error", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"error": "Server error", "details": str(e)}), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "hf_endpoint": HF_QUEUE_URL})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

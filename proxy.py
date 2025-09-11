from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app, origins=["*"])  # Allow GitHub Pages frontend

# ✅ Correct Hugging Face endpoint
HF_SPACE_URL = "https://anaswarsi-chatbot-demo.hf.space/run/predict"

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Chatbot Proxy Server is running!",
        "endpoints": {"/chat": "POST - Send message to chatbot"},
        "status": "healthy"
    })

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        user_message = data.get("message", "")
        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        payload = {"data": [user_message]}
        headers = {"Content-Type": "application/json"}

        response = requests.post(HF_SPACE_URL, json=payload, headers=headers, timeout=30)

        if response.status_code != 200:
            return jsonify({
                "error": f"HuggingFace API error: {response.status_code}",
                "details": response.text
            }), 500

        result = response.json()

        # ✅ HuggingFace returns {"data": ["bot reply"]}
        if "data" in result and len(result["data"]) > 0:
            return jsonify({"success": True, "response": result["data"][0]})
        else:
            return jsonify({"error": "Invalid response format", "details": result}), 500

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

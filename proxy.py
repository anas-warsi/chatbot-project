# proxy.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # allow frontend to access

SPACE_API_URL = "https://huggingface.co/spaces/anaswarsi/chatbot-demo/api/predict"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    if not data or "message" not in data:
        return jsonify({"error": "No message provided"}), 400

    message = data["message"]
    try:
        response = requests.post(
            SPACE_API_URL,
            json={"data": [message]},
            timeout=30
        )
        hf_data = response.json()
        bot_reply = hf_data.get("data", ["Sorry, no response."])[0]
        return jsonify({"reply": bot_reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)

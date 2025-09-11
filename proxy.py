from flask import Flask, request, jsonify
from flask_cors import CORS
from gradio_client import Client
import os

app = Flask(__name__)
CORS(app, origins=["*"])  # Allow all origins

# Initialize Gradio client for your HF Space
client = Client("anaswarsi/chatbot-demo")

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

        user_message = data.get("message", "")
        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        # Call the Gradio /predict API
        bot_response = client.predict(
            user_message,
            api_name="/predict"
        )

        return jsonify({"success": True, "response": bot_response})

    except Exception as e:
        return jsonify({"error": "Server error", "details": str(e)}), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "hf_space": "anaswarsi/chatbot-demo"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

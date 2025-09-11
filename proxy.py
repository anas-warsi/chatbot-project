from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app, origins=["*"])  # Allow all origins for GitHub Pages

# Your Hugging Face Space API endpoint
HF_SPACE_URL = "https://anaswarsi-chatbot-demo.hf.space/api/predict"

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Chatbot Proxy Server is running!",
        "endpoints": {
            "/chat": "POST - Send message to chatbot"
        }
    })

@app.route("/chat", methods=["POST"])
def chat():
    try:
        # Get user input from request
        data = request.get_json()
        user_message = data.get("message", "")
        
        if not user_message:
            return jsonify({"error": "No message provided"}), 400
        
        # Prepare data for Gradio API call
        payload = {
            "data": [user_message]
        }
        
        # Make request to Hugging Face Space
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            HF_SPACE_URL,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            # Extract the bot's response from Gradio format
            bot_response = result.get("data", ["Error getting response"])[0]
            return jsonify({
                "success": True,
                "response": bot_response
            })
        else:
            return jsonify({
                "error": f"HuggingFace API error: {response.status_code}",
                "details": response.text
            }), 500
            
    except requests.RequestException as e:
        return jsonify({
            "error": "Network error",
            "details": str(e)
        }), 500
    except Exception as e:
        return jsonify({
            "error": "Server error", 
            "details": str(e)
        }), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
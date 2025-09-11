from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
import json
import os

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
        
        # Prepare data for Gradio API call
        payload = {
            "data": [user_message]
        }
        
        # Make request to Hugging Face Space
        headers = {
            "Content-Type": "application/json"
        }
        
        print(f"Sending request to HF Space: {user_message}")  # Debug log
        
        response = requests.post(
            HF_SPACE_URL,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        print(f"HF Response status: {response.status_code}")  # Debug log
        
        if response.status_code == 200:
            result = response.json()
            print(f"HF Response data: {result}")  # Debug log
            
            # Extract the bot's response from Gradio format
            if "data" in result and len(result["data"]) > 0:
                bot_response = result["data"][0]
                return jsonify({
                    "success": True,
                    "response": bot_response
                })
            else:
                return jsonify({
                    "error": "Invalid response format from HuggingFace",
                    "details": str(result)
                }), 500
        else:
            return jsonify({
                "error": f"HuggingFace API error: {response.status_code}",
                "details": response.text
            }), 500
            
    except requests.RequestException as e:
        print(f"Network error: {str(e)}")  # Debug log
        return jsonify({
            "error": "Network error connecting to HuggingFace",
            "details": str(e)
        }), 500
    except Exception as e:
        print(f"Server error: {str(e)}")  # Debug log
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

# Production-ready configuration
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
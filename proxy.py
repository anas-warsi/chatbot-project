from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

HF_API_URL = "https://anaswarsi-chatbot-demo.hf.space/gradio_api/call/predict"

@app.route("/proxy", methods=["POST"])
def proxy():
    try:
        data = request.get_json()
        response = requests.post(HF_API_URL, json=data)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

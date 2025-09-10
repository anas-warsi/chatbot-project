from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from datetime import datetime
import torch
import os

app = Flask(__name__)
CORS(app)

MODEL_NAME = "distilgpt2"
model = None
tokenizer = None
generator = None

def load_model():
    global model, tokenizer, generator
    if model is None or tokenizer is None:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
        generator = pipeline("text-generation", model=model, tokenizer=tokenizer)

def get_current_date():
    return datetime.now().strftime("%Y-%m-%d")

def generate_reply(user_input):
    load_model()  # model will be loaded only on first request
    date_info = f"Today's date is {get_current_date()}."
    prompt = f"{date_info}\nUser: {user_input}\nBot:"
    outputs = generator(prompt, max_length=150, num_return_sequences=1,
                        do_sample=True, top_k=50, top_p=0.95, repetition_penalty=2.0)
    reply = outputs[0].get("generated_text", "")
    if "Bot:" in reply:
        reply = reply.split("Bot:")[-1].strip()
    return reply or "Sorry, I couldn’t generate a response."

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_input = data.get("message", "")
    if not user_input:
        return jsonify({"reply": "Please enter a message."})
    reply = generate_reply(user_input)
    return jsonify({"reply": reply})

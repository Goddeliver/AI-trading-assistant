from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    try:
        data = request.get_json()
        user_msg = data.get("message", "")
       
        # GodivaFX001 AI Answer
        answer = f"I am GodivaFX001 AI - Created by GodivaFX001, Forex Mentor from Enugu, Nigeria. I can teach: market structure, order block, FVG, liquidity, BOS, choch, gold/xauusd, lot. You asked: {user_msg}. Ask me anything!"

        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"answer": f"Error: {str(e)}"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)





import os
import requests
import base64
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

GROQ_KEY = os.getenv("GROQ_API_KEY","").strip()
TWELVE_KEY = os.getenv("TWELVEDATA_API_KEY","").strip()

def get_price():
    try:
        url = "https://api.twelvedata.com/price?symbol=XAU/USD&apikey=" + TWELVE_KEY
        data = requests.get(url, timeout=8).json()
        return data.get("price","---")
    except:
        return "---"

def get_logo():
    try:
        if os.path.exists("logo.png"):
            with open("logo.png","rb") as f:
                return base64.b64encode(f.read()).decode()
    except:
        pass
    return ""

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
<title>GODIVAFX001 AI</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{background:#000;color:#d4af37;font-family:Arial;text-align:center;padding:20px}
.card{background:#111;padding:20px;border-radius:15px;margin:15px auto;max-width:500px;border:1px solid #d4af37}
button{background:#d4af37;color:#000;padding:14px;border:none;border-radius:8px;font-weight:bold;width:90%;cursor:pointer}
input{padding:14px;width:85%;border-radius:8px;border:0;margin:10px}
.logo{width:120px;height:120px;border-radius:50%;border:3px solid #d4af37}
#ans{white-space:pre-wrap;text-align:left;color:#fff;background:#1a1a1a;padding:15px;border-radius:10px;margin-top:15px}
</style>
</head>
<body>
<img src="data:image/png;base64,{{logo}}" class="logo">
<h1>GODIVAFX001 AI</h1>
<div class="card">Live GOLD: ${{price}}</div>
<div class="card">
<input id="q" placeholder="Should I buy gold? What is turtle soup?">
<br><br>
<button onclick="ask()">Ask GODIVAFX001 AI</button>
<p id="ans"></p>
</div>
<script>
async function ask(){
 let q=document.getElementById('q').value;
 if(!q){alert('Type question');return}
 document.getElementById('ans').innerText='GODIVAFX001 AI analyzing...';
 let res=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:q})});
 let d=await res.json();
 document.getElementById('ans').innerText=d.answer;
}
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_PAGE, price=get_price(), logo=get_logo())

@app.route("/ask", methods=["POST"])
def ask_ai():
    q = request.json.get("question","")
    price = get_price()
    prompt_text = "Gold price is " + str(price) + ". User asks: " + str(q) + ". Answer all forex questions. If buy/sell, give BUY/SELL/WAIT, confidence, entry, SL, TP. Explain ICT concepts like Turtle Soup, Judas Swing."
    
    headers = {
        "Authorization": "Bearer " + GROQ_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "model": "qwen/qwen3-32b",
        "messages": [
            {"role": "system", "content": "You are GODIVAFX001

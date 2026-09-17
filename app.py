import os, requests, base64
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# FIX KEYS - AUTO JOIN EVEN IF YOU PASTE 2 LINES
GROQ_KEY_RAW = os.getenv("GROQ_API_KEY", "")
GROQ_API_KEY = GROQ_KEY_RAW.replace("\n","").replace("\r","").replace(" ","").strip()

TWELVE_KEY_RAW = os.getenv("TWELVEDATA_API_KEY", "")
TWELVEDATA_API_KEY = TWELVE_KEY_RAW.replace("\n","").replace("\r","").replace(" ","").strip()

def get_gold_price():
    try:
        url = f"https://api.twelvedata.com/price?symbol=XAU/USD&apikey={TWELVEDATA_API_KEY}"
        r = requests.get(url, timeout=10).json()
        return r.get("price", "---")
    except:
        return "---"

def get_logo_base64():
    try:
        if os.path.exists("logo.png"):
            with open("logo.png", "rb") as f:
                return base64.b64encode(f.read()).decode()
    except:
        pass
    return ""

HTML = """
<!DOCTYPE html>
<html>
<head><title>TANT - Gold AI</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{background:#0a0a0a;color:gold;font-family:Arial;text-align:center;padding:20px}
.card{background:#1a1a1a;padding:20px;border-radius:15px;margin:10px auto;max-width:500px;border:1px solid gold}
button{background:gold;color:black;padding:12px 20px;border:none;border-radius:8px;font-weight:bold}
input{padding:12px;width:80%;border-radius:8px;border:none;margin:10px}
.logo{width:120px;height:120px;border-radius:50%;object-fit:cover;border:2px solid gold}
</style>
</head>
<body>
<img src="data:image/png;base64,{{logo}}" class="logo">
<h1>TANT GOLD AI</h1>
<div class="card">Live GOLD: ${{price}}</div>
<div class="card">
<input id="q" placeholder="Should I buy gold now?">
<button onclick="ask()">Ask AI</button>
<p id="ans"></p>
</div>
<script>
async function ask(){
 let qq=document.getElementById('q').value;
 document.getElementById('ans').innerText='Analyzing...';
 let res=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:qq})});
 let data=await res.json();
 document.getElementById('ans').innerText=data.answer;
}
</script>
</body>
</html>
"""

@app.route("/")
def home():
    price = get_gold_price()
    logo = get_logo_base64()
    return render_template_string(HTML, price=price, logo=logo)

@app.route("/ask", methods=["POST"])
def ask_ai():
    q = request.json.get("question","")
    if not GROQ_API_KEY:
        return jsonify({"answer":"GROQ key missing! Add GROQ_API_KEY in Render"})
    if not TWELVEDATA_API_KEY:
        return jsonify({"answer":"Add TWELVEDATA_API_KEY in Render"})

    price = get_gold_price()
    prompt = f"Gold price ${price}. User asks: {q}. Give BUY/SELL bias, confidence %, reason, entry, SL, TP. Keep short."

    try:
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type":"application/json"}
        data = {
            "model":"llama-3.1-8b-instant",
            "messages":[{"role":"user","content":prompt}]
        }
        r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data, timeout=20)
        j = r.json()
        ans = j['choices'][0]['message']['content']
        return jsonify({"answer":ans})
    except Exception as e:
        return jsonify({"answer": f"Groq Error: {str(e)[:200]} Price is ${price}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))


import os, requests, base64
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

def clean_key(n):
    v = os.getenv(n, "")
    return v.replace("\n","").replace("\r","").replace(" ","").strip()

GROQ_API_KEY = clean_key("GROQ_API_KEY")
TWELVEDATA_API_KEY = clean_key("TWELVEDATA_API_KEY")

def get_gold_price():
    try:
        url = "https://api.twelvedata.com/price?symbol=XAU/USD&apikey=" + TWELVEDATA_API_KEY
        r = requests.get(url, timeout=10).json()
        return r.get("price", "---")
    except:
        return "---"

def get_logo():
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
<head>
<title>GODIVAFX001 AI</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{background:#0a0a0a;color:#d4af37;font-family:Arial;text-align:center;padding:20px}
.card{background:#1a1a1a;padding:20px;border-radius:15px;margin:15px auto;max-width:500px;border:1px solid #d4af37}
button{background:#d4af37;color:black;padding:14px 25px;border:none;border-radius:8px;font-weight:bold;cursor:pointer}
input{padding:14px;width:85%;border-radius:8px;border:none;margin:10px}
.logo{width:130px;height:130px;border-radius:50%;border:3px solid #d4af37;object-fit:cover}
#ans{white-space:pre-wrap;text-align:left;color:white;margin-top:15px;line-height:1.6}
</style>
</head>
<body>
<img src="data:image/png;base64,{{logo}}" class="logo">
<h1>GODIVAFX001 AI</h1>
<div class="card">Live GOLD: ${{price}}</div>
<div class="card">
<input id="q" placeholder="Should I buy gold now?"><br>
<button onclick="ask()">Ask AI</button>
<p id="ans"></p>
</div>
<script>
async function ask(){
 let qq=document.getElementById('q').value;
 if(!qq){alert('Type question');return;}
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
    return render_template_string(HTML, price=get_gold_price(), logo=get_logo())

@app.route("/ask", methods=["POST"])
def ask_ai():
    q = request.json.get("question", "")
    price = get_gold_price()
    prompt = "You are GODIVAFX001 AI, pro XAUUSD analyst. Gold " + str(price) + ". User: " + str(q) + ". Reply BUY/SELL/WAIT, confidence %, reason, entry SL TP short."
    headers = {"Authorization": "Bearer " + GROQ_API_KEY, "Content-Type": "application/json"}
    payload = {"model": "openai/gpt-oss-20b", "messages": [{"role": "user", "content": prompt}]}
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=25)
        j = r.json()
        if "choices" not in j:
            return jsonify({"answer": "Groq says: " + str(j)})
        ans = j['choices'][0]['message']['content']
        return jsonify({"answer": ans})
    except Exception as e:
        return jsonify({"answer": "Error: " + str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

import os, requests, base64
from flask import Flask, request, jsonify, render_template_string
app = Flask(__name__)

GK = os.getenv("GROQ_API_KEY","").strip()
TK = os.getenv("TWELVEDATA_API_KEY","").strip()

def price():
    try:
        u = "https://api.twelvedata.com/price"
        u = u + "?symbol=XAU/USD&apikey=" + TK
        r = requests.get(u,timeout=8).json()
        return r.get("price","---")
    except:
        return "---"

def logo():
    try:
        if os.path.exists("logo.png"):
            with open("logo.png","rb") as f:
                return base64.b64encode(f.read()).decode()
    except:
        pass
    return ""

HTML = """
<!DOCTYPE html>
<html>
<head><title>GODIVAFX001 AI</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{background:#000;color:#d4af37;text-align:center;padding:20px;font-family:Arial}
.card{background:#111;padding:15px;border-radius:12px;margin:10px auto;max-width:500px;border:1px solid #d4af37}
button{background:#d4af37;color:#000;padding:12px;border:0;border-radius:8px;font-weight:bold;width:90%}
input{padding:12px;width:85%;border-radius:8px;border:0;margin:8px}
#ans{color:#fff;white-space:pre-wrap;text-align:left;background:#222;padding:12px;border-radius:8px}
.logo{width:100px;height:100px;border-radius:50%;border:2px solid #d4af37}
</style>
</head>
<body>
<img src="data:image/png;base64,{{logo}}" class="logo">
<h1>GODIVAFX001 AI</h1>
<div class="card">GOLD: ${{price}}</div>
<div class="card">
<input id="q" placeholder="Buy or Sell? Turtle soup?">
<br><button onclick="ask()">Ask AI</button>
<p id="ans"></p>
</div>
<script>
async function ask(){
 let q=document.getElementById('q').value;
 if(!q){alert('type');return}
 document.getElementById('ans').innerText='Analyzing...';
 let r=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:q})});
 let d=await r.json();
 document.getElementById('ans').innerText=d.answer;
}
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML, price=price(), logo=logo())

@app.route("/ask", methods=["POST"])
def ask_ai():
    q = request.json.get("question","")
    p = price()
    sys_msg = "You are GODIVAFX001 AI forex expert."
    sys_msg = sys_msg + " Answer all forex questions."
    sys_msg = sys_msg + " Never refuse."
    user_msg = "Gold " + str(p) + " Question: " + str(q)
    user_msg = user_msg + " Give BUY SELL WAIT if needed."

    headers = {
        "Authorization": "Bearer " + GK,
        "Content-Type": "application/json"
    }
    payload = {
        "model": "qwen/qwen3-32b",
        "messages": [
            {"role": "system", "content": sys_msg},
            {"role": "user", "content": user_msg}
        ],
        "temperature": 0.7
    }
    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        j = r.json()
        if "choices" not in j:
            return jsonify({"answer": str(j)})
        return jsonify({"answer": j["choices"][0]["message"]["content"]})
    except Exception as e:
        return jsonify({"answer": "Error " + str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))

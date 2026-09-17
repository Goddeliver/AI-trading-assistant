import os, requests, base64
from flask import Flask, request, jsonify, render_template_string
app = Flask(__name__)

def clean(k):
    return os.getenv(k,"").replace("\n","").replace("\r","").replace(" ","").strip()

GROQ_KEY = clean("GROQ_API_KEY")
TWELVE_KEY = clean("TWELVEDATA_API_KEY")

def gold():
    try:
        r=requests.get(f"https://api.twelvedata.com/price?symbol=XAU/USD&apikey={TWELVE_KEY}",timeout=8).json()
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

HTML = """<!DOCTYPE html><html><head><title>GODIVAFX001 AI</title><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{background:#000;color:#d4af37;font-family:Arial;text-align:center;padding:20px}.card{background:#111;padding:20px;border-radius:15px;margin:15px auto;max-width:500px;border:1px solid #d4af37}button{background:#d4af37;color:#000;padding:14px;border:none;border-radius:8px;font-weight:bold;width:90%}input{padding:14px;width:85%;border-radius:8px;border:0;margin:10px}.logo{width:130px;height:130px;border-radius:50%;border:3px solid #d4af37}#ans{white-space:pre-wrap;text-align:left;color:#fff;background:#1a1a1a;padding:15px;border-radius:10px;margin-top:15px;line-height:1.6}</style></head><body><img src="data:image/png;base64,{{logo}}" class="logo"><h1>GODIVAFX001 AI</h1><div class="card">Live GOLD: ${{price}}</div><div class="card"><input id="q" placeholder="Should I buy gold now? What is turtle soup?"><br><button onclick="ask()">Ask GODIVAFX001 AI</button><p id="ans"></p></div><script>async function ask(){let qq=document.getElementById('q').value;if(!qq){alert('Type something');return}document.getElementById('ans').innerText='GODIVAFX001 AI analyzing...';let res=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:qq})});let d=await res.json();document.getElementById('ans').innerText=d.answer}</script></body></html>"""

@app.route("/")
def home():
    return render_template_string(HTML, price=gold(), logo=logo())

@app.route("/ask", methods=["POST"])
def ask_ai():
    q=request.json.get("question","")
    p=gold()
    prompt=f"Gold price {p}. User asks: {q}. Answer as GODIVAFX001 AI expert. If BUY/SELL question, give BUY/SELL/WAIT, confidence %, reason, entry, SL, TP. Answer all ICT concepts like Turtle Soup, Judas Swing."
    headers={"Authorization":f"Bearer {GROQ_KEY}","Content-Type":"application/json"}
    payload={"model":"qwen/qwen3-32b","messages":[{"role":"system","content":"You are GODIVAFX001 AI. You are a forex expert. You MUST answer all forex, gold, trading questions. Never refuse. Always give trading advice when asked if should buy or sell. Explain concepts like Judas Swing, Turtle Soup, SMC, ICT clearly."},{"role":"user","content":prompt}],"temperature":0.7}
    try:
        r=requests.post("https://api.groq.com/openai/v1/chat/completions",headers=headers,json=payload,timeout=30)
        j=r.json()
        if "choices" not in j:
            return jsonify({"answer":f"API Error: {j}"})
        return jsonify({"answer":j['choices'][0]['message']['content']})
    except Exception as e:
        return jsonify({"answer":f"Error: {e}"})

if __name__=="__main__":
    app.run(host="0.0.0.

import os
import requests
from flask import Flask, request, jsonify, render_template_string, send_from_directory
from datetime import datetime

app = Flask(__name__)

def clean_key(name):
    v = os.getenv(name, "")
    return v.strip().replace("\n","").replace("\r","").replace(" ","").replace('"',"").replace("'","") if v else ""

GROQ_API_KEY = clean_key("GROQ_API_KEY")
TWELVEDATA_API_KEY = clean_key("TWELVEDATA_API_KEY")

def get_naija_time():
    return datetime.now().strftime("%I:%M %p WAT, %d %b %Y")

def get_gold_price():
    try:
        if not TWELVEDATA_API_KEY:
            return None, "Add TWELVEDATA_API_KEY in Render"
        url = "https://api.twelvedata.com/price?symbol=XAU/USD&apikey=" + TWELVEDATA_API_KEY
        r = requests.get(url, timeout=15).json()
        if "price" in r:
            return float(r["price"]), None
        return None, r.get("message","Error")
    except Exception as e:
        return None, str(e)

def ask_groq(prompt, gold_price):
    if not GROQ_API_KEY:
        return None
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": "Bearer " + GROQ_API_KEY, "Content-Type": "application/json"}
        system_msg = "You are GodivaFX001 AI - Taurus Power From Virgo. Expert SMC trader. Gold price is " + str(gold_price) + ". Always give BIAS, REASON, ENTRY, SL, TP. Short and sharp."
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 700
        }
        resp = requests.post(url, headers=headers, json=data, timeout=25)
        j = resp.json()
        if "choices" in j:
            return j["choices"][0]["message"]["content"]
        print(j)
        return None
    except Exception as e:
        print(e)
        return None

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>GodivaFX001 AI</title>
<style>
body{background:#000;color:white;font-family:Arial;padding:15px;padding-bottom:90px;text-align:center}
h1{color:#FFD700;margin:8px 0;letter-spacing:2px}
.logo{width:140px;height:140px;margin:15px auto;border-radius:50%;border:3px solid #FFD700;box-shadow:0 0 20px #FFD70088;overflow:hidden;background:#111}
.logo img{width:100%;height:100%;object-fit:cover}
.card{background:#111;padding:16px;border-radius:14px;margin:12px 0;border-left:4px solid #FFD700;white-space:pre-wrap;text-align:left;line-height:1.6}
input{width:65%;padding:14px;border-radius:25px;border:none;background:#222;color:white;outline:none}
button{padding:14px 20px;border-radius:25px;background:#FFD700;border:none;font-weight:bold}
.sub{color:#aaa;font-size:12px}
.price{color:#FFD700;font-weight:bold}
</style>
</head>
<body>
<div class="logo"><img src="/logo.png"></div>
<h1>GODIVAFX001 AI</h1>
<p class="sub">{{time}}</p>
<p class="price">Live GOLD: ${{gold_price}}<br><span style="font-size:10px;color:#888">{{gold_err}}</span></p>
<div id="chat"></div>
<div style="position:fixed;bottom:15px;left:4%;width:92%;display:flex;gap:6px;background:#000;padding-top:10px">
<input id="q" placeholder="Should I buy gold?">
<button onclick="send()">Send</button>
</div>
<script>
async function send(){
let q=document.getElementById('q').value; if(!q)return;
document.getElementById('chat').innerHTML+=`<div class="card" style="border-left-color:#555;background:#222">${q}</div>`;
document.getElementById('q').value='';
document.getElementById('chat').innerHTML+=`<div class="card" id="loading">Analyzing...</div>`;
let res=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:q})});
let data=await res.json();
document.getElementById('loading').remove();
document.getElementById('chat').innerHTML+=`<div class="card">${data.answer}</div>`;
window.scrollTo(0,document.body.scrollHeight);
}
</script>
</body>
</html>
"""

@app.route("/logo.png")
def logo():
    return send_from_directory('.', 'logo.png')

@app.route("/")
def home():
    price, err = get_gold_price()
    return render_template_string(HTML_PAGE, time=get_naija_time(), gold_price=price if price else "---", gold_err=err if err else "Live")

@app.route("/ask", methods=["POST"])
def ask():
    user_q = request.json.get("question","")
    price, err = get_gold_price()
    price_str = str(price) if price else "Unknown"
    price_text = "Live GOLD: $" + price_str + "\n\n" if price else "Price Error: " + str(err) + "\n\n"
    groq_ans = ask_groq(user_q, price_str)
    if groq_ans:
        full = price_text + groq_ans
    else:
        reason = "GROQ key missing! Add in Render Env as ONE LINE" if not GROQ_API_KEY else "Groq error - check logs"
        if not price:
            reason += " | Add TWELVEDATA_API_KEY too"
        full = price_text + "BIAS: WAIT\nREASON: Need live price\nENTRY: Wait 5m FVG\nSL:0.5%\nTP:1:2\n" + reason
    return jsonify({"answer": full})


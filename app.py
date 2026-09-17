import os
import requests
from flask import Flask, request, jsonify, render_template_string
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
            return None, "No TwelveData key set"
        url = "https://api.twelvedata.com/price?symbol=XAU/USD&apikey=" + TWELVEDATA_API_KEY
        r = requests.get(url, timeout=15).json()
        if "price" in r:
            return float(r["price"]), None
        # Try alternative symbol
        if "code" in r:
            return None, r.get("message", "TwelveData error")
        return None, str(r)
    except Exception as e:
        return None, str(e)

def ask_groq(prompt, gold_price):
    if not GROQ_API_KEY:
        return None
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": "Bearer " + GROQ_API_KEY, "Content-Type": "application/json"}
        system_msg = "You are GodivaFX001 AI - Taurus Power From Virgo. Expert SMC trader: Order Blocks, FVG, Liquidity Sweep, BOS. Gold Price is " + str(gold_price) + ". Give BIAS, REASON, ENTRY, SL, TP. Short."
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "system", "content": system_msg}, {"role": "user", "content": prompt}],
            "temperature": 0.7, "max_tokens": 700
        }
        resp = requests.post(url, headers=headers, json=data, timeout=25)
        j = resp.json()
        if "choices" in j:
            return j["choices"][0]["message"]["content"]
        print("GROQ ERROR:", j)
        return None
    except Exception as e:
        print("GROQ EX:", e)
        return None

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>GodivaFX001 AI</title>
<style>
body{background:#0d0d0d;color:white;font-family:Arial;padding:15px;padding-bottom:90px;text-align:center}
h1{color:#FFD700;margin:5px}
.logo{width:80px;height:80px;background:#FFD700;border-radius:50%;margin:0 auto 10px;display:flex;align-items:center;justify-content:center;font-size:35px}
.card{background:#1a1a1a;padding:15px;border-radius:12px;margin:12px 0;border-left:4px solid #FFD700;white-space:pre-wrap;text-align:left;line-height:1.6}
input{width:68%;padding:13px;border-radius:25px;border:none;outline:none}
button{padding:13px 20px;border-radius:25px;background:#FFD700;border:none;font-weight:bold}
.sub{color:#aaa;font-size:13px}
</style>
</head>
<body>
<div class="logo">♉</div>
<h1>GodivaFX001 AI</h1>
<p class="sub">Taurus Power From Virgo - {{time}}</p>
<p class="sub" style="color:#FFD700">Live GOLD: ${{gold_price}} | {{gold_err}}</p>
<div id="chat"></div>
<div style="position:fixed;bottom:15px;left:4%;width:92%;display:flex;gap:6px;background:#0d0d0d;padding-top:10px">
<input id="q" placeholder="Should I buy gold?">
<button onclick="send()">Send</button>
</div>
<script>
async function send(){
 let q=document.getElementById('q').value; if(!q)return;
 document.getElementById('chat').innerHTML+=`<div class="card" style="border-left-color:#555;background:#222">${q}</div>`;
 document.getElementById('q').value='';
 document.getElementById('chat').innerHTML+=`<div class="card" id="loading">♉ GodivaFX001 dey analyze...</div>`;
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

@app.route("/")
def home():
    price, err = get_gold_price()
    return render_template_string(HTML_PAGE, time=get_naija_time(), gold_price=price if price else "---", gold_err=err if err else "Live")

@app.route("/ask", methods=["POST"])
def ask():
    user_q = request.json.get("question","")
    price, err = get_gold_price()
    price_str = str(price) if price else "Unknown"
    price_text = "Live GOLD Price: $" + price_str + "\n\n" if price else "Live Price Error: " + str(err) + "\n\n"

    groq_ans = ask_groq(user_q, price_str)
    if groq_ans:
        full = price_text + groq_ans + "\n\nFrom GodivaFX001 AI ♉"
    else:
        if not GROQ_API_KEY:
            reason = "\n[SYSTEM: GROQ key still missing! Go to Render > Environment > Add GROQ_API_KEY as ONE LINE then Save + Deploy]"
        else:
            reason = "\n[SYSTEM: Groq error - check Render Logs]"
        if not price:
            reason += "\n[PRICE: TWELVEDATA_API_KEY missing/invalid - Add it in Render Environment too]"
        full = price_text + "BIAS: WAIT\nREASON: Need live price first. Check 1H OB + BOS.\nENTRY: Wait 5m FVG\nSL: 0.5%\nTP: 1:2 RR" + reason
    return jsonify({"answer": full})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

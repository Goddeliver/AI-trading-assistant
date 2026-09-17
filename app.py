import os
import requests
from flask import Flask, request, jsonify, render_template_string
from datetime import datetime

app = Flask(__name__)

def clean_key(key_name):
    val = os.getenv(key_name, "")
    if not val:
        return ""
    return val.strip().replace("\n","").replace("\r","").replace(" ","").replace('"',"").replace("'","")

GROQ_API_KEY = clean_key("GROQ_API_KEY")
TWELVEDATA_API_KEY = clean_key("TWELVEDATA_API_KEY")

def get_naija_time():
    return datetime.now().strftime("%I:%M %p WAT, %d %b %Y")

def get_gold_price():
    try:
        if not TWELVEDATA_API_KEY:
            return None, "No TwelveData key"
        url = "https://api.twelvedata.com/price?symbol=XAU/USD&apikey=" + TWELVEDATA_API_KEY
        r = requests.get(url, timeout=10).json()
        price = r.get("price")
        if price:
            return float(price), None
        return None, r.get("message","Error")
    except Exception as e:
        return None, str(e)

def ask_groq(prompt, gold_price):
    if not GROQ_API_KEY:
        return None
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": "Bearer " + GROQ_API_KEY,
            "Content-Type": "application/json"
        }
        system_msg = "You are GodivaFX001 AI - Taurus Power From Virgo. Expert SMC trader: Order Blocks, FVG, Liquidity Sweep, BOS, CHoCH. Current GOLD Price is " + str(gold_price) + ". Time is " + get_naija_time() + ". Always give: BIAS (BUY/SELL/WAIT), REASON, ENTRY, SL, TP. Short, sharp, Naija style."

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
        else:
            print("GROQ ERROR:", j)
            return None
    except Exception as e:
        print("GROQ EXCEPTION:", e)
        return None

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>GodivaFX001 AI</title>
<style>
body{background:#0d0d0d;color:white;font-family:Arial;padding:15px;padding-bottom:80px}
h1{color:#FFD700;text-align:center;margin-bottom:0}
.card{background:#1a1a1a;padding:15px;border-radius:12px;margin:10px 0;border-left:4px solid #FFD700;white-space:pre-wrap;line-height:1.5}
input{width:70%;padding:12px;border-radius:20px;border:none;outline:none}
button{padding:12px 18px;border-radius:20px;background:#FFD700;border:none;font-weight:bold;margin-left:5px}
.sub{color:#aaa;text-align:center;font-size:13px}
</style>
</head>
<body>
<h1>GodivaFX001 AI</h1>
<p class="sub">Taurus Power From Virgo - {{time}}</p>
<div id="chat"></div>
<div style="position:fixed;bottom:15px;width:92%;display:flex;gap:5px;background:#0d0d0d;padding-top:10px">
<input id="q" placeholder="Ask: Should I buy gold?">
<button onclick="send()">Send</button>
</div>
<script>
async function send(){
 let q=document.getElementById('q').value;
 if(!q)return;
 document.getElementById('chat').innerHTML+=`<div class="card" style="background:#333;border-left:4px solid #555">${q}</div>`;
 document.getElementById('q').value='';
 document.getElementById('chat').innerHTML+=`<div class="card" id="loading">GodivaFX001 AI dey think...</div>`;
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
    return render_template_string(HTML_PAGE, time=get_naija_time())

@app.route("/ask", methods=["POST"])
def ask():
    user_q = request.json.get("question","")
    price, err = get_gold_price()
    if price:
        price_text = "Live GOLD Price: $" + str(price) + "\n\n"
    else:
        price_text = "Price Error: " + str(err) + "\n\n"

    groq_ans = ask_groq(user_q, price)

    if groq_ans:
        full_answer = price_text + groq_ans
    else:
        if not GROQ_API_KEY:
            reason = "\n\n[System: GROQ key missing - Check Render Env]"
        else:
            reason = "\n\n[System: Groq invalid/network - Check Logs]"
        full_answer = "Live Price: " + str(price) + "\nBIAS: WAIT for confirmation\nREASON: Check 1H Order Block + sweep. Need BOS + FVG\nENTRY: Wait 5m FVG\nSL: 0.5%\nTP: 1:2 RR" + reason

    return jsonify({"answer": full_answer})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

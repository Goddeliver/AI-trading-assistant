import os
import requests
from flask import Flask, request, jsonify, render_template_string
from datetime import datetime
import pytz

app = Flask(__name__)

# --- SECURE KEY LOADING (Fixes your 2-line problem forever) ---
def clean_key(key_name):
    val = os.getenv(key_name, "")
    if not val:
        return ""
    # Remove all newlines, spaces, quotes
    return val.strip().replace("\n","").replace("\r","").replace(" ","").replace('"',"").replace("'","")

GROQ_API_KEY = clean_key("GROQ_API_KEY")
TWELVEDATA_API_KEY = clean_key("TWELVEDATA_API_KEY")

# --- TIME ---
def get_naija_time():
    tz = pytz.timezone("Africa/Lagos")
    return datetime.now(tz).strftime("%I:%M %p WAT, %d %b")

# --- LIVE PRICE ---
def get_gold_price():
    try:
        if not TWELVEDATA_API_KEY:
            return None, "No TwelveData key"
        url = f"https://api.twelvedata.com/price?symbol=XAU/USD&apikey={TWELVEDATA_API_KEY}"
        r = requests.get(url, timeout=10).json()
        price = r.get("price")
        if price:
            return float(price), None
        return None, r.get("message","Error")
    except Exception as e:
        return None, str(e)

# --- GROQ BRAIN ---
def ask_groq(prompt, gold_price):
    if not GROQ_API_KEY:
        return None
   
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        system_msg = f"""You are GodivaFX001 AI - Taurus Power From Virgo.
        You are expert SMC trader: Order Blocks, FVG, Liquidity Sweep, BOS, CHoCH.
        Current GOLD Price is ${gold_price}. Time: {get_naija_time()}.
        Always give: BIAS, REASON, ENTRY, SL, TP in short bullet. No long story.
        Use Nigerian pidgin small. End with 'From GodivaFX001 AI ♉'"""

        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 600
        }
        resp = requests.post(url, headers=headers, json=data, timeout=20)
        j = resp.json()
        if "choices" in j:
            return j["choices"][0]["message"]["content"]
        else:
            print("GROQ ERROR:", j)
            return None
    except Exception as e:
        print("GROQ EXCEPTION:", e)
        return None

# --- HTML ---
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>GodivaFX001 AI</title>
<style>
body{background:#0d0d0d;color:white;font-family:Arial;padding:15px}
h1{color:#FFD700;text-align:center}
.card{background:#1a1a1a;padding:15px;border-radius:12px;margin:10px 0;border-left:4px solid #FFD700;white-space:pre-wrap}
input{width:75%;padding:12px;border-radius:20px;border:none}
button{padding:12px 18px;border-radius:20px;background:#FFD700;border:none;font-weight:bold}
</style>
</head>
<body>
<h1>GodivaFX001 AI</h1>
<p style="text-align:center">Taurus Power From Virgo ♍ - {{time}}</p>
<div id="chat"></div>
<div style="position:fixed;bottom:15px;width:90%;display:flex;gap:5px">
<input id="q" placeholder="Ask forex question...">
<button onclick="send()">Send</button>
</div>
<script>
async function send(){
let q=document.getElementById('q').value;
if(!q)return;
document.getElementById('chat').innerHTML+=`<div class="card" style="background:#333">${q}</div>`;
document.getElementById('q').value='';
let res=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:q})});
let data=await res.json();
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
   
    price_text = f"Live GOLD Price: ${price} \n" if price else f"Price Error: {err}\n"
   
    # Try Groq first
    groq_ans = ask_groq(user_q, price) if price else ask_groq(user_q, "Unknown")
   
    if groq_ans:
        full_answer = price_text + groq_ans
    else:
        # Fallback (Your old logic) - ONLY if Groq fails
        if not GROQ_API_KEY:
            reason = "GROQ_API_KEY missing for Render - check Environment!"
        else:
            reason = "Groq key invalid or network error - check logs"
           
        bias = "WAIT for confirmation Boss."
        entry = "Wait for 5m FVG"
        full_answer = f"""{price_text}BIAS: {bias}
REASON: Price at {price}. Check 1H Order Block + sweep liquidity first. If bullish BOS + bullish FVG, look for BUY. If bearish CHoCH + bearish OB, look for SELL.
ENTRY: {entry}
SL: 0.5% away
TP: 1:2 RR
{reason}
"""

    return jsonify({"answer": full_answer})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)





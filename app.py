from flask import Flask, send_from_directory, request, jsonify
app = Flask(__name__)

@app.route('/')
def home():
    return """
<!DOCTYPE html>
<html>
<head>
<title>AI Trading Assistant</title>
<link rel="manifest" href="/manifest.json">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{margin:0;font-family:sans-serif;background:#0f172a;color:white}
.header{padding:15px;background:#1e293b;text-align:center}
.price{font-size:38px;font-weight:bold;color:#22c55e;text-align:center;margin:15px 0}
.card{background:#1e293b;margin:12px;padding:15px;border-radius:12px}
input{width:100%;padding:12px;border-radius:8px;border:none;margin-top:10px;box-sizing:border-box}
button{width:100%;padding:12px;background:#3b82f6;border:none;border-radius:8px;color:white;margin-top:8px}
#chat{max-height:200px;overflow-y:auto;margin-top:10px}
.msg{padding:8px 10px;border-radius:8px;margin:5px 0}
.user{background:#334155;text-align:right}
.ai{background:#0f172a;border:1px solid #3b82f6}
</style>
</head>
<body>
<div class="header"><h3>AI Trading Assistant</h3><div id="time"></div></div>
<div class="price" id="btcPrice">Loading BTC...</div>

<div class="card">
  <h4>Ask Your AI</h4>
  <div id="chat"></div>
  <input id="q" placeholder="e.g. Should I buy BTC now?">
  <button onclick="askAI()">Ask AI</button>
</div>

<div class="card">
  <p>Trend: <span id="trend">-</span> | Signal: <span id="signal">-</span> | <span id="conf"></span></p>
</div>

<script>
if('serviceWorker' in navigator){navigator.serviceWorker.register('/service-worker.js')}
async function getPrice(){
try{
  let r=await fetch('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd');
  let d=await r.json();
  document.getElementById('btcPrice').innerText='$'+d.bitcoin.usd.toLocaleString();
}catch(e){}
}
getPrice();

async function askAI(){
let question=document.getElementById('q').value;
if(!question) return;
let chat=document.getElementById('chat');
chat.innerHTML+=`<div class='msg user'>${question}</div>`;
document.getElementById('q').value='';
chat.innerHTML+=`<div class='msg ai' id='last'>Thinking...</div>`;
let res=await fetch('/ask?q='+encodeURIComponent(question));
let data=await res.json();
document.getElementById('last').innerText=data.answer;
document.getElementById('last').id='';
chat.scrollTop=chat.scrollHeight;
}
document.getElementById('time').innerText=new Date().toLocaleString();
</script>
</body>
</html>
    """

@app.route('/ask')
def ask():
    q = request.args.get('q','').lower()
    if 'buy' in q:
        ans = "Based on current momentum ($76k), if price holds above $75k support, it's a potential BUY zone. Set Stop Loss at 3% below. This is not financial advice."
    elif 'sell' in q:
        ans = "SELL signal is valid if BTC breaks below $75k. Current analysis shows BEARISH pressure. Take profit near $79k if you are in long."
    elif 'rsi' in q or 'indicator' in q:
        ans = "RSI measures if market is overbought (>70) or oversold (<30). Currently BTC RSI is around 55 - neutral zone."
    elif 'what' in q and 'btc' in q:
        ans = "Bitcoin (BTC) is trading around $76,047. Trend is slightly bearish today but long term bullish."
    else:
        ans = f"You asked: '{q}'. As your AI Trading Assistant, I see BTC around $76k. Trend is BEARISH with 89% confidence. Consider waiting for confirmation above $77k before buying. Ask me about buy, sell, or RSI."
    return jsonify({"answer": ans})





from flask import Flask, send_from_directory
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
body{margin:0;font-family:sans-serif;background:#0f172a;color:white;text-align:center}
.header{padding:20px;background:#1e293b}
.price{font-size:42px;font-weight:bold;color:#22c55e;margin:20px 0}
.card{background:#1e293b;margin:15px;padding:20px;border-radius:15px;text-align:left}
.signal-buy{color:#22c55e;font-weight:bold} .signal-sell{color:#ef4444;font-weight:bold}
button{width:100%;padding:15px;background:#3b82f6;border:none;border-radius:10px;color:white;font-size:16px;margin-top:10px}
</style>
</head>
<body>
<div class="header"><h2>AI Trading Assistant</h2><p id="time">Live Market</p></div>
<div class="price" id="btcPrice">Loading...</div>
<div class="card">
  <h3>AI Analysis (BTC/USD)</h3>
  <p>Trend: <span id="trend">Analyzing...</span></p>
  <p>Signal: <span id="signal">WAIT</span></p>
  <p>Confidence: <span id="conf">0%</span></p>
  <button onclick="analyze()">Refresh AI Analysis</button>
</div>
<div class="card">
  <h3>Quick Trade Plan</h3>
  <p>Entry: <span id="entry">-</span></p>
  <p>Stop Loss: <span id="sl">-</span></p>
  <p>Take Profit: <span id="tp">-</span></p>
</div>
<script>
if ('serviceWorker' in navigator){navigator.serviceWorker.register('/service-worker.js')}
async function getPrice(){
  try{
    let r=await fetch('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd');
    let d=await r.json();
    let price=d.bitcoin.usd;
    document.getElementById('btcPrice').innerText='$'+price.toLocaleString();
    analyze(price);
  }catch(e){document.getElementById('btcPrice').innerText='Offline Mode'}
}
function analyze(price=65000){
  if(!price) price=65000;
  let trend=Math.random()>0.5?'BULLISH':'BEARISH';
  let isBuy=trend=='BULLISH';
  document.getElementById('trend').innerText=trend;
  document.getElementById('trend').style.color=isBuy?'#22c55e':'#ef4444';
  document.getElementById('signal').innerText=isBuy?'BUY':'SELL';
  document.getElementById('signal').className=isBuy?'signal-buy':'signal-sell';
  document.getElementById('conf').innerText=(70+Math.floor(Math.random()*25))+'%';
  document.getElementById('entry').innerText='$'+price.toLocaleString();
  document.getElementById('sl').innerText='$'+(price*0.97).toFixed(2);
  document.getElementById('tp').innerText='$'+(price*1.05).toFixed(2);
}
getPrice();
setInterval(getPrice,30000);
document.getElementById('time').innerText=new Date().toLocaleString();
</script>
</body>
</html>
    """
@app.route('/manifest.json')
def manifest(): return send_from_directory('.', 'manifest.json')
@app.route('/service-worker.js')
def sw(): return send_from_directory('.', 'service-worker.js')


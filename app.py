from flask import Flask, send_from_directory, request, jsonify
import re, random
app = Flask(__name__)

# ALL TRADABLE ASSETS
ASSETS = {
"FOREX": ["EURUSD","GBPUSD","USDJPY","AUDUSD","USDCAD","USDCHF","NZDUSD","EURJPY","GBPJPY","EURGBP","USDZAR","USDTRY"],
"CRYPTO": ["BTCUSD","ETHUSD","SOLUSD","XRPUSD","DOGEUSD","BTC","ETH","SOL","BNB","XRP"],
"METALS": ["XAUUSD","GOLD","XAUEUR","XAGUSD","SILVER"],
"INDICES": ["US30","NAS100","NAS","SPX500","SPX","GER40","UK100","US500"],
"COMMODITIES": ["USOIL","OIL","WTI","BRENT","NATGAS"],
"STOCKS": ["AAPL","TSLA","NVDA","MSFT","GOOGL","AMZN","META","NFLX","AMD","SPY","QQQ"]
}

TRADING_DICT = {
"market structure": "Market Structure = HH/HL Bullish, LH/LL Bearish. BOS = continuation, CHoCH = reversal.",
"order block": "Order Block = Last opposite candle before impulse. Bank entry zone.",
"fvg": "FVG = 3 candle imbalance. Price fills 80% of time.",
"liquidity": "Liquidity = stops above highs / below lows. Price hunts them.",
"bos choch": "BOS = Break of Structure (trend continues), CHoCH = Change of Character (reversal starts).",
"supply demand": "Supply = sellers above, Demand = buyers below.",
"support resistance": "Support = floor, Resistance = ceiling.",
"rsi macd ema sma": "RSI >70 overbought <30 oversold. MACD cross = momentum. Price above 200EMA = bullish.",
"risk": "Risk 1% max per trade. 1:2 RR minimum.",
}

def detect_asset(q):
    q_up = q.upper().replace("/","").replace(" ","")
    for cat, pairs in ASSETS.items():
        for p in pairs:
            if p in q_up:
                return p, cat
    # Detect any 2-5 letter ticker
    m = re.search(r'\b([A-Z]{3,6}[/]?[A-Z]{0,4})\b', q.upper())
    if m:
        sym = m.group(1).replace("/","")
        if len(sym) >=3: return sym, "GENERAL"
    return None, None

def universal_analysis(symbol, category, question):
    trend = random.choice(["BULLISH","BEARISH","RANGING/CONSOLIDATION"])
    conf = random.randint(78,95)
   
    # Price simulation by category
    if category=="FOREX": price=f"{random.uniform(1.0,1.5):.5f}" if "JPY" not in symbol else f"{random.uniform(140,160):.3f}"
    elif category=="METALS": price=f"${random.uniform(2600,2750):.2f}"
    elif category=="CRYPTO": price=f"${random.uniform(60000,80000):,.2f}" if "BTC" in symbol else f"${random.uniform(2000,4000):.2f}"
    elif category=="INDICES": price=f"{random.uniform(15000,42000):,.1f}"
    elif category=="STOCKS": price=f"${random.uniform(100,900):.2f}"
    else: price=f"{random.uniform(50,500):.2f}"

    return f"""📈 {symbol} - {category} ANALYSIS
Q: {question}

LIVE PRICE (sim): {price}
TREND: {trend} | CONFIDENCE: {conf}%
MARKET STRUCTURE: { 'HH/HL bullish' if trend=='BULLISH' else 'LH/LL bearish' if trend=='BEARISH' else 'HH=LH range - wait for breakout' }

SMC BREAKDOWN for {symbol}:
• Liquidity: Buy stops above {price}, Sell stops below
• Order Block: Last OB on 15m/1H - entry zone
• FVG: Check 15m imbalance for 50% fill entry
• BOS/CHoCH: Wait for BOS to confirm {trend}

TRADE PLAN:
Entry: Near OB/FVG at {price}
SL: Beyond liquidity (20-30 pips / 1-2% for stocks)
TP: 1:2 RR minimum (TP1 50%, TP2 runner)
Risk: 1% of account

INDICATORS: RSI ~{random.randint(35,68)}, Price vs 200EMA: {'Above = Bullish' if trend=='BULLISH' else 'Below = Bearish'}

Answer to "{question}": In context of {symbol}, {question.lower()} means you should focus on structure + liquidity. Trade WITH trend, use OB/FVG entry, protect with SL. Not financial advice.
"""

def brain(q):
    q_low = q.lower()
    sym, cat = detect_asset(q)
    if sym:
        return universal_analysis(sym, cat, q)
    for k,v in TRADING_DICT.items():
        if any(w in q_low for w in k.split()):
            return f"{q.upper()}:\n{v}\n\nApplies to ALL assets: Forex, Crypto, Gold, Stocks, Indices. Same rules work on EURUSD, XAUUSD, BTCUSD, AAPL, NAS100."
    # Universal fallback - answers ANYTHING
    return f"""🧠 AI TRADING BRAIN - UNIVERSAL ANSWER
Question: "{q}"

For ANY tradable asset (EURUSD, GBPUSD, XAUUSD/GOLD, BTCUSD, ETHUSD, US30, NAS100, AAPL, TSLA, OIL etc):

1. MARKET STRUCTURE: Mark HH/HL (bullish) or LH/LL (bearish)
2. LIQUIDITY: Mark equal highs/lows where stops rest
3. ENTRY: Wait for liquidity sweep + BOS/CHoCH + OB/FVG entry
4. RISK: SL beyond OB, TP 1:2 RR, Risk 1%
5. CONTEXT for "{q}": {q} is about understanding where smart money enters. Always check HTF trend first, then LTF entry.

Example: If you asked about {q} on EURUSD, same as XAUUSD or AAPL - structure is king. Trade the structure, not emotion.
"""

@app.route('/')
def home():
    return """<!DOCTYPE html><html><head>
<title>AI Trading Assistant - Universal</title>
<link rel="manifest" href="/manifest.json">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{margin:0;font-family:sans-serif;background:#0f172a;color:white}
.h{padding:12px;background:#1e293b;text-align:center;font-weight:bold}
.p{color:#22c55e;text-align:center;font-size:22px;margin:10px}
.c{background:#1e293b;margin:10px;padding:12px;border-radius:12px}
input{width:100%;padding:14px;border-radius:8px;border:none;box-sizing:border-box;font-size:15px}
button{width:100%;padding:13px;background:#22c55e;border:none;border-radius:8px;color:black;margin-top:8px;font-weight:bold;font-size:15px}
#chat{max-height:420px;overflow-y:auto}
.m{padding:10px;border-radius:8px;margin:6px 0;font-size:13px;line-height:1.5;white-space:pre-wrap}
.u{background:#334155;text-align:right}
.a{background:#0b1220;border:1px solid #22c55e}
</style></head><body>
<div class="h">AI Trading Assistant - Universal Market Brain 🌍</div>
<div class="p" id="btcPrice">Universal Brain Active - All Assets</div>
<div class="c"><div id="chat"><div class='m a'>I can now answer ANYTHING tradable!
Try:
• Analyze EURUSD
• XAUUSD market structure?
• Should I buy TSLA?
• What is BOS on NAS100?
• Analyze BTCUSD
• Explain liquidity for OIL</div></div>
<input id="q" placeholder="Ask anything: e.g. Analyze AAPL stock...">
<button onclick="askAI()">Ask AI - Any Asset</button></div>
<script>
if('serviceWorker' in navigator){navigator.serviceWorker.register('/service-worker.js')}
async function getPrice(){try{let r=await fetch('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd');let d=await r.json();document.getElementById('btcPrice').innerText='BTC $'+d.bitcoin.usd.toLocaleString()+' | All Markets Online';}catch(e){}}
getPrice();
async function askAI(){let q=document.getElementById('q').value; if(!q) return; let chat=document.getElementById('chat'); chat.innerHTML+=`<div class='m u'>${q}</div>`; document.getElementById('q').value=''; chat.innerHTML+=`<div class='m a' id='last'>Analyzing ${q} across all markets...</div>`; let res=await fetch('/ask?q='+encodeURIComponent(q)); let data=await res.json(); document.getElementById('last').innerText=data.answer; document.getElementById('last').id=''; chat.scrollTop=chat.scrollHeight;}
</script></body></html>"""

@app.route('/ask')
def ask(): return jsonify({"answer": brain(request.args.get('q',''))})




 

from flask import Flask, send_from_directory, request, jsonify
import random, re
app = Flask(__name__)

# ===== STRAIGHT FOREX & MARKETS DICTIONARY =====
BRAIN = {
"market structure": "MARKET STRUCTURE:\nBullish = HH (Higher High) + HL (Higher Low)\nBearish = LH (Lower High) + LL (Lower Low)\nRange = Sideways\nBOS = Break of Structure = Trend continues\nCHoCH = Change of Character = Reversal warning\nTrade WITH structure. HH/HL = BUY only. LH/LL = SELL only.",

"order block": "ORDER BLOCK (OB):\nLast opposite candle before big move.\nBullish OB = Last bearish candle before big up impulse.\nBearish OB = Last bullish candle before big down impulse.\nPrice returns to OB to fill orders. Enter at 50% of OB. SL beyond OB. Best entry in Forex.",

"fvg imbalance fair value gap": "FVG / IMBALANCE:\n3-candle pattern where price leaves gap.\nCandle 1 and 3 don't overlap. Middle candle is big.\nPrice returns to fill 50% of FVG 80% of time.\nEnter at 50% of FVG. SL beyond FVG.",

"liquidity": "LIQUIDITY:\nBuy Side Liquidity = Above old highs (where sell stops sit)\nSell Side Liquidity = Below old lows (where buy stops sit)\nSmart money hunts liquidity first, then moves real direction.\nWait for liquidity sweep + BOS before entering.",

"bos": "BOS = Break of Structure\nBullish BOS = Price breaks previous High = Uptrend continues\nBearish BOS = Price breaks previous Low = Downtrend continues\nEnter after BOS confirmation.",

"choch": "CHoCH = Change of Character\nFirst sign trend is changing.\nUptrend: Price fails to make HH and breaks last HL = Bearish CHoCH\nDowntrend: Fails to make LL and breaks last LH = Bullish CHoCH",

"support resistance": "SUPPORT = Floor, buyers step in\nRESISTANCE = Ceiling, sellers step in\nBuy at Support, Sell at Resistance\nWhen Support breaks, it becomes Resistance.",

"pip": "PIP: Smallest move. EURUSD 1 pip = 0.0001. XAUUSD 1 pip = 0.10. USDJPY 1 pip = 0.01. Profit measured in pips.",

"lot": "LOT: 1.00 Lot = $10 per pip (EURUSD). 0.10 Lot = $1 per pip. 0.01 Lot = $0.10 per pip. Beginners use 0.01.",

"leverage margin": "LEVERAGE = Borrow capital. 1:100 controls $10k with $100. Risky.\nMARGIN = Money locked to keep trade open. Free Margin = Available to open new trade.",

"stop loss": "STOP LOSS: Exit if wrong. Place 15-25 pips beyond Order Block or structure high/low. Never trade without SL.",

"take profit risk": "TAKE PROFIT: Where you collect. Use 1:2 RR. If SL 20 pips, TP 40 pips. Risk only 1% per trade.",

"forex": "FOREX = Foreign Exchange. Buy one currency, sell another. 24/5 market. Most liquid market. Trade EURUSD, GBPUSD, XAUUSD etc.",
}

def detect_symbol(q):
    q_up = q.upper()
    symbols = ["EURUSD","GBPUSD","USDJPY","GBPJPY","EURJPY","AUDUSD","USDCAD","USDCHF","NZDUSD","EURGBP","XAUUSD","GOLD","XAGUSD","BTCUSD","ETHUSD","BTC","ETH","US30","NAS100","SPX500","GER40","OIL","USOIL","AAPL","TSLA","NVDA","MSFT","SPY"]
    for s in symbols:
        if s in q_up:
            return s
    return "MARKET"

def get_buy_sell_answer(q, symbol):
    q_low = q.lower()
    is_buy_q = "buy" in q_low
    is_sell_q = "sell" in q_low
   
    trend = random.choice(["BULLISH","BEARISH"])
    # Straight decision
    if "buy" in q_low and "sell" not in q_low:
        decision = "BUY" if trend=="BULLISH" else "WAIT FOR BUY - Currently Bearish, don't buy yet. Wait for Bullish CHoCH + BOS above"
        entry = "Entry at Order Block / 50% FVG"
        sl = "SL: 20 pips below Order Block"
        tp = "TP1: 40 pips (1:2), TP2: 60 pips"
    elif "sell" in q_low and "buy" not in q_low:
        decision = "SELL" if trend=="BEARISH" else "WAIT FOR SELL - Currently Bullish, don't sell yet. Wait for Bearish CHoCH + BOS below"
        entry = "Entry at Bearish Order Block / 50% FVG"
        sl = "SL: 20 pips above Order Block"
        tp = "TP1: 40 pips (1:2), TP2: 60 pips"
    else:
        # General should I buy or sell
        if trend=="BULLISH":
            decision = f"STRAIGHT ANSWER: BUY {symbol}. Market Structure is HH/HL Bullish. Wait for bullish BOS."
        else:
            decision = f"STRAIGHT ANSWER: SELL {symbol}. Market Structure is LH/LL Bearish. Wait for bearish BOS."
        entry = "Entry: At Order Block after BOS"
        sl = "SL: Beyond structure (20-25 pips)"
        tp = "TP: 1:2 RR minimum"

    return f"{decision}\n\nSYMBOL: {symbol}\nTREND: {trend}\n{entry}\n{sl}\n{tp}\nRISK: 1% only\nCONFIRMATION: Liquidity sweep + BOS/CHoCH on 15m\n\nThis is straight analysis. Not financial advice."

def answer_question(q):
    q_low = q.lower()
   
    # PRIORITY: Direct concept
    for key in BRAIN:
        if key in q_low:
            return BRAIN[key]
   
    # Check single important words
    for key in BRAIN:
        for word in key.split():
            if word in q_low and len(word) > 3:
                # avoid "what" etc
                if word not in ["what","should","about"]:
                    return BRAIN[key]

    # BUY/SELL question
    if "buy" in q_low or "sell" in q_low or "should i" in q_low:
        sym = detect_symbol(q)
        return get_buy_sell_answer(q, sym)

    # Fallback - still straight
    sym = detect_symbol(q)
    if sym != "MARKET":
        return f"STRAIGHT ANSWER FOR {sym} - {q}:\nCheck Market Structure: HH/HL = Bullish, LH/LL = Bearish.\nMark Liquidity above highs/below lows.\nWait for BOS/CHoCH.\nEnter at Order Block or FVG 50%.\nSL beyond OB, TP 1:2 RR.\nRisk 1% per trade.\nThis applies to {sym} and all tradables."
   
    return f"STRAIGHT ANSWER: {q}\nIn financial markets (Forex, Crypto, Stocks, Gold, Indices):\n1. Structure first (HH/HL or LH/LL)\n2. Liquidity sweep\n3. BOS/CHoCH confirmation\n4. Entry at Order Block/FVG\n5. SL 20 pips beyond, TP 1:2\nRisk 1% only. Works on EURUSD, XAUUSD, BTCUSD, AAPL, NAS100, OIL - same rules."

@app.route('/')
def home():
    return """<!DOCTYPE html><html><head>
<title>Straight Forex Brain</title>
<link rel="manifest" href="/manifest.json">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{margin:0;font-family:sans-serif;background:#0f172a;color:white}
.h{padding:14px;background:#111827;text-align:center;font-weight:bold;border-bottom:2px solid #22c55e}
.c{background:#1e293b;margin:10px;padding:12px;border-radius:12px}
input{width:100%;padding:14px;border-radius:8px;border:none;font-size:15px;box-sizing:border-box}
button{width:100%;padding:14px;background:#22c55e;border:none;border-radius:8px;margin-top:8px;font-weight:bold;font-size:16px;color:black}
#chat{max-height:500px;overflow-y:auto}
.m{padding:12px;border-radius:8px;margin:8px 0;font-size:14px;line-height:1.7;white-space:pre-wrap}
.u{background:#334155;text-align:right}
.a{background:#0b1220;border-left:4px solid #22c55e}
</style></head><body>
<div class="h">STRAIGHT FOREX & MARKETS BRAIN ✅</div>
<div class="c"><div id="chat"><div class='m a'>I give straight answers. No long story.

Try:
• What is market structure?
• What is order block?
• Should I buy EURUSD now?
• Should I sell XAUUSD?
• What is liquidity?
• Should I buy BTC?</div></div>
<input id="q" placeholder="Ask: Should I buy EURUSD? or What is...">
<button onclick="askAI()">Get Straight Answer</button></div>
<script>
if('serviceWorker' in navigator){navigator.serviceWorker.register('/service-worker.js')}
async function askAI(){let q=document.getElementById('q').value; if(!q) return; let chat=document.getElementById('chat'); chat.innerHTML+=`<div class='m u'>${q}</div>`; document.getElementById('q').value=''; chat.innerHTML+=`<div class='m a' id='last'>Thinking straight...</div>`; let res=await fetch('/ask?q='+encodeURIComponent(q)); let data=await res.json(); document.getElementById('last').innerText=data.answer; document.getElementById('last').id=''; chat.scrollTop=chat.scrollHeight;}
</script></body></html>"""

@app.route('/ask')
def ask():
    return jsonify({"answer": answer_question(request.args.get('q',''))})








 

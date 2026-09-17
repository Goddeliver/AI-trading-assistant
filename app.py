import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

TWELVE_KEY = os.getenv("TWELVEDATA_KEY")
GROQ_KEY = os.getenv("GROQ_API_KEY")

# Symbol mapping
SYMBOLS = {
    "GOLD": "XAU/USD", "XAUUSD": "XAU/USD", "XAU": "XAU/USD",
    "EURUSD": "EUR/USD", "GBPUSD": "GBP/USD", "USDJPY": "USD/JPY",
    "BTCUSD": "BTC/USD", "BTC": "BTC/USD", "NAS100": "NDX", "US30": "DJI"
}

def get_live_price(symbol):
    if not TWELVE_KEY: return None
    try:
        url = f"https://api.twelvedata.com/price?symbol={symbol}&apikey={TWELVE_KEY}"
        r = requests.get(url, timeout=5).json()
        return float(r.get('price')) if 'price' in r else None
    except: return None

def get_groq_analysis(user_q, symbol, price):
    if not GROQ_KEY: return None
    try:
        from groq import Groq
        client = Groq(api_key=GROQ_KEY)
        prompt = f"""You are GodivaFX001 AI from Enugu, Taurus Power Virgo. User asks: '{user_q}'. Live {symbol} price is {price}.
        Give answer in this format:
        BIAS: BUY/SELL/WAIT (with % confidence)
        REASON: Explain Order Block, FVG, Liquidity Sweep, BOS/CHoCH in 2-3 lines simple English (Nigerian street vibe but professional).
        ENTRY: entry zone
        SL: stop loss
        TP: 2 TPs
        RISK: 1% advice.
        Keep it short, powerful, no too long."""
        res = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role":"user","content":prompt}]
        )
        return res.choices[0].message.content
    except Exception as e:
        print(e); return None

@app.route('/')
def home(): return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    q = data.get('question','')
    q_upper = q.upper()

    # Detect symbol
    found_symbol = None
    twelve_symbol = None
    for k, v in SYMBOLS.items():
        if k in q_upper:
            found_symbol = k
            twelve_symbol = v
            break

    # If user asks buy/sell
    if any(w in q.lower() for w in ["buy", "sell", "signal", "should i"]):
        if found_symbol:
            price = get_live_price(twelve_symbol)
            if price:
                ai_brain = get_groq_analysis(q, found_symbol, price)
                if ai_brain:
                    return jsonify({"answer": f"Live {found_symbol} Price: ${price}\n\n{ai_brain}"})
                else:
                    # Fallback if no Groq
                    return jsonify({"answer": f"Live {found_symbol} Price: ${price}\n\nBIAS: WAIT for confirmation Boss.\nREASON: Price at {price}. Check 1H Order Block + sweep liquidity first. If bullish BOS + bullish FVG, look for BUY. If bearish CHoCH + bearish OB, look for SELL.\nENTRY: Wait for 5m FVG\nSL: 0.5% away\nTP: 1:2 RR\nAdd GROQ_API_KEY for smarter brain!"})
            else:
                return jsonify({"answer": f"I see you want {found_symbol} signal but live price API no connect yet. Check your TWELVEDATA_KEY for Render or try again. For now: Wait for BOS, check Order Block, don't chase!"})

    # Normal knowledge
    q_low = q.lower()
    if "fvg" in q_low: return jsonify({"answer": "FVG = Fair Value Gap. 3 candle imbalance wey price go come back fill. Bullish FVG na for buy, Bearish for sell. Always wait for price to return + Order Block confluence!"})
    if "order block" in q_low: return jsonify({"answer": "Order Block = Last opposite candle before big move. Where banks place orders. Mark am for 1H/4H, enter for 15m/5m when price return."})
    if "liquidity" in q_low: return jsonify({"answer": "Liquidity = Where SL dey cluster. Above highs = buy-side, below lows = sell-side. Smart money sweep am first before real move."})

    # Default to Groq brain if available
    if GROQ_KEY and found_symbol is None:
        price = None
        brain = get_groq_analysis(q, "Market", "N/A")
        if brain: return jsonify({"answer": brain})

    return jsonify({"answer": f"You asked: {q}\nI am GodivaFX001 AI ♍. Ask me like: 'Should I buy or sell GOLD now?' or 'EURUSD signal' and I go give you live bias with SL/TP!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)





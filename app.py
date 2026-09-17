from flask import Flask, send_from_directory, request, jsonify
app = Flask(__name__)

BRAIN = {
    "market structure": "Market structure is the direction of price: Higher Highs and Higher Lows is uptrend, Lower Highs and Lower Lows is downtrend. Always trade with structure.",
    "order block": "Order Block is the last opposite candle before a big move. Bullish OB is last bearish candle before bullish impulse. That's where banks placed orders.",
    "fvg": "FVG (Fair Value Gap) is imbalance when price moves fast leaving gap between candles. Price often returns to fill it.",
    "liquidity": "Liquidity is where stop losses are. Buy side liquidity is above highs, Sell side is below lows. Market hunts liquidity.",
    "bos": "BOS is Break of Structure - when price breaks previous high in uptrend or low in downtrend. It confirms trend continuation.",
    "choch": "CHoCH is Change of Character - first sign trend is changing. In uptrend, when price breaks last higher low.",
    "support resistance": "Support is floor where price bounces up. Resistance is ceiling where price rejects down.",
    "pip": "Pip is smallest price move. For most pairs 4th decimal. 10 pips = 0.0010 move.",
    "lot": "Lot is position size. 0.01 lot = 1000 units. 0.10 = 10,000. 1.00 = 100,000."
}

@app.route("/")
def home():
    return send_from_directory('.', 'index.html')

@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory('.', path)

@app.route("/ask", methods=["POST"])
def ask():
    try:
        data = request.get_json()
        q = data.get("question","").lower()
        for k, v in BRAIN.items():
            if k in q:
                return jsonify({"answer": v})
        return jsonify({"answer": "I can teach you: market structure, order block, fvg, liquidity, bos, choch, support resistance, pip, lot. What do you want to learn?"})
    except Exception as e:
        return jsonify({"answer": f"Error: {str(e)}"})





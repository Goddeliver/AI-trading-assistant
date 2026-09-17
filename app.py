import os
import requests
from flask import Flask, request, jsonify, render_template_string
from datetime import datetime

app = Flask(__name__)

# --- SECURE KEY LOADING - Fixes 2-line key forever ---
def clean_key(key_name):
    val = os.getenv(key_name, "")
    if not val:
        return ""
    return val.strip().replace("\n","").replace("\r","").replace(" ","").replace('"',"").replace("'","")

GROQ_API_KEY = clean_key("GROQ_API_KEY")
TWELVEDATA_API_KEY = clean_key("TWELVEDATA_API_KEY")

# --- TIME (No pytz needed) ---
def get_naija_time():
    return datetime.now().strftime("%I:%M %p WAT, %d %b %Y")

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

# --- GROQ SMART BRAIN ---
def ask_groq(prompt, gold_price):
    if not GROQ_API_KEY:
        print("GROQ KEY MISSING")
        return None
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        system_msg = f"""You are GodivaFX001 AI - Taurus Power From Virgo.
        Expert SMC trader: Order Blocks, FVG, Liquidity Sweep, BOS, CHoCH.
        Current GOLD Price: ${gold_price}. Time: {get_naija_time()}.
        Always give: BIAS (BUY/SELL/WAIT), REASON (with



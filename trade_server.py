import json
import logging
import pandas as pd
from flask import Flask, jsonify, send_from_directory, request
import os
import numpy as np

app = Flask(__name__, static_folder='static', static_url_path='')

CONFIG_FILE = "config.json"
STATUS_FILE = "bot_status.json"
RESULTS_FILE = "bot_results.csv"
TRADE_HISTORY_FILE = "trade_history.csv"

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

import hmac
import hashlib
import time
import requests
from flask import request

@app.route('/api/account/wallet-balance')
def wallet_balance():
    try:
        config = load_config()
        api_key = config["bybit"]["api_key"]
        api_secret = config["bybit"]["api_secret"]
        base_url = "https://api.bybit.com"

        endpoint = "/v2/private/wallet/balance"
        timestamp = str(int(time.time() * 1000))
        params = f"api_key={api_key}&timestamp={timestamp}"

        # Create signature
        sign_payload = f"{endpoint}?{params}"
        signature = hmac.new(api_secret.encode(), sign_payload.encode(), hashlib.sha256).hexdigest()

        url = f"{base_url}{endpoint}?{params}&sign={signature}"
        response = requests.get(url)
        data = response.json()

        if data.get("ret_code") == 0:
            balances = data.get("result", {})
            coins = []
            for coin, info in balances.items():
                coins.append({
                    "coin": coin,
                    "walletBalance": float(info.get("wallet_balance", 0)),
                    "equity": float(info.get("equity", 0)),
                    "availableBalance": float(info.get("available_balance", 0))
                })
            return jsonify({"coins": coins})
        else:
            return jsonify({"error": data.get("ret_msg", "API error")}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/profit_loss')
def profit_loss():
    try:
        df = pd.read_csv(RESULTS_FILE)
        profit = df["capital"].iloc[-1] - load_config()["initial_capital"]
        return jsonify({"profit": round(profit, 2)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/training_status')
def training_status():
    try:
        with open(STATUS_FILE) as f:
            status = json.load(f)
        log = [f"{status['scenario']} - Epoch {status['epoch']} | Step {status['step']} | Reward {status['reward']} | Capital {status['capital']}"]
        return jsonify({"logs": log})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/trade_history')
def trade_history():
    try:
        if os.path.exists(TRADE_HISTORY_FILE):
            df = pd.read_csv(TRADE_HISTORY_FILE)
            trades = df.tail(50).iloc[::-1].to_dict("records")
            return jsonify(trades)
        else:
            return jsonify({"trades": []})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/model_indicators')
def model_indicators():
    try:
        config = load_config()
        df = pd.read_csv(config["engineered_data_file"])
        latest = df.iloc[-1].to_dict()
        close_price = latest.get('close', None)
        indicators = {k: round(v, 4) if isinstance(v, (float, np.float64)) else v for k, v in latest.items()}
        reasoning = f"Latest close price: {close_price}, indicators updated in real-time."
        return jsonify({"indicators": indicators, "reasoning": reasoning})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def dashboard():
    return app.send_static_file('index.html')

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(host='0.0.0.0', port=5000, debug=True)

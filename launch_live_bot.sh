#!/bin/bash

echo "🚀 Launching the live trading bot with profit monitoring..."

# Activate virtual environment
source venv/bin/activate

# Check if best model exists
if [ ! -f "best_model_default.weights.h5" ]; then
  echo "❌ Best model not found. Please train the model first."
  exit 1
fi

# Start the live trading server
nohup python trade_server.py > logs/trade_server.log 2>&1 &
echo "📈 Live trading server started with PID $!"

# Start continuous training in background
nohup python train_forever.py > logs/train_forever.log 2>&1 &
echo "🔁 Continuous training started with PID $!"

# Monitor profit and restart bot if needed
while true; do
  profit=$(curl -s http://localhost:5000/api/profit_loss | jq -r '.profit')
  echo "Current profit: $profit"
  if (( $(echo "$profit < 0" | bc -l) )); then
    echo "⚠️ Profit negative, consider reviewing strategy or restarting bot."
  fi
  sleep 60
done

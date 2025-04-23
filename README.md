
Built by https://www.blackbox.ai

---

```markdown
# Trading Bot

## Project Overview
This project implements a trading bot that utilizes reinforcement learning techniques, specifically Double Deep Q-Networks (DDQN), to trade cryptocurrency based on historical market data. The bot features a trading environment that simulates market conditions, a replay buffer for experience storage, and various trading algorithms that can be adjusted through different scenarios and architectures.

## Installation
To get started with the trading bot, you need to set up your Python environment with the required dependencies:

1. Clone the repository:
   ```bash
   git clone https://your-repo-url.git
   cd trading-bot
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

   Make sure `tensorflow`, `numpy`, `pandas`, and `TA-Lib` are included in your `requirements.txt`.

4. Set up API credentials in `config.json`.
   You need to provide your Bybit API key and secret, as well as Telegram bot credentials for notifications.

## Usage
To train the trading bot, you can run the main script:
```bash
python main.py
```

To continuously train the model, you can use:
```bash
python train_forever.py
```

This will load the configuration, execute the training process, and allow for iterative improvement of the trading model.

You can also run a local server to monitor trading status, profit/loss, and other indicators by executing:
```bash
python trade_server.py
```
Access the API at `http://localhost:5000/api`.

## Features
- **Reinforcement Learning**: Utilizes DDQN for decision-making in trading.
- **Customizable Scenarios**: Different trading strategies can be configured through `config.json`.
- **Real-time Data Fetching**: Fetch historical market data from Bybit and engineer features using TA-Lib.
- **Logging and Notifications**: Monitor trading progress and receive updates via Telegram.
- **API Dashboard**: Provides real-time information via a local Flask web server.

## Dependencies
The project requires the following Python packages:
- `tensorflow`
- `numpy`
- `pandas`
- `requests`
- `TA-Lib`
- `Flask` (for the API)
- Other commonly used libraries (you can list all in `requirements.txt`)

## Project Structure
Here's a high-level overview of the project structure:

```
trading-bot/
│
├── config.json           # Configuration file for settings and API keys
├── main.py               # Main execution script for training
├── train_forever.py      # Script for continuous training of the model
├── trade_server.py       # Flask server for providing trading information via API
│
├── environment.py        # Defines the trading environment
├── agent.py              # Implements the DDQN agent and training logic
├── model.py              # Builds the neural network architecture
├── replay_buffer.py       # Implements the experience replay buffer
├── feature_engineering.py # Contains functions for feature engineering
├── fetch_bybit_data.py   # Fetches market data from Bybit
├── telegram_bot.py       # Sends notifications to Telegram
├── utils.py              # Utility functions for logging trades
│
├── trade_history.csv      # Logs of trade history
├── bot_status.json        # Current status of the trading bot
└── results.csv           # Results of the trading bot's performance
```

## License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
```
#!/bin/bash

echo "Welcome to the Fast RL Trading Bot Interactive Launcher!"

read -p "Do you want to run the setup (install dependencies, fetch data, train initial model)? (y/n): " run_setup
if [[ "$run_setup" =~ ^[Yy]$ ]]; then
    echo "Running setup..."
    ./setup_bot.sh
    if [ $? -ne 0 ]; then
        echo "Setup failed. Please check the errors above."
        exit 1
    fi
    echo "Setup completed successfully."
else
    echo "Skipping setup."
fi

read -p "Do you want to launch the live trading bot now? (y/n): " run_live
if [[ "$run_live" =~ ^[Yy]$ ]]; then
    echo "Launching live trading bot..."
    ./launch_live_bot.sh
    if [ $? -ne 0 ]; then
        echo "Failed to launch live trading bot. Please check the errors above."
        exit 1
    fi
    echo "Live trading bot launched successfully."
else
    echo "Live trading bot launch skipped."
fi

echo "Interactive launcher finished."

# Algorithms

## [SimpleYahoo.py](SimpleYahoo.py)

`SimpleYahoo.py` is a Python script that utilizes Yahoo Finance data to build a stock price predictor using PyTorch. The main objective is to create a proof-of-concept AI model that predicts stock prices based on historical data.

#### Key Components:
- **Libraries Used**: The script imports libraries such as PyTorch for building and training the neural network, NumPy for numerical operations, and `yfinance` for fetching stock data.
- **Model Architecture**: It defines a `StockPredictor` class using LSTM (Long Short-Term Memory) layers, suitable for time series prediction.
- **Data Handling**: The script retrieves recent stock price data, processes it, and calculates a desired median price for adjustments.
- **Training Loop**: It implements a training loop that adjusts the input data based on perturbations to improve the model's learning.
- **Redis Integration**: Redis is used to manage ticker symbols for multiple stocks, allowing batch processing.
- **Model Saving**: After training, the model's state is saved to a file for later use.
- **Prediction**: Finally, the script demonstrates the model's predictions against actual prices and visualizes the stock price data using `plotext`.

This code serves as a foundational approach to applying machine learning in financial predictions.

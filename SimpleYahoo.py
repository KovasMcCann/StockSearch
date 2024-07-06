#######################################################
# Name: SimpleYahoo.py                                #
# Description: simple yahoo and tensorflow predictor  #
# Idea: use yahoo finance to build an ai              #
#######################################################

# the code bellow is to learn about tensor flow
import tensorflow as tf
import numpy as np
import yfinance as yf
import multiprocessing
import redis

#redis config   
redis_host = '10.1.10.131'
redis_port = 6379
redis_db = 0  # default database
redis_password = None  # no password set
r = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db, password=redis_password)

#model config 
model = tf.keras.Sequential([
    tf.keras.layers.LSTM(50, activation='relu', input_shape=(20, 1)), # what does this mean
    tf.keras.layers.Dense(1)
])

# Generate dataset

def trainticker(ticker):
    #print(f'Training: {ticker}')
    ticker_obj = yf.Ticker(ticker)

    try:
        todays_data = ticker_obj.history(period='1d', interval='1m')
        if todays_data.empty:
            raise ValueError(f"No data found for today for ticker {ticker}")
        Y = [todays_data['Close'].iloc[-1]]  # price now

        historical_data = ticker_obj.history(period='1mo')  # '1mo' fetches approximately the last 30 days
        if historical_data.empty or len(historical_data['Close']) < 20:
            raise ValueError(f"Not enough historical data for ticker {ticker}")

        X = historical_data['Close'].tolist()

        X = np.array(X, dtype=np.float32).reshape((1, 20, 1))
        Y = np.array(Y, dtype=np.float32)

        # Compile the model
        model.compile(optimizer='adam', loss='mse')

        # Train the model
        model.fit(X, Y, epochs=200, verbose=0)
        #print(f"Training completed for: {ticker}")
    except ValueError as e:
        print(e)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    """
    print(f'Training: {ticker}')
    ticker = yf.Ticker(ticker)
    Y = [] #price now

    todays_data = ticker.history(period='1d', interval='1m')
    Y.append(todays_data['Close'].iloc[-1])
    #print(f'Y: {Y}')

    #X = [] #price previous price
    
    todays_data = ticker.history(period='1mo')  # '1mo' fetches approximately the last 30 days
    X = todays_data['Close'].tolist()

    #X.append(closing_prices)
    #print(f'X length: {len(X)}')
    
    X = np.array(X)
    Y = np.array(Y)
    # Reshape X for LSTM [samples, time steps, features]
    X = np.array(X, dtype=np.float32).reshape((1, 20, 1))
    #X = X.reshape((X.shape[0], X.shape[1], 1))

    # Compile the model
    model.compile(optimizer='adam', loss='mse')

    # Train the model
    model.fit(X, Y, epochs=200, verbose=0)
    """

    """
    for i in range(start, end - 3):
        sequence = np.array([i, i + 1, i + 2], dtype=np.float32)
        target = np.array([i + 3], dtype=np.float32)
        X.append(sequence)
        Y.append(target)
    return np.array(X), np.array(Y)
    """

# X= [1, 2, 3] 
# Y= [4]

# could be used to predict stock prices
# old stock data in x eg. [123.5, 124.5, 125.5]
# new stock data in y eg. [126.5]

r.select(0)

# Retrieve all keys (tickers) and calculate the total number
tickers = r.keys('*')
total_tickers = len(tickers)

current_ticker_number = 0
for ticker in tickers:
    current_ticker_number += 1
    print(f"Processing ticker : {ticker.decode('utf-8')} {current_ticker_number}/{total_tickers}")
    trainticker(ticker.decode('utf-8'))

"""
semaphore = multiprocessing.Semaphore(1)  # Correctly allow only 3 processes at a time

# Assuming 'r' is previously defined and is a Redis connection
r.select(0)

processes = []

masterdictionary = multiprocessing.Manager().dict()

for ticker in r.keys('*'):
    semaphore.acquire()
    try:
        process = multiprocessing.Process(target=trainticker, args=(ticker.decode('utf-8'),))
        processes.append(process)
        process.start()
    finally:
        semaphore.release()

for process in processes:
    process.join()
"""

#import sys
#sys.exit()  

#X, Y = generate_sequence(1, 100)

# Demonstrate prediction for MSFT


#X, Y = generate_price('MSFT')

# try to save model * not tested *
from tensorflow import keras
model.save('stock_predictor.h5')

guessticker = yf.Ticker('MSFT')
Y = [] #price now

todays_data = guessticker.history(period='1d', interval='1m')
Y.append(todays_data['Close'].iloc[-1])
#print(f'Y: {Y}')
#X = [] #price previous price
todays_data = guessticker.history(period='1mo')  # '1mo' fetches approximately the last 30 days
X = todays_data['Close'].tolist()

print(f'Y: {Y}')

# Demonstrate prediction
test_input = np.array(X, dtype=np.float32).reshape((1, 20, 1))
predicted_number = model.predict(test_input).flatten()[0]
print(f'Predicted Price: {predicted_number}')

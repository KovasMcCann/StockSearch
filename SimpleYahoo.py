#######################################################
# Name: SimpleYahoo.py                                #
# Description: simple yahoo and tensorflow predictor  #
# Idea: use yahoo finance to build an ai              #
#######################################################

# the code bellow is to learn about tensor flow
import tensorflow as tf
from tensorflow.keras.callbacks import TerminateOnNaN
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
    tf.keras.layers.LSTM(50, activation='tanh', input_shape=(None, 1), kernel_initializer='glorot_uniform'), # what does this mean
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(1)
])
# Compile the model
# model.compile(optimizer='adam', loss='mse')
model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001, clipvalue=0.5), loss='mse') 

callbacks = [TerminateOnNaN()]

# Generate dataset

def trainticker(ticker, time):
    #print(f'Training: {ticker}')
    ticker_obj = yf.Ticker(ticker)

    try:
        todays_data = ticker_obj.history(period='1d', interval='1m')
        if todays_data.empty:
            raise ValueError(f"No data found for today for ticker {ticker}")
        Y = [todays_data['Close'].iloc[-1]]  # price now

        historical_data = ticker_obj.history(period=f'{time}')  # '1mo' fetches approximately the last 30 days
        if historical_data.empty or len(historical_data['Close']) < 20:
            raise ValueError(f"Not enough historical data for ticker {ticker}")

        X = historical_data['Close'].tolist()
        X = X[:-1]
        lenx = len(X)

        print(f"Data Size: {lenx} days")

        #X = np.array(X, dtype=np.float32).reshape((1, lenx, 1))
        #Y = np.array(Y, dtype=np.float32)

        # Train the model

        # shows the data 10 times to the model with a step of 10
        i = 10
        while i < 100:
            X = np.array(X, dtype=np.float32).reshape((1, lenx, 1)) + i 
            Y = np.array(Y, dtype=np.float32) + i
            print(f"Training... at i: {i} for ticker: {ticker} with price: {Y} ")
            model.fit(X, Y, epochs=200, verbose=0, callbacks=callbacks)
            i += 10

        #print(f"Training completed for: {ticker}")
    except ValueError as e:
        print(e)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# X= [1, 2, 3] 
# Y= [4]

r.select(0)

# Retrieve all keys (tickers) and calculate the total number
tickers = r.keys('*')
total_tickers = len(tickers)

current_ticker_number = 0

for ticker in tickers[:100]: # run first 10 tickers becase programs fails
    #for ticker in tickers: 
    current_ticker_number += 1
    print(f"Processing ticker : {ticker.decode('utf-8')} {current_ticker_number}/{total_tickers}")
    trainticker(ticker.decode('utf-8'), '1y')\

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
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
model.save('stock_predictor.keras')

guessticker = yf.Ticker('lea')
Y = [] #price now

todays_data = guessticker.history(period='1d', interval='1m')
Y.append(todays_data['Close'].iloc[-1])
#print(f'Y: {Y}')
#X = [] #price previous price
todays_data = guessticker.history(period='1y')  # '1mo' fetches approximately the last 30 days
X = todays_data['Close'].tolist()

print(f'Y: {Y}')

# Demonstrate prediction
lenx = len(X)
test_input = np.array(X, dtype=np.float32).reshape((1, lenx, 1))
predicted_number = model.predict(test_input).flatten()[0]
print(f'Predicted Price: {predicted_number}')
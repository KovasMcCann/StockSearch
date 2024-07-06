#######################################################
# Name: SimpleYahoo.py                                #
# Description: simple yahoo and tensorflow predictor  #
# Idea: use yahoo finance to build an ai              #
#######################################################

# the code bellow is to learn about tensor flow
import tensorflow as tf
import numpy as np
import yfinance as yf
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
#r.select(0)

"""
pipeline = r.pipeline()

for ticker in r.keys('*'):
    pipeline.get(ticker)

results = pipeline.execute()

for num in results:
    generate_price(ticker)
"""

def generate_price(ticker):
    ticker = yf.Ticker(ticker)
    Y = [] #price now

    todays_data = ticker.history(period='1d', interval='1m')
    Y.append(todays_data['Close'].iloc[-1])
    print(f'Y: {Y}')

    #X = [] #price previous price
    
    todays_data = ticker.history(period='1mo')  # '1mo' fetches approximately the last 30 days
    X = todays_data['Close'].tolist()

    #X.append(closing_prices)
    #print(f'X length: {len(X)}')
    return np.array(X), np.array(Y)

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

X, Y = generate_price('AAPL')

#import sys
#sys.exit()  

#X, Y = generate_sequence(1, 100)

print(f'X: {X}')
print(f'Y: {Y}')

print(f'X length: {len(X)} Y length: {len(Y)}')

# Reshape X for LSTM [samples, time steps, features]
X = np.array(X, dtype=np.float32).reshape((1, 20, 1))
#X = X.reshape((X.shape[0], X.shape[1], 1))

print(f'X length: {len(X)} Y length: {len(Y)}')

# Compile the model
model.compile(optimizer='adam', loss='mse')

# Train the model
model.fit(X, Y, epochs=200, verbose=0)

# Demonstrate prediction for MSFT

X, Y = generate_price('MSFT')
print(f'X: {X}')
print(f'Y: {Y}')

# Demonstrate prediction
test_input = np.array(X, dtype=np.float32).reshape((1, 20, 1))
predicted_number = model.predict(test_input).flatten()[0]
print(f'Predicted Price: {predicted_number}')

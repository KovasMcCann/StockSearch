#######################################################
# Name: tensor.py                                     #
# Description: Tensor class for tensor operations     #
# Idea: use sec forms and yahoo finance to build an ai#
#######################################################

# the code bellow is to learn about tensor flow
import tensorflow as tf
import numpy as np

# Generate dataset
def generate_sequence(start, end):
    X = []
    Y = []
    for i in range(start, end - 3):
        sequence = np.array([i, i + 1, i + 2], dtype=np.float32)
        target = np.array([i + 3], dtype=np.float32)
        X.append(sequence)
        Y.append(target)
    return np.array(X), np.array(Y)

# X= [1, 2, 3] 
# Y= [4]

# could be used to predict stock prices
# old stock data in x eg. [123.5, 124.5, 125.5]
# new stock data in y eg. [126.5]


X, Y = generate_sequence(1, 100)

print(f'X: {X}')
print(f'Y: {Y}')

# Reshape X for LSTM [samples, time steps, features]
X = X.reshape((X.shape[0], X.shape[1], 1))

# Define LSTM model
model = tf.keras.Sequential([
    tf.keras.layers.LSTM(50, activation='relu', input_shape=(3, 1)), # what does this mean
    tf.keras.layers.Dense(1)
])

# Compile the model
model.compile(optimizer='adam', loss='mse')

# Train the model
model.fit(X, Y, epochs=200, verbose=0)

# Demonstrate prediction
test_input = np.array([97, 98, 99], dtype=np.float32).reshape((1, 3, 1))
predicted_number = model.predict(test_input).flatten()[0]
print(f'Predicted number: {predicted_number}')

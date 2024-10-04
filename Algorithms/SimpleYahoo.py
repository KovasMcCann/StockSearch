############################################################
# Name: SimpleYahoo.py                                     #
# Description: simple yahoo and pytorch predictor          #
# Idea: use yahoo finance to build an ai (proof of concept)#
# Note: I dont think the GPU is enabled                    #
############################################################

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import yfinance as yf
import redis
import plotext as plt
from torch.utils.data import DataLoader, TensorDataset

# Redis config   
redis_host = '10.1.10.131'
redis_port = 6379
redis_db = 0  # default database
redis_password = None  # no password set
r = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db, password=redis_password)

# Check if GPU is available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Define the model
class StockPredictor(nn.Module):
    def __init__(self):
        super(StockPredictor, self).__init__()
        self.lstm1 = nn.LSTM(input_size=1, hidden_size=50, batch_first=True)
        self.lstm2 = nn.LSTM(input_size=50, hidden_size=50, batch_first=True)
        self.dropout = nn.Dropout(0.3)
        self.dense1 = nn.Linear(50, 25)
        self.dense2 = nn.Linear(25, 1)
        self.relu = nn.ReLU()

    def forward(self, x):
        x, _ = self.lstm1(x)
        x, _ = self.lstm2(x)
        x = self.dropout(x)
        x = self.relu(self.dense1(x[:, -1, :]))
        x = self.dense2(x)
        return x

model = StockPredictor().to(device)

# Define the optimizer and loss function
optimizer = optim.Adam(model.parameters(), lr=0.001)
criterion = nn.MSELoss()

# Generate dataset
def trainticker(ticker, time):
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

        # Desired median
        #desired_median = 100

        # Calculate current median
        current_median = np.median(X)

        # Calculate the difference
        difference = desired_median - current_median

        # Adjust the array to have the desired median
        X = np.array(X, dtype=np.float32) + difference
        Y = np.array(Y, dtype=np.float32) + difference

        # Reshape the array
        X = X.reshape((1, lenx, 1))
        
        print(f"Data Size: {lenx} days")
        print(f"New Median: {np.median(X)}")

        # Parameters
        base_perturbation = -10  # Start below the base price
        max_perturbation = 10    # End above the base price
        num_steps = 10          # Number of steps

        # Calculate the step size for perturbation
        step_size = (max_perturbation - base_perturbation) / num_steps

        # Prepare data for DataLoader
        X_tensor = torch.tensor(X, dtype=torch.float32).reshape((1, lenx, 1)).to(device)
        Y_tensor = torch.tensor(Y, dtype=torch.float32).to(device)
        dataset = TensorDataset(X_tensor, Y_tensor)
        dataloader = DataLoader(dataset, batch_size=1, shuffle=True)

        # Training loop
        for i in range(num_steps + 1):  # Iterate through the number of steps
            # Calculate the current perturbation
            perturbation = base_perturbation + (i * step_size)
    
            for X_batch, Y_batch in dataloader:
                # Adjust data
                X_adjusted = X_batch + i
                Y_adjusted = Y_batch + perturbation
    
                print(f"Training... at step: {i} with perturbation: {perturbation} for ticker: {ticker} with price: {Y_adjusted}")

                Y_adjusted = Y_adjusted.reshape((1, 1))
    
                # Fit the model with the adjusted data
                model.train()
                optimizer.zero_grad()
                output = model(X_adjusted)
                loss = criterion(output, Y_adjusted)
                loss.backward()
                optimizer.step()

    except ValueError as e:
        print(e)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

#Gather Mean

guessticker = yf.Ticker('lea')
Y = [] # price now

todays_data = guessticker.history(period='1d', interval='1m')
Y.append(todays_data['Close'].iloc[-1])

todays_data = guessticker.history(period='5d')  # '1mo' fetches approximately the last 30 days
X = todays_data['Close'].tolist()


# Calculate current median
desired_median = np.median(X)

r.select(0)

# Retrieve all keys (tickers) and calculate the total number
tickers = r.keys('*')
total_tickers = len(tickers)

current_ticker_number = 0

#for ticcker in tickers[:10]: # run first 10 tickers because programs fails
for ticker in tickers[:500]: # run first 10 tickers because programs fails
    current_ticker_number += 1
    print(f"Processing ticker : {ticker.decode('utf-8')} {current_ticker_number}/{total_tickers}")
    trainticker(ticker.decode('utf-8'), '1y')

# Save the model
torch.save(model.state_dict(), 'stock_predictor.pth')

"""
# Demonstrate prediction
guessticker = yf.Ticker('lea')
Y = [] # price now

todays_data = guessticker.history(period='1d', interval='1m')
Y.append(todays_data['Close'].iloc[-1])

todays_data = guessticker.history(period='5d')  # '1mo' fetches approximately the last 30 days
X = todays_data['Close'].tolist()

desired_median = 100

# Calculate current median
current_median = np.median(X)

# Calculate the difference
difference = desired_median - current_median
"""

# Adjust the array to have the desired median
X = np.array(X, dtype=np.float32)

# Plot data
plt.clf()   
plt.plot(X.flatten())
plt.show()

lenx = len(X)
test_input = torch.tensor(X, dtype=torch.float32).reshape((1, lenx, 1)).to(device)
model.eval()
with torch.no_grad():
    predicted_number = model(test_input).flatten().item()
print(f'--------------------------------------------------------------------')
print(f'Predicted Price: {predicted_number} Actual Price: {Y}')
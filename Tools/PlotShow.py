import pandas as pd
import pickle
import redis
import matplotlib.pyplot as plt
from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import print_formatted_text
from prompt_toolkit.shortcuts import button_dialog
from prompt_toolkit.application import Application
from prompt_toolkit.layout import Layout, HSplit, VSplit, Window
from prompt_toolkit.widgets import TextArea, Box, Label

# Redis Config
redis_host = '10.1.10.121'  # Replace with '127.0.0.1' if necessary
redis_port = 6379
redis_db = 2  # default database
redis_password = None  # no password set
r = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db, password=redis_password)

def get_stock_list():
    return r.keys('*')  # Assume 'stock_list' is the key containing all stock symbols

def load_data(ticker):
    data = r.hget(f'{ticker}', 'Data')
    if data:
        try:
            # Deserialize DataFrame from binary data
            data = pickle.loads(data)
        except (pickle.UnpicklingError, TypeError) as e:
            print(f"Error during unpickling: {e}")
            data = None
    return data

def plot(data):
    if data is None:
        print("No data to plot.")
        return

    df = pd.DataFrame(data)

    # Convert 'index' to datetime and 'row' to the actual values
    df['row'] = df['row'].astype(str)
    df['Open'] = df['row'].str.extract(r'Open\s+([0-9\.e+-]+)')[0].astype(float)

    # Filter to keep only 'Open' values
    df = df[['index', 'Open']]
    df.set_index('index', inplace=True)

    # Plotting
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['Open'], marker='o', linestyle='-', color='b')
    plt.title('Open Prices Over Time')
    plt.xlabel('Date')
    plt.ylabel('Open Price')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def display_stocks(stocks, start_index=0, page_size=50):
    end_index = min(start_index + page_size, len(stocks))
    stock_list = stocks[start_index:end_index]

    print_formatted_text(f"\nStocks ({start_index+1}-{end_index} of {len(stocks)}):")
    for idx, stock in enumerate(stock_list, start=start_index+1):
        print_formatted_text(f"{idx}. {stock.decode('utf-8')}")
    
    return end_index < len(stocks)  # Return True if there are more stocks to display

def main():
    stocks = get_stock_list()
    page_size = 10
    start_index = 0

    while True:
        more = display_stocks(stocks, start_index, page_size)
        
        user_input = prompt("\nEnter the stock number to view, 'n' for next page, or 'q' to quit: ").strip()

        if user_input.lower() == 'q':
            break
        elif user_input.lower() == 'n':
            if more:
                start_index += page_size
            else:
                print("No more stocks to display.")
        else:
            try:
                stock_number = int(user_input)
                if 1 <= stock_number <= len(stocks):
                    ticker = stocks[stock_number - 1].decode('utf-8')
                    data = load_data(ticker)
                    plot(data)
                else:
                    print("Invalid stock number.")
            except ValueError:
                print("Invalid input. Please enter a number.")

if __name__ == "__main__":
    main()

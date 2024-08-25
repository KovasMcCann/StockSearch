import pandas
import pickle
import redis
import matplotlib.pyplot as plt
from prompt_toolkit import prompt

# Redis Config
redis_host = '10.1.10.121' # Replace with '127.0.0.1' if necessary
redis_port = 6379
redis_db = 2  # default database
redis_password = None  # no password set
r = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db, password=redis_password)

def plot(data):
    if data is None:
        print("No data to plot.")
        return

    df = pandas.DataFrame(data)

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

def load(ticker):
    data = r.hget(f'{ticker}', 'Data')
    if data:
        try:
            # Deserialize DataFrame from binary data
            data = pickle.loads(data)
        except (pickle.UnpicklingError, TypeError) as e:
            # Handle errors and log them
            print(f"Error during unpickling: {e}")
            data = None
    return data

def main():
    ticker = prompt("Enter the ticker symbol (e.g., 'aapl'): ").strip()
    if ticker:
        data = load(ticker)
        plot(data)
    else:
        print("No ticker symbol entered.")

if __name__ == "__main__":
    main()

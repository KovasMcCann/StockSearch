# echo-client.py

import socket

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 699  # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b"Hello, world")
    data = s.recv(1024)

print(f"Received {data!r}")

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

def plot(data):
    df = pandas.DataFrame(data)

    # Convert 'index' to datetime and 'row' to the actual values
    df['row'] = df['row'].astype(str) 
    df['Open'] = df['row'].str.extract(r'Open\s+([0-9\.e+-]+)')[0].astype(float)

    # Fi   lter to keep only 'Open' values
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

plot(load('aapl'))
###############################################################
# Name: PriceSocket.py                                        #
# Description: Socket to allow you to get data from redis db  # 
###############################################################

#imports
import yfinance as yf
import socket
import selectors
import redis

# Redis init
redis_host = '10.1.10.131' #will be 127.0.0.1
redis_port = 6379
redis_db = 0  # default database
redis_password = None  # no password set
r = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db, password=redis_password)

# Sockets
HOST = '127.0.0.1'

PORT = 699

# Selector
sel = selectors.DefaultSelector()

# will run two functions simultaneously

def updatedb():
    # Get the data for the stock Apple by specifying the stock ticker, start date, and end date
    data = yf.download('AAPL', '2021-01-01', '2021-12-31')
    print(data)
    # Save the data to a CSV file
    data.to_csv('AAPL.csv')

def socketlisten():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            while True:
                data = conn.recv(1024) #data recived from client
                data = b"fuck you"
                if not data:
                    break
            conn.sendall(data)

socketlisten()
###############################################################
# Name: PriceSocket.py                                        #
# Description: Socket to allow you to get data from redis db  # 
###############################################################

#imports
import yfinance as yf
import socket
import selectors
import redis
import concurrent.futures
import time

# Redis init
redis_host = '10.1.10.131' #will be 127.0.0.1
redis_port = 6379
redis_db = 2  # default database
redis_password = None  # no password set
r = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db, password=redis_password)

# Sockets
HOST = '127.0.0.1'

PORT = 699

# will run two functions simultaneously


def builddb(): # will be used as a starting base 

    r.select(0)

    tickers = r.keys('*')

    r.select(2) #db 2 will store pirce data 

    def set_ticker(ticker): #use json for for better qires
        r.hset(ticker.decode('utf-8'), mapping= { 'last update': '69420',
                                                'array of values': 'value'})  # Assuming you want to set an empty string as the value

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(set_ticker, tickers)

def testsearch(): #needle in the hay
    r.select(2)  # Ensure we are in the correct database
    keys = r.keys('*')

    def process_key(key):
        fields = r.hgetall(key)
        if b'last update' in fields and fields[b'last update'] == b'69':
            print(f"Key: {key.decode('utf-8')}, Fields: {fields}")

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(process_key, keys)

def updatedb():
    r.set('foo', 'basr')
    text = r.get('foo')
    print(text.decode('utf-8'))

#updatedb()
#builddb()
print(time.strftime("%Y%m%d%H%M", time.localtime()))
testsearch()

"""
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
"""
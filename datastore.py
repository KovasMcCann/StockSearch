#imports
import requests
import asyncio
import aiohttp
import redis
import time
from datetime import datetime, timedelta
import yfinance #back up and to fill in old data
import pandas
import pickle
import random
import logging
import matplotlib.pyplot as plt

# Redis Config
redis_host = '10.1.10.131' #will be 127.0.0.1
redis_port = 6379
redis_db = 2  # default database
redis_password = None  # no password set
r = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db, password=redis_password)

##### Color Codes #####
RED = '\033[91m'
ORANGE = '\033[38;5;208m'
YELLOW = '\033[93m'
GREEN = '\033[92m'
CYAN = '\033[96m'
BLUE = '\033[94m'
PURPLE = '\033[95m'
WHITE = '\033[97m'
GRAY = '\033[90m'
BLACK = '\033[30m'
BROWN = '\033[38;5;52m'
def RANDOM():
    return f'\033[38;5;{random.randint(0,255)}m'
RESET = '\033[0m'


################################
import concurrent.futures
def builddb(): # will be used as a starting base 

    r.select(0)

    tickers = r.keys('*')

    r.select(2) #db 2 will store pirce data 
    import random #temp

    def set_ticker(ticker): #use json for for better qires
        r.hset(ticker.decode('utf-8'), mapping= { 
                                                'last update': 'NULL', #rand int is temp
                                                'Frequency': 'NULL',
                                                'Data': 'NULL'})  # Assuming you want to set an empty string as the value

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(set_ticker, tickers)
################################

def curl(ticker):
    url = f'https://generic709.herokuapp.com/stockc/{ticker}'
    table = requests.get(url)
    if table.status_code == 200:
        data = table.json()
        if data.get("price") is None or table.json() == None:
            return 'NULL'
        else:
            return table.json()['price']

def ycurl(ticker):
    print("ERROR: reverting to yfinance") 
    stock = yfinance.Ticker(ticker)
    data = stock.history(period='1m')
    if data.empty:  
        return 'NULL'
    else:
        return data['Open'][0]
    
def getweeks(firstday, today):
    # Convert the date strings to datetime.date objects
    date1 = datetime.strptime(firstday, "%Y-%m-%d").date()
    date2 = datetime.strptime(today, "%Y-%m-%d").date()
    
    # Calculate the difference in days
    delta = date2 - date1
    
    # Convert days to weeks
    weeks = delta.days / 7
    
    return weeks

def buildarray(ticker): #builds the array of the stock in 1 day intervals
    stock = yfinance.Ticker(ticker)

    DB = []

    nohalt = True

    logging.getLogger('yfinance').setLevel(logging.CRITICAL)

    #Get todays dat
    today = time.strftime("%Y-%m-%d", time.localtime())
    
    #Get the first day of stock
    data = stock.history(start='1069-04-20',end=f'{today}', interval='1d') #start data is very old to get last data
    if data.empty:
        print(f'{BLUE}NO DATA {ticker}{RESET}')
        nohalt = False
        r.hset(f'{ticker}', mapping={
            'last update':time.strftime("%Y%m%d%H%M", time.localtime()), 
            'Data': 'Dead'
        })
        print(f"{BLUE}Data Stored as Dead{RESET}")

        return

    firstday = time.strftime('%Y-%m-%d', time.strptime(str(data.index[0]).split()[0], '%Y-%m-%d'))
    #print(getweeks(firstday, today))

    print(f'building {ticker}') 

    tick = 0
    total = getweeks(firstday, today)
    cutoff_date = datetime.now() - timedelta(days=30)
    
    while datetime.strptime(firstday, "%Y-%m-%d") < cutoff_date and nohalt:
        nohalt = True 
        #print(getweeks(firstday, today))
        #get data
        new_date_str = (datetime.strptime(f"{firstday}", "%Y-%m-%d") + timedelta(days=7)).strftime("%Y-%m-%d")
        print(f'\r{GREEN}Getting Data From: {firstday} - {new_date_str} for {RESET}{WHITE}[{RESET}{RANDOM()}{ticker}{RESET}{WHITE}]{RESET}', end='')
        
        data = stock.history(start=f'{firstday}',end=f'{new_date_str}', interval='1d')
        if data.empty:
            print(f'{RED}Stock Died at {new_date_str}{RESET}')
            nohalt = False
            break
        
        for index, row in data.iterrows():
            #print(index, row)
            DB.append((index, row))
        
        #update firstday
        firstday = new_date_str
        tick += 1

    while getweeks(firstday, today) > 0 and nohalt:
        #print(getweeks(firstday, today))
        #get data
        new_date_str = (datetime.strptime(f"{firstday}", "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
        print(f'\r{GREEN}Getting Data From: {firstday} - {new_date_str} for {RESET}{WHITE}[{RESET}{RANDOM()}{ticker}{RESET}{WHITE}]{RESET}', end='')

        if int(datetime.strptime(new_date_str, "%Y-%m-%d").strftime("%Y%m%d")) > int(datetime.strptime(today, "%Y-%m-%d").strftime("%Y%m%d")):
            break
        try:
            data = stock.history(start=f'{firstday}',end=f'{new_date_str}', interval='1m')
        except Exception as e:        
            print(f'{RED}Error: {e}{RESET}')

        if data.empty:
            print(f'\r{YELLOW}weekend {new_date_str}{RESET}', end='')
        else: 
            for index, row in data.iterrows():
                #print(index, row)
                DB.append((index, row))

        #update firstday
        firstday = new_date_str
        tick += 1
    
    #print(f'{tick} / {total}')
    print('exporting to redis')
    DB_df = pandas.DataFrame(DB, columns=['index', 'row'])  # Convert list to DataFrame if needed
    
    #Data = buildarray(ticker)

    steralized = pickle.dumps(DB_df)

    r.hset(f'{ticker}', mapping={
        'last update':time.strftime("%Y%m%d%H%M", time.localtime()), 
        'Data': steralized
    })

def load(ticker):
    data = r.hget(f'{ticker}', 'Data')
    if data:
        try:
            # Deserialize DataFrame from binary data
            data = pickle.loads(data)
        except (pickle.UnpicklingError, TypeError) as e:
            # Handle errors and log them
            print(f"{RED}Error during unpickling: {e}{RESET}")
            data = None
    return data

def write_ticker(ticker):
    #print(r.hget(ticker, 'Data'))
    try:
        if r.hget(ticker, 'Data').decode('utf-8') == 'Dead':
            print(f'Dead Stock [{ticker}]')
            return
    except:
        pass

    # Load existing data from Redis
    old_data = load(ticker)
    if old_data is not None:
        print('Data Loaded')
        #try:
        if True:
            # Retrieve the latest data from yfinance

            old_data = pandas.DataFrame(old_data, columns=['index', 'row'])  # Convert list to DataFrame if needed
            new_data = yfinance.Ticker(ticker).history(period='1d', interval='1m')
            db = []
            for index, row in new_data.iterrows():
                db.append((index, row))
            new_data = pandas.DataFrame(db, columns=['index', 'row'])
            old_data = old_data.applymap(lambda x: str(x) if isinstance(x, (list, pandas.Series)) else x)
            new_data = new_data.applymap(lambda x: str(x) if isinstance(x, (list, pandas.Series)) else x)
            old_data.reset_index(drop=True, inplace=True)
            new_data.reset_index(inplace=True)
            if not new_data.empty:
                combined_data = pandas.concat([old_data, new_data]).drop_duplicates()
                
                # Serialize the updated DataFrame
                serialized_data = pickle.dumps(combined_data)
                
                # Update Redis with the new data
                r.hset(ticker, mapping={
                    'last update': time.strftime("%Y%m%d%H%M", time.localtime()),
                    'Data': serialized_data
                })
                print("Data Stored")
            else:
                print(f'No new data for {ticker}')
        """
        except Exception as e:
            print(f'Error: {e} for {ticker}')
        """
    else:
        print('Data Not Loaded')
        # Optionally rebuild the data
        # buildarray(ticker)

#write_ticker('aapl')

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

tickers = r.keys('*')

for ticker in tickers:
    print(ticker.decode('utf-8'))
    write_ticker(ticker.decode('utf-8'))
    #buildarray(ticker.decode('utf-8'))
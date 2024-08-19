import asyncio
import aioredis
import requests
import asyncio
import redis
import time
from datetime import datetime, timedelta
import yfinance #back up and to fill in old data
import pandas
import pickle
import random
import logging

t = aioredis.from_url("redis://10.1.10.131", db=0)
p = aioredis.from_url("redis://10.1.10.131", db=2)

##############################################
#imports
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

##############################################

import asyncio
import os
from concurrent.futures import ThreadPoolExecutor

# Mock function to simulate some processing
#def buildarray(ticker):
#    import time
#    time.sleep(1)  # Simulate a blocking operation
#    print(f"Processed {ticker}")

# Define the asynchronous task
async def run_task(ticker, executor):
    print(f"running {ticker}")
    # Run the blocking function in a separate thread
    await asyncio.get_event_loop().run_in_executor(executor, buildarray, ticker)

import aioredis

r = aioredis.from_url("redis://10.1.10.131")

# Define the main function
async def main():
    #keys = ['AAPL', 'TSLA', 'GOOGL', 'AMZN', 'MSFT', 'FB', 'NVDA', 'INTC', 'AMD', 'CSCO']
    
    keys = await r.keys('*')
    keys = [key.decode('utf-8') for key in keys]
    
    # Get the number of CPU cores
    num_cores = os.cpu_count()
    
    # Create a ThreadPoolExecutor with the number of CPU cores
    with ThreadPoolExecutor(max_workers=num_cores) as executor:
        # Create a list of tasks

        tasks = [run_task(ticker, executor) for ticker in keys]

        # Run tasks concurrently
        await asyncio.gather(*tasks)

# Run the main function
if __name__ == "__main__":
    asyncio.run(main())
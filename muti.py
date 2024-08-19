import asyncio
#from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
#import redis
import aioredis
#import time
import random
import sys
import os

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

"""
#Redis Config
redis_host = '10.1.10.131' #will be 127.0.0.1
redis_port = 6379
redis_db = 2  # default database
redis_password = None  # no password set
r = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db, password=redis_password)
"""

def printtop(message):
    sys.stdout.write(f'\033[F\033[K{message}\n')
    sys.stdout.flush()

def next_minute():
    now = datetime.now()
    current = now.strftime("%S")
    return 60 - int(current)


class MarketOpen:
    @staticmethod
    def is_holiday(date):
        return (date.month, date.day) in MarketOpen.holidays

    @staticmethod
    def time_range(current_time): 
        return current_time < 800 or current_time > 1459 # for chicago time
        #return current_time < 900 or current_time > 1559 # for new york time

    @staticmethod
    def is_weekend(date):
        return date >= 5

    @staticmethod
    def status():
        now = datetime.now()
        day = now.weekday()
        #day = int(6)
        current_time = int(now.strftime("%H%M"))
        display_time = now.strftime("%H:%M %m/%d/%Y")

        if MarketOpen.is_holiday(now):
            sys.stdout.write(f'\r[{display_time}] {RED}Market Closed: Holiday{RESET}') #need to add partial holidays
            sys.stdout.flush()
            return "CLOSED"
        elif MarketOpen.is_weekend(day):
            sys.stdout.write(f'\r[{display_time}] {RED}Market Closed: Weekend{RESET}')
            sys.stdout.flush()
            return "CLOSED"
        elif MarketOpen.time_range(current_time):
            sys.stdout.write(f'\r[{display_time}] {YELLOW}Market Closed{RESET}')
            sys.stdout.flush()
            return "CLOSED"
        else:
            sys.stdout.write(f'\r[{display_time}] {GREEN}Market Open{RESET}')
            sys.stdout.flush()
            return "OPEN"

    # Define holidays and non-working days
    holidays = [
        (1, 1),  # January 1
        (1, 15), # January 15 (MLK Day varies)
        (2, 19), # February 19 Washington Birthday varies)
        (3, 29), # March 29 (Good Friday varies)
        (5, 27), # May 27 (Memorial Day varies)
        (6, 19), # June 19 (Juneteenth)
        (9, 2),  # September 2 (Labor Day varies)
        (7, 4),  # July 4
        (11, 28),# November 28 (Thanksgiving varies)
        (12, 25) # December 25 
    ]

def printtop(message):
    sys.stdout.write(f'\033[F\033[K{message}\n')
    sys.stdout.flush()

# Create a Redis client
r = aioredis.from_url("redis://10.1.10.131")

# Define the asynchronous task
async def run_task(ticker):
    print(f"running {ticker.decode('utf-8')}")
    await asyncio.sleep(1)

# Define the main function
async def main():
    # Get the number of CPU cores
    num_cores = os.cpu_count()
    # Create a semaphore with the number of cores
    semaphore = asyncio.Semaphore(num_cores)

    # Get all keys from Redis
    keys = await r.keys('*')

    # Define a function to run tasks with semaphore
    async def sem_task(ticker):
        async with semaphore:
            await run_task(ticker)

    # Create a list of tasks
    tasks = [sem_task(ticker) for ticker in keys]

    # Run tasks concurrently
    await asyncio.gather(*tasks)

# Run the main function
if __name__ == "__main__":
    asyncio.run(main())
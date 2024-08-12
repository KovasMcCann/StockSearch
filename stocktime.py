from datetime import datetime
import time


import requests
import asyncio
#redis config
####################################
import redis

# Redis init
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

def is_holiday(date):
    return (date.month, date.day) in holidays
def time_range(current_time): 
    return current_time < 1000 or current_time > 1459 # for chicago time
    #return current_time < 900 or current_time > 1600 # for new york time

def is_weekend(date):
    return date >= 5

def next_minute():
    now = datetime.now()
    current = now.strftime("%S")
    return 60 - int(current)

def main():
    while True:
        now = datetime.now()
        day = now.weekday()
        #day = int(6)
        current_time = int(now.strftime("%H%M"))
        display_time = now.strftime("%H:%M %m/%d/%Y")

        if is_holiday(now):
            print(f'[{display_time}] {RED}Market Closed: Holiday{RESET}') #need to add partial holidays
        elif is_weekend(day):
            print(f'[{display_time}] {RED}Market Closed: Weekend{RESET}')
        elif time_range(current_time):
            print(f'[{display_time}] {YELLOW}Market Closed{RESET}')
        else:
            print(f'[{display_time}] {GREEN}Market Open{RESET}')
            #Start storing data

        # Sleep to prevent excessive CPU usage
        time.sleep(next_minute())  # Check every minute

if __name__ == "__main__":
    main()


import asyncio
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
import time
import random
import sys

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

# Define CPU-bound task function
def cpu_bound_task(x):
    result = 0
    for i in range(x):
        result += i * i
    return result

# Function to run CPU-bound tasks in parallel
def run_cpu_bound_tasks(data):
    with ProcessPoolExecutor() as executor:
        results = list(executor.map(cpu_bound_task, data))
    return results

async def run_cpu_bound_tasks_async(data):
    loop = asyncio.get_running_loop()
    # Run CPU-bound tasks using ProcessPoolExecutor
    with ProcessPoolExecutor() as executor:
        results = await loop.run_in_executor(executor, run_cpu_bound_tasks, data)
    return results

async def async_io_bound_task():
    await asyncio.sleep(1)
    return "I/O Task Complete"


async def main():
    while True:
        if MarketOpen.status() == "CLOSED":
            #if MarketOpen.status() == "OPEN": #for testing
            printtop("Market is closed.")
            time.sleep(next_minute())
            
        else:
            printtop("Market is open. Running tasks...")

            # Run I/O-bound tasks
            io_result = await async_io_bound_task()
            printtop(io_result)

            # Prepare data for CPU-bound tasks
            data = [1000000, 2000000, 3000000]

            # Run CPU-bound tasks in parallel
            cpu_results = await run_cpu_bound_tasks_async(data)
            printtop(f"CPU tasks results:{cpu_results}")
            time.sleep(next_minute())

# Execute the main async function
asyncio.run(main())

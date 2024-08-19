import asyncio
import aioredis
import yfinance
import pandas as pd
import pickle
import time
from datetime import datetime, timedelta
import logging
import os
from concurrent.futures import ThreadPoolExecutor
import aiohttp

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Redis Config
redis_url = "redis://10.1.10.131"
redis_db_price = 2
redis_db_general = 0

async def get_redis_client(db):
    logging.info(f"Connecting to Redis database {db}...")
    return await aioredis.from_url(redis_url, db=db)

async def fetch_stock_data(session, ticker, start_date, end_date, interval):
    try:
        stock = yfinance.Ticker(ticker)
        data = stock.history(start=start_date, end=end_date, interval=interval)
        return data
    except Exception as e:
        logging.error(f"Error fetching data for {ticker} from {start_date} to {end_date}: {e}")
        return pd.DataFrame()  # Return empty DataFrame on error

def getweeks(firstday, today):
    date1 = datetime.strptime(firstday, "%Y-%m-%d").date()
    date2 = datetime.strptime(today, "%Y-%m-%d").date()
    delta = date2 - date1
    weeks = delta.days / 7
    logging.debug(f"Calculating weeks: {weeks} weeks between {firstday} and {today}")
    return weeks

async def buildarray(ticker, redis_client):
    logging.info(f"Processing ticker: {ticker}")
    DB = []
    today = time.strftime("%Y-%m-%d", time.localtime())
    firstday = '1069-04-20'  # Very old start date to ensure data coverage

    # Fetch data in chunks
    chunk_size = timedelta(weeks=1)
    cutoff_date = datetime.now() - timedelta(days=30)
    
    while datetime.strptime(firstday, "%Y-%m-%d") < cutoff_date:
        new_date_str = (datetime.strptime(firstday, "%Y-%m-%d") + chunk_size).strftime("%Y-%m-%d")
        data = await fetch_stock_data(None, ticker, firstday, new_date_str, '1d')
        if data.empty:
            logging.warning(f"No data returned for week starting {firstday}. Stopping.")
            break
        DB.extend([(index, row) for index, row in data.iterrows()])
        firstday = new_date_str

    # Fetch minute-level data
    while getweeks(firstday, today) > 0:
        new_date_str = (datetime.strptime(firstday, "%Y-%m-%d") + timedelta(day

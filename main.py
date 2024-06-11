import requests

def getprice(symbol):
  import requests
  url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey=ZN9F4XFJ9CHZYZ44"
  r = requests.get(url)
  data = r.json()
  print(data)

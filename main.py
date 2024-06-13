import requests

def getprice(symbol):
  url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey=ZN9F4XFJ9CHZYZ44"
  r = requests.get(url)
  data = r.json()
  print(data)

#Available form types [0-Q, 10-K,8-K, 20-F, 40-F, 6-K]
def getdoc(symbol, formtype):
  print ("hello")

if  __name__ == "__main__":
  getprice('nvda')
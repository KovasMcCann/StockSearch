import requests
from bs4 import BeautifulSoup


#header for SEC access
headers = {
  'User-Agent': 'Kovas McCann (KovasMcCann@outlook.com)'
}


def getprice(symbol):
  url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey=ZN9F4XFJ9CHZYZ44"
  r = requests.get(url)
  data = r.json()
  print(data)

#Available form types [0-Q, 10-K,8-K, 20-F, 40-F, 6-K]
def getdoc(symbol, formtype):
  print ("hello")

#if  __name__ == "__main__":
#  getprice('nvda')

import requests
from bs4 import BeautifulSoup

def cik(company_name):
    search_url = "https://www.sec.gov/cgi-bin/browse-edgar"
    params = {
        'action': 'getcompany',
        'company': company_name,
        'owner': 'exclude',
        'count': '10'
    }

    
    response = requests.get(search_url, params=params, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        cik_tag = soup.find('input', {'name': 'CIK'})
        if cik_tag:
            return cik_tag['value']
        else:
            return "Company not found or CIK not available."
    else:
        print("Error fetching data:", response.status_code)
        return None

company_name = cik("Apple Inc")
print(f"CIK is: {company_name}")

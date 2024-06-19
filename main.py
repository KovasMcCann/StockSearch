import requests
from bs4 import BeautifulSoup
#header for SEC access

usr_agnt = {'User-Agent' : 'Kovas McCann (KovasMcCann@outlook.com)'}
Polygon_API_KEY = ''
search_url = "https://www.sec.gov/cgi-bin/browse-edgar"

def getprice(symbol):
  print("hello")
  #use polygon.io

#Available form types [0-Q, 10-K,8-K, 20-F, 40-F, 6-K]
#SEC implementation

def Get_CIK(company_name):
  params = {
    'action': 'getcompany',
    'company': company_name,
    'owner': 'exclude',
    'count': '10'
  }
    
  response = requests.get(search_url, params=params, headers=usr_agnt)
    
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

def Get_10k(cik):
  params = {
    'action': 'getcompany',
    'owner': 'exclude',
    'count': '10',
    'CIK': cik
  }

  response = requests.get(search_url, params=params, headers=usr_agnt)

  if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    filings = soup.find_all('a', string='10-K')  # Find all links with '10-K' text

    if filings:
      # Take the first 10-K filing link
      filing_link = filings[0]['href']
      full_filing_url = 'https://www.sec.gov' + filing_link
      return full_filing_url
    else:
      return f"10-K form not found for CIK {cik}"
  else:
    print("Error fetching data:", response.status_code)
    return None

print(Get_CIK('Apple inc.'))
print(Get_10k(Get_CIK('Apple inc.')))
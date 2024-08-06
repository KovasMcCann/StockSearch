#######################################################
# Name: sec.py                                        #
# Description: SEC class for SEC operations           #
#######################################################

import requests
from bs4 import BeautifulSoup
import json
import redis 
import yfinance as yf

#redis config 
redis_host = '10.1.10.131'
redis_port = 6379
redis_db = 0  # default database
redis_password = None  # no password set
r = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db, password=redis_password)

#header for SEC access
usr_agnt = {'User-Agent' : 'Kovas McCann (KovasMcCann@outlook.com)'}
Polygon_API_KEY = '7YQ8QUtevb_KLZnnAYH9CkKGON4dDKJ1'
search_url = "https://www.sec.gov/cgi-bin/browse-edgar"

class Get:
  #Available form types [0-Q, 10-K,8-K, 20-F, 40-F, 6-K]
  #SEC implementation
  @staticmethod
  def buildTkrDB():
    r.flushdb(0)
    url = 'https://www.sec.gov/include/ticker.txt'
    table = requests.get(url, headers=usr_agnt)
    if table.status_code == 200:
      stored = table.text.split()
      # Switch to database 0 once instead of doing it in the loop
      r.select(0)
      # Use a pipeline to batch commands
      pipeline = r.pipeline()
      for i in range(0, len(stored), 2):
        pipeline.set(stored[i], stored[i+1])
        # Execute all commands in the batch
        pipeline.execute()
    #value = r.get('aapl') #needs to be lower case 
    #print(value.decode('utf-8'))
    else:
      print('Error fetching data:', table.status_code)

  @staticmethod
  def CIK(company_name):
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

  @staticmethod
  def Json(cik):
    params = {
      'action': 'getcompany',
      'owner': 'exclude',
      'count': '10',
      'CIK': cik
    }
    session = requests.Session()
    response = session.get(f'https://data.sec.gov/submissions/CIK{cik}.json', params=params, headers=usr_agnt)

    if response.status_code == 200:
      #print(response.json())
      return response.json()
  def buildlnkDB():
    r.select(0)

    pipeline = r.pipeline()

    for ticker in r.keys('*'):
      pipeline.get(ticker)

    results = pipeline.execute()

    for num in results:
      num = num.decode('utf-8')
      #print(num)
    
      #num = str(r.get('aapl').decode('utf-8'))
      #print(num)

      # CIK needs to be 10 digits
      num_length = len(num)
      needed_zeros = 10 - num_length  # Calculate how many zeros are needed to make num 10 characters long
      zeros = '0' * needed_zeros  # Create a string of zeros of the needed length

      content = Get.Json(zeros + num)
      #print(content)

      forms = {
        '10-Q': [],
        '10-K': [],
        '8-K': [],
        '20-F': [],
        '40-F': [],
        '6-K': [],
      }
      flist = ['10-Q', '10-K', '8-K', '20-F', '40-F', '6-K']
      for i in range(0, len(content['filings']['recent']['accessionNumber'])):
        #r.select(1)
        #r.set(content['cik'], json.dumps(forms)) 
        form_type = content['filings']['recent']['form'][i]
        if form_type in flist:
          accession_number = content['filings']['recent']['accessionNumber'][i]
          primary = content['filings']['recent']['primaryDocument'][i]
          filingdate = content['filings']['recent']['filingDate'][i]
          cik = content['cik']

          #url = f'https://www.sec.gov/Archives/edgar/data/{cik}/{accession_number.split('-')}/{primary}'
          url = f'https://www.sec.gov/Archives/edgar/data/{cik}/{"".join(accession_number.split("-"))}/{primary}'
          print(url)
          #print(content['filings']['recent']['form'][i])
          forms[form_type].append({'url': url, 'date': filingdate})

      r.select(1)
      #r.append(content['cik'], str(forms))
      #print(forms)
      r.set(content['cik'], json.dumps(forms))

  def tree(num):
    r.select(num)
    keys = r.keys('*')

    for key in keys:
      value = r.get(key)
      #print(f'Key: {key.decode("utf-8")}, Value: {value.decode("utf-8")}')
      print(f'Key: {key.decode("utf-8")}, Value: {value}')
  def gethistory(ticker):

    # Download historical data for a specific stock
    #ticker = "AAPL"
    data = yf.download(ticker, start="2020-01-01", end="2020-12-31")


    tck = yf.Ticker(ticker)
    tck.info

    #print all data in terminal 
    import pandas as pd

    pd.set_option('display.max_columns', None)  # or 1000
    pd.set_option('display.max_rows', None)  # or 1000A
    pd.set_option('display.max_colwidth', None)  # or 199

    hist = tck.history(period="1y")
    print(hist)

    #print(data)
Get.buildTkrDB()
#Get.updateTickerDB()
Get.buildlnkDB()
#Get.tree(1)
Get.gethistory('AAPL')
Get.gethistory('TSLA')

""" 
Proper output.json links to the SEC website for the company's filings.
https://www.sec.gov/Archives/edgar/data/xslF345X05/0000320193-24-000075-index.html
to get this link you need to look at the:
primaryDocument - xslF345X05
accessionNumber - 0000320193-24-000075

Redis Database config 
database 0 - for ticker and CIK
database 1 - for the filing url

Get primary doc 
https://www.sec.gov/Archives/edgar/data/320193/000192109424000702/xsl144X01/primary_doc.xml
https://www.sec.gov/Archives/edgar/data/{cik without zero}/{acessionNumber without -}/primaryDocument
"""
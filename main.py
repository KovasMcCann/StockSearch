import requests
from bs4 import BeautifulSoup
import json
#header for SEC access

usr_agnt = {'User-Agent' : 'Kovas McCann (KovasMcCann@outlook.com)'}
Polygon_API_KEY = ''
search_url = "https://www.sec.gov/cgi-bin/browse-edgar"
class Get:
  #Available form types [0-Q, 10-K,8-K, 20-F, 40-F, 6-K]
  #SEC implementation
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

    response = requests.get(f'https://data.sec.gov/submissions/CIK{cik}.json', params=params, headers=usr_agnt)

    if response.status_code == 200:
      #print(response.json())
      return response.json()
  def tenk(json):
    Print('try')
  
class Parse:
  def tenk(json):
    print('try')
  def tenq(json):
    print('try')
  def eightk(json):
    print('try')
  def fourteena(json):
    print('try')
  
num = str(Get.CIK('Apple Inc.'))
#print(GetJson.Get_URL(num))
#print(Get.CIK('Apple Inc.'))
content = Get.Json(num)

with open("output.json", "w") as file: 
  json.dump(content, file, indent=4)

""" Propere output.josn links to the SEC website for the company's filings.
https://www.sec.gov/Archives/edgar/data/xslF345X05/0000320193-24-000075-index.html
to get this link you need to look at the:
primaryDocument - xslF345X05
accessionNumber - 0000320193-24-000075



"""

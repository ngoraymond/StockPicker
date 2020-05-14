import requests
from bs4 import BeautifulSoup
import pandas

ticker = []
name = []
PE_Ratio = []
mCap = []


seperator = 0
url = requests.get('https://www.slickcharts.com/sp500')
info = BeautifulSoup(url.text,'html.parser')
for x in info.findAll('tr'):
    for y in x('td'):
        for z in y.findAll('a'):
            if seperator%2==0:
                name.append(z.get_text())
            else:
                ticker.append(z.get_text())
            seperator+=1
for TK in ticker:
    apiURL = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/market/get-quotes"
    querySections = {"region":"US", "lang":"en", "symbols":TK}
    headers = {
    'x-rapidapi-host': "apidojo-yahoo-finance-v1.p.rapidapi.com",
    'x-rapidapi-key': "be50e8f3e5msh62f544c3ff62dc6p1c79fejsn3f817ebc536d"
    }
    try:
        res = requests.request("GET", apiURL, headers = headers, params = querySections)
        res.raise_for_status()
        obj = (res.json())["quoteResponse"]["result"][0]
        print(obj["longName"])
        mCap.append(obj["marketCap"])
        PE_Ratio.append(obj["forwardPE"])
    except:
        PE_Ratio.append("N/A")
        mCap.append("N/A")

    
df = pandas.DataFrame({'Name':name,'Ticker':ticker,'Market Cap':mCap, "PE":PE_Ratio}) 
df.to_excel("Stock Picker/stonks.xlsx")

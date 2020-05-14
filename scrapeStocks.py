import requests
import yfinance as yf
from bs4 import BeautifulSoup
import pandas
import time

ticker = []
name = []
PE_Ratio = []
Sector = []
mCap = []
info = []

print(yf.Ticker("MSFT").info)

separater = 0
url = requests.get('https://www.slickcharts.com/sp500')
info = BeautifulSoup(url.text,'html.parser')
for x in info.findAll('tr'):
    for y in x('td'):
        for z in y.findAll('a'):
            if separater%2==0:
                name.append(z.get_text())
            else:
                ticker.append(z.get_text())
            separater+=1
for TK in ticker:
    print(TK)
    TK = TK.replace(".","-")
    try:
        tikInfo = yf.Ticker(TK).info
        print(tikInfo["longBusinessSummary"])
        mCap.append(tikInfo["marketCap"])
        PE_Ratio.append(tikInfo["forwardPE"])
        Sector.append(tikInfo["sector"])
        info.append(tikInfo["longBusinessSummary"])
    except: 
        mCap.append("N/A")
        PE_Ratio.append("N/A")
        Sector.append("N/A")
        info.append("N/A")
       
print("DONE!")
df = pandas.DataFrame({'Name':name,'Ticker':ticker, 'Sector':Sector,'Market Cap':mCap, 'PE':PE_Ratio, 'Info':info}) 
df.to_excel("Stock Picker/stonks.xlsx")

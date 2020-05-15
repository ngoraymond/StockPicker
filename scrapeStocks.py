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
desc = []

#print(yf.Ticker("REGN").info)
#time.sleep(1000)

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
        tik = yf.Ticker(TK)
        try:
            print(tik.info["longBusinessSummary"])
        except:
            print("No Summary")
        mCap.append(tik.info["marketCap"])
        PE_Ratio.append(tik.info["forwardPE"])
        try:
            Sector.append(tik.info["sector"])
        except:
            Sector.append("N/A")
        try:
            desc.append(tik.info["longBusinessSummary"])
        except:
            desc.append("N/A")
    except: 
        mCap.append("N/A")
        PE_Ratio.append("N/A")
        Sector.append("N/A")
        desc.append("N/A")
       
print("DONE!")
df = pandas.DataFrame({'Name':name,'Ticker':ticker, 'Sector':Sector,'Market Cap':mCap, 'PE':PE_Ratio, 'Desc':desc}) 
df.to_excel("Stock Picker/stonks.xlsx")

import requests
import yfinance as yf
from bs4 import BeautifulSoup
import pandas
import time

def sp500_ticker_name():
    ticker = []
    name = []
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
    res = []
    res.append(ticker)
    res.append(name)
    return res

def get_stock_info():
    PE_Ratio = []
    Sector = []
    mCap = []
    desc = []

    tick_name = sp500_ticker_name()
    ticker = tick_name[0]
    name = tick_name[1]
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

if __name__ == '__main__':
    get_stock_info()

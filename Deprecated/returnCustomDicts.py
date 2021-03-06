import requests
import yfinance as yf
from bs4 import BeautifulSoup
import pandas
import time

def sp500_ticker_name():
    stockDict = []
    separater = 0
    url = requests.get('https://www.slickcharts.com/sp500')
    info = BeautifulSoup(url.text,'html.parser')
    for x in info.findAll('tr'):
        for y in x('td'):
            for z in y.findAll('a'):
                if separater%2==1:
                    stockDict.append({'ticker':z.get_text()})
                separater+=1
    return stockDict

def get_stock_info():
    tick_list = sp500_ticker_name()
    stockInfos = []
    for TK in tick_list:
        tk_name = TK['ticker']
        print(tk_name)
        tk_name = tk_name.replace(".","-")
        try:
            tik = yf.Ticker(tk_name)
            TK['name'] = tik.info["longName"]
            try:
                print(tik.info["longBusinessSummary"])
            except:
                print("No Summary")
            TK['marketCap'] = tik.info["marketCap"]
            TK['PE_Ratio'] = tik.info["forwardPE"]
            try:
                TK['Sector'] = tik.info["sector"]
            except:
                TK['Sector'] = 'N/A'
            try:
                TK['desc'] = tik.info["longBusinessSummary"]
            except:
                TK['desc'] = 'N/A'
        except: 
            TK['name'] = 'N/A'
            TK['mCap'] = 'N/A'
            TK['PE_Ratio'] = 'N/A'
            TK['Sector'] = 'N/A'
            TK['desc'] = 'N/A'
        
    print("DONE!")
    print(tick_list)
    return 0
    df = pandas.DataFrame({'Name':name,'Ticker':ticker, 'Sector':Sector,'Market Cap':mCap, 'PE':PE_Ratio, 'Desc':desc}) 
    df.to_excel("Stock Picker/stonks.xlsx")

if __name__ == '__main__':
    get_stock_info()

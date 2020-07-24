import requests
import yfinance as yf
from bs4 import BeautifulSoup
import pandas
import time
import pickle
import os
from pathlib import Path

filePath = "Stock Picker/stockInfo.xlsx"

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
    with open('Stock Picker/sp500List', 'wb') as fp:
        pickle.dump(stockDict, fp)
    return stockDict

def get_stock_info():
    tick_list = sp500_ticker_name()
    stockInfos = []
    failed = []
    for TK in tick_list:
        tk_name = TK['ticker']
        print(tk_name)
        tk_name = tk_name.replace(".","-")
        if tk_name == 'GOOGL':
            continue
        try:
            tik = yf.Ticker(tk_name)
            #TK['name'] = tik.info["shortName"]
            stockInfos.append(tik.info)
            try:
                print(tik.info["longBusinessSummary"])
            except:
                print("No Summary")
        except: 
            print(tk_name + ' Not found')  
            failed.append(tk_name)
        time.sleep(1.0)
    print(failed)
    if len(stockInfos) < 450:
        return []
    else:
        print("DONE!")
        #PUT TO EXCEL
        df = pandas.DataFrame(stockInfos) 
        df.to_excel(filePath)
        #DUMP TO FILE
        with open('Stock Picker/stockInfo', 'wb') as fp:
            pickle.dump(stockInfos,fp)
        return stockInfos

def picker():
    if Path(filePath).is_file():
        last_modified = os.stat(filePath).st_mtime
        elapsedTime = time.time() - last_modified
        if elapsedTime > 86400:
            get_stock_info()
    else:
        get_stock_info()
    grpBy = pandas.read_excel(filePath)
    stock_dict = grpBy.to_dict('records')
    if len(stock_dict) < 450:
        print('Redoing')
        get_stock_info()
        picker()
    only_profitable = lambda elem:elem['forwardPE'] > 0 and elem['trailingEps'] > 0
    stock_profit = filter(only_profitable, stock_dict)
    for itm in stock_profit:
        print(itm['shortName'] + ' ' + itm['sector'])
    by_sector = grpBy.groupby('sector')
        

if __name__ == '__main__':
    picker()

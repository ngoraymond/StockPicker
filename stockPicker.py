import requests
import yfinance as yf
from bs4 import BeautifulSoup
import pandas
import time
import pickle
import os
import itertools
import statistics
from pathlib import Path

filePath = "Stock Picker/stockInfo.xlsx"

def sleep():
    time.sleep(3.0)

def sp500_ticker_name():
    stockList = []
    separater = 0
    url = requests.get('https://www.slickcharts.com/sp500')
    info = BeautifulSoup(url.text,'html.parser')
    for x in info.findAll('tr'):
        for y in x('td'):
            for z in y.findAll('a'):
                if separater%2==1:
                    stockList.append({'ticker':z.get_text()})
                separater+=1
    with open('Stock Picker/sp500List', 'wb') as fp:
        pickle.dump(stockList, fp)
    print('Scraped S&P 500')
    return stockList

def new_scraper():
    wikiScrape = pandas.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    #first entry is the current members
    onlyCurrent = wikiScrape[0]
    with open('Stock Picker/sp500List.txt', 'wb') as fp:
        pickle.dump(onlyCurrent, fp)
    return onlyCurrent['Symbol'].tolist()

def get_stock_info():
    tick_list = new_scraper()
    stockInfos = []
    failed = []
    for TK in tick_list:
        #For the other function
        #tk_name = TK['ticker']
        tk_name = TK
        print(tk_name)
        tk_name = tk_name.replace(".","-")
        try:
            tik = yf.Ticker(tk_name)
            #TK['name'] = tik.info["shortName"]
            if len(stockInfos) > 0 and tik.info['shortName'] == stockInfos[-1]['shortName']:
                sleep()
                continue 
            stockInfos.append(tik.info)
            try:
                print(tik.info["longBusinessSummary"])
            except:
                print("No Summary")
        except: 
            #try twice
            try:
                sleep()
                stockInfos.append(yf.Ticker(tk_name).info)
                print('Second Chance Success')
            except:
                print(tk_name + ' Not found')  
                failed.append(tk_name)
        sleep()
    print('Unable to be found ')
    print(failed)
    for tk_name in failed:
        try:
            stockInfos.append(yf.Ticker(tk_name).info)
            print(tk_name + ' Third Chance Success')
        except:
            print('Fail ' + tk_name)
        sleep()
    if len(stockInfos) < 450:
        print('NOT ENOUGH INFO')
        return stockInfos
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
    #Get info for S&P 500 stocks every day
    if Path(filePath).is_file():
        last_modified = os.stat(filePath).st_mtime
        elapsedTime = time.time() - last_modified
        if elapsedTime > 86400:
            get_stock_info()
    else:
        get_stock_info()
    #GO TO EXCEL FILE, MAKE SURE AT LEAST CERTAIN AMOUNT OF STOCKS
    grpBy = pandas.read_excel(filePath)
    stock_dict = grpBy.to_dict('records')
    if len(stock_dict) < 450:
        print('Redoing')
        get_stock_info()
        picker()
    
    #ACTUAL STOCK PICKING STARTS HERE

    #ONLY PROFITABLE
    only_profitable = lambda elem:elem['forwardPE'] > 0 and elem['trailingEps'] > 0
    stock_profit = filter(only_profitable, stock_dict)
    #for itm in stock_profit:
        #print(itm['longName'] + ': ' + itm['sector'])

    #SEPARATE BY SECTOR
    sectorFunc = lambda x : str(x['sector'])
    #Dataframe version grpBy.groupby('sector')
    by_sector = itertools.groupby(sorted(stock_profit, key=sectorFunc), sectorFunc)
    for x in by_sector:
        listOfStocks = list(x[1])
        print(listOfStocks[0]['sector'])
        #GET the average forward PE of each sector
        avgforwardPE = statistics.mean(map(lambda x:x['forwardPE'], listOfStocks))
        belowAvgPE = filter(lambda x: x['forwardPE'] < avgforwardPE, listOfStocks)
        for y in belowAvgPE:
            print('    '+y['shortName'])
        

if __name__ == '__main__':
    picker()

import requests
import yfinance as yf
from bs4 import BeautifulSoup
import pandas
import time
import os
import itertools
import statistics
import json
from pathlib import Path

filePath = "Stock Picker/stockInfo.xlsx"

def sleep():
    time.sleep(3.0)

def sp500_ticker_name():
    storeFile = 'Stock Picker/sp500List'
    with open(storeFile, 'r') as fp:
        return json.load(fp)
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
    with open(storeFile, 'wb') as fp:
        fp.write(json.dumps(stockList), indent=4)
    print('Scraped S&P 500')
    return stockList

def new_scraper():
    wikiScrape = pandas.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    #first entry is the current members
    onlyCurrent = wikiScrape[0]
    with open('Stock Picker/sp500List', 'wb') as fp:
        fp.write(json.dumps(onlyCurrent), indent=4)
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

def screener(x):
    #Beta below 1.5
    lowBeta = x['beta'] < 1.5
    #checks the previous close is not the 52 week low, and the 50 day average is higher than 200 day average
    aboveLows = x['regularMarketPreviousClose'] > x['fiftyTwoWeekLow']
    goldenCross = x['fiftyDayAverage'] > x['twoHundredDayAverage']
    #growing = x['earningsQuarterlyGrowth'] >= 0
    return lowBeta and aboveLows and goldenCross

def picker():
    #Get info for S&P 500 stocks every day
    if Path(filePath).is_file():
        last_modified = os.stat(filePath).st_mtime
        elapsedTime = time.time() - last_modified
        if elapsedTime > 86400:
            print('Refreshing')
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

    recommendedStock = {}

    #ONLY PROFITABLE
    only_profitable = lambda elem:elem['forwardPE'] > 0 and elem['trailingEps'] > 0
    stock_profit = filter(only_profitable, stock_dict)

    #SEPARATE BY SECTOR
    sectorFunc = lambda x : str(x['industry'])
    #Dataframe version grpBy.groupby('sector')
    by_sector = itertools.groupby(sorted(stock_profit, key=sectorFunc), sectorFunc)
    for x in by_sector:
        add = []
        listOfStocks = list(x[1])
        #GET the average forward PE of each sector
        avgforwardPE = statistics.mean(map(lambda x:x['forwardPE'], listOfStocks))
        belowAvgPE = filter(lambda x: x['forwardPE'] <= avgforwardPE, listOfStocks)
        #run screener
        passesScreen = filter(screener, belowAvgPE)
        print(listOfStocks[0]['industry'])
        for y in passesScreen:
            add.append(y)
            print('    '+y['shortName'])
        print('----------------------------------------------------------------')
        recommendedStock[listOfStocks[0]['industry']] = add
    return json.dumps(recommendedStock, indent=4)

        

if __name__ == '__main__':
    print(picker())

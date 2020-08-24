import requests
import yfinance as yf
from bs4 import BeautifulSoup
import pandas
import time
from datetime import datetime, timedelta
import os
import itertools
import statistics
import json
from pathlib import Path

sp500_info_json_path =  'Stock Picker/Results/sp500List.json'
stock_info_excel_path = "Stock Picker/Results/stockInfo.xlsx"

#get dateTime
curtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
oneyearago = datetime.now().replace(year=datetime.now().year - 1).strftime("%Y-%m-%d %H:%M:%S")

def sleep():
    time.sleep(3.0)

def sp500_ticker_name():
    with open(sp500_info_json_path, 'r') as fp:
        return json.load(fp)
    stockList = []
    separater = 0
    url = requests.get('https://www.slickcharts.com/sp500')
    info = BeautifulSoup(url.text,'html.parser')
    for x in info.findAll('tr'):
        for y in x('td'):
            for z in y.findAll('a'):
                if separater%2==1:
                    stockList.append(z.get_text())
                separater+=1
    with open(sp500_info_json_path, 'w') as fp:
        fp.write(json.dumps(stockList, indent=4))
    print('Scraped S&P 500')
    return stockList

def new_scraper():
    wikiScrape = pandas.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    #first entry is the current members
    onlyCurrent = wikiScrape[0]
    onlyCurrent.to_json(r'Stock Picker/Results/sp500List.json', orient='records', indent=4)
    return onlyCurrent['Symbol'].tolist()

def stock_info_all_at_once():
    tick_list = new_scraper()
    request_string = ''
    for x in tick_list:
        request_string = request_string + x + ' '
    all_info = yf.Tickers(request_string)
    stockInfos = []
    for tk in tick_list:
        strCMD = 'all_info.tickers.'+tk+'.info'
        print(tk)
        stockInfos.append(exec(strCMD))
    if len(stockInfos) < 450:
        print('NOT ENOUGH INFO')
        return stockInfos
    else:
        print("DONE!")
        #PUT TO EXCEL
        stockInfos = sorted(stockInfos, key=lambda x: x['marketCap'], reverse=True)
        df = pandas.DataFrame(stockInfos) 
        df.to_excel(stock_info_excel_path)
        #DUMP TO FILE
        with open('Stock Picker/Results/stockInfo.json', 'w') as fp:
            fp.write(json.dumps(stockInfos, indent=4))
        return stockInfos
    


def get_stock_info():
    tick_list = new_scraper()
    stockInfos = []
    failed = []
    for tk_name in tick_list:
        print(tk_name)
        tk_name = tk_name.replace(".","-")
        try:
            tik = yf.Ticker(tk_name)
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
        stockInfos = sorted(stockInfos, key=lambda x: x['marketCap'], reverse=True)
        df = pandas.DataFrame(stockInfos) 
        df.to_excel(stock_info_excel_path)
        #DUMP TO FILE
        with open('Stock Picker/Results/stockInfo.json', 'w') as fp:
            fp.write(json.dumps(stockInfos, indent=4))
        return stockInfos

def screener(x):
    #Beta below 1.5
    lowBeta = x['beta'] < 1.5
    #checks the previous close is not the 52 week low, and the 50 day average is higher than 200 day average
    aboveLows = x['regularMarketPreviousClose'] > x['fiftyTwoWeekLow']
    goldenCross = x['fiftyDayAverage'] > x['twoHundredDayAverage']
    #growing = x['earningsQuarterlyGrowth'] >= 0

    if not (lowBeta and aboveLows and goldenCross):
        return False

    #GATHERING SENTIMENT VIA STOCK DOWNGRADES/UPGRADES
    #check for the actions made
    try:
        recentRecs = yf.Ticker(x['symbol']).recommendations
        #move the date to become a regular column   
        recentRecs['Date'] = recentRecs.index
        #filter for recent ratings only
        mask = (df['Date'] > oneyearago) & (df['Date'] <= curtime)

        recList = recentRecs.loc[mask].to_dict('list')['Action']
        numPos = len([x for x in recList if x == 'up'])
        numNeg = len([x for x in recList if x == 'down'])
        posSentiment = numPos >= numNeg

        return posSentiment
    except:
        return True

def picker():
    #Get info for S&P 500 stocks every day
    if Path(stock_info_excel_path).is_file():
        last_modified = os.stat(stock_info_excel_path).st_mtime
        elapsedTime = time.time() - last_modified
        if elapsedTime > 86400:
            print('Refreshing')
            get_stock_info()
    else:
        get_stock_info()
    #GO TO EXCEL FILE, MAKE SURE AT LEAST CERTAIN AMOUNT OF STOCKS
    grpBy = pandas.read_excel(stock_info_excel_path)
    stock_dict = grpBy.to_dict('records')
    if len(stock_dict) < 450:
        print('Redoing')
        get_stock_info()
        picker()

    #updating date
    curtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    oneyearago = datetime.now().replace(year=datetime.now().year - 1).strftime("%Y-%m-%d %H:%M:%S")
    
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
    result = picker()
    with open('Stock Picker/selected_stocks.json', 'w') as fp:
        fp.write(result)

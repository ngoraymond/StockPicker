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

filePath = "Stock Picker/Results/stockInfo.xlsx"

#SLEEP TIME
def sleep():
    time.sleep(3.0)

#SCRAPER FOR SLICKCHARTS
def sp500_ticker_name():
    storeFile = 'Stock Picker/Results/sp500List.json'
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
    with open(storeFile, 'w') as fp:
        fp.write(json.dumps(stockList, indent=4))
    print('Scraped S&P 500')
    return stockList

#SCRAPE FROM WIKIPEDIA
def new_scraper():
    wikiScrape = pandas.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    #first entry is the current members
    onlyCurrent = wikiScrape[0]
    onlyCurrent.to_json(r'Stock Picker/Results/sp500List.json', orient='records', indent=4)
    return onlyCurrent['Symbol'].tolist()

#SCRAPE ONE BY ONE
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
        stockInfos = sorted(stockInfos, key=lambda x: x['marketCap'], reverse=True)
        df = pandas.DataFrame(stockInfos) 
        df.to_excel(filePath)
        #DUMP TO FILE
        with open('Stock Picker/Results/stockInfo.json', 'w') as fp:
            fp.write(json.dumps(stockInfos, indent=4))
        return stockInfos
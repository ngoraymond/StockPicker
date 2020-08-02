import yfinance as yf 
import json

print(json.dumps(yf.Ticker('t').info, indent=4))

print(yf.Ticker('t').recommendations.to_dict('list')['Action'])

yf.Ticker('aapl').recommendations.to_excel('APPLERECS.xlsx')
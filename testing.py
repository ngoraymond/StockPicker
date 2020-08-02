import yfinance as yf 
import json

print(json.dumps(yf.Ticker('t').info, indent=4))

print(type(yf.Ticker('t').info['marketCap']))
import yfinance as yf 
import json

print(json.dumps(yf.Ticker('VZ').info, indent=4))
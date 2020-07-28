import yfinance as yf 
import json

print(json.dumps(yf.Ticker('PG').info, indent=4))
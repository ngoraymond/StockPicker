import yfinance as yf 
import json
from datetime import datetime, timedelta


print(json.dumps(yf.Ticker('t').info, indent=4))

#try to make date a normal column instead of an index column
df = yf.Ticker('t').recommendations

curtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
oneyearago = datetime.now().replace(year=datetime.now().year - 1).strftime("%Y-%m-%d %H:%M:%S")

#turn date from an index to a column
df['Date'] = df.index

#filter out older recommendations
mask = (df['Date'] > oneyearago) & (df['Date'] <= curtime)

print(df.loc[mask].to_dict('list')['Action'])

yf.Ticker('aapl').recommendations.to_excel('APPLERECS.xlsx')

#print(df[.loc[df['Date'].between(oneyearago, curtime)]])

tks = yf.Tickers('AAPL MMM BRK.B')
print(tks.tickers.AAPL.info)
import os
from binance.client import Client

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

#Binance client object
binance_client = Client(API_KEY, API_SECRET)
#The coins or tokens which the bot will trade with
TICKERS=["BTCUSDT"]

#The asset used to buy/sell the various coins or tokens
LIQUIDITY_ASSET = "USDT"

#Amount to paper trade with. amount in usdt 
#Currently removed from the program
PAPER_TRADING_AMOUNT = 1000

#Everything below are the trading bot settings. 
# I recommend not messing with them unless you know what you're doing

#The timeperiod in which the bot gets candlestick data. 
# The lower the value, more the amount of trades that will happen. 
# Example values: 1MINUTE, 15MINUTES, 1HOUR, 1DAY
KLINE_TIME_PERIOD="1MINUTE"
#The amount of historical data points the bot will collect. 
# Higher value results in more accurate calculations
DATA_POINT_PERIOD="30 day ago UTC"
#The timeperiod in which relative strength index is calculated
RSI_TIMEPERIOD=6
#The lower limit of RSI. 
#If rsi of an asset reaches below this value, a buy order will be executed (assuming that asset is not already there in portfolio). 
#Typically, a value below 30 indicates that an asset is in oversold region (Good buying opportunity)
RSI_LOWER_POINT=45
#The upper limit of RSI. 
#If rsi of an asset reaches above this value, a sell order will be executed (assuming that asset is already in portfolio). 
#Typically, a value above 70 indicates that an asset is in overbought region (Good selling opportunity)
RSI_UPPER_POINT=50
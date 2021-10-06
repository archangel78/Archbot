import os

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

#The coins or tokens which the bot will trade with
TICKERS=["BTCUSDT","ETHUSDT","ADAUSDT","WRXUSDT","SOLUSDT"]
#The trading bot settings. I recommend not messing with them unless you know what you're doing

#The timeperiod in which the bot gets candlestick data. The lower the value, more the amount of trades that will happen. Example values: 1MINUTE, 15MINUTES, 1HOUR, 1DAY
KLINE_TIME_PERIOD="5MINUTE"
#The amount of historical data points the bot will collect. Higher value results in more accurate calculations
DATA_POINT_PERIOD="40 day ago UTC"
#The timeperiod in which relative strength index is calculated
RSI_TIMEPERIOD=14
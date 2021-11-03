import json
import config
import socket
import requests
from binance.client import Client

#reads the data in temp_data.json and stores it in variables
def get_temp_data():
    temp_file = open("datafiles/temp_data.json")
    temp_file_data = json.load(temp_file)
    return temp_file_data

#Gets the historical closes of the ticker
def get_closes(ticker):
    try:
        closes = []    
        candle_sticks = config.binance_client.get_historical_klines(ticker, Client.KLINE_INTERVAL_1MINUTE, config.DATA_POINT_PERIOD)
        for candle in candle_sticks:
            closes.append(float(candle[4]))
        return closes
    except socket.timeout:
        print("[x] "+ticker+" socket timed out")
        print("[x] Terminating trading with "+ticker)
        exit()
    except requests.exceptions.Timeout:
        print("[x] "+ticker+" socket timed out")
        print("[x] Terminating trading with "+ticker)
        exit()
    except requests.exceptions.ConnectionError:
        print("[x] "+ticker+" socket timed out")
        print("[x] Terminating trading with "+ticker)
        exit()

#gets last few closes of ticker
def get_last_closes(ticker_string, ticker_closes):
    klines = config.binance_client.get_historical_klines(ticker_string, Client.KLINE_INTERVAL_1MINUTE, "6 minute ago UTC")
    i = -1
    while ticker_closes[i]!=float(klines[0][4]):
        i = i -1
    ticker_closes = ticker_closes[:i]
    for candle in klines:
        ticker_closes.append(float(candle[4]))
    return ticker_closes

#gets current balance of any asset
def get_asset_balance(ticker):
    return float(config.binance_client.get_asset_balance(ticker)["free"])
import os
import config
import csv
import talib
import json
from time import sleep
from threading import Thread
from numpy import genfromtxt, log
from binance.client import Client

client = Client(config.API_KEY, config.API_SECRET)
verbose = True
total_usdt = 1000
usdt_amount = 0
asset_amount = []
token_currently_in_portfolio = []

def buy(buy_ticker,ticker_id):
    global usdt_amount, asset_amount
    ticker = get_ticker(buy_ticker)
    last_price = float(ticker["lastPrice"])
    asset_amount[ticker_id] = (total_usdt/len(config.TICKERS))/last_price
    asset_worth = asset_amount[ticker_id]*last_price
    usdt_amount = usdt_amount - asset_worth
    token_currently_in_portfolio[ticker_id] = "True"
    write_trade(buy_ticker, "Buy", last_price, ticker_id, asset_worth)

def sell(sell_ticker,ticker_id):
    global usdt_amount, asset_amount
    ticker = get_ticker(sell_ticker)
    last_price = float(ticker["lastPrice"])
    sold_usdt_amount = asset_amount[ticker_id]*last_price
    usdt_amount = usdt_amount + sold_usdt_amount
    asset_amount[ticker_id] = 0
    token_currently_in_portfolio[ticker_id] = "False"
    write_trade(sell_ticker, "Sell", last_price, ticker_id, sold_usdt_amount)
    buy_flag = True

def get_data(ticker):
    candle_sticks = client.get_historical_klines(ticker, Client.KLINE_INTERVAL_1MINUTE, config.DATA_POINT_PERIOD)
    csvfile = open("priceDataFiles/"+ticker+"_priceData.csv","w",newline="")
    candle_stick_writer = csv.writer(csvfile, delimiter=",")
    for candle in candle_sticks:
        candle_stick_writer.writerow(candle)
    csvfile.close()

def check_rsi(ticker,ticker_id):
    csv_data = genfromtxt("priceDataFiles/"+ticker+"_priceData.csv", delimiter=",")
    closes = csv_data[:,4]
    rsi_indicator = talib.RSI(closes,config.RSI_TIMEPERIOD)
    log_data("[*] Current RSI value: "+str(rsi_indicator[-1]),"high")
    if(rsi_indicator[-1] >= 62):
        log_data("[*] Rsi indicator indicates that "+ticker+" is in overbought region","high")
        if token_currently_in_portfolio[ticker_id]=="True":
            log_data("[*] Selling existing assets of "+ticker,"low")
            sell(ticker, ticker_id)
    elif(rsi_indicator[-1] <= 38):
        log_data("[*] Rsi indicator indicates that "+ticker+" is in oversold region","high")
        if token_currently_in_portfolio[ticker_id]=="False":
            log_data("[*] Buying assets of "+ticker,"low")
            buy(ticker, ticker_id)
    else:
        log_data("[*] Rsi indicator suggests that "+ticker+" is currently neutral, waiting for optimal entry/exit","high")

def write_trade(ticker, trade_type, trade_price, ticker_id, asset_worth):
    global usdt_amount, asset_amount, token_currently_in_portfolio

    trade_file = open("trades.json")
    trade_file_data = json.load(trade_file)

    print("[*] "+ticker+" Trade completed: ")
    print("\t- Ticker: "+ticker+"\n\t- Trade type: "+trade_type)

    current_trade = {}
    current_trade["ticker"] = ticker
    current_trade["trade_type"] = trade_type
    if(trade_type=="Buy"):
        current_trade["buying_price"] = trade_price
        current_trade["amount_bought"] = asset_amount[ticker_id]
        print("\t- Buying price: "+str(trade_price)+"\n\t- Amount bought: "+str(asset_amount[ticker_id]))
    else:
        current_trade["selling_price"] = trade_price
        current_trade["amount_sold"] = asset_worth/trade_price
        print("\t- Selling price: "+str(trade_price)+"\n\t- Amount sold: "+str(asset_amount[ticker_id]))
        
    current_trade["asset_worth"] = asset_worth
    trade_file_data["trades"].append(current_trade)
    trade_file_data["usdt_amount"] = usdt_amount
    trade_file_data["currently_holding_amount"] = asset_amount
    trade_file_data["currently_holding_boolean"] = token_currently_in_portfolio

    with open ("trades.json", "w") as outputFile:
        outputFile.write(str(trade_file_data).replace("\'","\""))

def get_ticker(ticker_string):
    tickers = client.get_ticker()
    for ticker in tickers:
        if ticker["symbol"] == ticker_string:
            return ticker

def start_trading(ticker,ticker_id):
    log_data("[*] Trading started with the following ticker: "+ticker,"high")
    while 1:
        get_data(ticker)
        check_rsi(ticker,ticker_id)
        sleep(10)

def log_data(string, verbosity):
    if(verbosity=="high" and verbose):
        print(string)
    elif(verbosity=="low"):
        print(string)


if __name__=="__main__":
    os.system("mkdir priceDataFiles")
    trade_file = open("trades.json")
    trade_file_data = json.load(trade_file)
    asset_amount = trade_file_data["currently_holding_amount"]
    usdt_amount = trade_file_data["usdt_amount"]
    token_currently_in_portfolio = trade_file_data["currently_holding_boolean"]

    threads = []
    for i in range(len(config.TICKERS)):
        thread = Thread(target=start_trading, args=(config.TICKERS[i],i,))
        thread.start()
        threads.append(thread)
        sleep(5)

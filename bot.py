import os
import csv
import talib
import json
import config
import socket
import optparse
import requests.exceptions
from time import sleep
from threading import Thread
from numpy import genfromtxt
from binance.client import Client

verbose = False
buy_flag = True
total_usdt = 1000
usdt_amount = 0
continue_trading = True
exit_trading = False

threads = []
asset_amount = []
token_currently_in_portfolio = []
client = Client(config.API_KEY, config.API_SECRET)

def buy(buy_ticker,ticker_id):
    global usdt_amount, asset_amount
    ticker = get_ticker(buy_ticker)
    last_price = float(ticker["price"])
    asset_amount[ticker_id] = (total_usdt/len(config.TICKERS))/last_price
    asset_worth = asset_amount[ticker_id]*last_price
    usdt_amount = usdt_amount - asset_worth
    token_currently_in_portfolio[ticker_id] = "True"
    write_trade(buy_ticker, "Buy", last_price, ticker_id, asset_worth)

def sell(sell_ticker,ticker_id):
    global usdt_amount, asset_amount
    ticker = get_ticker(sell_ticker)
    last_price = float(ticker["price"])
    sold_usdt_amount = asset_amount[ticker_id]*last_price
    usdt_amount = usdt_amount + sold_usdt_amount
    asset_amount[ticker_id] = 0
    token_currently_in_portfolio[ticker_id] = "False"
    write_trade(sell_ticker, "Sell", last_price, ticker_id, sold_usdt_amount)

def sell_all():
    trade_file = open("trades.json")
    trade_file_data = json.load(trade_file)
    currently_holding_boolean = trade_file_data["currently_holding_boolean"]
    for i in range(len(currently_holding_boolean)):
        if(currently_holding_boolean[i] == "True"):
            sell(trade_file_data["tickers"][i], i)

def get_data(ticker):
    if not continue_trading:
        return
    try:
        candle_sticks = client.get_historical_klines(ticker, Client.KLINE_INTERVAL_1MINUTE, config.DATA_POINT_PERIOD)
        csvfile = open("priceDataFiles/"+ticker+"_priceData.csv","w",newline="")
        candle_stick_writer = csv.writer(csvfile, delimiter=",")
        for candle in candle_sticks:
            candle_stick_writer.writerow(candle)
        csvfile.close()
    except socket.timeout:
        print("[*] "+ticker+" socket timed out. skipping iteration")
    except requests.exceptions.Timeout:
        print("[*] "+ticker+" socket timed out. skipping iteration")

def check_rsi(ticker,ticker_id):
    if not continue_trading:
        return
    csv_data = genfromtxt("priceDataFiles/"+ticker+"_priceData.csv", delimiter=",")
    closes = csv_data[:,4]
    rsi_indicator = talib.RSI(closes,config.RSI_TIMEPERIOD)
    log_data("[*] "+ticker+": ", "high")
    log_data("\t- Current RSI value: "+str(rsi_indicator[-1]),"high")
    if(rsi_indicator[-1] >= config.RSI_UPPER_POINT):
        print("\t- Rsi indicator indicates that "+ticker+" is in overbought region")
        if token_currently_in_portfolio[ticker_id]=="True":
            print("\t- Selling existing assets of "+ticker,"high")
            sell(ticker, ticker_id)
    elif(rsi_indicator[-1] <= config.RSI_LOWER_POINT):
        log_data("\t- Rsi indicator indicates that "+ticker+" is in oversold region","high")
        if not buy_flag:
            return
        if token_currently_in_portfolio[ticker_id]=="False":
            print("\t- Buying assets of "+ticker)
            buy(ticker, ticker_id)
    else:
        log_data("\t- Rsi indicator suggests that "+ticker+" is currently neutral, waiting for optimal entry/exit","high")

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
        print("\t- Selling price: "+str(trade_price)+"\n\t- Amount sold: "+str(asset_worth))
        
    current_trade["asset_worth"] = asset_worth
    trade_file_data["trades"].append(current_trade)
    trade_file_data["usdt_amount"] = usdt_amount
    trade_file_data["currently_holding_amount"] = asset_amount
    trade_file_data["currently_holding_boolean"] = token_currently_in_portfolio

    with open ("trades.json", "w") as outputFile:
        outputFile.write(str(trade_file_data).replace("\'","\""))

def get_ticker(ticker_string):
    try:
        ticker = client.get_symbol_ticker(symbol=ticker_string)
        return ticker
    except socket.timeout:
        print("[*] "+ticker_string+" socket timed out. skipping iteration")


def start_trading(ticker,ticker_id):
    print("[*] Trading started with the following ticker: "+ticker)
    while 1:
        if(exit_trading or (not buy_flag and token_currently_in_portfolio[ticker_id]=="False")):
            print("[*] Stopping trading with "+ticker)
            exit()
        if(continue_trading):
            get_data(ticker)
            check_rsi(ticker,ticker_id)
        sleep(10)

def log_data(string, verbosity):
    if(verbosity=="high" and verbose):
        print(string)
    elif(verbosity=="low"):
        print(string)

def reset_trades_file():
    if os.path.isdir("priceDataFiles"):
        os.system("rm -r priceDataFiles")

    trade_file = open("trades.json")
    trade_file_data = json.load(trade_file)
    trade_file_data["tickers"] = []
    trade_file_data["currently_holding_amount"] = []
    trade_file_data["currently_holding_boolean"] = []
    trade_file_data["trades"] = []

    for ticker in config.TICKERS:
        trade_file_data["tickers"].append(ticker)
        trade_file_data["currently_holding_amount"].append(0)
        trade_file_data["currently_holding_boolean"].append("False")

    with open ("trades.json", "w") as outputFile:
        outputFile.write(str(trade_file_data).replace("\'","\""))

def get_trades_data():
    global asset_amount, usdt_amount, token_currently_in_portfolio
    trade_file = open("trades.json")
    trade_file_data = json.load(trade_file)
    asset_amount = trade_file_data["currently_holding_amount"]
    usdt_amount = trade_file_data["usdt_amount"]
    token_currently_in_portfolio = trade_file_data["currently_holding_boolean"]

def create_ticker_threads():
    global threads
    for i in range(len(config.TICKERS)):
        thread = Thread(target=start_trading, args=(config.TICKERS[i],i,))
        thread.start()
        threads.append(thread)
        sleep(1)

def input_commands():
    global continue_trading, exit_trading, buy_flag
    while 1:
        command = input().upper()
        print("[*] Command Executed, please wait 45 seconds ... ")
        continue_trading = False
        sleep(45)

        if(command == "SELL_ALL"):
            choice = input("[*] Are you sure you want to sell all assets, regardless of profit or loss? [Y/N]: ")
            if(choice.upper() == "Y"):
                print("[*] Selling all assets")
                sell_all()
                exit_trading = True
                exit()
            else:
                print("[*] Continuing trading")
        elif(command == "QUIT"):
            print("[*] Quiting without selling assets. To sell all assets in portfolio, run \"python3 bot.py -s\" ")
            exit_trading = True
            exit()
        elif(command == "STOP_BUYING"):
            print("[*] No more buy orders will be executed. The program will continue to run untill all assets are sold")
            buy_flag = False
            continue_trading = True
            exit()

def get_command_line_arguments():
    cmd_parser = optparse.OptionParser()
    cmd_parser.add_option("-t", "--start-trading", action='store_true', dest='start_trading', help="Start trading with all assets given in tickers (Check config.py file)")
    cmd_parser.add_option("-v", "--verbose", action='store_true', dest='verbose', help="Prints/logs more information (Verbose output)")
    cmd_parser.add_option("-r", "--reset", action='store_true', dest='reset', help="Resets the trades.json file and sells all assets currently in portfolio. Do this before making any changes to tickers (Traded assets) in config.py file")
    cmd_parser.add_option("-s", "--sell-all", action='store_true', dest='sell_all', help="Sells all assets currently in portfolio")
    options, arguments = cmd_parser.parse_args()

    return options

def do_commands(options):
    global verbose
    get_trades_data()
    if(options.reset):
        choice = input("Are you sure you want to sell all assets currently in portfolio regardless of whether the trade is in profit/loss? (Y/N): ")
        if(choice.upper()=="Y"):
            print("\n[*] Selling all assets in portfolio")
            sell_all()
            print("[*] Reseting trades.json file")
            reset_trades_file()
        else:
            print("[*] Exiting ... ")
        exit()
    elif(options.sell_all):
        sell_all()
        exit()
    elif(options.verbose and not options.start_trading):
        print("[*] Nothing to do. Use \"-t\" to start trading: python3 bot.py -t -v")
    elif(options.verbose):
        verbose = True
    
    if(options.start_trading):
        if not os.path.isdir("priceDataFiles"):
            os.system("mkdir priceDataFiles")
        input_thread = Thread(target=input_commands)
        input_thread.start()
        create_ticker_threads()
    else:
        print("[*] Nothing to do. Use \"-t\" to start trading: python3 bot.py -t")

if __name__=="__main__":
    options = get_command_line_arguments()
    do_commands(options)
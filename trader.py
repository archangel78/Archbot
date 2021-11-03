import time
import numpy
import talib
import config
import orders
import get_data
from time import sleep
from threading import Thread

verbose = False
buy_flag = True
order_lock = False
exit_trading = False
continue_trading = True
currently_holding_qty = []
currently_holding_boolean = []

#creates input threads, initializes variables
#TODO create input threads function
def start_trading(verbose_val):
    global verbose, currently_holding_boolean, currently_holding_qty
    verbose = verbose_val
    temp_file_data = get_data.get_temp_data()
    currently_holding_qty = temp_file_data["currently_holding_qty"]
    currently_holding_boolean = temp_file_data["currently_holding_boolean"]
    # input_thread = Thread(target=input_commands)
    # input_thread.start()
    create_ticker_threads()
    
#creates one thread for each ticker to be traded with
#TODO remove threads list if unnecessary
def create_ticker_threads():
    threads = []
    for i in range(len(config.TICKERS)):
        thread = Thread(target=start_ticker_trading, args=(config.TICKERS[i],i,))
        thread.start()
        threads.append(thread)
        sleep(1)

#gets ticker closes, rsi data of each ticker and runs every 60 seconds
#TODO make it so that time waited between each iteration is based on kline time period in config file
def start_ticker_trading(ticker,ticker_id):
    print("[*] Trading started with the following ticker: "+ticker)
    ticker_closes = get_data.get_closes(ticker)
    wait_time = 59
    while 1:
        if(exit_trading or (not buy_flag and currently_holding_boolean[ticker_id]=="False")):
            print("[*] Stopping trading with "+ticker)
            exit()
        if(continue_trading):
            begin = time.time()
            ticker_closes = get_data.get_last_closes(ticker, ticker_closes)
            check_rsi(ticker,ticker_id, ticker_closes)
            end = time.time()
            wait_time = 60 - (end - begin)
            sleep(wait_time)
        else:
            sleep(1)

#Takes in closes of the asset and calculates rsi value. Places buy or sell orders if rsi in ranges based on limits mentioned in config file
#TODO: buy and sell order functions
def check_rsi(ticker,ticker_id, ticker_closes):
    global order_lock
    if not continue_trading:
        return
    closes_array = numpy.array(ticker_closes)
    rsi_indicator = talib.RSI(closes_array,config.RSI_TIMEPERIOD)
    log_data("[*] "+ticker+": ", "high")
    log_data("\t- Current RSI value: "+str(rsi_indicator[-1]),"high")

    if(rsi_indicator[-1] >= config.RSI_UPPER_POINT):
        log_data("\t- Rsi indicator indicates that "+ticker+" is in overbought region","high")
        if currently_holding_boolean[ticker_id]=="True":
            while(order_lock):
                sleep(0.1)
            order_lock = True
            print("\t- Selling existing assets of "+ticker,"high")
            order_status, qty = orders.market_sell(ticker, ticker_id)
            if(order_status):
                update_temp_data(ticker_id, qty, "False")
            else:
                print("[*] Failed to buy")
            order_lock = False
    
    elif(rsi_indicator[-1] <= config.RSI_LOWER_POINT):
        log_data("\t- Rsi indicator indicates that "+ticker+" is in oversold region","high")
        if not buy_flag:
            return
        if currently_holding_boolean[ticker_id]=="False":
            while(order_lock):
                sleep(0.1)
            order_lock = True
            print("[*] Buying assets of "+ticker)
            order_status, qty = orders.market_buy(ticker, ticker_id, currently_holding_boolean)
            if(order_status):
                update_temp_data(ticker_id, qty, "True")
            else:
                print("[*] Failed to buy")
            order_lock = False

    else:
        log_data("\t- Rsi indicator suggests that "+ticker+" is currently neutral, waiting for optimal entry/exit","high")

#updates temp_data.json after each order is executed
def update_temp_data(ticker_id, qty, holding_bool):
    global currently_holding_qty, currently_holding_boolean
    currently_holding_boolean[ticker_id] = holding_bool
    currently_holding_qty[ticker_id] = qty
    temp_file_data = get_data.get_temp_data()
    temp_file_data["currently_holding_boolean"] = currently_holding_boolean
    temp_file_data["currently_holding_qty"] = currently_holding_qty
    temp_file_data["usdt_bal"] = get_data.get_asset_balance(config.LIQUIDITY_ASSET)
    with open ("datafiles/temp_data.json", "w") as outputFile:
        outputFile.write(str(temp_file_data).replace("\'","\""))

#prints data based on verbosity
#TODO fix this
def log_data(string, verb_val):
    print(string)
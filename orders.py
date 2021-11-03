import math
import json
import config
import get_data
from binance.enums import *

def round_down(coin, number):
    info = config.binance_client.get_symbol_info(coin)
    step_size = [float(_['stepSize']) for _ in info['filters'] if _['filterType'] == 'LOT_SIZE'][0]
    step_size = '%.8f' % step_size
    step_size = step_size.rstrip('0')
    decimals = len(step_size.split('.')[1])
    return math.floor(number * 10 ** decimals) / 10 ** decimals

def market_buy(ticker_name, ticker_id, currently_holding_boolean):
    liquidity_asset_amount = get_data.get_asset_balance(config.LIQUIDITY_ASSET)
    divide_no = 0
    for i in currently_holding_boolean:
        if(i=="False"):
            divide_no = divide_no + 1
    ticker = config.binance_client.get_symbol_ticker(symbol=ticker_name)
    last_price = ticker["price"]
    qty = liquidity_asset_amount/float(last_price)
    qty = round_down(ticker_name, qty)
    order = config.binance_client.order_market_buy(
        symbol=ticker_name,
        quantity=qty)

    save_trade(ticker_name, order)
    if(order["status"]=="FILLED"):
        return True, order["executedQty"]
    return False, 0

def market_sell(ticker_name, ticker_id):
    qty = get_data.get_asset_balance(ticker_name[:-len(config.LIQUIDITY_ASSET)])
    order = config.binance_client.create_order(
        symbol=ticker_name,
        side=SIDE_SELL,
        type=ORDER_TYPE_MARKET,
        quantity=qty)

    save_trade(ticker_name, order)
    if(order["status"]=="FILLED"):
        return True, order["executedQty"]
    return False, 0

def save_trade(ticker, order):
    trade = {}
    trade["ticker"] = ticker
    trade["trade_type"] = order["side"]
    trade["fills"] = order["fills"]
    trade["qty"] = order["executedQty"]
    print("[*]"+ticker+" trade executed")
    for key in trade:
        print("\t[-] "+key+": "+str(trade[key]))
    print()
    trade_file = open("datafiles/trades.json")
    trade_file_data = json.load(trade_file)
    trade_file_data.append(trade)
    with open ("datafiles/trades.json", "w") as outputFile:
        outputFile.write(str(trade_file_data).replace("\'","\""))

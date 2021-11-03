import os
import config
import trader
import optparse
import get_data

#verifies the various settings in config.py
def verify_config():
    temp_file_data = get_data.get_temp_data()
    if temp_file_data["first_run"]=="True":
        set_initial_config()
    if config.RSI_LOWER_POINT >= config.RSI_UPPER_POINT:
        print("[x] Invalid rsi values. rsi lower point can't be higher than upper point")
        exit()

#sets current usdt balance, tickers to be traded and sets up temp_data file
def set_initial_config():
    usdt_bal = get_data.get_asset_balance(config.LIQUIDITY_ASSET)
    if(usdt_bal < len(config.TICKERS)*12):
        print("[x] Not enough "+config.LIQUIDITY_ASSET+" balance for the number of trading assets in config.py.\n[x] The current number of assets requires atleast "+str(len(config.TICKERS)*12)+" "+config.LIQUIDITY_ASSET+"\n[x] Reduce the number of tickers in config.py to reduce required balance\n[x] Terminating")
        exit()
    currently_holding_qty = []
    currently_holding_boolean = []
    for ticker in config.TICKERS:
        currently_holding_qty.append(0)
        currently_holding_boolean.append("False")
    temp_file_data = get_data.get_temp_data()
    temp_file_data["usdt_bal"] = usdt_bal
    temp_file_data["tickers"] = config.TICKERS
    temp_file_data["currently_holding_qty"] = currently_holding_qty
    temp_file_data["currently_holding_boolean"] = currently_holding_boolean
    temp_file_data["first_run"] = "False"
    with open ("datafiles/temp_data.json", "w") as outputFile:
        outputFile.write(str(temp_file_data).replace("\'","\""))

#Gets and defines command line arguments using optparse
def get_command_line_arguments():
    cmd_parser = optparse.OptionParser()
    cmd_parser.add_option("-t", "--start-trading", action='store_true', dest='start_trading', help="Start trading with all assets given in tickers (Check config.py file)")
    cmd_parser.add_option("-v", "--verbose", action='store_true', dest='verbose', help="Prints/logs more information (Verbose output)")
    cmd_parser.add_option("-r", "--reset", action='store_true', dest='reset', help="Resets the trades.json file and sells all assets currently in portfolio. Do this before making any changes to tickers (Traded assets) in config.py file")
    cmd_parser.add_option("-s", "--sell-all", action='store_true', dest='sell_all', help="Sells all assets currently in portfolio")
    options, arguments = cmd_parser.parse_args()

    return options

#executes the command line arguments, calls the appropriate functions
#TODO: Fix remaining command line arguments
def execute_commands(options):
    verbose = False
    # get_trades_data()
    # if(options.reset):
    #     choice = input("Are you sure you want to sell all assets currently in portfolio regardless of whether the trade is in profit/loss? (Y/N): ")
    #     if(choice.upper()=="Y"):
    #         print("\n[*] Selling all assets in portfolio")
    #         sell_all()
    #         print("[*] Reseting trades.json file")
    #         reset_trades_file()
    #     else:
    #         print("[*] Exiting ... ")
    #     exit()
    # elif(options.sell_all):
    #     sell_all()
    #     exit()
    if(options.verbose and not options.start_trading):
        print("[*] Nothing to do. Use \"-t\" to start trading: python3 archbot.py -t -v")
    elif(options.verbose):
        verbose = True
    
    if(options.start_trading):
        trader.start_trading(verbose)
    else:
        print("[*] Nothing to do. Use \"-t\" to start trading: python3 bot.py -t")

if __name__=="__main__":
    verify_config()
    cmd_options = get_command_line_arguments()
    execute_commands(cmd_options)
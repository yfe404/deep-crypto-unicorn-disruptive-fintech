#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# References
# https://docs.gdax.com/?python

## Include required libs
import talib, pandas
import numpy as np
import json, requests
import os, time, datetime
from coinbase import CoinbaseExchangeAuth
from simulator import Simulator

# Read secrets from env
#API_KEY = os.environ['GDAX_API_KEY']
#API_SECRET = os.environ['GDAX_API_SECRET']
#API_PASS = os.environ['GDAX_API_PASS']

# VIEW ONLY PUBLIC KEY
API_KEY = "ca554f4040cd56adb1b625d63eaab096"
API_SECRET = "kILvSj7TAsLfOHlhAo/0eoYJg7AGQ2U8RHmu4splW+Eb+Lgo20yhHPB2i4729N2zBIJiMJcXq3tXCTEICHbCyw=="
API_PASS = "v2qdfkysrdf"


#### Params
product = 'BTC-USD'
investment = 1000.0
profit = 0.0
reinvest_profit_rate=0.5



# DEBUG mode
DEBUG=True


# Helpers
def print_json(jayson):
    print(json.dumps(jayson, indent=4))


api_url = 'https://api.gdax.com/' # <----- REAL MONEY $$$
# api_url = 'https://api-public.sandbox.gdax.com/'

# Get an auth token from coinbase
auth = CoinbaseExchangeAuth(API_KEY, API_SECRET, API_PASS)

## Fetch accounts and print them
r = requests.get(api_url + 'accounts', auth=auth)
print_json(r.json())


# Flag that indicates if we have the traded asset in stock or not
IS_STOCK_FULL=False
cumulative_return = 0.0
capital_under_management = investment
stock_btc=0.0
last_capital = capital_under_management


simulator = Simulator()

while True:


    # Get historic rates
    dtime_now = datetime.datetime.utcnow()
    dtime_past = dtime_now - datetime.timedelta(minutes=5)
    
    params = {
        'start': dtime_past.isoformat(),
        'end': dtime_now.isoformat(),
        'granularity': 20,
    }
    

    r = requests.get(api_url + 'products/{}/candles'.format(product), params=params, auth=auth)
    print(params)
    #print_json(r.json())
    
    close_prices = np.array([x[4] for x in r.json()])
    if DEBUG:
        print(close_prices)
        print(close_prices.shape)
    
    ## apply strategy 
  
    upper, middle, lower = talib.BBANDS(
        close_prices,
        timeperiod=10,
        # number of non-biased standard deviations from the mean
        nbdevup=2,
        nbdevdn=2,
        # Moving average type: simple moving average here
        matype=0)
        
    # If close_prices is below the recent lower band and we have
    # no long positions then invest the entire
    # portfolio value into SPY
    
    if DEBUG:
        print "Close price: {}".format(close_prices[-1])
        print "Upper: {}".format(upper[-1])
        print "Middle: {}".format(middle[-1])
        print "Lower: {}".format(lower[-1])
        print "Stock full?: {}".format(IS_STOCK_FULL)
        print "Stock BTC: {}".format(stock_btc)

        print "Portfolio value: {}".format(capital_under_management + stock_btc * close_prices[-1])
    	print "Absolute Secured Profit: {}".format(profit)
	print "Secured Profit to Investment: {}%".format(profit/investment*100)

    if close_prices[-1] <= lower[-1] and not IS_STOCK_FULL:
        ## Buy max
        stock_btc = capital_under_management / close_prices[-1]
        capital_under_management = 0.0
        IS_STOCK_FULL = True

        simulator.buy(product, stock_btc, close_prices[-1])

        if DEBUG:
            print ">>> BUY SIGNAL"
        
            
        # If close_prices is above the recent upper band and we have
        # no short positions then invest the entire
        # portfolio value to short SPY
    elif close_prices[-1] >= upper[-1] and IS_STOCK_FULL:
	 ## short max
        capital_under_management = close_prices[-1] * stock_btc
        stock_btc = 0.0
        IS_STOCK_FULL = False

        simulator.sell(product, stock_btc, close_prices[-1])

	#Reinvest
	if ( capital_under_management-last_capital > 0.0 ):
		print "<<< $$ MADE : {}".format(capital_under_management-last_capital)
		profit += (capital_under_management-last_capital) * (1-reinvest_profit_rate)
		capital_under_management += (capital_under_management-last_capital)*reinvest_profit_rate
	 	last_capital = capital_under_management

       
        if DEBUG:
            print ">>> SELL SIGNAL"
    
    else:
        # Do Nothing
        if DEBUG:
            print "... do nothing"
        pass
            

    time.sleep(8)
    ## END LOOP ##    

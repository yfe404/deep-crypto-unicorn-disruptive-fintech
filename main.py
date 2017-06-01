#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# References
# https://docs.gdax.com/?python

# Include required libs
import os, json, requests, time, datetime, sys
import talib, pandas, numpy as np
from coinbase import CoinbaseExchangeAuth
from simulator import PortfolioSimulator
import argparse

def print_json(jayson):
    print(json.dumps(jayson, indent=4))

# Read secrets from env
#API_KEY = os.environ['GDAX_API_KEY']
#API_SECRET = os.environ['GDAX_API_SECRET']
#API_PASS = os.environ['GDAX_API_PASS']

# VIEW ONLY PUBLIC KEY
API_KEY = "ca554f4040cd56adb1b625d63eaab096"
API_SECRET = "kILvSj7TAsLfOHlhAo/0eoYJg7AGQ2U8RHmu4splW+Eb+Lgo20yhHPB2i4729N2zBIJiMJcXq3tXCTEICHbCyw=="
API_PASS = "v2qdfkysrdf"

# Params
product = 'BTC-USD'
investment = 1000.0
reinvest_rate = 0.5

# parse arguments
DEBUG = False
YOLO = False
parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", help="increase output verbosity",
                    action="store_true")
parser.add_argument("-y", "--yolo", help="output logs become crazy", action="store_true")
args = parser.parse_args()
if args.verbose:
    print "verbosity turned on"
    DEBUG = True

if args.yolo:
    print "Crazy logs turned on ! Yolo !"
    YOLO = True
    DEBUG = True
sys.stdout.flush()

api_url = 'https://api.gdax.com/' # <----- REAL MONEY $$$
# api_url = 'https://api-public.sandbox.gdax.com/'

# Get an auth token from coinbase
auth = CoinbaseExchangeAuth(API_KEY, API_SECRET, API_PASS)

# Setup simulator
simulator = PortfolioSimulator(investment, reinvest_rate)
simulator.set_balance('BTC', 0)
simulator.set_balance('USD', investment)

while True:
    did_something = False

    ## Get historic rates
    dtime_now = datetime.datetime.utcnow()
    dtime_past = dtime_now - datetime.timedelta(minutes=15)
    params = {
        'start': dtime_past.isoformat(),
        'end': dtime_now.isoformat(),
        'granularity': 60,
    }
    r = requests.get(api_url + 'products/{}/candles'.format(product), params=params, auth=auth)
    rates_sorted = sorted(r.json(), key=lambda x: x[0])
    close_prices = np.array([x[4] for x in rates_sorted])

    if YOLO:
        print(close_prices)
    
    ## Apply strategy 
    upper, middle, lower = talib.BBANDS(
        close_prices,
        timeperiod=10,
        # number of non-biased standard deviations from the mean
        nbdevup=2,
        nbdevdn=2,
        # Moving average type: simple moving average here
        matype=0)
        
    # If the last close price is under the lower band
    # and we have USD to buy BTC
    if close_prices[-1] <= lower[-1] and simulator.balance('USD') > 0:
        if DEBUG:
            print ">>> BUY SIGNAL"

        ## Buy all the BTC we can
        btc_qty = simulator.balance('USD') / close_prices[-1]
        simulator.buy(product, btc_qty, close_prices[-1])
        did_something = True

    # If close_prices is above the recent upper band and we have
    # no short positions then invest the entire
    # portfolio value to short BTC
    elif close_prices[-1] >= upper[-1] and simulator.balance('BTC') > 0:
        if DEBUG:
            print ">>> SELL SIGNAL"

        ## Sell all the BTC we have
        btc_qty = simulator.balance('BTC')
        simulator.sell(product, btc_qty, close_prices[-1])
        did_something = True

    else:
        # Do Nothing
        if YOLO:
            print "... do nothing"
        pass


    if YOLO:
        print "Last close price: {}".format(close_prices[-1])
        print "Upper / Middle / Lower bands: {} / {} / {}".format(upper[-1], middle[-1], lower[-1])
    if(DEBUG and did_something) or YOLO:
        print "BTC balance: {} BTC".format(simulator.balance('BTC'))
        print "BTC balance: {} USD (at last close price)".format(simulator.balance('BTC') * close_prices[-1])
        print "USD balance: {} USD".format(simulator.balance('USD'))
        # print "Portfolio value: {}".format(capital_under_management + stock_btc * close_prices[-1])
        print "Profit: {}".format(simulator.balance('profit'))

    sys.stdout.flush()
    time.sleep(30)
    ## END LOOP ##    

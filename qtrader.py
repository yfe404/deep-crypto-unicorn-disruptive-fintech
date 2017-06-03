#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# References
# https://docs.gdax.com/?python

# Include required libs
import os, json, requests, time, datetime, sys, argparse
import pandas as pd, numpy as np
import pickle
from lib.coinbase import CoinbaseExchangeAuth
from lib.simulator import PortfolioSimulator
from lib.historic_rates_fetchers import *
from lib.rates_helpers import *

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
parser.add_argument("--dataset", help="load historic rates from file")
args = parser.parse_args()
if args.verbose:
    print "verbosity turned on"
    DEBUG = True

if args.yolo:
    print "Crazy logs turned on ! Yolo !"
    YOLO = True
    DEBUG = True

if args.dataset:
    print('Using historic rates dataset')
    MODE = 'dataset'
else:
    print('Using live rates from API')
    MODE = 'api'

sys.stdout.flush()

api_url = 'https://api.gdax.com/' # <----- REAL MONEY $$$
# api_url = 'https://api-public.sandbox.gdax.com/'

# Setup simulator
simulator = PortfolioSimulator(investment, reinvest_rate)
simulator.set_balance('BTC', 0)
simulator.set_balance('USD', investment)

# Setup historic rate fetcher
rate_fetcher = None

if MODE == 'dataset':
    rate_fetcher = CSVHistoricRateFetcher(args.dataset)
else:
    granularity = 60
    auth = CoinbaseExchangeAuth(API_KEY, API_SECRET, API_PASS)
    rate_fetcher = APIHistoricRateFetcher(api_url, auth, product, granularity)

class Qtrader:

    def __init__(self):
        Q_pkl = open('Q_1496526999.62.pkl', 'rb')
        self.Q = pickle.load(Q_pkl)
        self.long_positions = False

    def chooseAction(self, state, action_space):
        action = action_space[np.argmax(self.Q[state])]
        if  action == "BUY":
            if self.long_positions:
                return "NOTHING"
            else:
                self.long_positions = True
                return "BUY"

        if action == "SELL":
            if self.long_positions:
                self.long_positions = False
                return "SELL"
            else:
                return "NOTHING"
        return action

qTrader = Qtrader()
action_space = ['BUY', 'SELL', 'NOTHING']

def __rsi(window, prices):
    delta = prices.diff()
    dUp, dDown = delta.copy(), delta.copy()
    dUp[dUp < 0] = 0
    dDown[dDown > 0] = 0
    RolUp = dUp.rolling(window=window, center=False).mean()
    RolDown = dDown.rolling(window=window, center=False).mean().abs()
    RS = RolUp / RolDown
    rsi = 100 - (100 / (1 + RS))
    return rsi

def __discretizer(data, steps):
    data = data.copy()
    stepsize = len(data) / steps
    data.sort()
    threshold = [0 for i in range(steps)]
    for i in range(0, steps):
        threshold[i] = data[(i+1) * stepsize -1]
    return lambda(x): np.sum([x > i for i in threshold])

while True:
    did_something = False

    ## Get historic rates
    window = 15*15*60 # 15 minutes
    rates_sorted = rate_fetcher.next(window)
    # Don't interpolate in dataset mode
    if MODE == 'api':
        rates_sorted = resample_rates(rates_sorted, granularity)
    close_prices = np.array([x[4] for x in rates_sorted])

    if YOLO:
        print(close_prices)

    if len(close_prices) < 1:
        print('No rates received... Skipping')
        if MODE is 'api':
            time.sleep(30)
        continue

    
    ## Apply strategy
    
    ### Compute state
    prices = pd.Series(close_prices)
    
    sma10 = prices.rolling(window=10, center=False).mean()
    bb_upper_10 = sma10 + 2* prices.rolling(window=10, center=False).std()
    bb_lower_10 = sma10 - 2* prices.rolling(window=10, center=False).std()
    rsi9 = __rsi(9, prices)
    
    sma10_norm = sma10 / prices -1
    bbvalue = (prices - sma10) / \
                           (2 * prices.rolling(window=10, center=False).std())
    
    d_sma10 = __discretizer(sma10.values, 10)
    d_bbvalue = __discretizer(bbvalue.values, 10)
    d_rsi9 = __discretizer(rsi9.values, 10)
    
    sma10_discrete = sma10.apply(d_sma10)
    bbvalue_discrete = bbvalue.apply(d_bbvalue)
    rsi9_discrete = rsi9.apply(d_bbvalue)
    state =  sma10_discrete.iloc[-1]*100 + \
                          bbvalue_discrete.iloc[-1]*10 + \
                          rsi9_discrete.iloc[-1]*1
    state = (1000 * 1 if qTrader.long_positions else 0) + state
    state = int(state)

    
    ### Choose action
    action = qTrader.chooseAction(state, action_space)
    
    if action == "BUY" and simulator.balance('USD') > 0:
        if DEBUG:
            print ">>> BUY SIGNAL"

        ## Buy all the BTC we can
        btc_qty = simulator.balance('USD') / close_prices[-1]
        simulator.buy(product, btc_qty, close_prices[-1])
        did_something = True

    elif action == "SELL" and simulator.balance('BTC') > 0:
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
        print "State: {}".format(state)
    if(DEBUG and did_something) or YOLO:
        print "BTC balance: {} BTC".format(simulator.balance('BTC'))
        print "BTC balance: {} USD (at last close price)".format(simulator.balance('BTC') * close_prices[-1])
        print "USD balance: {} USD".format(simulator.balance('USD'))
        # print "Portfolio value: {}".format(capital_under_management + stock_btc * close_prices[-1])
        print "Profit: {}".format(simulator.balance('profit'))

    sys.stdout.flush()

    # Don't sleep in dataset mode
    if MODE is 'api':
        time.sleep(30)

    ## END LOOP ##    

#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# References
# https://docs.gdax.com/?python

## Include required libs
import talib, pandas
import numpy as np
import json, hmac, hashlib, time, requests, base64
import os, time, datetime
from requests.auth import AuthBase

# Read secrets from env
#API_KEY = os.environ['GDAX_API_KEY']
#API_SECRET = os.environ['GDAX_API_SECRET']
#API_PASS = os.environ['GDAX_API_PASS']

# YOLO Hardcode sandbox credentials
#API_KEY = "eedbdb921b0ea5425cc575cec4f6d295"
#API_SECRET = "ARZD+5zandRAB27tO/j/KGTWthxDR1m/aXdKtzsZ4C9CWvVVf5R6vPP5d//Dk7INDjmaVI6w61Z6p//tXl94vg=="
#API_PASS = "ax55rmwaafl"

# VIEW ONLY PUBLIC KEY
API_KEY = "ca554f4040cd56adb1b625d63eaab096"
API_SECRET = "kILvSj7TAsLfOHlhAo/0eoYJg7AGQ2U8RHmu4splW+Eb+Lgo20yhHPB2i4729N2zBIJiMJcXq3tXCTEICHbCyw=="
API_PASS = "v2qdfkysrdf"

# DEBUG mode
DEBUG=True


## auth
# Create custom authentication for Exchange
class CoinbaseExchangeAuth(AuthBase):
    def __init__(self, api_key, secret_key, passphrase):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase

    def __call__(self, request):
        timestamp = str(time.time())
        message = timestamp + request.method + request.path_url + (request.body or '')
        hmac_key = base64.b64decode(self.secret_key)
        signature = hmac.new(hmac_key, message, hashlib.sha256)
        signature_b64 = signature.digest().encode('base64').rstrip('\n')

        request.headers.update({
            'CB-ACCESS-SIGN': signature_b64,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        })
        return request

# I want you to deal with your problems by becoming rich!

def print_json(jayson):
    print(json.dumps(jayson, indent=4))

api_url = 'https://api.gdax.com/' # <----- REAL MONEY $$$
# api_url = 'https://api-public.sandbox.gdax.com/'
auth = CoinbaseExchangeAuth(API_KEY, API_SECRET, API_PASS)

## fetch hist data
r = requests.get(api_url + 'accounts', auth=auth)
print_json(r.json())

# Sell 0.01 BTC for 20 USD
#order = {
#    'size': 0.01,
#    'price': 20.0,
#    'side': 'sell',
#    'product_id': 'BTC-USD',
#}
#r = requests.post(api_url + 'orders', json=order, auth=auth)
#print_json(r.json())

# Buy 0.01 BTC for 20 USD
# Doesn't work -> stay in pending ?
#order = {
#    'size': 0.01,
#    'price': 20.0,
#    'side': 'buy',
#    'product_id': 'BTC-USD',
#}
#r = requests.post(api_url + 'orders', json=order, auth=auth)
#print_json(r.json())
#
## But 0.01 BTC at market price
#order = {
#    'type': 'market',
#    'size': 0.01,
#    'side': 'buy',
#    'product_id': 'BTC-USD',
#}
#r = requests.post(api_url + 'orders', json=order, auth=auth)
#print_json(r.json())

# Flag that indicates if we have the traded asset in stock or not
IS_STOCK_FULL=False
cumulative_return = 0.0
capital_under_management = 1000.0
stock_btc=0.0

while True:

    
    # Get historic rates
    dtime_now = datetime.datetime.utcnow()
    dtime_past = dtime_now - datetime.timedelta(minutes=5)
    
    params = {
        'start': dtime_past.isoformat(),
        'end': dtime_now.isoformat(),
        'granularity': 20,
    }
    
    product = 'BTC-USD'
    r = requests.get(api_url + 'products/{}/candles'.format(product), params=params, auth=auth)
    print(params)
    #print_json(r.json())
    
    close_prices = np.array([x[4] for x in r.json()])
    if DEBUG:
        print(close_prices)
        print(close_prices.shape)
    
    ## apply strategy 
    
    
    
    #
    #def handle_data(context, data):
    #    todays_date = get_datetime().date()
    #    
    #    # Do nothing unless the date has changed
    #    if todays_date == context.date:
    #        return
    #    # Set the new date
    #    context.date = todays_date
    #
    #    current_position = context.portfolio.positions[context.stock].amount
    #
        ## START LOOP ##
    
            
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
        print "Capital: {}".format(capital_under_management)
        print "Portfolio value: {}".format(capital_under_management + stock_btc * close_prices[-1])
    
    
    if close_prices[-1] <= lower[-1] and not IS_STOCK_FULL:
        ## Buy max
        stock_btc = 1000.0 / close_prices[-1]
        capital_under_management = capital_under_management -1000.0
        IS_STOCK_FULL = True
#        cumulative_return 
        if DEBUG:
            print ">>> BUY SIGNAL"
        
            
        # If close_prices is above the recent upper band and we have
        # no short positions then invest the entire
        # portfolio value to short SPY
    elif close_prices[-1] >= upper[-1] and IS_STOCK_FULL:
        capital_under_management = capital_under_management + close_prices[-1] * stock_btc
        stock_btc = 0.0
        IS_STOCK_FULL = False

        ## short max
        if DEBUG:
            print ">>> SELL SIGNAL"
    
    else:
        # Do Nothing
        if DEBUG:
            print "... do nothing"
        pass
            

    time.sleep(8)
    ## END LOOP ##    

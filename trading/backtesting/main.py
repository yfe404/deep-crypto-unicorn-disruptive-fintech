from exchange import Exchange
from coinbase import CoinbaseExchangeAuth
from trader import Trader
from strategy import RaptorStrategy

import datetime as dt
import logging
from coinbase import CoinbaseExchangeAuth
import os
import pandas as pd


logging.basicConfig(level=logging.DEBUG)

# Sandbox API keys
SBOX_API_KEY = '889eac5ee10ffe31417e5c3728a1d46a'
SBOX_API_SECRET = 'CKzRGCr9nzbBe2awSF9xfqyF5ysFBsJiESmTeFvzpbx6dpIZaAl+TvJYaBEvCmloHMqqdwHaoQcCNrMoCzwx6Q=='
SBOX_API_PASS = '6y54dvm18pk'


# Instantiate strategy
#strategy = RaptorStrategy()

# Instantiate bot
#granularity = 3200
#n_samples = 50

#bot = RaptorBot('BTC', 'EUR', granularity, n_samples)
#bot.set_rates_api_client(prod_client)
#bot.set_order_api_client(prod_client)
#bot.set_strategy(strategy)

# Test bot
# bot.__update_historic_rates__()
# bot.__update_positions__()
# print(bot.state)
#bot.run(30)

CURRENCY_PAIR='BTC-EUR'
START_TIME=dt.datetime(2017, 5, 23)
END_TIME=dt.datetime.today()
GRANULARITY=60*60*6  #  in seconds
NB_SAMPLES = 5

def test_run():
    exchange = Exchange(CoinbaseExchangeAuth(SBOX_API_KEY, SBOX_API_SECRET, SBOX_API_PASS), 'https://api.gdax.com')
    exchange.fetch_historical_data(CURRENCY_PAIR, START_TIME, END_TIME, GRANULARITY)
    exchange.money_money_money('EUR', 1000)
    #print (exchange.list_accounts())
    #print(exchange.get_historic_rates(START_TIME, START_TIME + 2*dt.timedelta(seconds=GRANULARITY)))
    #print (exchange.data)
    #print(exchange.get_account('EUR').get('available'))
    print (len(exchange.data))
    
    # Instantiate strategy
    strategy = RaptorStrategy()

    
    # Instantiate bot

    bot = Trader('BTC', 'EUR', GRANULARITY, NB_SAMPLES, START_TIME, END_TIME)
    bot.set_rates_api_client(exchange)
    bot.set_order_api_client(exchange)
    bot.set_strategy(strategy)

    bot.run(0)


    

if __name__ == "__main__":
    test_run()

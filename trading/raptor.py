# -*- coding: utf-8 -*-
import datetime as dt
import logging
from bots import RaptorBot
from clients import GDAXAPIClient
from coinbase import CoinbaseExchangeAuth
from strategy import RaptorStrategy

logging.basicConfig(level=logging.DEBUG)

# Prod API keys

# Sandbox API keys
SBOX_API_KEY = '4e45cabd25f7036f569b646707d6712f'
SBOX_API_SECRET = 'T5arAaJeZDx932tMoXDoxD5hx1H5xw9F1H7g7Q+96gLpbI7laqiHefLpho11VA8N/iraQI3NeWq43L8726nRMg=='
SBOX_API_PASS = 'hppy4e6dnwn'

sandbox_client = GDAXAPIClient(CoinbaseExchangeAuth(SBOX_API_KEY, SBOX_API_SECRET, SBOX_API_PASS), 'https://api-public.sandbox.gdax.com')
prod_client = GDAXAPIClient(CoinbaseExchangeAuth(PROD_API_KEY, PROD_API_SECRET, PROD_API_PASS), 'https://api.gdax.com')

# Instantiate strategy
strategy = RaptorStrategy()

# Instantiate bot
granularity = 3600
n_samples = 50

bot = RaptorBot('BTC', 'EUR', granularity, n_samples)
bot.set_rates_api_client(prod_client)
bot.set_order_api_client(prod_client)
bot.set_strategy(strategy)

# Test bot
# bot.__update_historic_rates__()
# bot.__update_positions__()
# print(bot.state)
bot.run(30)

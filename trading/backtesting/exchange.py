# -*- coding: utf-8 -*-
import requests
import logging
import json
import pandas as pd


class Exchange():
    def __init__(self, auth, api_url):
        self.auth = auth
        self.api_url = api_url
        self.data = None
        

    def __request__(self, method, path, params, data, default):
        j = None
        if data is not None:
            j = json.dumps(data)

        try:
            r = requests.request(
                method,
                self.api_url + path,
                params=params,
                data=j,
                auth=self.auth,
            )

            if r.status_code == 200:
                return r.json()
            else:
                logging.error('Non-200 status code from API: {} / {}'.format(r.status_code, r.content))
                return default

        except requests.exceptions.RequestException as e:
            logging.error('RequestException: {}'.format(e))
            return default

    def __get__(self, path, params=None, default=None):
        return self.__request__('GET', path, params, None, default)

    def __post__(self, path, params=None, data=None, default=None):
        return self.__request__('POST', path, params, data, default)

    # Market Data

    def fetch_historical_data(self, currency_pair, start_time, end_time, granularity):
        # Creates accounts according to currency pair
        self.accounts = dict()
        for currency in currency_pair.split('-'):
            self.accounts[currency] = {'currency': currency, 'available': 0.0}


        # Fetch data using API

        logging.info('Fetching historic rates for {} from {} to {} ({}s)'.format(currency_pair, start_time, end_time, granularity))
        # Check if more than 200 points

        params = {
            'start': start_time.isoformat(),
            'end': end_time.isoformat(),
            'granularity': granularity
        }

        data = self.__get__('/products/{}/candles'.format(currency_pair), params=params, default=[])
        candles = sorted(data, key=lambda x: x[0])

        if len(candles) > 1:
            self.data = pd.DataFrame(data=candles, columns=['time', 'low', 'high', 'open', 'close', 'volume']).set_index('time')
        else:
            ## todo: raise exception
            pass

    
    def get_historic_rates(self, start_time, end_time):
        start_time_as_timestamp = int(start_time.strftime("%s")) 
        end_time_as_timestamp = int(end_time.strftime("%s"))
        interv = (self.data.index >= start_time_as_timestamp) & (self.data.index <= end_time_as_timestamp)

        return self.data[interv]

    # Orders

    def place_market_order(self, currency_pair, side, amount, price):

        currency1, currency2 = currency_pair.split('-')

        if side == 'buy':
            self.accounts[currency1]['available'] += float(amount) / float(price)
            self.accounts[currency2]['available'] -= amount
        elif side == 'sell':
            self.accounts[currency1]['available'] -= amount
            self.accounts[currency2]['available'] += amount * price
        

    def place_limit_order(self, product_id, side, price, size):
        # TODO: Truncate decimals
        data = {
            'type': 'limit',
            'product_id': product_id,
            'side': side,
            'price': price,
            'size': size
        }

        logging.info('Placing limit order: {}'.format(data))
        data = self.__post__('/orders', data=data, default={})
        return data

    # Accounts

    def list_accounts(self):
        return self.accounts


    def get_account(self, currency):
        accounts = self.list_accounts()
        account = {}
        for k,v in accounts.iteritems():
            if k == currency:
                account = v
                break
        return account

    def money_money_money(self, currency, amount):
        if currency in self.accounts:
            self.accounts[currency]['available'] += amount




# -*- coding: utf-8 -*-
import requests
import logging
import json

class ExchangeAPIClient:
    None

class GDAXAPIClient(ExchangeAPIClient):

    def __init__(self, auth, api_url):
        self.auth = auth
        self.api_url = api_url

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

    def get_historic_rates(self, product_id, start_time, end_time, granularity):
        logging.info('Fetching historic rates for {} from {} to {} ({}s)'.format(product_id, start_time, end_time, granularity))
        # Check if more than 200 points

        params = {
            'start': start_time.isoformat(),
            'end': end_time.isoformat(),
            'granularity': granularity
        }

        data = self.__get__('/products/{}/candles'.format(product_id), params=params, default=[])
        rates = sorted(data, key=lambda x: x[0])

        # TODO: Truncate or warn
        return rates

    # Orders

    def place_market_order(self, product_id, side, funds=0, size=0):
        data = {
            'type': 'market',
            'product_id': product_id,
            'side': side
        }

        if funds != 0:
            data['funds'] = funds
        
        if size != 0:
            data['size'] = size

        logging.info('Placing market order: {}'.format(data))
        data = self.__post__('/orders', data=data, default={})
        return data

    def place_limit_order(self, product_id, side, price, size):
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
        data = self.__get__('/accounts', default=[])
        return data

    def get_account(self, currency):
        accounts = self.list_accounts()
        account = {}
        for obj in accounts:
            if obj['currency'] == currency:
                account = obj
                break
        return account






# -*- coding: utf-8 -*-
import time
import logging
import datetime as dt
import pandas as pd


class Trader():
    def __init__(self, crypto_currency, fiat_currency, granularity, n_samples, start_time, end_time):
        self.crypto_currency = crypto_currency
        self.fiat_currency = fiat_currency
        self.product = '{}-{}'.format(crypto_currency, fiat_currency)
        self.granularity = granularity
        self.n_samples = n_samples
        self.start_time = start_time
        self.end_time = end_time
        self.state = {}
        self.state['long'] = False
        self.state['data'] = pd.DataFrame(columns=['time', 'low', 'high', 'open', 'close', 'volume']).set_index('time')

    def set_strategy(self, strategy):
        self.strategy = strategy

    def set_rates_api_client(self, api_client):
        self.rates_api_client = api_client

    def set_order_api_client(self, api_client):
        self.order_api_client = api_client

    def run(self, sleep_time):
        window = self.granularity * self.n_samples
        nb_iterations = (int(self.end_time.strftime("%s")) - int(self.start_time.strftime("%s"))) / window 
        for iteration in range(1, nb_iterations): 
            self.__update_historic_rates__(iteration)
#            logging.debug(self.state)

            action = self.strategy.apply(self.state)
            self.__handle_action__(action)

    def __handle_action__(self, action):
        logging.info('Handling action {}'.format(action))

        if action == 'buy':
            # Buy everything
            fiat_available = self.order_api_client.get_account(self.fiat_currency).get('available')
            if fiat_available and float(fiat_available) > 0.0:
                self.order_api_client.place_market_order(self.product, 'buy', float(fiat_available), self.state['data'].iloc[-1]['close'])
            elif fiat_available and float(fiat_available) <= 0.0:
                logging.warning('Failed to place order, no funds')
            else:
                logging.error('Failed to place order, cannot get current balance')
            self.__update_positions__()
                        

        elif action == 'sell':
            # Sell everything
            crypto_available = self.order_api_client.get_account(self.crypto_currency).get('available')
            if crypto_available and float(crypto_available) > 0.0:
                self.order_api_client.place_market_order(self.product, 'sell', float(crypto_available), self.state['data'].iloc[-1]['close'])
            elif crypto_available and float(crypto_available) <= 0.0:
                logging.warning('Failed to place order, no funds')
            else:
                logging.error('Failed to place order, cannot get current balance')

            self.__update_positions__()
                        
        elif action == 'nothing':
            pass

        else:
            logging.warning('Unknown action: {}'.format(action))

    def __update_historic_rates__(self, iteration):
        window = self.granularity * self.n_samples
        start_time = self.start_time + iteration * dt.timedelta(seconds=window)
        end_time = start_time + dt.timedelta(seconds=window)

        rates = self.rates_api_client.get_historic_rates(start_time, end_time)

        if len(rates) > 1:
            self.state['data'] = rates

        else:
            logging.warn('Failed to update rates, got empty response (less than 2 rates)')

    def __update_positions__(self):
        accounts = self.order_api_client.list_accounts()
        crypto_account = accounts[self.crypto_currency]
        available = crypto_account.get('available')
        print (accounts)
        if available != None and float(available) > 0.01:
            self.state['long'] = True
        elif available != None and float(available) <= 0.01:
            self.state['long'] = False
        else:
            logging.warn('Failed to update long positions')


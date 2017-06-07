# -*- coding: utf-8 -*-
import time
import logging
import datetime as dt
import pandas as pd

class TradingBot:
    
    def run(self, sleep_time):
        raise NotImplementedError()

class RaptorBot(TradingBot):

    def __init__(self, crypto_currency, fiat_currency, granularity, n_samples):
        self.crypto_currency = crypto_currency
        self.fiat_currency = fiat_currency
        self.product = '{}-{}'.format(crypto_currency, fiat_currency)
        self.granularity = granularity
        self.n_samples = n_samples
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
        while True:
            self.__update_historic_rates__()
            self.__update_positions__()
            logging.debug(self.state)

            action = self.strategy.apply(self.state)
            self.__handle_action__(action)

            # TODO: Sleep less because of requests time ?
            time.sleep(sleep_time)

    def __handle_action__(self, action):
        logging.info('Handling action {}'.format(action))

        if action == 'buy':
            # Buy everything
            fiat_available = self.order_api_client.get_account(self.fiat_currency).get('available')
            if fiat_available and float(fiat_available) > 0.0:
                self.order_api_client.place_market_order(self.product, 'buy', funds=float(fiat_available))
            elif fiat_available and float(fiat_available) <= 0.0:
                logging.warning('Failed to place order, no funds')
            else:
                logging.error('Failed to place order, cannot get current balance')

        elif action == 'sell':
            # Sell everything
            crypto_available = self.order_api_client.get_account(self.crypto_currency).get('available')
            if crypto_available and float(crypto_available) > 0.0:
                self.order_api_client.place_market_order(self.product, 'sell', size=float(crypto_available))
            elif crypto_available and float(crypto_available) <= 0.0:
                logging.warning('Failed to place order, no funds')
            else:
                logging.error('Failed to place order, cannot get current balance')

        elif action == 'nothing':
            pass

        else:
            logging.warning('Unknown action: {}'.format(action))

    def __update_historic_rates__(self):
        window = self.granularity * self.n_samples
        end_time = dt.datetime.utcnow()
        start_time = end_time - dt.timedelta(seconds=window)
        rates = self.rates_api_client.get_historic_rates(self.product, start_time, end_time, self.granularity)

        if len(rates) > 1:
            df = pd.DataFrame(data=rates, columns=['time', 'low', 'high', 'open', 'close', 'volume']).set_index('time')

            # Drop last row if incomplete
            print(df.index.values[-1])
            print(df.index.values[-2])
            # if (df.index.values[-1] - df.index.values[-2]) < self.granularity:
            df = df.drop(df.index[-1])
            self.state['data'] = df

        else:
            logging.warn('Failed to update rates, got empty response (less than 2 rates)')

    def __update_positions__(self):
        crypto_account = self.order_api_client.get_account(self.crypto_currency)
        available = crypto_account.get('available')
        if available and float(available) > 0.01:
            self.state['long'] = True
        elif available and float(available) <= 0.01:
            self.state['long'] = False
        else:
            logging.warn('Failed to update long positions')


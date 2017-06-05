# -*- coding: utf-8 -*-

class PortfolioSimulator:

    def __init__(self, fees_percent=0.0):
        self.balances = {}
        self.fees_ratio = fees_percent / 100.0
        self.__log('Initializing with {}% fees'.format(fees_percent))

    def buy(self, product, quantity, price):
        if quantity < 0.0 or price < 0.0:
            self.__log('Cannot buy negative amounts')
            return

        # Ex: BTC-USD
        # cur1 = BTC, cur2 = USD
        currency1, currency2 = product.split('-')

        # Ex: Buy 0.5 BTC at 1000 USD
        # amount = 500 (USD)
        amount = quantity * price

        # Ex: 1% fees
        # fees = 5 (USD)
        fees = amount * self.fees_ratio

        # Ex: 1% fees (5 USD), BTC price is 1000 USD
        # fees_cur1 = 0.005 (BTC)
        fees_cur1 = float(fees) / float(price)

        # Credit BTC account, minus the fees
        diff_cur1 = quantity - fees_cur1
        self.__update_balance(currency1, diff_cur1)

        # Debit USD account
        diff_cur2 = -amount
        self.__update_balance(currency2, diff_cur2)

        self.__log('Buying {} {} at {} {} each. Fees = {} {} ({} {})'.format(quantity, currency1, price, currency2, fees, currency2, fees_cur1, currency1))
        self.__log('{} {} / +{} {}'.format(diff_cur2, currency2, diff_cur1, currency1))
        self.__log_balance(currency1)
        self.__log_balance(currency2)

    def sell(self, product, quantity, price):
        if quantity < 0.0 or price < 0.0:
            self.__log('Cannot sell negative amounts')
            return

        # Ex: BTC-USD
        # cur1 = BTC, cur2 = USD
        currency1, currency2 = product.split('-')

        # Ex: Sell 0.5 BTC at 1000 USD
        # amount = 500 (USD)
        amount = quantity * price

        # Debit BTC account
        self.__update_balance(currency1, -quantity)

        # Credit USD account
        self.__update_balance(currency2, amount)

        self.__log('Selling {} {} at {} {} each'.format(quantity, currency1, price, currency2))
        self.__log('{} {} / +{} {}'.format(-quantity, currency1, amount, currency2))
        self.__log_balance(currency1)
        self.__log_balance(currency2)

    def get_balance(self, currency):
        return self.balances.get(currency, 0)

    def set_balance(self, currency, value):
        self.balances[currency] = value

    def __update_balance(self, currency, diff):
        current = self.balances.get(currency, 0)
        self.balances[currency] = current + diff

    def __log_balance(self, currency):
        self.__log('{} balance = {} {}'.format(currency, self.balances.get(currency, 0), currency))

    def __log(self, msg):
        print('[PortfolioSimulator] {}'.format(msg))


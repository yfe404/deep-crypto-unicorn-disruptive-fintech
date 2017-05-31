# -*- coding: utf-8 -*-

class Simulator:
    FEES_RATIO = (0.25/100) # 0.25% fees

    def __init__(self):
        self.balances = {}

    def buy(self, product, quantity, price):
        currency1, currency2 = product.split('-')

        amount = quantity * price
        fees = amount * self.FEES_RATIO

        self.__update_balance(currency1, quantity)
        self.__update_balance(currency2, -(amount+fees))

        print('[Simulator] Buying {} {} at {} {} each').format(quantity, currency1, price, currency2)
        print('[Simulator] Total price = {} {} + {} {} (fees)').format(amount, currency2, fees, currency2)
        self.__print_balance(currency1)
        self.__print_balance(currency2)

    def sell(self, product, quantity, price):
        currency1, currency2 = product.split('-')

        amount = quantity * price
        fees = amount * self.FEES_RATIO

        self.__update_balance(currency1, -quantity)
        self.__update_balance(currency2, +(amount-fees))

        print('[Simulator] Selling {} {} at {} {} each').format(quantity, currency1, price, currency2)
        print('[Simulator] Total earnings = {} {} - {} {} (fees)').format(amount, currency2, fees, currency2)
        self.__print_balance(currency1)
        self.__print_balance(currency2)

    def balance(self, currency):
        return self.balances.get(currency, 0)

    def __update_balance(self, currency, diff):
        current = self.balances.get(currency, 0)
        self.balances[currency] = current + diff

    def __print_balance(self, currency):
        print('[Simulator] {} balance = {} {}').format(currency, self.balances.get(currency, 0), currency)

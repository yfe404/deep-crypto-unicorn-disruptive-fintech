# -*- coding: utf-8 -*-

class PortfolioSimulator:
    FEES_RATIO = (0.25/100) # 0.25% fees

    def __init__(self, investment, reinvest):
        self.balances = {}
        self.balances["profit"] = 0
        self.previous_sell_result = investment
        self.reinvest_percentage = reinvest

    def buy(self, product, quantity, price):
        currency1, currency2 = product.split('-')

        amount = quantity * price
        fees = amount * self.FEES_RATIO
        fees_cur1 = fees / price

        self.__update_balance(currency1, quantity-fees_cur1)
        self.__update_balance(currency2, -amount)

        print('[Simulator] Buying {} {} at {} {} each').format(quantity, currency1, price, currency2)
        print('[Simulator] Fees = {} {} ({} {})').format(fees, currency2, fees_cur1, currency1)
        self.__print_balance(currency1)
        self.__print_balance(currency2)

    def sell(self, product, quantity, price):
        currency1, currency2 = product.split('-')

        amount = quantity * price

        self.__update_balance(currency1, -quantity)
        self.__update_balance(currency2, amount)

        #update profit & reinvest some
        profit = amount - previous_sell_result
        if (profit > 0.0):
            self.__update_balance(currency2, profit * self.reinvest_percentage ) 
            self.__update_balance("profit", profit * (1-self.reinvest_percentage))
        previous_sell_result = amount

        print('[Simulator] Selling {} {} at {} {} each').format(quantity, currency1, price, currency2)
        print('[Simulator] Total earnings = {} {}').format(amount, currency2)
        self.__print_balance(currency1)
        self.__print_balance(currency2)

    def balance(self, currency):
        return self.balances.get(currency, 0)

    def set_balance(self, currency, value):
        self.balances[currency] = value

    def __update_balance(self, currency, diff):
        current = self.balances.get(currency, 0)
        self.balances[currency] = current + diff

    def __print_balance(self, currency):
        print('[Simulator] {} balance = {} {}').format(currency, self.balances.get(currency, 0), currency)


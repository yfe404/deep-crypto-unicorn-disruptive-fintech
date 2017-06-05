# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 ft=python

import unittest, sys, os

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from lib.simulator import PortfolioSimulator

class PortfolioSimulatorTestCase(unittest.TestCase):
    def setUp(self):
        self.portfolio = PortfolioSimulator()
        self.portfolio.set_balance('BTC', 0)
        self.portfolio.set_balance('USD', 1000)

    def test_buy_negative(self):
        btc_balance_before = self.portfolio.get_balance('BTC')
        usd_balance_before = self.portfolio.get_balance('USD')
        
        self.portfolio.buy('BTC-USD', 0.2, -1000)
        self.portfolio.buy('BTC-USD', -0.7, 1000)
        
        btc_balance_after = self.portfolio.get_balance('BTC')
        usd_balance_after = self.portfolio.get_balance('USD')
        
        self.assertEqual(btc_balance_before, btc_balance_after)
        self.assertEqual(usd_balance_before, usd_balance_after)

    def test_sell_negative(self):
        btc_balance_before = self.portfolio.get_balance('BTC')
        usd_balance_before = self.portfolio.get_balance('USD')
        
        self.portfolio.sell('BTC-USD', 0.2, -1000)
        self.portfolio.sell('BTC-USD', -0.7, 1000)
        
        btc_balance_after = self.portfolio.get_balance('BTC')
        usd_balance_after = self.portfolio.get_balance('USD')
        
        self.assertEqual(btc_balance_before, btc_balance_after)
        self.assertEqual(usd_balance_before, usd_balance_after)

    def test_buy(self):
        btc_balance_before = self.portfolio.get_balance('BTC')
        usd_balance_before = self.portfolio.get_balance('USD')

        self.portfolio.buy('BTC-USD', 0.2, 1000)

        btc_balance_after = self.portfolio.get_balance('BTC')
        usd_balance_after = self.portfolio.get_balance('USD')

        self.assertEqual(btc_balance_before + 0.2, btc_balance_after)
        self.assertEqual(usd_balance_before - 200, usd_balance_after)
 
    def test_sell(self):
        btc_balance_before = self.portfolio.get_balance('BTC')
        usd_balance_before = self.portfolio.get_balance('USD')

        self.portfolio.sell('BTC-USD', 0.2, 1000)

        btc_balance_after = self.portfolio.get_balance('BTC')
        usd_balance_after = self.portfolio.get_balance('USD')

        self.assertEqual(btc_balance_before - 0.2, btc_balance_after)
        self.assertEqual(usd_balance_before + 200, usd_balance_after)
        
    def test_buy_with_fees(self):
        self.portfolio = PortfolioSimulator(fees_percent=0.25)
        self.portfolio.set_balance('BTC', 0)
        self.portfolio.set_balance('USD', 1000)

        btc_balance_before = self.portfolio.get_balance('BTC')
        usd_balance_before = self.portfolio.get_balance('USD')

        self.portfolio.buy('BTC-USD', 0.2, 1000)

        btc_balance_after = self.portfolio.get_balance('BTC')
        usd_balance_after = self.portfolio.get_balance('USD')

        expected_fees = (0.25/100.0) * 0.2

        self.assertEqual(btc_balance_before + (0.2 - expected_fees), btc_balance_after)
        self.assertEqual(usd_balance_before - 200, usd_balance_after)

if __name__ == '__main__':
    unittest.main()

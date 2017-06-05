#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import print_function
import os, json, requests, time, datetime, sys, argparse
import talib, pandas, numpy as np
from lib.historic_rates_fetchers import *

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

parser = argparse.ArgumentParser()
parser.add_argument("-y", "--yolo", help="output logs become crazy", action="store_true")
parser.add_argument("dataset", metavar='DATASET', help="load historic rates from file")
parser.add_argument("granularity", metavar='GRANULARITY', type=int, help="interval between candlesticks")
parser.add_argument("periods", metavar='PERIODS', type=int, help="number of periods on which to compute the BB at each iterations (10 is a good value)")
args = parser.parse_args()

rate_fetcher = CSVHistoricRateFetcher(args.dataset)
result = []

while rate_fetcher.has_next():
    # Get historic rates
    window = args.periods*args.granularity
    rates_sorted = rate_fetcher.next(window)

    close_prices = np.array([x[4] for x in rates_sorted])
    close_timestamp = rates_sorted[-1][0]

    if args.yolo:
        eprint(close_prices)

    # Compute Bollinger Bands
    upper, middle, lower = talib.BBANDS(
        close_prices,
        timeperiod=args.periods,
        # number of non-biased standard deviations from the mean
        nbdevup=2,
        nbdevdn=2,
        # Moving average type: simple moving average here
        matype=0)
 
    action = 'NOTHING'

    # If the last close price is under the lower band
    if close_prices[-1] <= lower[-1]:
        action = 'BUY'

    # If close_prices is above the recent upper band
    elif close_prices[-1] >= upper[-1]:
        action = 'SELL'

    eprint('{} >>> {}'.format(close_timestamp, action))
    result.append([close_timestamp, action])

with open('bb_out.csv', 'w') as f:
    f.write('time,action\n')
    for row in result:
        f.write('{},{}\n'.format(row[0], row[1]))

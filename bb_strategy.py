#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import print_function
import os, json, requests, time, datetime, sys, argparse
import talib, pandas, numpy as np
from lib.simulator import PortfolioSimulator
from lib.historic_rates_fetchers import *
from lib.rates_helpers import *

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

# parse arguments
YOLO = False

parser = argparse.ArgumentParser()
parser.add_argument("-y", "--yolo", help="output logs become crazy", action="store_true")
parser.add_argument("dataset", metavar='DATASET', help="load historic rates from file")
args = parser.parse_args()

if args.yolo:
    eprint("Crazy logs turned on ! Yolo !")
    YOLO = True

sys.stdout.flush()

# TODO: Ensure input dataset is clean (no missing data points)
rate_fetcher = CSVHistoricRateFetcher(args.dataset)

result = []
while True:
    # Get historic rates
    #window = 15*15*60 # 15 points of 15 minutes "candles"
    window = 15*60 # 15 points of 1 minutes "candles"
    rates_sorted = rate_fetcher.next(window)

    close_prices = np.array([x[4] for x in rates_sorted])

    if len(rates_sorted) < 1:
        break

    close_timestamp = rates_sorted[-1][0]

    eprint(close_timestamp)

    if YOLO:
        eprint(close_prices)

    # Compute Bollinger Bands
    upper, middle, lower = talib.BBANDS(
        close_prices,
        timeperiod=10,
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

    if YOLO:
        eprint('>>> {}'.format(action))

    result.append([close_timestamp, action])
    sys.stdout.flush()

with open('bb_out.csv', 'w') as f:
    f.write('time,action\n')
    for row in result:
        f.write('{},{}\n'.format(row[0], row[1]))

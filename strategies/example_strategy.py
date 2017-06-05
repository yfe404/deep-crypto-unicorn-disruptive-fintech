#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 ft=python

import os, json, requests, time, datetime, sys, argparse
import talib
import numpy as np
import pandas as pd

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from lib.historic_rates_fetchers import *

parser = argparse.ArgumentParser()

# Generic arguments
parser.add_argument('-v', '--verbose', help='output logs become crazy', action='store_true')
parser.add_argument('dataset', metavar='DATASET', help='load historic rates from file')

# Strategy-specific arguments
# parser.add_argument('granularity', metavar='GRANULARITY', type=int, help='interval between candlesticks')
# parser.add_argument('periods', metavar='PERIODS', type=int, help='number of periods on which to compute the BB at each iterations (10 is a good value)')

args = parser.parse_args()

rate_fetcher = CSVHistoricRateFetcher(args.dataset)
result = []

while rate_fetcher.has_next():
    # Fetch rates for the last XXX seconds
    # Rates are sorted chronologically: [0] is the most ancient, [-1] the most recent
    window = 3600
    rates_sorted = rate_fetcher.next(window)
    last_timestamp = rates_sorted[0][-1]

    if args.verbose:
        print(rates_sorted)

    # Do something and set action to
    # BUY, SELL, NOTHING
    action = 'NOTHING'

    print('{} >>> {}'.format(last_timestamp, action))
    result.append([last_timestamp, action])

with open('MY_STRATEGY.csv', 'w') as f:
    f.write('time,action\n')
    for row in result:
        f.write('{},{}\n'.format(row[0], row[1]))


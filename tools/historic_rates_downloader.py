#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import print_function
import os, sys, json, requests
from datetime import datetime, timedelta
from coinbase import CoinbaseExchangeAuth
from rates_helpers import resample_rates

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

API_URL = 'https://api.gdax.com/'

API_KEY = os.environ['GDAX_API_KEY']
API_SECRET = os.environ['GDAX_API_SECRET']
API_PASS = os.environ['GDAX_API_PASS']

if len(sys.argv) is not 5:
    eprint('Usage: {} START_DATE END_DATE GRANULARITY PRODUCT'.format(sys.argv[0]))
    eprint('Example: {} 2017-01-01T06:00:00 2017-01-31T23:00:00 30 BTC-USD'.format(sys.argv[0]))
    eprint('Date is an ISO8601 string and granularity is in seconds.')
    exit(1)

start_date = datetime.strptime(sys.argv[1],'%Y-%m-%dT%H:%M:%S')
end_date = datetime.strptime(sys.argv[2],'%Y-%m-%dT%H:%M:%S')
granularity = int(sys.argv[3])
product = sys.argv[4]

eprint('Downloading historic rates between {} and {} with granularity of {} seconds'.format(start_date, end_date, granularity))

auth = CoinbaseExchangeAuth(API_KEY, API_SECRET, API_PASS)
result = []

# NOTE: API limit is 200 data points per request
delta = timedelta(seconds=200*granularity)
current_date = start_date
while current_date < end_date:
    intermediate_date = current_date + delta
    eprint('Downloading rates between {} and {} ...'.format(current_date, intermediate_date))

    try:
        params = {'start': current_date.isoformat(), 'end': intermediate_date.isoformat(), 'granularity': granularity}
        r = requests.get(API_URL + 'products/{}/candles'.format(product), params=params, auth=auth)
        if r.status_code == 200:
            result.extend(r.json())
    except requests.exceptions.RequestException as e:
        eprint('Exception: {}'.format(e))

    current_date = intermediate_date

# Sort by date
result_sorted = sorted(result, key=lambda x: x[0])

# Interpolate missing points
result_sorted = resample_rates(result_sorted, granularity)

# Output CSV
print('time,low,high,open,close,volume')
for rates in result_sorted:
    # OPTIMIZE
    timestamp = int((rates[0].to_pydatetime() - datetime(1970,1,1)).total_seconds())
    print('{},{},{},{},{},{}'.format(timestamp, rates[1], rates[2], rates[3], rates[4], rates[5]))


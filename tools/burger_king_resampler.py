#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import pandas as pd
import argparse
from datetime import datetime


parser = argparse.ArgumentParser()
parser = argparse.ArgumentParser(description='Fill missing datapoints in the given dataset')
parser.add_argument('data_set', metavar='STOCK', help='path to the stock rates dataset')
parser.add_argument('granularity', metavar='GRANULARITY', help='Data set granularity in seconds')
args = parser.parse_args()

data = pd.read_csv(args.data_set)
data['time'] = pd.to_datetime(data['time'], unit='s', origin='unix')
data = data.set_index('time')

# Resample and fill missing values
data_resampled = data.resample(str(args.granularity) + 'S').bfill().ffill()

# Restore timestamp
data_resampled = data_resampled.reset_index()
data_resampled['time'] = data_resampled['time'].apply(lambda x: int((x.to_pydatetime() - datetime(1970,1,1)).total_seconds()))
data_resampled = data_resampled.set_index('time')

data_resampled.to_csv('{}_resampled.csv'.format(args.data_set))

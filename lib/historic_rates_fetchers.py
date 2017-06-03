from __future__ import division
import csv, math, time, datetime, requests

# Granularity and Window parameters are in seconds

class APIHistoricRateFetcher:

    def __init__(self, api_url, auth, product, granularity):
        self.api_url = api_url
        self.auth = auth
        self.product = product
        self.granularity = granularity

    def next(self, window):
        requested_points = math.ceil(window / self.granularity)
        if requested_points > 200:
            print('[APIHistoricRateFetcher] WARN: Requesting more than 200 data points. API request will likely fail.')

        dtime_now = datetime.datetime.utcnow()
        dtime_past = dtime_now - datetime.timedelta(seconds=window)

        params = {
            'start': dtime_past.isoformat(),
            'end': dtime_now.isoformat(),
            'granularity': self.granularity,
        }

        rates = []

        try:
            r = requests.get(self.api_url + 'products/{}/candles'.format(self.product), params=params, auth=self.auth)
        except requests.exceptions.RequestException as e:
            print('[APIHistoricRateFetcher] RequestException: {}'.format(e))

        if r.status_code != 200:
            print('[APIHistoricRateFetcher] ERROR: Non-200 status code from API: {} / {}'.format(r.content))
            return []

        rates = sorted(r.json(), key=lambda x: x[0])

        if len(rates) < requested_points:
            print('[APIHistoricRateFetcher] WARN: API returned less points than expected.')
        elif len(rates) > requested_points:
            print('[APIHistoricRateFetcher] WARN: API returned more points than expected. Output will be truncated to requested window.')
            # TODO: Cleanup
            timestamp_start = (dtime_past - datetime.datetime(1970,1,1)).total_seconds()
            timestamp_end = (dtime_now - datetime.datetime(1970,1,1)).total_seconds()
            rates = [x for x in rates if x[0] >= timestamp_start and x[0] <= timestamp_end]

        return rates


class CSVHistoricRateFetcher:

    def __init__(self, path):
        with open(path, 'rb') as csvfile:
            # Skip first line
            # TODO: Check if has header
            next(csvfile, None)
            print('Loading rates from {}...'.format(path))
            reader = csv.reader(csvfile, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
            table = list(reader)
            print('Sorting rates...')
            self.table = sorted(table, key=lambda x: x[0])
            self.table_len = len(table)

        self.cur = 0

    # Pay attention to CSV granularity...
    def next(self, window):
        if self.cur >= self.table_len - 1:
            return []

        result = []
        tmp_cur = self.cur
        start_timestamp = self.table[tmp_cur][0]
        cur_timestamp = self.table[tmp_cur][0]

        while cur_timestamp < (start_timestamp + window) and tmp_cur < self.table_len - 1:
            result.append(self.table[tmp_cur])
            tmp_cur += 1
            cur_timestamp = self.table[tmp_cur][0]
        
        self.cur += 1

        return result

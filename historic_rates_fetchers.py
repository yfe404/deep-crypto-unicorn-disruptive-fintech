import csv, datetime, requests


class APIHistoricRateFetcher:

    # Granularity in seconds
    def __init__(self, api_url, auth, product, granularity):
        self.api_url = api_url
        self.auth = auth
        self.product = product
        self.granularity = granularity

    # Window in seconds
    def next(self, window):
        dtime_now = datetime.datetime.utcnow()
        dtime_past = dtime_now - datetime.timedelta(seconds=window)

        params = {
            'start': dtime_past.isoformat(),
            'end': dtime_now.isoformat(),
            'granularity': self.granularity,
        }
        r = requests.get(self.api_url + 'products/{}/candles'.format(self.product), params=params, auth=self.auth)
        return sorted(r.json(), key=lambda x: x[0])


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

    # Window in seconds (pay attention to CSV granularity...)
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

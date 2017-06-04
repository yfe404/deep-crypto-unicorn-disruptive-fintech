import pandas as pd
import datetime

# NOTE: Assume rates are sorted
def resample_rates(rates, granularity):
    df = pd.DataFrame(rates)
    df[0] = pd.to_datetime(df[0], unit='s', origin='unix')
    df = df.set_index(0)

    df_resampled = df.resample(str(granularity) + 'S')#.interpolate(method='time')
    df_resampled = df.fillna(method='ffill', inplace='TRUE')
    df_resampled = df.fillna(method='backfill', inplace='TRUE')
    return df_resampled.reset_index().values

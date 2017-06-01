"""Utility functions"""

import os
import pandas as pd
import matplotlib.pyplot as plt 

def symbol_to_path(symbol, base_dir="data"):
    """Return CSV file path given ticker symbol"""
    return os.path.join(base_dir, "{}.csv".format(str(symbol)))


def get_data(syms, dates, drop_ref=False):
    """Read stock data (adjusted close) for given symbols from CSV files."""
    df = pd.DataFrame(index=dates)
    # Make a copy of syms input argument to prevent modifying it
    symbols = [s for s in syms]
    if 'SPY' not in symbols: # add SPY for reference, if absent
        symbols.insert(0, 'SPY')

    for symbol in symbols:
        # Read and join data for each symbol
        dfTemp = pd.read_csv(symbol_to_path(symbol, "../data"), index_col = 'Date', parse_dates=True, usecols = ["Date", "Adj Close"], na_values=['nan'])

        # Rename 'Adj Close' to prevent clash
        dfTemp = dfTemp.rename(columns={'Adj Close':symbol})
        # Join the two dataframes using DataFrame.join()
        df = df.join(dfTemp)
        if symbol == "SPY": # Drop dates SPY did not trade
            df = df.dropna(subset=['SPY'])

    # drop SPY column if specified
    if drop_ref : 
        del df['SPY']
            
    return df



def plot_data(df, title="Stock prices", ylabel="Price"):
    """Plot stock prices"""
    ax = df.plot(title=title)
    ax.set_xlabel("Date")
    ax.set_ylabel(ylabel)
    plt.show() # Must be called to show plots in some environments

def plot_selected(df, columns, start, end) :
    """Plot selected data"""
    plot_data(df.ix[start:end, columns])

def normalize_data(df):
    """Normalize stock prices using the first row of the dataframe 'df'"""
    return df / df.ix[0,:]

def fill_missing_values(df):
    """Fill any gaps in the data, in place"""
    df.fillna(method='ffill', inplace='TRUE')
    return df.fillna(method='backfill', inplace='TRUE')

def compute_daily_returns(df):
    """Compute and return the daily return values."""
    daily_returns = df.copy() # copy given DataFrame to match size and columns
    # compute daily returns for row 1 onwards
    daily_returns[1:] = (df[1:] / df[:-1].values)-1
    daily_returns.ix[0, :] = 0 # set daily returns for row 0 to 0
    return daily_returns

def compute_cumulative_returns(df):
    """Compute and return the cumulative return"""
    cumulative_returns = df.copy() # copy given DataFrame to match size and columns
    # compute cumulative returns for row 1 onwards
    cumulative_returns = ( df / df.ix[0,:] )-1
    return cumulative_returns

def get_rolling_mean(serie, window):
    """Return rolling mean of given values, using specified window size."""
    return pd.rolling_mean(serie, window)

def get_rolling_std(serie, window):
    """Return rolling standard deviation of given values, using specified window size."""
    return pd.rolling_std(serie, window)

def get_bollinger_bands(rm, rstd):
    """ Return upper and lower Bollinger Bands."""
    upper_band = rm + rstd * 2
    lower_band = rm - rstd * 2
    return upper_band, lower_band


def test_run():
    # Define a date range
    dates = pd.date_range("2012-12-21", "2013-12-21")

    # Choose stock symbols to read
    symbols = ["GOOG", "IBM", "GLD", "XOM"] # SPY will be added in get_data()

    # Get stock data
    df = get_data(symbols, dates)
    print df
    plot_data(normalize_data(df))



** Global statistics 

#+BEGIN_SRC python :results output

import utils as utl
import pandas as pd

def test_run():
    # Read data 
    dates = pd.date_range('2010-01-01', '2012-12-31')
    symbols = ["SPY", "IBM", "GOOG", "GLD"]
    df = utl.get_data(symbols, dates)
    utl.plot_data(df)

    # Compute global statistics for each stock
    print df.mean()


if __name__ == "__main__":
    test_run()

#+END_SRC

#+RESULTS:
: SPY     112.771641
: IBM     144.180436
: GOOG    290.865224
: GLD     145.029775
: dtype: float64

** Rolling statistics

#+BEGIN_SRC python :results output

import utils as utl
import matplotlib.pyplot as plt
import pandas as pd

def test_run():
    # Read data 
    dates = pd.date_range('2010-01-01', '2012-12-31')
    symbols = ["SPY"]
    df = utl.get_data(symbols, dates)
    
    # Plot SPY data, retain matplotlib axis object
    ax = df['SPY'].plot(title="SPY rolling mean", label='SPY')

    # Compute rolling mean using a 20-day window
    rm_SPY = pd.rolling_mean(df['SPY'], 20)
    
    # Add rolling mean to same plot
    rm_SPY.plot(label='Rolling mean', ax=ax)
    
    # Add axis labels and legend
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend(loc="upper left")

    plt.show()


if __name__ == "__main__":
    test_run()

#+END_SRC

#+RESULTS:

** Computing Bollinger Bands

#+BEGIN_SRC python :results output

import utils as utl
import pandas as pd
import matplotlib.pyplot as plt


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
    # Read data
    dates = pd.date_range('2012-01-01', '2012-12-31')
    symbols = ['SPY']
    df = utl.get_data(symbols, dates)

    # Compute Bollinger Bands
    # 1. Computer rolling mean
    rm_SPY = get_rolling_mean(df['SPY'], window=20)

    # 2. Compute rolling standard deviation
    rstd_SPY = get_rolling_std(df['SPY'], window=20)

    # 3. Compute upper and lower bands
    upper_band, lower_band = get_bollinger_bands(rm_SPY, rstd_SPY)


    # Plot raw SPY values, rolling mean and Bollinger Bands
    ax = df['SPY'].plot(title="Bollinger Bands", label='SPY')
    rm_SPY.plot(label="Rolling mean", ax=ax)
    upper_band.plot(label='upper band', ax=ax)
    lower_band.plot(label='lower band', ax=ax)

    # Add axis labels and legend
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend(loc='upper left')
    plt.show()
    
if __name__ == "__main__":
    test_run()

#+END_SRC

#+RESULTS:

** Daily returns

#+BEGIN_SRC python :results output 

import utils as utl
import pandas as pd 

def compute_daily_returns(df):
    """Compute and return the daily return values."""
    daily_returns = df.copy() # copy given DataFrame to match size and columns
    # compute daily returns for row 1 onwards
    daily_returns[1:] = (df[1:] / df[:-1].values)-1
    daily_returns.ix[0, :] = 0 # set daily returns for row 0 to 0
    return daily_returns


def test_run():
    # Read data
    dates = pd.date_range('2012-01-01', '2012-02-01') 
    symbols = ['SPY', 'GOOG']
    df = utl.get_data(symbols, dates)
    utl.plot_data(df)

    # Compute daily returns
    daily_returns = compute_daily_returns(df)
    utl.plot_data(daily_returns, title="Daily returns")

if __name__ == "__main__":
    test_run()

#+END_SRC

#+RESULTS:

** Cumulative returns

#+BEGIN_SRC python :results output 

import pandas as pd
import utils as utl

def compute_cumulative_returns(df):
    """Compute and return the cumulative return"""
    cumulative_returns = df.copy() # copy given DataFrame to match size and columns
    # compute cumulative returns for row 1 onwards
    cumulative_returns = ( df / df.ix[0,:] )-1
    return cumulative_returns


def test_run():
    # Read data
    dates = pd.date_range('2012-01-01', '2013-02-01') 
    symbols = ['SPY', 'GOOG']
    df = utl.get_data(symbols, dates)
    utl.plot_data(df)
   
    # Compute cumulative returns
    cumulative_returns = compute_cumulative_returns(df)
    utl.plot_data(cumulative_returns, title="Cumulative returns")

if __name__ == "__main__":
    test_run()


#+END_SRC

#+RESULTS:

** Global statistics 

#+BEGIN_SRC python :results output

import utils as utl
import pandas as pd

def test_run():
    # Read data 
    dates = pd.date_range('2010-01-01', '2012-12-31')
    symbols = ["SPY", "IBM", "GOOG", "GLD"]
    df = utl.get_data(symbols, dates)
    utl.plot_data(df)

    # Compute global statistics for each stock
    print df.mean()


if __name__ == "__main__":
    test_run()

#+END_SRC

#+RESULTS:
: SPY     112.771641
: IBM     144.180436
: GOOG    290.865224
: GLD     145.029775
: dtype: float64

** Rolling statistics

#+BEGIN_SRC python :results output

import utils as utl
import matplotlib.pyplot as plt
import pandas as pd

def test_run():
    # Read data 
    dates = pd.date_range('2010-01-01', '2012-12-31')
    symbols = ["SPY"]
    df = utl.get_data(symbols, dates)
    
    # Plot SPY data, retain matplotlib axis object
    ax = df['SPY'].plot(title="SPY rolling mean", label='SPY')

    # Compute rolling mean using a 20-day window
    rm_SPY = pd.rolling_mean(df['SPY'], 20)
    
    # Add rolling mean to same plot
    rm_SPY.plot(label='Rolling mean', ax=ax)
    
    # Add axis labels and legend
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend(loc="upper left")

    plt.show()


if __name__ == "__main__":
    test_run()

#+END_SRC

#+RESULTS:

** Computing Bollinger Bands

#+BEGIN_SRC python :results output

import utils as utl
import pandas as pd
import matplotlib.pyplot as plt


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
    # Read data
    dates = pd.date_range('2012-01-01', '2012-12-31')
    symbols = ['SPY']
    df = utl.get_data(symbols, dates)

    # Compute Bollinger Bands
    # 1. Computer rolling mean
    rm_SPY = get_rolling_mean(df['SPY'], window=20)

    # 2. Compute rolling standard deviation
    rstd_SPY = get_rolling_std(df['SPY'], window=20)

    # 3. Compute upper and lower bands
    upper_band, lower_band = get_bollinger_bands(rm_SPY, rstd_SPY)


    # Plot raw SPY values, rolling mean and Bollinger Bands
    ax = df['SPY'].plot(title="Bollinger Bands", label='SPY')
    rm_SPY.plot(label="Rolling mean", ax=ax)
    upper_band.plot(label='upper band', ax=ax)
    lower_band.plot(label='lower band', ax=ax)

    # Add axis labels and legend
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend(loc='upper left')
    plt.show()
    
if __name__ == "__main__":
    test_run()

#+END_SRC

#+RESULTS:

** Daily returns

#+BEGIN_SRC python :results output 

import utils as utl
import pandas as pd 

def compute_daily_returns(df):
    """Compute and return the daily return values."""
    daily_returns = df.copy() # copy given DataFrame to match size and columns
    # compute daily returns for row 1 onwards
    daily_returns[1:] = (df[1:] / df[:-1].values)-1
    daily_returns.ix[0, :] = 0 # set daily returns for row 0 to 0
    return daily_returns


def test_run():
    # Read data
    dates = pd.date_range('2012-01-01', '2012-02-01') 
    symbols = ['SPY', 'GOOG']
    df = utl.get_data(symbols, dates)
    utl.plot_data(df)

    # Compute daily returns
    daily_returns = compute_daily_returns(df)
    utl.plot_data(daily_returns, title="Daily returns")

if __name__ == "__main__":
    test_run()

#+END_SRC

#+RESULTS:

** Cumulative returns

#+BEGIN_SRC python :results output 

import pandas as pd
import utils as utl

def compute_cumulative_returns(df):
    """Compute and return the cumulative return"""
    cumulative_returns = df.copy() # copy given DataFrame to match size and columns
    # compute cumulative returns for row 1 onwards
    cumulative_returns = ( df / df.ix[0,:] )-1
    return cumulative_returns


def test_run():
    # Read data
    dates = pd.date_range('2012-01-01', '2013-02-01') 
    symbols = ['SPY', 'GOOG']
    df = utl.get_data(symbols, dates)
    utl.plot_data(df)
   
    # Compute cumulative returns
    cumulative_returns = compute_cumulative_returns(df)
    utl.plot_data(cumulative_returns, title="Cumulative returns")

if __name__ == "__main__":
    test_run()


#+END_SRC

#+RESULTS:



# load training data 
    df = pd.read_csv("../data/appl.csv")

# append states info aka features 
""" 
Features
adjusted cose / SMA
BB value
holding stock 
return since entry (percentage)
"""

# normalize / discretize features 

"""
stepsize = size(data) / steps
data.sort()
for i in range (0, steps) 
    threshold[i] = data[(i + 1) * stepsize]
"""

# builds a utility table as the agent interacts w/ the world
print np.random.normal(size=(5,4)) 
""" 
Select training data 
iterate vertme <s,a,r,s'>
- set starttime, init Q w/ random
- select a 
- observe r,s'
- update Q
test policy pi (apply it to get the state for the next val
repeat until converge 

Update Q using Bellman equation
gamma : discount rate 
alpha: learning rate
Q'[s,a] = (1 - alpha) * Q[s,a] + alpha*(r+gamma*Q[s', argmaxa'(Q[s',a']))

""" 
""" 
success depends on exploration 
choose a random action w/ proba c typically 0.3 at the beg of learning
diminish overtime to 0
""" 



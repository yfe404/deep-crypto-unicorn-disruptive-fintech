import util as utl
import pandas as pd
import numpy as np

DEBUG=True

def log(message):
    if DEBUG:
        print message

def test_run():
    # load training data 
    log("Loading Data")
    df = pd.read_csv("/home/unicorn/work/datasets/rates_2017_january_may_1min.csv")
    log("########## Training set head ##########")
    log(df.head(5))

    log("Cleaning Data - Removing unused columns.....")
    # Removing unused columns 
    for colname in ["low", "high", "open", "volume"]:
        df.drop(colname, axis=1, inplace=True)
    log("########## Training set head ##########")
    log(df.head(5))
    

    # append states info aka features 
    log("Building World OKLM #God #Jesus #7daysIsForLosers.....")
    log("Adding SMA 25, 50, 75, 100")
    log("Adding Bollinger Bands 25, 50, 75, 100")
    for window in range(25, 101, 25):
        rm = utl.get_rolling_mean(df.close, window)
        rstd = utl.get_rolling_std(df.close, window)
        upper_band, lower_band = utl.get_bollinger_bands(rm, rstd)
        df["s_sma{}".format(window)] = rm 
        df["s_bb{}_lower".format(window)] = lower_band 
        df["s_bb{}_upper".format(window)] = upper_band 
    log("########## Training set tail ##########")
    log(df.tail(5))


    log("Adding holding stock feature")
    df['holding_stock'] = 0


    log("Adding returns")
#    @todo: change function name as it is not use in the context of inter day trading 
    # compute daily returns for row 1 onwards
    df['returns'] = df['close']
    df.loc[1:, 'returns'] = (df.loc[1:, 'close'] / df['close'][:-1].values)-1

    df.loc[0, 'returns'] = 0 # set daily returns for row 0 to 0
    log("########## Training set head ##########")
    log(df.head(5))

    log("########## Training set tail ##########")
    log(df.tail(5))

    # normalize / discretize features 
#    log("# normalize / discretize features ")
#    columns_to_norm = [col for col in df.columns if col not in ['time', 'holding_stock', 'returns']]
#    df_norm = (df[columns_to_norm] - df[columns_to_norm].mean()) / (df[columns_to_norm].max() - df[columns_to_norm].min())
    
    log("Setting start time")
    start_time = df.loc[0, 'time']
    log("start time = {}".format(start_time))
    
    log("Init Q w/ random values")
    Q = np.random.normal(size=(10,3))  ## 3 actions * 10 states (just to try, there will be much more")
    log("Q matrix = {}".format(Q))




if __name__ == "__main__":
    test_run()
    


""" 
Features
adjusted cose / SMA
BB value
holding stock 
return since entry (percentage) -- Not yet
"""

# normalize / discretize features 

"""
stepsize = size(data) / steps
data.sort()
for i in range (0, steps) 
    threshold[i] = data[(i + 1) * stepsize]
"""

# builds a utility table as the agent interacts w/ the world
###print np.random.normal(size=(5,4)) 
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



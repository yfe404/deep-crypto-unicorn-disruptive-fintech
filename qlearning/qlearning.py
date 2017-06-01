import util as utl
import pandas as pd
import numpy as np
import math

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
    
    ACTIONS = ['BUY', 'SELL', 'NOTHING']
    STATES = [0, 1, 2, 3, 4, 5]
    ## STATES : 
    ### 0: close price < lower band 25 && and not holding position 
    ### 1: close price < lower band 25 && and holding position 
    ### 2: close price > lower band 25 and close price < upper band 25 && and not holding position 
    ### 3: close price > lower band 25 and close price < upper band 25 && and holding position 
    ### 4: close price > upper band 25 && and not holding position 
    ### 5: close price > upper band 25 && and holding position 

    
    log("Setting start time")
    start_idx = 23
    log("start index = {}".format(start_idx))
    
    log("Init Q w/ random values")
    Q = np.random.normal(size=(5,3))  ## 3 actions * 5 states (just to try, there will be much more")
    log("Q matrix = {}".format(Q))

    for cursor in range (start_idx, start_idx+3):

        timestamp = df.loc[cursor, 'time']
        bb25_lower = df.loc[cursor, 's_bb25_lower']
        bb25_upper = df.loc[cursor, 's_bb25_upper']
        close_price = df.loc[cursor, 'close']
        holding_position = df.loc[cursor, 'holding_stock'] == 1

        state = compute_state(bb25_lower, bb25_upper, close_price, holding_position)

        log("$$$$$$$$$ Iteration {}: $$$$$$$$$".format(cursor-start_idx))
        log("1 - Reading state")
        log("Timestamp: {}".format(timestamp))
        log("BB25 lower: {}".format(bb25_lower))
        log("close price: {}".format(close_price))
        log("BB25 upper: {}".format(bb25_upper))
        log("Is holding position: {}".format(holding_position))
        log("Corresponding state is : {}".format(state))
        
        log("2 - Select an action")
        action = chooseAction(Q,state)
        log("Action chosen is {}".format(action))
        
        log("3 - Observing reward and next state")
        log("TODO")

        log("4 - update Q")
        #gamma : discount rate 
        #alpha: learning rate
        #Q'[s,a] = (1 - alpha) * Q[s,a] + alpha*(r+gamma*Q[s', argmaxa'(Q[s',a']))
        
        learning_rate = 0.3
        discount_rate = 0.3
        reward = 1.0 # constant to test
        next_state = 1 # constant to test

        a = np.argmax(Q[state])
        Q[state, a] = \
            (1 - learning_rate) * \
            Q[state, a] + \
            learning_rate * (reward + discount_rate * Q[next_state, np.argmax(Q[next_state])])

        log("Q matrix = {}".format(Q))
        
def chooseAction(Q, state):
    ACTIONS = ['BUY', 'SELL', 'NOTHING']
    return ACTIONS[np.argmax(Q[state])]


def applyAction(current):
    ## La flemme je sais meme pas ce que je vais mettre en prototype
    ## J'ai mis current au pif, j'aurais aussi bien pu mettre diplodocus
    pass



def compute_state(bb25_lower, bb25_upper, close_price, holding_position):
    if math.isnan(bb25_lower) or math.isnan(bb25_upper):
        return 3 if holding_position else 2

    isAbove = close_price > bb25_upper
    isBelow = close_price < bb25_lower
    isBetween = close_price <= bb25_upper and close_price >= bb25_lower

    if isBetween:
        return 3 if holding_position else 2
    if isBelow:
        return 1 if holding_position else 0
    if isAbove:
        return 5 if holding_position else 4


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



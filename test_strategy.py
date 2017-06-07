from strategy import RaptorStrategy

import pandas as pd
import numpy as np



class State:
    def __init__(self, data, long=False):
        self.data = data.copy()
        self.long = long

def test_run():

    data = pd.read_csv("apr_7200.csv")
    long = False
    state = State(data, long)
    strategy = RaptorStrategy()
    start_time = 0
    window = 45
    
    for i in range(start_time, len(data)):
        _slice = data.loc[start_time+i:window+i,:]

        state.data = _slice
        order = strategy.apply(state)
        if order == "BUY":
            state.long = True
        if order == "SELL":
            state.long = False

        if order != "NOTHING":
            print data.iloc[i].time
            print data.iloc[i].close
            print(order)

if __name__ == "__main__":
    test_run()

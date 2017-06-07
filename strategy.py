import pandas as pd 

class TradingStrategy:
    def apply(self, state):
        print 'Please implement me'


class RaptorStrategy(TradingStrategy):
    def apply(self, state):


        EMAs = [5, 10, 15, 20, 25, 30, 35, 40, 45]
        ema_labels = ['ema{}'.format(ema) for ema in EMAs]

        # Ignore the last since it obviously crosses with itself anytime
        crossover_flags = [0 for _ in EMAs[:-1]] 
        action = "NOTHING"
        
        if not state:
            return action

        data = state.data.copy()
        

        ## Add Exponential Moving Averages to state
        for ema in EMAs:
            data['ema{}'.format(ema)] = data['close'].ewm(span=ema).mean()

        ## Check for a signal
        for j in range(len(ema_labels[:-1])): 
            if data.iloc[-1][ema_labels[j]] - data.iloc[-1][ema_labels[-1]] >= 0:
                crossover_flags[j] = 1
            else:
                crossover_flags[j] = 0

        if state.long and sum(crossover_flags) == 0:
            #print 'Sell signal generated at {} when price was {}'.format(int(.data.iloc[i].time), .data.iloc[i].close)
            action = "SELL"
        elif not state.long and sum(crossover_flags) == len(crossover_flags):
            #print 'Buy signal generated at {} when price was {}'.format(int(.data.iloc[i].time), .data.iloc[i].close)
            action = "BUY"

        return action
        

import pandas as pd 

class TradingStrategy:
    def apply(self, state):
        print 'Please implement me'


######################################################################################################


#  ____             _                   _             _                   
# |  _ \ __ _ _ __ | |_ ___  _ __   ___| |_ _ __ __ _| |_ ___  __ _ _   _ 
# | |_) / _` | '_ \| __/ _ \| '__| / __| __| '__/ _` | __/ _ \/ _` | | | |
# |  _ < (_| | |_) | || (_) | |    \__ \ |_| | | (_| | ||  __/ (_| | |_| |
# |_| \_\__,_| .__/ \__\___/|_|    |___/\__|_|  \__,_|\__\___|\__, |\__, |
#            |_|                                              |___/ |___/ 
#
# Trade the Raptor way
# 
###
# Basic strategy implementing Moving Average Ribbon <see https://tinyurl.com/y93tdw9w>
######################################################################################################
#                                                   .--.__
#                                                 .~ (@)  ~~~---_                  |   ,-,__,
#                                                {     `-_~,,,,,,)                 |  { / /__\
#                                                {    (_  ',                       | { `}'- -/
#                                                 ~    . = _',                     | {_}/\ o/
#                                                  ~-   '.  =-'                    |   __}  {__
#                                                    ~     :                       | /     "   \
# .                                             _,.-~     ('');                    |/ /| 0}  0} \        
# '.                                         .-~        \  \ ;                     / / \`~' `"/\ \
#   ':-_                                _.--~            \  \;      _-=,.         { :   }    {  : }
#     ~-:-.__                       _.-~                 {  '---- _'-=,.           \ \  }  . { / /
#        ~-._~--._             __.-~                     ~---------=,.`            |\ \/      \ /
#            ~~-._~~-----~~~~~~       .+++~~~~~~~~-__   /                          | j{   \ /  }t
#                 ~-.,____           {   -     +   }  _/                           |  {    Y   }
#                         ~~-.______{_    _ -=\ / /_.~                             |   \    \ /
#                              :      ~--~    // /         ..-                     |    \    V
#                              :   / /      // /         ((                        |     `,   \
#                              :  / /      {   `-------,. ))                       |      {`   }
#                              :   /        ''=--------. }o                        |_____ {'  /______
#                 .=._________,'  )                     ))                                ;  /
#                 )  _________ -''                     ~~                                ;  /
#                / /  _ _                                                               ,  ,
#               (_.-.'O'-'.                                                             (, k
#                                                                                        \,,,
######################################################################################################
class RaptorStrategy(TradingStrategy):
    def apply(self, state):


        EMAs = [2, 3, 4]
        ema_labels = ['ema{}'.format(ema) for ema in EMAs]

        # Ignore the last since it obviously crosses with itself anytime
        crossover_flags = [0 for _ in EMAs[:-1]] 
        action = "nothing"
        
        if not state:
            return action

        data = state["data"].copy()
        

        ## Add Exponential Moving Averages to state
        for ema in EMAs:
            data['ema{}'.format(ema)] = data['close'].ewm(span=ema).mean()

        ## Check for a signal
        for j in range(len(ema_labels[:-1])): 
            if data.iloc[-1][ema_labels[j]] - data.iloc[-1][ema_labels[-1]] >= 0:
                crossover_flags[j] = 1
            else:
                crossover_flags[j] = 0

        if state["long"] and sum(crossover_flags) == 0:
            #print 'Sell signal generated at {} when price was {}'.format(int(.data.iloc[i].time), .data.iloc[i].close)
            action = "sell"
        elif not state["long"] and sum(crossover_flags) == len(crossover_flags):
            #print 'Buy signal generated at {} when price was {}'.format(int(.data.iloc[i].time), .data.iloc[i].close)
            action = "buy"

        return action
        

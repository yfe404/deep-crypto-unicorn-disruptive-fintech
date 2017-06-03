#!/usr/bin/env python2
# -*- coding: utf-8 -*-


import util as utl
import pandas as pd
import numpy as np
import math
import talib

DEBUG=True



class Environment:
    def __init__(self):

        # Load CSV
        self.data = pd.read_csv("/home/unicorn/work/datasets/rates_2017_january_may_1min.csv")

        ## Changing default index to timestamps
        self.data.index = self.data['time']
        self.data = self.data.drop('time', axis=1)

        ## Compute and normalize indicators
        self.data['sma5'] = self.data['close']. \
                            rolling(window=5, center=False).mean()
        self.data['sma10'] = self.data['close']. \
                             rolling(window=10, center=False).mean()
        self.data['bb_upper_10'] = self.data['sma10'] + \
                                   2* self.data['close'].rolling(window=10, center=False).std()
        self.data['bb_lower_10'] = self.data['sma10'] - \
                                   2* self.data['close'].rolling(window=10, center=False).std()
        self.data['rsi9'] = self.__rsi(9, self.data['close'])
        self.data['rsi14'] = self.__rsi(14, self.data['close'])

        self.data['sma5_norm'] = self.data['sma5'] / self.data['close'] -1
        self.data['sma10_norm'] = self.data['sma10'] / self.data['close'] -1
        self.data['bbvalue'] = (self.data['close'] - self.data['sma10']) / \
                               (2 * self.data['close'].rolling(window=10, center=False).std())

        ## Compute all rewards
        self.data['reward'] = self.__daily_returns(self.data['close'])


        ## Build disretizers
        d_sma5 = self.__discretizer(self.data['sma5'].values, 10)
        d_sma10 = self.__discretizer(self.data['sma10'].values, 10)
        d_bbvalue = self.__discretizer(self.data['bbvalue'].values, 10)
        d_rsi9 = self.__discretizer(self.data['rsi9'].values, 10)
        d_rsi14 = self.__discretizer(self.data['rsi14'].values, 10)
        




        self.state_idx = 0
        self.long_positions = False
        self.close_prices = self.data['close'].values
        self.action_space = ['BUY', 'SELL', 'NOTHING']

        self.upper_band_5, \
        self.sma_5, \
        self.lower_band_5 = talib.BBANDS(
            self.close_prices,
            timeperiod=5,
            # number of non-biased standard deviations from the mean
            nbdevup=2,
            nbdevdn=2,
            # Moving average type: simple moving average here
            matype=0)

        self.returns = np.zeros(len(self.data))
        self.returns[1:] = (self.close_prices[1:] / self.close_prices[:-1])-1


    def reset(self):
        self.state_idx = 0
        self.long_positions = 0


    def step(self, action):
        self.state_idx = self.state_idx + 1

        observation = None
        reward = 0
        done = self.state_idx >= len(self.data)
        info = None

        if not done:
            if action == "BUY" and not self.long_positions:
                self.long_positions = True
            elif action == "SELL" and self.long_positions:
                self.long_positions = False

            if self.long_positions:
                reward = self.returns[self.state_idx]

            observation = self.__compute_state()
            
        return observation, reward, done, info



    def __rsi(self, window, prices):
        delta = prices.diff()
        dUp, dDown = delta.copy(), delta.copy()
        dUp[dUp < 0] = 0
        dDown[dDown > 0] = 0
        RolUp = dUp.rolling(window=window, center=False).mean()
        RolDown = dDown.rolling(window=window, center=False).mean().abs()
        RS = RolUp / RolDown
        rsi = 100 - (100 / (1 + RS))
        return rsi

    def __daily_returns(self, prices):
        """Compute and return the daily return values."""
        daily_returns = prices.copy() # copy given Serie to match size 
        # compute daily returns for row 1 onwards
        daily_returns[1:] = (prices[1:] / prices[:-1].values)-1
        daily_returns.iloc[0] = 0 # set daily returns for row 0 to 0
        return daily_returns

    def __discretizer(self, data, steps):
        data = data.copy()
        stepsize = len(data) / steps
        data.sort()
        threshold = [0 for i in range(steps)]
        for i in range(0, steps):
            threshold[i] = data[(i+1) * stepsize -1]
        return lambda(x): np.sum([x > i for i in threshold])



 
    def __compute_state(self):
        if math.isnan(self.upper_band_5[self.state_idx]) \
           or math.isnan(self.lower_band_5[self.state_idx]):
            return 3 if self.long_positions else 2

        isAbove = self.close_prices[self.state_idx] > self.upper_band_5[self.state_idx]
        isBelow = self.close_prices[self.state_idx] < self.lower_band_5[self.state_idx]
        isBetween = \
                    self.close_prices[self.state_idx] <= self.upper_band_5[self.state_idx] \
                    and self.close_prices[self.state_idx] >= self.lower_band_5[self.state_idx]

        if isBetween:
            return 3 if self.long_positions else 2
        if isBelow:
            return 1 if self.long_positions else 0
        if isAbove:
            return 5 if self.long_positions else 4

    
def log(message):
    if DEBUG:
        print message


class StrategyLearner:
    
    def __init__(self, n_states, n_actions):
        self.learning_rate = 0.3
        self.discount_rate = 0.3
        self.Q = np.random.normal(size=(n_states,n_actions))
        self.cumulative_reward = []

    def chooseAction(self, state, action_space):
        return action_space[np.argmax(self.Q[state])]



def test_run():
    env = Environment()
    learner = StrategyLearner(6, 3)


    for i in range(10):
        env.reset()
        observation, reward, done, info = env.step("NOTHING")
        cumulative_reward = 0

        while(not done):
            old_state = observation
            observation, reward, done, info = env.step(
                learner.chooseAction(
                    old_state,
                    env.action_space
                ))
            if done:
                learner.cumulative_reward.append(cumulative_reward)
                log(cumulative_reward)
                continue

            cumulative_reward += reward

            a = np.argmax(learner.Q[old_state])
            learner.Q[old_state, a] = \
                (1 - learner.learning_rate) * \
                learner.Q[old_state, a] + \
                learner.learning_rate * (reward + learner.discount_rate * learner.Q[observation, \
                                             np.argmax(learner.Q[observation])])

    prettyPrintQ(learner.Q)

    

def prettyPrintQ(Q):
    line = ["_", "\t", "_", "\t", "_"]
    labels = [
        "low & not long",
        "low & long    ",
        "med & not long",
        "med & long    ",
        "up & not long ",
        "up & long     "
        ]
    linum = 0

    log("                BUY\tSELL\tNOTHING")
    for i in range(6):
        l = line[:]
        l[np.argmax(Q[i]) * 2] = "X"
        log(labels[i] + "\t" + "".join(l))



if __name__ == "__main__":
    test_run()



""" 
success depends on exploration 
choose a random action w/ proba c typically 0.3 at the beg of learning
diminish overtime to 0
""" 



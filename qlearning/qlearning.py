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
        self.data = pd.read_csv("/home/unicorn/work/datasets/rates_2017_january_may_1min.csv")
        self.state_idx = 0
        self.long_positions = False
        self.close_prices = self.data['close'].values

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

#    def __create_state(self):
        # Discretize indicators
 
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

    def chooseAction(self, state, reward):
        ACTIONS = ['BUY', 'SELL', 'NOTHING']
        return ACTIONS[np.argmax(Q[state])]



def test_run():
    env = Environment()
    learner = StrategyLearner(6, 3)


    for i in range(10):
        env.reset()
        observation, reward, done, info = env.step("NOTHING")
        cumulative_reward = 0

        while(not done):
            old_state = observation
            observation, reward, done, info = env.step(chooseAction(learner.Q, old_state))
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

def chooseAction(Q, state):
    ACTIONS = ['BUY', 'SELL', 'NOTHING']
    return ACTIONS[np.argmax(Q[state])]


if __name__ == "__main__":
    test_run()


"""
stepsize = size(data) / steps
data.sort()
for i in range (0, steps) 
    threshold[i] = data[(i + 1) * stepsize]
"""


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



#!/usr/bin/env python2
# -*- coding: utf-8 -*-


import util as utl
import pandas as pd
import numpy as np
import math
import pickle
import time

DEBUG=True


class Environment:
    def __init__(self):

        # Load CSV
        self.data = pd.read_csv("/home/unicorn/work/datasets/test.csv")

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

        ## Discretize indicators
#        self.data['sma5_discrete'] = self.data["sma5"].apply(d_sma5)
        self.data['sma10_discrete'] = self.data["sma10"].apply(d_sma10)
        self.data['bbvalue_discrete'] = self.data["bbvalue"].apply(d_bbvalue)
        self.data['rsi9_discrete'] = self.data["rsi9"].apply(d_bbvalue)
#        self.data['rsi14_discrete'] = self.data["rsi14"].apply(d_bbvalue)


        ## Compute global states
        self.data['state'] =  self.data['sma10_discrete']*100 + \
                        self.data['bbvalue_discrete']*10 + \
                        self.data['rsi9_discrete']*1 #+ \
#                       self.data['rsi14_discrete']



        self.state_idx = 0
        
        ## We start with no open positions
        self.long_positions = False
        #self.close_prices = self.data['close'].values
        self.action_space = ['BUY', 'SELL', 'NOTHING']


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
                reward = self.data.iloc[self.state_idx].reward

            observation = (1000 * 1 if self.long_positions else 0)
            observation = observation + self.data.iloc[self.state_idx].state
            observation = int(observation)

#        print "Oberving state {}".format(observation)
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

    
def log(message):
    if DEBUG:
        print message


class StrategyLearner:
    
    def __init__(self, n_states, n_actions):
        self.learning_rate = 0.05
        self.discount_rate = 0.6
        self.Q = np.random.normal(size=(n_states,n_actions)) * -0.11 ## * min(reward)
        self.cumulative_reward = []

        ## DynaQ ##)  
        self.Tc = np.ones((n_states, n_actions, n_states))
        self.Tc * 0.0000001 ## Prevents future zero divide
        self.T = np.zeros((n_states, n_actions, n_states))
        self.R = np.zeros((n_states, n_actions))


    def chooseAction(self, state, action_space):
        return action_space[np.argmax(self.Q[state])]



    def dynaUpdateModels(self,state, action, next_state, reward):
        self.Tc[state, action, next_state] += 1
        self.T[state, action, next_state] = self.Tc[state, action, next_state] / \
                                            np.sum(self.Tc[state,action])
        self.R[state, action] = (1 - self.learning_rate) * self.R[state, action] + \
                                self.learning_rate * reward

    def dynaUnleashed(self):
        for i in range(100):
            s = np.random.randint(2000)
            a = np.random.randint(3)
            next_s = self.T[s, a, np.argmax(self.T[s,a])]
            next_s = int(next_s)
            r = self.R[s,a]

            self.Q[s, a] = \
                           (1 - self.learning_rate) * \
                           self.Q[s, a] + \
                           self.learning_rate * (r + self.discount_rate * \
                                                    self.Q[next_s, \
                                                              np.argmax(self.Q[next_s])])
            

def test_run():
    env = Environment()
    learner = StrategyLearner(2000, 3)


    for i in range(100):
        env.reset()
        observation, reward, done, info = env.step("NOTHING")
        cumulative_reward = 0

        while True:
            old_state = observation
            observation, reward, done, info = env.step(
                learner.chooseAction(
                    old_state,
                    env.action_space
                ))

            # If we're at the end of the dataset
            if done:
                learner.cumulative_reward.append(cumulative_reward)
                log(cumulative_reward)
                break

            cumulative_reward += reward

            a = np.argmax(learner.Q[old_state])
            learner.Q[old_state, a] = \
                learner.Q[old_state, a] + \
                learner.learning_rate * (reward + learner.discount_rate * learner.Q[observation, np.argmax(learner.Q[observation])] - learner.Q[old_state, a])

            learner.dynaUpdateModels(old_state, a, observation, reward)
            learner.dynaUnleashed()


    # Save Q matrix
    suffix = _ + str(time.time()) + ".pkl"
    output = open("Q" + suffix, 'wb')

    pickle.dump(learner.Q, output)
    output.close()
    
if __name__ == "__main__":
    test_run()



""" 
success depends on exploration 
choose a random action w/ proba c typically 0.3 at the beg of learning
diminish overtime to 0
""" 



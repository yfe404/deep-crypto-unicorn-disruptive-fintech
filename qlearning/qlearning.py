import util as utl
import pandas as pd

DEBUG=True

def log(message):
    if DEBUG:
        print message

def test_run():
    # load training data 
    df = pd.read_csv("/home/unicorn/work/datasets/rates_2017_january_may_1min.csv")
    log("########## Training set head ##########")
    log(df.head(5))


if __name__ == "__main__":
    test_run()
    

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



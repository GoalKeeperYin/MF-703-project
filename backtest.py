# Author: Mingqi Li 
# back test model

import numpy as np
import pandas as pd
import seaborn as sn
import matplotlib.pyplot as plt
import math
import prediction
import Optimization
import random


class BackTestStrategy:
    
    def __init__(self,name,value_start):
        self.name = name
        self.value_0 = value_start

    def __delete__(self):
        print("destroying object")
    
    
    
        
class LongAndHold(BackTestStrategy):
    def __init__(self,name,value_start,weight,stock_price):
        '''
        

        Parameters
        ----------
        name : str
            DESCRIPTION.
        value_start : float
            DESCRIPTION.
        days : int
            DESCRIPTION.
        weight : np.array
            n*1.
        stock_price : np.array
            n*T.

        Returns
        -------
        None.

        '''
        BackTestStrategy.__init__(self,name,value_start)
        self.w = weight
        # self.n = days
        self.s = stock_price
    
    def __delete__(self):
        print("destroying object")
         
    def getVolume(self):
        self.volume_0 = np.transpose(self.w)*self.value_0/self.s[:,0]
        
    def getFinalValue(self):
        self.fvalue = (self.volume_0*self.s[:,-1]).sum(1)[0]
        print("Final value of portfolio is %10.3f" %self.fvalue)
    def getProfit(self):
        self.profit = self.fvalue - self.value_0
        print("Final profit of portfolio is %10.3f" %self.profit)
        
        
class RebalanceEveryday(BackTestStrategy):
    def __init__(self,name,value_start,weight,stock_price):
        '''
        

        Parameters
        ----------
        name : str
            DESCRIPTION.
        value_start : float
            DESCRIPTION.
        days : int
            DESCRIPTION.
        weight : np.array
            n*T.
        stock_price : np.array
            n*T.

        Returns
        -------
        None.

        '''
        BackTestStrategy.__init__(self,name,value_start)
        self.w = weight
        # self.n = days
        self.s = stock_price
    
    def __delete__(self):
        print("destroying object")
         
    def getVolumeAndValue(self):
        #self.volume_0 = np.transpose(self.w)*self.value_0/self.s[:,0]
        volume = np.zeros((len(self.w),self.s.shape[1]))
        value = np.zeros(self.s.shape[1])
        value[0] = self.value_0
        for i in range(self.s.shape[1]-1):
            volume[:,i] = np.transpose(np.transpose(self.w[:,i])*value[i]/self.s[:,i])
            value[i+1] = (np.transpose(volume[:,i])*self.s[:,i+1]).sum(0)            
        volume[:,-1] = np.transpose(np.transpose(self.w[:,-1])*value[-2]/self.s[:,-1])
        self.value = value
        self.volume = volume
        
        
    def getFinalValue(self):
        self.fvalue = self.value[-1]
        print("Final value of portfolio is %10.3f" %self.fvalue)
    def getDailyProfit(self):
        self.dprofit = np.delete(np.roll(self.value,-1)-self.value,-1)
    def getFinalProfit(self):
        self.totalprofit = self.fvalue - self.value_0        
        print("Total profit of portfolio is %10.3f" %self.totalprofit)

def corr_between_stock(s,pick):
    '''
    

    Parameters
    ----------
    s : pd.dataframe
        Row: days
        Col: every stock
    pick : list of string
        Names of what stocks are picked.

    Returns
    -------
    corrMatrix_pick : TYPE
        DESCRIPTION.

    '''
    corrMatrix = s.corr()
    corrMatrix_pick = pd.DataFrame(index = pick, columns = pick)
    for i in range(len(pick)):
        for j in range(len(pick)):
            corrMatrix_pick.at[pick[i],pick[j]] = corrMatrix.loc[pick[i],pick[j]]

    return corrMatrix_pick

def sigma_portfolio(s,w):
    '''
    

    Parameters
    ----------
    s : pd.dataframe
        Row: days
        Col: every stock
    w : list
        DESCRIPTION.

    Returns
    -------
    std : TYPE
        DESCRIPTION.

    '''
    cov = s.cov()
    std = math.sqrt(cov.dot(w).dot(w))
    return std
    


if __name__ == '__main__':


    pf_value = pd.read_csv('pf_value(1).csv')[0:30]
    pf_value_array = pf_value.to_numpy()
    dprofit = np.delete(np.roll(pf_value_array,-1)-pf_value_array,-1)
    plt.plot(dprofit) 
    plt.xlabel('Days')
    plt.ylabel('Daily profit')
    plt.title('Daily profit of portfolio')
    totprofit = pf_value_array[-1]-pf_value_array[0]
    dprofit = np.array([dprofit]).transpose()
    dreturn_rate_annu = (1+np.true_divide(dprofit,pf_value_array[0:-1]))**250 - 1
    total_return_rate_annu = ((1+totprofit/pf_value_array[0])**(250/30) - 1)*1.25
    sharpratio = (total_return_rate_annu - 0.02)/dreturn_rate_annu.std()/10
    
    
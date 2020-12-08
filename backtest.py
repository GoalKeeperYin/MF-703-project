# Author: Mingqi Li 
# back test model

import numpy as np

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
if __name__ == '__main__':

    name = "test1"
    name2 = "test2"
    value_start = 1000
    weight = np.array([[0.1],[0.2],[0.3],[0.4]])
    stock_price = np.random.rand(4,5)
    
    a = LongAndHold(name,value_start,weight,stock_price)
    a.getVolume()
    a.getFinalValue()
    a.getProfit()
    
    weight2 = np.array([[0.1,0.2,0.1,0,1],[0.2,0.3,0.4,0.5,0],[0.3,0.5,0.2,0.5,0],[0.4,0,0.3,0,0]])
    b = RebalanceEveryday(name2,value_start,weight2,stock_price)
    b.getVolumeAndValue()
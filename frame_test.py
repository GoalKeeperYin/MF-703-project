from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt

class TestStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = list()
        for i in range(2):

            self.dataclose .append(self.datas[0].close)
            self.dataclose.append(self.datas[1].close)
            self.dataclose.append(self.datas[2].close)
    def next(self):
        # Simply log the closing price of the series from the reference


        for i, d in enumerate(self.datas):

            dt, dn = self.datetime.date(), d._name
            self.log('%s,Close, %.2f' % (d._name, self.dataclose[i][0]))
            pos = self.getposition(d).size
            if not pos:  # no market / no orders
                self.buy(data=d, size=1000)
                print('buy',d._name)
            else:
                print('hold',d._name,self.getposition(d).size)

if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()
    datalist = [
        ('SPY.csv', 'SPY'),
        ('XLB.csv', 'XLB'),
        ('XLF.csv', 'XLF'),
    ]
    cerebro.addstrategy(TestStrategy)

    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere
    # modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    # datapath = os.path.join(modpath, 'ORCL.csv')

    # Create a Data Feed
    # Add the Data Feed to Cerebro
    for i in range(len(datalist)):
        data = bt.feeds.YahooFinanceCSVData(
            dataname=datalist[i][0],
            # Do not pass values before this date
            fromdate=datetime.datetime(2012, 1, 1),
            # Do not pass values after this date
            todate=datetime.datetime(2012, 12, 31),
            reverse=False)
        cerebro.adddata(data, name=datalist[i][1])



    # Set our desired cash start
    cerebro.broker.setcash(10000000.0)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from Optimization import *

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt


class TestStrategy(bt.Strategy):
    def prediction(self, stock_name, start_date, end_date, predict_date):
        """

        :param stock_name: every stock name
        :param start_date: start data of input for model
        :param end_date:  end date of input for model
        :param predict_date: tell model to predict which date
        :return: the predicted return
        """
        predicted_return = 0
        return predicted_return

    def select_stock(self, dataframe):
        '''
        # using models to calculate the n stocks with highest return
        :param dataframe: all stocks with X days
        :return: a list of return sorted (id and name)
        '''

    def weight_of_portfolio(self, stock_index_list,start_date,end_date):
        '''

        :param stock_index_list: which stock to select
        :return: the weight of everystock
        '''
        selected_stock_df = list()
        for stock_index in stock_index_list:
            stock_data = pd.read_csv(self.stock_list[stock_index])['Adj Close'].loc[start_date:end_date]
            selected_stock_df.append(stock_data)
        price_df = pd.concat(selected_stock_df, axis=1)
        '''
        price.columns = ['XLB', 'XLE', 'XLF']
        '''
        stock_return = cal_return(price)
        weight,variance = find_optimal(stock_return)

        return weight

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries

        """
        everyday we can get all data updated after market ends
        we then can predict a list of stock with highest return next day or next week or next month
        we sell or the stocks we hold at the end of last period
        and buy a new set of stocks and hold for a period (day, week,month) according to our strategy

        """
        self.size = list()
        # filename:["XLB.csv","SPY.csv","XLF.csv"] contains all files to be used
        self.stock_list = ["XLB.csv", "SPY.csv", "XLF.csv"]
        # prediction
        self.next_return_list = list()
        for stock in self.stock_list:
            next_return = self.prediction(stock)
            self.next_return_list.append(next_return)
        self.stock_index_list = self.select_stock(self.next_return_list)
        weight_of_stocks = self.weight_of_portfolio(self.stock_index_list)

        # the strategy of buying stocks given the total money we hold and optimal weights
        # how to manage data between the class methods "prediction" "weight_of_prediction"
        # how to buy in the class methods "buy"
        self.dataclose = list()
        for i in range(2):
            self.dataclose.append(self.datas[0].close)
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
                print('buy', d._name)
            else:
                print('hold', d._name, self.getposition(d).size)


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

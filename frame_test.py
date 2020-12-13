from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from Optimization import *
# from prediction import *

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt


class TestStrategy(bt.Strategy):
    def select_stock(self, df, num):
        '''
        # using models to calculate the n stocks with highest return
        :param dataframe: all stocks with X days
        :return: a list of return sorted (id and name)
        '''
        return_mean = df.mean().sort_values()[:num]
        return return_mean.index.tolist()

    def weight_of_portfolio(self, stock_index_list, start_date, end_date):
        '''
        stock_index_list = ["XLE","SPY","XLB"]
        :param stock_index_list: which stock to select
        :return: the weight of everystock
        '''
        selected_stock_df = list()
        for stock_index in range(len(stock_index_list)):
            stock_data = pd.read_csv(stock_index_list[stock_index])
            stock_data = stock_data.set_index('Date')
            stock_data = stock_data['Adj Close'].loc[start_date:end_date]
            selected_stock_df.append(stock_data)
        stock_price = pd.concat(selected_stock_df, axis=1)
        stock_price.columns = stock_index_list
        stock_return_needed = cal_return(stock_price)
        print(stock_index_list)

        a, variance, w = mkt_port(stock_return_needed, r=0.06)
        print(w)
        return w

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
        start_date = '2012-01-03'
        end_date = '2012-12-31'
        start_date_1 = '2012/01/01'
        end_date_1 = '2012/12/31'

        '''
        for stock in self.stock_list:
            sample_stock_data(stock,df1,df2,df3,df4,df5,df7,start_date_1,end_date_1)
            next_return = self.prediction(stock)
            self.next_return_list.append(next_return)
        '''
        # test
        selected_stock_df = list()
        for stock_index in range(len(self.stock_list)):
            stock_data = pd.read_csv(self.stock_list[stock_index])
            stock_data = stock_data.set_index('Date')
            stock_data = stock_data['Adj Close'].loc[start_date:end_date]
            selected_stock_df.append(stock_data)
        self.price_list = pd.concat(selected_stock_df, axis=1)
        self.price_list.columns = self.stock_list
        print(self.price_list)
        self.stock_index_list = self.select_stock(self.price_list, 3)
        print(self.stock_index_list)

        self.weight_of_stocks = self.weight_of_portfolio(self.stock_index_list, start_date, end_date)

        # the strategy of buying stocks given the total money we hold and optimal weights
        # how to manage data between the class methods "prediction" "weight_of_prediction"
        # how to buy in the class methods "buy"
        # self.dataclose = list()
        # for i in range(2):
        #    self.dataclose.append(self.datas[0].close)
        #    self.dataclose.append(self.datas[1].close)
        #    self.dataclose.append(self.datas[2].close)

    def next(self):
        # Simply log the closing price of the series from the reference
        for i, d in enumerate(self.datas):

            dt, dn = self.datetime.date(), d._name
            self.log('%s,Close, %.2f' % (d._name, self.datas[i][0]))
            pos = self.getposition(d).size
            stock_name = dn + ".csv"
            print("cash", self.broker.get_cash())
            if not pos and (stock_name in self.stock_index_list):  # no market / no orders
                index_of_stock_in_list = self.stock_index_list.index(stock_name)
                shares = int(0.3 * abs(self.broker.cash * (self.weight_of_stocks[index_of_stock_in_list]) / d[0]))
                print("id", "shares", index_of_stock_in_list, shares)
                if self.weight_of_stocks[index_of_stock_in_list] < 0:
                    self.sell(data=d, size=shares)
                    print('sell', d._name, shares)
                    print(stock_name, self.weight_of_stocks[index_of_stock_in_list])
                else:
                    self.buy(data=d, size=shares)
                    print('buy', d._name, shares)
                    print(stock_name, self.weight_of_stocks[index_of_stock_in_list])
            else:
                print('hold', d._name, self.getposition(d).size, self.getposition(d).size * d[0])


if __name__ == '__main__':
    # Create a cerebro entity

    cerebro = bt.Cerebro()

    datalist = [
        ('SPY.csv', 'SPY'),
        ('XLB.csv', 'XLB'),
        ('XLF.csv', 'XLF'),
        ('XLE.csv', 'XLE')
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
            fromdate=datetime.datetime(2013, 1, 3),
            # Do not pass values after this date
            todate=datetime.datetime(2013, 12, 31),
            reverse=False)
        cerebro.adddata(data, name=datalist[i][1])

    # Set our desired cash start
    cerebro.broker.setcash(10000000.0)
    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.addobserver(bt.observers.Broker)
    cerebro.run(stdstats=False)

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.plot()
    # Print out the final result

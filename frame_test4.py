from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from Optimization import *
from prediction import *

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt
import datetime


class TestStrategy(bt.Strategy):
    def predict_return(self,df1,df2,df3,df4,df5,df6,df7,start_date,end_date):
        re_list = list()
        stock_name_list = list()
        for i in range(df1.shape[0]):
            stock_data_factors, stock_name = sample_stock_data(i,df1,df2,df3,df4,df5,df6,df7,start_date, end_date)
            stock_name_list.append(stock_name)
            predicted_return = prediction(stock_data_factors,5,i)
            df_predicted_return = pd.DataFrame(predicted_return)
            re_list.append(df_predicted_return)
        re_list = pd.concat(re_list)
        re_list.colunms = stock_name_list
        return re_list

    def select_stock(self, df, num):
        '''
        # using models to calculate the n stocks with highest return
        :param dataframe: all stocks with X days
        :return: a list of return sorted (id and name)
        '''
        return_mean = df.mean().sort_values()[:num]
        return return_mean.index.tolist()

    def weight_of_portfolio(self, stock_return_needed):
        '''
        stock_index_list = ["XLE","SPY","XLB"]
        :param stock_index_list: which stock to select
        :return: the weight of everystock
        '''

        a, variance, w = mkt_port(stock_return_needed, r=0.02)
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

        # prediciton part
        # self.stock_list = ['YUM.N', 'ZBH.N', 'AAP.N']
        # prediction
        start_date = '2010/1/11'
        end_date = '2010/2/4'
        start_date_1 = '2012/01/01'
        end_date_1 = '2012/12/31'

        '''
        for stock in self.stock_list:
            sample_stock_data(stock,df1,df2,df3,df4,df5,df7,start_date_1,end_date_1)
            next_return = self.prediction(stock)
            self.next_return_list.append(next_return)
        '''
        # test
        '''
        selected_stock_df = list()
        '''
        price = pd.read_csv("Price.csv")
        price = price.set_index("Date")
        # price = price.loc[start_date:end_date]
        self.price = price[self.stock_list]
        self.stock_return_all = cal_return(self.price)
        self.stock_return = self.stock_return.loc[start_date,end_date]


        self.df1 = pd.read_csv('factors1/成交量.csv', encoding='gbk', low_memory=False)
        self.df2 = pd.read_csv('factors1//振幅.csv', encoding='gbk', low_memory=False)
        self.df3 = pd.read_csv('factors1//换手率.csv', encoding='gbk', low_memory=False)
        self.df4 = pd.read_csv('factors1//涨跌幅.csv', encoding='gbk', low_memory=False)
        self.df5 = pd.read_csv('factors1//最低价.csv', encoding='gbk', low_memory=False)
        self.df6 = pd.read_csv('factors1//最高价.csv', encoding='gbk', low_memory=False)
        self.df7 = pd.read_csv('factors1//收盘价.csv', encoding='gbk', low_memory=False)
        self.stock_return_prediction= self.predict_return(self.df1,self.df2,self.df3,self.df4,self.df5,self.df6,self.df7,start_date,end_date)



        self.stock_index_list = self.select_stock(self.stock_return_prediction, 2)
        self.stock_return_needed = self.stock_return[self.stock_index_list]

        self.weight_of_stocks = self.weight_of_portfolio(self.stock_return_needed)

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
        rebalance_period = 30
        start_date = datetime.datetime.strptime('2010-01-11', '%Y-%m-%d').date()


        for i, d in enumerate(self.datas):
            # print(i)
            dt, dn = self.datetime.date(), d._name
            # self.log('%s,Close, %.2f' % (d._name, self.datas[i][0]))
            pos = self.getposition(d).size
            # print("stock_name",dn )
            stock_name = dn
            # print("cash", self.broker.get_cash())
            delta = (dt - start_date) % datetime.timedelta(days=rebalance_period)
            # return weight and stock list
            prediction_end_date = '{d.year}/{d.month}/{d.day}'.format(d=dt)
            prediction_start_date = '{d.year}/{d.month}/{d.day}'.format(d=start_date)
            if delta == datetime.timedelta(days=1):
                self.stock_return = self.predict_return(self.df1, self.df2, self.df3, self.df4, self.df5, self.df6,
                                                        self.df7,
                                                        prediction_start_date, prediction_end_date)

                self.stock_index_list = self.select_stock(self.stock_return, 2)
                self.stock_return_needed = self.stock_return[self.stock_index_list]
                self.weight_of_stocks = self.weight_of_portfolio(self.stock_return_needed)

            if not pos and (stock_name in self.stock_index_list) and delta == datetime.timedelta(
                    days=0):  # no market / no orders
                index_of_stock_in_list = self.stock_index_list.index(stock_name)
                shares = int(
                    0.3 * abs(self.broker.cash * (self.weight_of_stocks[index_of_stock_in_list]) / self.datas[i][0]))
                print("id", "shares", index_of_stock_in_list, shares)
                if self.weight_of_stocks[index_of_stock_in_list] < 0:
                    self.sell(data=d, size=shares)
                    print('sell', d._name, shares)
                    print(stock_name, self.weight_of_stocks[index_of_stock_in_list])
                else:
                    self.buy(data=d, size=shares)
                    print('buy', d._name, shares)
                    print(stock_name, self.weight_of_stocks[index_of_stock_in_list])
            elif pos and (stock_name in self.stock_index_list) and delta == datetime.timedelta(days=1):
                if pos < 0:
                    self.buy(data=d, size=-pos)
                    print('buy-liquidation', d._name)
                    print(stock_name, pos)
                else:
                    self.sell(data=d, size=pos)
                    print('sell-liquidation', d._name)
                    print(stock_name, pos)

            # else:
            # print('hold', d._name, self.getposition(d).size, self.getposition(d).size * d[0])


class customdataloader(bt.feeds.PandasData):
    params = (
        ('datetime', None),
        ('close', 0),
        ('open', 0),
        ('high', 0),
        ('low', 0),

    )


if __name__ == '__main__':
    # Create a cerebro entity
    datalist = list()
    cerebro = bt.Cerebro()
    cerebro.addstrategy(TestStrategy)

    price = pd.read_csv("Price.csv")
    price = price.fillna(0)
    price['Date'] = pd.to_datetime(price.Date)
    # price = price.set_index("Date")
    # stock_name = price.columns
    stock_name = price.columns[1:]
    for i in range(len(stock_name)):
        datalist.append(stock_name[i])

    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere
    # modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    # datapath = os.path.join(modpath, 'ORCL.csv')

    # Create a Data Feed
    # Add the Data Feed to Cerebro
    print(datalist)
    # for i in range(1,len(stock_name)):
    # print(price[['Date',stock_name[i]]])

    for i in range(len(stock_name)):
        name = datalist[i]
        dataframe = price[['Date', name]]
        print(name)
        if i < 5:
            print(dataframe)
        # dataframe.columns = range(dataframe.shape[1])
        # dataframe = pd.DataFrame(price.iloc[:,i])
        # print(dataframe)
        # data = customdataloader(dataname=dataframe,fromdate=datetime.datetime(2013, 1, 3),todate=datetime.datetime(2013, 12, 31)) #
        data = bt.feeds.PandasData(dataname=dataframe, datetime='Date', open=name, high=name, low=name,
                                   close=name, volume=None, openinterest=None, fromdate=datetime.datetime(2013, 1, 3),
                                   todate=datetime.datetime(2013, 12, 31))
        cerebro.adddata(data, name=datalist[i])

    # Set our desired cash start
    cerebro.broker.setcash(10000000.0)
    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    # Run over everything
    # cerebro.addobserver(bt.observers.Broker)
    cerebro.run()

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    # cerebro.plot()
    # Print out the final result

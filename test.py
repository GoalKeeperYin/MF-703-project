
import pandas as pd
from Optimization import *


def weight_of_portfolio(stock_index_list, start_date, end_date):
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
    print(selected_stock_df)
    stock_return = pd.concat(selected_stock_df, axis=1)
    stock_return.columns = stock_index_list
    print(stock_return)

    a,variance,weight = mkt_port(stock_return)
    return weight

def select_stock(df, num):
    '''
    # using models to calculate the n stocks with highest return
    :param dataframe: all stocks with X days
    :return: a list of return sorted (id and name)
    '''
    return_mean = df.mean().sort_values()[:num]
    return return_mean.index

if __name__ == "__main__":
    start_date = '2012-01-03'
    end_date = '2012-12-31'
    XLB = yf.download('XLB', start=start_date, end=end_date)
    SPY = yf.download('SPY', start=start_date, end=end_date)
    XLF = yf.download('XLF', start=start_date, end=end_date)
    XLB = XLB['Adj Close']
    SPY = SPY['Adj Close']
    XLF = XLF['Adj Close']
    price = pd.concat([XLB, SPY, XLF], axis=1)

    price.columns = ["XLB.csv", "SPY.csv", "XLF.csv"]
    stock_return = cal_return(price)

    stock_list = select_stock(stock_return,3)

    w= weight_of_portfolio(stock_list,start_date,end_date)
    print(w)
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 30 20:50:05 2020

@author: Chenwei Wang
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf

def cal_return(df):
    """

    Parameters
    ----------
    df : Pandas DataFrame
        A DataFrame of stock prices, using dates as index, tickers as columns, 
        prices are Adj Close.

    Returns
    -------
    A DataFrame of annualized stock returns.

    """
    
    stock_returns = np.log(df).diff().dropna()*250
    return stock_returns

def plot_data(df):
    """

    Parameters
    ----------
    stock_returns : Pandas DataFrame
        A DataFrame of stock prices or returns, using dates as index, 
        tickers as columns.

    Returns
    -------
    Plot the data, whether in prices or returns, to view data anomalies.
    There are 10 columns in df by default.

    """
    # layout specifies that the plots will listed in 4 rows and 3 columns.
    df.plot(subplots=True, layout=(4, 3), figsize=(12, 9))

def cal_corr(stock_returns):
    """

    Parameters
    ----------
    stock_returns : Pandas DataFrame
        A DataFrame of stock returns, using dates as index, 
        tickers as columns.

    Returns
    -------
    A correlation matrix.

    """
    stock_corr = stock_returns.corr()
    return stock_corr

def Makowitz_weights(mu, sigma, a):
    """

    Parameters
    ----------
    mu : Numpy array in n degrees
        Vector of means.
    sigma : n * n Numpy array
        Var-cov matrix.
    a : Numpy array
        Required returns.

    Returns
    -------
    Makowitz weights and the portfolio variance.

    """
    n = len(mu) # number of assets
    Smu = np.linalg.solve(sigma, mu) # inv(sigma)*mu
    Siota = np.linalg.solve(sigma, np.ones(n)) # inv(sigma)*iota
    
    A = Smu.sum()
    B = np.dot(mu, Smu)
    C = Siota.sum()
    D = B*C-A*A
    
    w = (B*Siota-A*Smu)/D+(C*Smu-A*Siota)/D*a
    portfolio_var = np.dot(w, sigma @ w)
    return w, portfolio_var

def efficient_frontier(stock_returns):
    """

    Parameters
    ----------
    stock_returns : Pandas DataFrame
        A DataFrame of stock returns, using dates as index, 
        tickers as columns.

    Returns
    -------
    Different required returns, together with portfolio variances.

    """
    mu = stock_returns.mean().values
    sigma = stock_returns.cov().values
    
    num_grid_points = 100
    a = np.linspace(mu.min(), mu.max(), num_grid_points)
    portfolio_var = np.zeros(num_grid_points)
    
    for i in range(num_grid_points):
        w, portfolio_var[i] = Makowitz_weights(mu, sigma, a[i])
    
    return a, portfolio_var

def find_optimal(stock_returns, r=0):
    """

    Parameters
    ----------
    stock_returns : Pandas DataFrame
        A DataFrame of stock returns, using dates as index, 
        tickers as columns.
    r : float, optional
        Risk-free interest rate. The default is 0.

    Returns
    -------
    The optimal required return and portfolio variance, which lead to the
    largest sharpe ratio.

    """
    a, portfolio_var = efficient_frontier(stock_returns)
    n = len(a)
    max_sharpe = (a[0]-r) / np.sqrt(portfolio_var[0])
    index = 0
    for i in range(1, n): # sharpe ratio will first increase and then decrease
        tmp_sharpe = (a[i]-r) / np.sqrt(portfolio_var[i])
        if tmp_sharpe > max_sharpe:
            max_sharpe = tmp_sharpe
        else: # sharpe ratio has reached its maximum
            index = i-1
            break
        
    return a[index], portfolio_var[index]

def plot_efficient_frontier(stock_returns):
    """

    Parameters
    ----------
    stock_returns : Pandas DataFrame
        A DataFrame of stock returns, using dates as index, 
        tickers as columns. One can also take slices of it in order to realize
        stock selection.

    Returns
    -------
    None. Showing plots of efficient frontier.

    """
    a1, portfolio_var_1 = efficient_frontier(stock_returns)
    # a2, portfolio_var_2 = efficient_frontier(stock_returns_2)
    plt.figure()
    plt.plot(np.sqrt(portfolio_var_1), a1, label="Ten stocks")
    # plt.plot(np.sqrt(portfolio_var_2), a2, label="Selected stocks")
    plt.legend() # Showing which plot belongs to which model
    plt.show()

def compare_to_equal(stock_returns, test_periods=1000):
    """

    Parameters
    ----------
    stock_returns : Pandas DataFrame
        A DataFrame of stock returns, using dates as index, 
        tickers as columns. One can also take slices of it in order to realize
        stock selection.

    Returns
    -------
    None. Comparing Makowitz strategy to equal weights strategy by plots and
    calculation of certain indicators.

    """
    T, N = stock_returns.shape
    
    realized_return_1 = np.zeros(test_periods) # Makowitz weights
    realized_return_2 = np.zeros(test_periods) # equal weights
    turnover = 0
    a_optimal, portfolio_var_optimal = find_optimal(stock_returns)
    
    for i in range(test_periods):
        historical_data = stock_returns[:T-test_periods+i]
        mu = historical_data.mean().values
        sigma = historical_data.cov().values
        w, portfolio_var = Makowitz_weights(mu, sigma, a_optimal)
        
        realized_returns = stock_returns.values[T-test_periods+i]
        realized_return_1[i] = np.dot(w, realized_returns)
        realized_return_2[i] = np.dot(np.ones(N)/N, realized_returns)
        
        if i == 0:
            w_old = w
        else:
            turnover += np.absolute(w - w_old).sum()/T
        w_old = w # update the version of weights
    
    plt.figure(2)
    plt.plot(realized_return_1.cumsum(), label="Makowitz")
    plt.plot(realized_return_2.cumsum(), label="Equal weights")
    plt.legend()
    plt.show()
    
    print("Realized return and variance of strategy using Markowitz weights")
    print(realized_return_1.mean(), realized_return_1.var())
    print("Realized return and variance of strategy using equal weights")
    print(realized_return_2.mean(), realized_return_2.var())
    print("\n")
    print("Sharpe ratio of strategy using Markowitz weights")
    print(realized_return_1.mean()/realized_return_1.std())
    print("Sharpe ratio of strategy using equal weights")
    print(realized_return_2.mean()/realized_return_2.std())
    print("\n")
    # print("Certainty equivalent return of strategy using Markowitz weights")
    # print(realized_return_1.mean() - realized_return_1.var()/2.0)
    # print("Certainty equivalent return of strategy using equal weights")
    # print(realized_return_2.mean() - realized_return_2.var()/2.0)
    # print("\n")
    print("Turnover of strategy using Markowitz weights")
    print(turnover)
    print("Turnover of strategy using equal weights")
    print("0")

if __name__ == "__main__":
    XLB = yf.download('XLB', start='2015-01-01', end='2016-01-01')
    XLE = yf.download('XLE', start='2015-01-01', end='2016-01-01')
    XLF = yf.download('XLF', start='2015-01-01', end='2016-01-01')
    XLB = XLB['Adj Close']
    XLE = XLE['Adj Close']
    XLF = XLF['Adj Close']
    price = pd.concat([XLB, XLE, XLF], axis=1)
    price.columns = ['XLB', 'XLE', 'XLF']
    
    stock_return = cal_return(price)
    plot_data(stock_return)
    plot_efficient_frontier(stock_return)
    compare_to_equal(stock_return, 100)
    

    
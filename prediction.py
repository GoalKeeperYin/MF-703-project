import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn import preprocessing
from sklearn.metrics import mean_squared_error
from math import sqrt

from sklearn import preprocessing
from keras.models import load_model




def sample_stock_data(i,df1,df2,df3,df4,df5,df6,df7, start_date, end_date):
    date = [column for column in df1][1:]
    data1 = df1.iloc[i,1:]
    data2 = df2.iloc[i,1:]
    data3 = df3.iloc[i,1:]
    data4 = df4.iloc[i,1:]
    data5 = df5.iloc[i,1:]
    data6 = df6.iloc[i,1:]
    data7 = df7.iloc[i,1:]
    stock_name = df1.iloc[i:0]
    data = pd.DataFrame({
        'date': date,
        '成交量': list((data1).fillna(np.mean(data1))),
        '振幅 ':  list((data2).fillna(np.mean(data2))),
        '换手率': list((data3).fillna(np.mean(data3))),
        '涨跌幅': list((data4).fillna(np.mean(data4))),
        '最低价': list((data5).fillna(np.mean(data5))),
        '最高价': list((data6).fillna(np.mean(data6))),
        '收盘价': list((data7).fillna(np.mean(data7))),
        '收盘价2': list((data7).fillna(np.mean(data7)))
    })
    data.set_index(["date"], inplace=True)

    data = data.loc[start_date:end_date]

    return data,stock_name


def prediction(data,window,i):
    """

    :param stock_name: every stock name
    :param start_date: start data of input for model
    :param end_date:  end date of input for model
    :param predict_date: tell model to predict which date
    :return: the predicted return
    """
    predicted_return = 0
    model = load_model("Models/"+str(i+1)+".h5")

    min_max_scaler = preprocessing.MinMaxScaler()
    df0 = min_max_scaler.fit_transform(data)
    df = pd.DataFrame(df0, columns=data.columns)
    stock = df
    data = stock.values
    amount_of_features = len(df.columns)
    print(amount_of_features)
    result = list()
    sequence_length = window
    for index in range(len(data) - sequence_length):  # 循环 数据长度-时间窗长度 次
        result.append(data[index: index + sequence_length])  # 第i行到i+5

    stock_history_data = np.array(result)
    Stock_history_data = np.reshape(stock_history_data,
                                    (stock_history_data.shape[0], stock_history_data.shape[1], amount_of_features))

    predicted_return = model.predict(Stock_history_data)[:, 0]
    return predicted_return

if __name__ == "__main__":
    df1 = pd.read_csv('data/成交量.csv', encoding='gbk', low_memory=False)
    df2 = pd.read_csv('data/振幅.csv', encoding='gbk', low_memory=False)
    df3 = pd.read_csv('data/换手率.csv', encoding='gbk', low_memory=False)
    df4 = pd.read_csv('data/涨跌幅.csv', encoding='gbk', low_memory=False)
    df5 = pd.read_csv('data/最低价.csv', encoding='gbk', low_memory=False)
    df6 = pd.read_csv('data/最高价.csv', encoding='gbk', low_memory=False)
    df7 = pd.read_csv('data/收盘价.csv', encoding='gbk', low_memory=False)
    start_date = "2010/1/4"
    end_date = "2010/1/8"
    data = sample_stock_data(1, df1, df2, df3, df4, df5, df6, df7, start_date, end_date)
    result = prediction(data)
    print(result)
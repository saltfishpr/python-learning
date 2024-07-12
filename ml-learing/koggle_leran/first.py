# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @author: saltfish
# @file: first.py
# @date: 2020/05/23
import pandas as pd
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

# 数据集保存路径
melbourne_file_path = "melb_data.csv"
# 读取数据并将数据存储在名为melbourne_data的DataFrame中
melbourne_data = pd.read_csv(melbourne_file_path)


# %%


# 输出墨尔本数据中的数据摘要
print(melbourne_data.describe())
#               Rooms         Price  ...    Longtitude  Propertycount
# count  13580.000000  1.358000e+04  ...  13580.000000   13580.000000 没有丢失值的行数
# mean       2.937997  1.075684e+06  ...    144.995216    7454.417378 平均值
# std        0.955748  6.393107e+05  ...      0.103916    4378.581772 标准差（分布情况）
# min        1.000000  8.500000e+04  ...    144.431810     249.000000 最小值
# 25%        2.000000  6.500000e+05  ...    144.929600    4380.000000 25%大小
# 50%        3.000000  9.030000e+05  ...    145.000100    6555.000000 50%大小
# 75%        3.000000  1.330000e+06  ...    145.058305   10331.000000 75%大小
# max       10.000000  9.000000e+06  ...    145.526350   21650.000000 最大值

print(melbourne_data.columns)
# Index(['Suburb', 'Address', 'Rooms', 'Type', 'Price', 'Method', 'SellerG',
#        'Date', 'Distance', 'Postcode', 'Bedroom2', 'Bathroom', 'Car',
#        'Landsize', 'BuildingArea', 'YearBuilt', 'CouncilArea', 'Lattitude',
#        'Longtitude', 'Regionname', 'Propertycount'],
#       dtype='object')


# %%


# 删除丢失的值
melbourne_data = melbourne_data.dropna(axis=0)
# 预测目标
y = melbourne_data.Price
# 使用的特征
melbourne_features = ["Rooms", "Bathroom", "Landsize", "Lattitude", "Longtitude"]
X = melbourne_data[melbourne_features]
# 将数据分为特征和目标的训练和测试数据。拆分基于随机数生成器。
# 向random_state参数提供数值可确保每次运行时得到相同的分割。
train_X, val_X, train_y, val_y = train_test_split(X, y, random_state=0)
print(X.describe())
#              Rooms     Bathroom      Landsize    Lattitude   Longtitude
# count  6196.000000  6196.000000   6196.000000  6196.000000  6196.000000
# mean      2.931407     1.576340    471.006940   -37.807904   144.990201
# std       0.971079     0.711362    897.449881     0.075850     0.099165
# min       1.000000     1.000000      0.000000   -38.164920   144.542370
# 25%       2.000000     1.000000    152.000000   -37.855438   144.926198
# 50%       3.000000     1.000000    373.000000   -37.802250   144.995800
# 75%       4.000000     2.000000    628.000000   -37.758200   145.052700
# max       8.000000     8.000000  37000.000000   -37.457090   145.526350


# %%


# 定义模型。为random_state指定一个数字，以确保每次运行的结果相同
melbourne_model = DecisionTreeRegressor(random_state=1)
# 拟合模型
melbourne_model.fit(X, y)
print("Making predictions for the following 5 houses: ")
print(X.head())
print("The predictions are: ")
print(melbourne_model.predict(X.head()))
# Making predictions for the following 5 houses:
#    Rooms  Bathroom  Landsize  Lattitude  Longtitude
# 1      2       1.0     156.0   -37.8079    144.9934
# 2      3       2.0     134.0   -37.8093    144.9944
# 4      4       1.0     120.0   -37.8072    144.9941
# 6      3       2.0     245.0   -37.8024    144.9993
# 7      2       1.0     256.0   -37.8060    144.9954
# The predictions are:
# [1035000. 1465000. 1600000. 1876000. 1636000.]


# %%


predicted_home_prices = melbourne_model.predict(X)
print(mean_absolute_error(y, predicted_home_prices))
# 1115.7467183128902


# %%


# Define model
melbourne_model = DecisionTreeRegressor()
# Fit model
melbourne_model.fit(train_X, train_y)
# get predicted prices on validation data
val_predictions = melbourne_model.predict(val_X)
print(mean_absolute_error(val_y, val_predictions))
# 278385.4673983215


# %%


def get_mae(max_leaf_nodes, train_X, val_X, train_y, val_y):
    model = DecisionTreeRegressor(max_leaf_nodes=max_leaf_nodes, random_state=0)
    model.fit(train_X, train_y)
    preds_val = model.predict(val_X)
    mae = mean_absolute_error(val_y, preds_val)
    return mae


# compare MAE with differing values of max_leaf_nodes
for max_leaf_nodes in [5, 50, 500, 5000]:
    my_mae = get_mae(max_leaf_nodes, train_X, val_X, train_y, val_y)
    print(
        "Max leaf nodes: %d  \t\t Mean Absolute Error:  %d" % (max_leaf_nodes, my_mae)
    )
# Max leaf nodes: 5          Mean Absolute Error:  385696
# Max leaf nodes: 50         Mean Absolute Error:  279794
# Max leaf nodes: 500        Mean Absolute Error:  261718
# Max leaf nodes: 5000       Mean Absolute Error:  271996


# %%


forest_model = RandomForestRegressor(random_state=1)
forest_model.fit(train_X, train_y)
melb_preds = forest_model.predict(val_X)
print(mean_absolute_error(val_y, melb_preds))


#%%

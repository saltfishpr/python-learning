# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @author: SaltFish
# @file: titanic.py
# @date: 2020/05/24
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

train_path = "datasets/titanic/train.csv"
test_path = "datasets/titanic/test.csv"
result_path = "datasets/titanic/result.csv"

train_data = pd.read_csv(train_path)
test_data = pd.read_csv(test_path)

features = ["Pclass", "Sex", "Age", "SibSp", "Parch"]
train_X = train_data[features]
test_X = test_data[features]
train_y = train_data["Survived"]

# 使用loc避免链式索引
train_X.loc[train_X["Sex"] == "male", ("Sex",)] = 1
train_X.loc[train_X["Sex"] == "female", ("Sex",)] = 0
test_X.loc[test_X["Sex"] == "male", ("Sex",)] = 1
test_X.loc[test_X["Sex"] == "female", ("Sex",)] = 0

# 使用前面一个值替换nan
train_X = train_X.fillna(method="ffill", axis=0)
test_X = test_X.fillna(method="ffill", axis=0)

# 使用线性方式填充nan
# train_X = train_X.interpolate(method="linear", axis=0)
# test_X = test_X.interpolate(method="linear", axis=0)

forest_model = RandomForestClassifier(random_state=1)
forest_model.fit(train_X, train_y)
pred_y = forest_model.predict(test_X)

result = pd.DataFrame(
    {"PassengerId": test_data.loc[:, "PassengerId"], "Survived": pd.Series(pred_y)}
)

result.to_csv(result_path, index=False)

# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @author: SaltFish
# @file: intermediate_ml.py
# @date: 2020/05/27
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.impute import SimpleImputer

# Read the data
X_full = pd.read_csv("datasets/HousingPricesCompetition/train.csv", index_col="Id")
X_test_full = pd.read_csv("datasets/HousingPricesCompetition/test.csv", index_col="Id")

# 删除缺少目标的行，将目标与预测变量分开
X_full.dropna(axis=0, subset=["SalePrice"], inplace=True)
y = X_full.SalePrice
X_full.drop(["SalePrice"], axis=1, inplace=True)

# 为简单起见，仅使用数值预测变量
X = X_full.select_dtypes(exclude=["object"])
X_test = X_test_full.select_dtypes(exclude=["object"])

# 从训练数据中分离验证集
X_train, X_valid, y_train, y_valid = train_test_split(
    X, y, train_size=0.8, test_size=0.2, random_state=0
)


# Function for comparing different approaches
def score_dataset(X_train, X_valid, y_train, y_valid):
    model = RandomForestRegressor(n_estimators=100, random_state=0)
    model.fit(X_train, y_train)
    preds = model.predict(X_valid)
    return mean_absolute_error(y_valid, preds)


#%%
# 仅删除缺失列
cols_with_missing = [col for col in X_train.columns if X_train[col].isnull().any()]
reduced_X_train = X_train.drop(cols_with_missing, axis=1)
reduced_X_valid = X_valid.drop(cols_with_missing, axis=1)
print(score_dataset(reduced_X_train, reduced_X_valid, y_train, y_valid))


#%%
# 用平均值填充缺失值
my_imputer = SimpleImputer()
imputed_X_train = pd.DataFrame(my_imputer.fit_transform(X_train))
imputed_X_valid = pd.DataFrame(my_imputer.transform(X_valid))
imputed_X_train.columns = X_train.columns
imputed_X_valid.columns = X_valid.columns
print(score_dataset(imputed_X_train, imputed_X_valid, y_train, y_valid))


#%%
final_imputer = SimpleImputer(strategy="median")
final_X_train = pd.DataFrame(final_imputer.fit_transform(X_train))
final_X_valid = pd.DataFrame(final_imputer.transform(X_valid))
final_X_train.columns = X_train.columns
final_X_valid.columns = X_valid.columns

# Define and fit model
model = RandomForestRegressor(n_estimators=100, random_state=0)
model.fit(final_X_train, y_train)

# Get validation predictions and MAE
preds_valid = model.predict(final_X_valid)
print("MAE (Your approach):")
print(mean_absolute_error(y_valid, preds_valid))

# Preprocess test data
final_X_test = pd.DataFrame(final_imputer.transform(X_test))
# Get test predictions
preds_test = model.predict(final_X_test)

# Save test predictions to file
# output = pd.DataFrame({"Id": X_test.index, "SalePrice": preds_test})
# output.to_csv("submission.csv", index=False)

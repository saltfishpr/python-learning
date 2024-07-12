# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @author : saltfish
# @Filename : intro_to_neural_nets.py
# @Date : 2020/4/3
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras import layers
from matplotlib import pyplot as plt
import seaborn as sns

pd.options.display.max_rows = 10
pd.options.display.float_format = "{:.1f}".format


def plot_the_loss_curve(epochs, mse):
    plt.figure()
    plt.xlabel("Epoch")
    plt.ylabel("Mean Squared Error")

    plt.plot(epochs, mse, label="Loss")
    plt.legend()
    plt.ylim([mse.min() * 0.95, mse.max() * 1.03])
    plt.show()


# # 创建简单的线性回归模型
# def create_model(my_learning_rate, feature_layer):
#     model = tf.keras.models.Sequential()
#     model.add(feature_layer)
#     model.add(tf.keras.layers.Dense(units=1, input_shape=(1,)))
#     model.compile(
#         optimizer=tf.keras.optimizers.RMSprop(lr=my_learning_rate),
#         loss="mean_squared_error",
#         metrics=[tf.keras.metrics.MeanSquaredError()],
#     )
#     return model


# def train_model(model, dataset, epochs, batch_size, label_name):
#     features = {name: np.array(value) for name, value in dataset.items()}
#     label = np.array(features.pop(label_name))
#     history = model.fit(
#         x=features, y=label, batch_size=batch_size, epochs=epochs, shuffle=True
#     )
#     epochs = history.epoch
#     hist = pd.DataFrame(history.history)
#     rmse = hist["mean_squared_error"]
#     return epochs, rmse


# 创建深度神经网络
def create_model(my_learning_rate, my_feature_layer):
    model = tf.keras.models.Sequential()
    # 添加特征层
    model.add(my_feature_layer)

    # Describe the topography of the model by calling the tf.keras.layers.Dense
    # method once for each layer. We've specified the following arguments:
    #   * units specifies the number of nodes in this layer.
    #   * activation specifies the activation function (Rectified Linear Unit).
    #   * name is just a string that can be useful when debugging.
    # 定义具有20个节点的第一个隐藏层，激活函数为relu函数，正则化为l2正则化
    model.add(
        tf.keras.layers.Dense(
            units=6,
            activation="relu",
            kernel_regularizer=tf.keras.regularizers.l2(l=0.03),
            name="Hidden1",
        )
    )
    # 添加Dropout正则化层
    # model.add(tf.keras.layers.Dropout(rate=0.25))
    # 定义具有12个节点的第二个隐藏层
    model.add(
        tf.keras.layers.Dense(
            units=4,
            activation="relu",
            kernel_regularizer=tf.keras.regularizers.l2(l=0.02),
            name="Hidden2",
        )
    )
    # 定义输出层
    model.add(tf.keras.layers.Dense(units=1, name="Output"))
    # 编译模型
    model.compile(
        optimizer=tf.keras.optimizers.Adam(lr=my_learning_rate),
        loss="mean_squared_error",
        metrics=[tf.keras.metrics.MeanSquaredError()],
    )

    return model


def train_model(model, dataset, epochs, label_name, batch_size=None):
    # Split the dataset into features and label.
    features = {name: np.array(value) for name, value in dataset.items()}
    label = np.array(features.pop(label_name))
    # 虽然将所有的特征都传入了fit函数，但只有在创建模型时的my_feature_layer中定义的特征才能被用到
    history = model.fit(
        x=features, y=label, batch_size=batch_size, epochs=epochs, shuffle=True
    )
    epochs = history.epoch
    hist = pd.DataFrame(history.history)
    mse = hist["mean_squared_error"]
    return epochs, mse


if __name__ == "__main__":
    # 加载数据集
    train_df = pd.read_csv(
        "https://download.mlcc.google.com/mledu-datasets/california_housing_train.csv"
    )
    # 打乱排序
    train_df = train_df.reindex(np.random.permutation(train_df.index))
    test_df = pd.read_csv(
        "https://download.mlcc.google.com/mledu-datasets/california_housing_test.csv"
    )
    # 标准化数据集
    train_df_mean = train_df.mean()
    train_df_std = train_df.std()
    train_df_norm = (train_df - train_df_mean) / train_df_std

    test_df_mean = test_df.mean()
    test_df_std = test_df.std()
    test_df_norm = (test_df - test_df_mean) / test_df_std

    # 创建一个列表，存放要使用的特征列
    feature_columns = []
    # 将特征列全部转换为Z-score，0.3度为一个分区
    resolution_in_Zs = 0.3
    # 经度
    latitude_as_a_numeric_column = tf.feature_column.numeric_column("latitude")
    latitude_boundaries = list(
        np.arange(
            int(min(train_df_norm["latitude"])),
            int(max(train_df_norm["latitude"])),
            resolution_in_Zs,
        )
    )
    latitude = tf.feature_column.bucketized_column(
        latitude_as_a_numeric_column, latitude_boundaries
    )
    # 纬度
    longitude_as_a_numeric_column = tf.feature_column.numeric_column("longitude")
    longitude_boundaries = list(
        np.arange(
            int(min(train_df_norm["longitude"])),
            int(max(train_df_norm["longitude"])),
            resolution_in_Zs,
        )
    )
    longitude = tf.feature_column.bucketized_column(
        longitude_as_a_numeric_column, longitude_boundaries
    )
    # 创建交叉特征
    latitude_x_longitude = tf.feature_column.crossed_column(
        [latitude, longitude], hash_bucket_size=100
    )
    crossed_feature = tf.feature_column.indicator_column(latitude_x_longitude)
    feature_columns.append(crossed_feature)

    # 将收入-中位数表示为浮点值
    median_income = tf.feature_column.numeric_column("median_income")
    feature_columns.append(median_income)

    # 将人口表示为浮点值
    population = tf.feature_column.numeric_column("population")
    feature_columns.append(population)

    # 将特征列表转换为一个层，稍后将其输入模型中。
    my_feature_layer = tf.keras.layers.DenseFeatures(feature_columns)

    # 超参数
    learning_rate = 0.007
    epochs = 150
    batch_size = 1000
    label_name = "median_house_value"

    # 简单的线性回归模型找到基线损失
    my_model = create_model(learning_rate, my_feature_layer)
    epochs, mse = train_model(my_model, train_df_norm, epochs, label_name, batch_size)
    plot_the_loss_curve(epochs, mse)
    test_features = {name: np.array(value) for name, value in test_df_norm.items()}
    test_label = np.array(test_features.pop(label_name))  # isolate the label
    print("\n Evaluate the new model against the test set:")
    my_model.evaluate(x=test_features, y=test_label, batch_size=batch_size)

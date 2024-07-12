# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @author : saltfish
# @Filename : validation_and_test_sets.py
# @Date : 2020/4/1
import numpy as np
import pandas as pd
import tensorflow as tf
from matplotlib import pyplot as plt

pd.options.display.max_rows = 10
pd.options.display.float_format = "{:.1f}".format


if __name__ == "__main__":
    train_df = pd.read_csv(
        "https://download.mlcc.google.com/mledu-datasets/california_housing_train.csv"
    )
    test_df = pd.read_csv(
        "https://download.mlcc.google.com/mledu-datasets/california_housing_test.csv"
    )
    # 缩放标签值
    scale_factor = 1000.0
    train_df["median_house_value"] /= scale_factor
    test_df["median_house_value"] /= scale_factor

    # 创建并编译简单的线性回归模型
    def build_model(my_learning_rate):
        # 最简单的tf.keras模型是顺序的
        model = tf.keras.models.Sequential()
        # 在模型中添加一个线性层以产生简单的线性回归
        model.add(tf.keras.layers.Dense(units=1, input_shape=(1,)))
        # 将模型拓扑编译为TensorFlow可以有效执行的代码。配置训练以最小化模型的均方误差
        model.compile(
            optimizer=tf.keras.optimizers.RMSprop(lr=my_learning_rate),
            loss="mean_squared_error",
            metrics=[tf.keras.metrics.RootMeanSquaredError()],
        )

        return model

    def train_model(
        model,
        df,
        feature,
        label,
        my_epochs,
        my_batch_size=None,
        my_validation_split=0.1,
    ):
        """Feed a dataset into the model in order to train it."""

        history = model.fit(
            x=df[feature],
            y=df[label],
            batch_size=my_batch_size,
            epochs=my_epochs,
            validation_split=my_validation_split,
        )

        # Gather the model's trained weight and bias.
        trained_weight = model.get_weights()[0]
        trained_bias = model.get_weights()[1]

        # The list of epochs is stored separately from the
        # rest of history.
        epochs = history.epoch

        # Isolate the root mean squared error for each epoch.
        hist = pd.DataFrame(history.history)
        rmse = hist["root_mean_squared_error"]

        return epochs, rmse, history.history

    # 绘制loss与epoch的曲线
    def plot_the_loss_curve(epochs, mae_training, mae_validation):
        plt.figure()
        plt.xlabel("Epoch")
        plt.ylabel("Root Mean Squared Error")

        plt.plot(epochs[1:], mae_training[1:], label="Training Loss")
        plt.plot(epochs[1:], mae_validation[1:], label="Validation Loss")
        plt.legend()

        # 不绘制第一步的图，因为第一步的损失通常远大于其他步的损失
        merged_mae_lists = mae_training[1:] + mae_validation[1:]
        highest_loss = max(merged_mae_lists)
        lowest_loss = min(merged_mae_lists)
        delta = highest_loss - lowest_loss
        print(delta)

        top_of_y_axis = highest_loss + (delta * 0.05)
        bottom_of_y_axis = lowest_loss - (delta * 0.05)

        plt.ylim([bottom_of_y_axis, top_of_y_axis])
        plt.show()

    # 对数据集进行随机排序
    shuffled_train_df = train_df.reindex(np.random.permutation(train_df.index))

    # 超参数
    learning_rate = 0.08
    epochs = 30
    batch_size = 100
    # 验证集和训练集之比
    validation_split = 0.2

    my_feature = "median_income"
    my_label = "median_house_value"

    # 舍弃该模型的任何先前版本
    my_model = None

    # 构建和训练模型
    my_model = build_model(learning_rate)
    epochs, rmse, history = train_model(
        my_model,
        shuffled_train_df,
        my_feature,
        my_label,
        epochs,
        batch_size,
        validation_split,
    )

    plot_the_loss_curve(
        epochs,
        history["root_mean_squared_error"],
        history["val_root_mean_squared_error"],
    )

    # 训练集和验证集的表现相差很多
    # 检查数据集发现数据集中的房屋信息是按照经度排序的

    x_test = test_df[my_feature]
    y_test = test_df[my_label]

    results = my_model.evaluate(x_test, y_test, batch_size=batch_size)

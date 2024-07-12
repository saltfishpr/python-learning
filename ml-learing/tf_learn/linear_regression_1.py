# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @author : saltfish
# @Filename : linear_regression_1.py
# @Date : 2020/3/30
import pandas as pd
import tensorflow as tf
from matplotlib import pyplot as plt


# 定义构建和训练模型的功能
def build_model(my_learning_rate):
    """
    创建并编译简单的线性回归模型
    """
    # 大多数简单的tf.keras模型都是顺序的
    # 顺序模型包含一个或多个层
    model = tf.keras.models.Sequential()

    # 描述模型的"地形"
    # 简单线性回归模型的地形是单层中的单个节点
    model.add(tf.keras.layers.Dense(units=1, input_shape=(1,)))

    # 将模型拓扑编译为TensorFlow可以有效执行的代码。配置训练以最小化模型的均方误差。
    model.compile(
        optimizer=tf.keras.optimizers.RMSprop(lr=my_learning_rate),
        loss="mean_squared_error",
        metrics=[tf.keras.metrics.RootMeanSquaredError()],
    )
    return model


def train_model(model, feature, label, epochs, batch_size):
    """
    提供数据来训练模型
    """

    # 将特征值和标签值输入模型。该模型将针对指定的时期数进行训练，逐步学习特征值与标签值之间的关系。
    history = model.fit(x=feature, y=label, batch_size=None, epochs=epochs)

    # 收集经过训练的模型的斜率和截距
    trained_weight = model.get_weights()[0]
    trained_bias = model.get_weights()[1]

    # epoch list与其他历史记录分开存储
    epochs = history.epoch

    # 收集每一步的历史记录（快照）
    hist = pd.DataFrame(history.history)

    # 收集每一步的均方根误差
    rmse = hist["root_mean_squared_error"]

    return trained_weight, trained_bias, epochs, rmse


def plot_the_model(trained_weight, trained_bias, feature, label):
    plt.xlabel("feature")
    plt.ylabel("label")

    plt.scatter(feature, label)
    # 创建代表模型的红线。红线开始于坐标（x0，y0），结束于坐标（x1，y1）
    x0 = 0
    y0 = trained_bias
    x1 = my_feature[-1]
    y1 = trained_bias + (trained_weight * x1)
    plt.plot([x0, x1], [y0, y1], c="r")
    # 绘制散点图和红线
    plt.show()


def plot_the_loss_curve(epochs, rmse):
    """
    绘制损失曲线，显示损失与步数。
    """

    plt.figure()
    plt.xlabel("Epoch")
    plt.ylabel("Root Mean Squared Error")

    plt.plot(epochs, rmse, label="Loss")
    plt.legend()
    plt.ylim([rmse.min() * 0.97, rmse.max()])
    plt.show()


if __name__ == "__main__":
    # 数据集
    my_feature = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0]
    my_label = [5.0, 8.8, 9.6, 14.2, 18.8, 19.5, 21.4, 26.8, 28.9, 32.0, 33.8, 38.2]
    learning_rate = 0.05  # 学习速率
    epochs = 100  # 步数
    my_batch_size = 1  # 一批的大小
    my_model = build_model(learning_rate)
    trained_weight, trained_bias, epochs, rmse = train_model(
        my_model, my_feature, my_label, epochs, my_batch_size
    )
    plot_the_model(trained_weight, trained_bias, my_feature, my_label)
    plot_the_loss_curve(epochs, rmse)

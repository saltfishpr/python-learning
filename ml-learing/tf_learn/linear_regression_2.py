# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @author : saltfish
# @Filename : linear_regression_2.py
# @Date : 2020/3/30
import pandas as pd
import numpy as np
import tensorflow as tf
from matplotlib import pyplot as plt

pd.options.display.max_rows = 10
pd.options.display.float_format = "{:.1f}".format

if __name__ == "__main__":
    # 导入数据集
    training_df = pd.read_csv(
        filepath_or_buffer="https://download.mlcc.google.com/mledu-datasets"
        "/california_housing_train.csv "
    )
    # 调整数据集
    training_df["median_house_value"] /= 1000.0
    training_df["rooms_per_person"] = (
        training_df["total_rooms"] / training_df["population"]
    )
    print(training_df.head())
    print(training_df.describe())

    training_df.corr()

    # 创建并编译简单的线性回归模型
    def build_model(my_learning_rate):
        model = tf.keras.models.Sequential()
        model.add(tf.keras.layers.Dense(units=1, input_shape=(1,)))
        model.compile(
            optimizer=tf.keras.optimizers.RMSprop(lr=my_learning_rate),
            loss="mean_squared_error",
            metrics=[tf.keras.metrics.RootMeanSquaredError()],
        )
        return model

    # 用数据训练模型
    def train_model(model, df, feature, label, epochs, batch_size):
        history = model.fit(x=df[feature], y=df[label], batch_size=None, epochs=epochs)
        trained_weight = model.get_weights()[0]
        trained_bias = model.get_weights()[1]
        epochs = history.epoch
        # 找出每个epoch的误差
        hist = pd.DataFrame(history.history)
        rmse = hist["root_mean_squared_error"]
        return trained_weight, trained_bias, epochs, rmse

    # 针对200个随机训练示例绘制训练模型
    def plot_the_model(trained_weight, trained_bias, feature, label):
        plt.xlabel(feature)
        plt.ylabel(label)

        # 从数据中抽取200个随机点创建散点图
        random_examples = training_df.sample(n=200)
        plt.scatter(random_examples[feature], random_examples[label])

        # 绘制预测线
        x0 = 0
        y0 = trained_bias
        x1 = 10000
        y1 = trained_bias + (trained_weight * x1)
        plt.plot([x0, x1], [y0, y1], c="r")
        plt.show()

    # 绘制损失，步数图像
    def plot_the_loss_curve(epochs, rmse):
        plt.figure()
        plt.xlabel("Epoch")
        plt.ylabel("Root Mean Squared Error")

        plt.plot(epochs, rmse, label="loss")
        plt.legend()
        plt.ylim([rmse.min() * 0.97, rmse.max()])
        plt.show()

    # 超参数
    learning_rate = 0.02
    epochs = 100
    batch_size = 30

    # 指定特征和标签
    my_feature = "median_income"
    my_label = "median_house_value"

    my_model = build_model(learning_rate)
    weight, bias, epochs, rmse = train_model(
        my_model, training_df, my_feature, my_label, epochs, batch_size
    )
    print("\nThe learned weight for your model is %.4f" % weight)
    print("The learned bias for your model is %.4f\n" % bias)
    plot_the_model(weight, bias, my_feature, my_label)
    plot_the_loss_curve(epochs, rmse)

    # 根据特征预测房屋价值
    def predict_house_values(n, feature, label):
        batch = training_df[feature][10000 : 10000 + n]
        predicted_values = my_model.predict_on_batch(x=batch)

        print("feature   label          predicted")
        print("  value   value          value")
        print("          in thousand$   in thousand$")
        print("--------------------------------------")
        for i in range(n):
            print(
                "%5.0f %6.0f %15.0f"
                % (
                    training_df[feature][i],
                    training_df[label][i],
                    predicted_values[i][0],
                )
            )

    print()
    predict_house_values(10, my_feature, my_label)

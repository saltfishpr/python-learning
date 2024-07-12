# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @author : saltfish
# @Filename : multi_class_classification_with_MNIST.py
# @Date : 2020/4/3
from __future__ import absolute_import, division, print_function, unicode_literals
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras import layers
from matplotlib import pyplot as plt

# The following lines adjust the granularity of reporting.
pd.options.display.max_rows = 10
pd.options.display.float_format = "{:.1f}".format

# The following line improves formatting when ouputting NumPy arrays.
np.set_printoptions(linewidth=200)


def plot_curve(epochs, hist, list_of_metrics):
    plt.figure()
    plt.xlabel("Epoch")
    plt.ylabel("Value")
    for m in list_of_metrics:
        x = hist[m]
        plt.plot(epochs[1:], x[1:], label=m)
    plt.legend()
    plt.show()


def create_model(my_learning_rate):
    model = tf.keras.models.Sequential()
    # 将图像展平成一维数组
    model.add(tf.keras.layers.Flatten(input_shape=(28, 28)))
    # 隐含层
    model.add(tf.keras.layers.Dense(units=256, activation="relu"))
    # 使用dropout正则化
    model.add(tf.keras.layers.Dropout(rate=0.3))
    model.add(tf.keras.layers.Dense(units=128, activation="relu"))
    model.add(tf.keras.layers.Dropout(rate=0.2))
    # unites参数设置为10，因为该模型必须在10个可能的输出值中进行选择
    model.add(tf.keras.layers.Dense(units=10, activation="softmax"))
    # 构建模型
    # 多类分类的损失函数与二分类的损失函数不同
    # sparse_categorical_crossentropy 稀疏分类交叉熵
    model.compile(
        optimizer=tf.keras.optimizers.Adam(lr=my_learning_rate),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def train_model(
    model, train_features, train_label, epochs, batch_size=None, validation_split=0.1
):
    history = model.fit(
        x=train_features,
        y=train_label,
        batch_size=batch_size,
        epochs=epochs,
        shuffle=True,
        validation_split=validation_split,  # 验证集比例
    )
    epochs = history.epoch
    hist = pd.DataFrame(history.history)
    return epochs, hist


if __name__ == "__main__":
    # 加载MNIST数据集
    (x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()
    plt.imshow(x_train[2917])
    plt.colorbar()
    plt.show()
    # 规格化特征值
    x_train_normalized = x_train / 255.0
    x_test_normalized = x_test / 255.0
    # 超参数
    learning_rate = 0.003
    epochs = 100
    batch_size = 4000
    validation_split = 0.2

    my_model = create_model(learning_rate)
    epochs, hist = train_model(
        my_model, x_train_normalized, y_train, epochs, batch_size, validation_split
    )
    list_of_metrics_to_plot = ["accuracy"]
    plot_curve(epochs, hist, list_of_metrics_to_plot)
    print("\n Evaluate the new model against the test set:")
    my_model.evaluate(x=x_test_normalized, y=y_test, batch_size=batch_size)

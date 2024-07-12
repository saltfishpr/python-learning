# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @author : saltfish
# @Filename : representation_with_feature_cross.py
# @Date : 2020/4/1
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import feature_column
from tensorflow.keras import layers

from matplotlib import pyplot as plt

# The following lines adjust the granularity of reporting.
pd.options.display.max_rows = 10
pd.options.display.float_format = "{:.1f}".format

tf.keras.backend.set_floatx("float32")

if __name__ == "__main__":
    # 加载，缩放和随机排序
    # Load the dataset
    train_df = pd.read_csv(
        "https://download.mlcc.google.com/mledu-datasets/california_housing_train.csv"
    )
    test_df = pd.read_csv(
        "https://download.mlcc.google.com/mledu-datasets/california_housing_test.csv"
    )

    # Scale the labels
    scale_factor = 1000.0
    # Scale the training set's label.
    train_df["median_house_value"] /= scale_factor
    # Scale the test set's label
    test_df["median_house_value"] /= scale_factor

    # Shuffle the examples
    train_df = train_df.reindex(np.random.permutation(train_df.index))

    resolution_in_degrees = 0.5

    # 创建一个空列表，该列表将最终包含所有特征
    feature_columns = []

    # 创建一个数值特征列来表示纬度
    latitude_as_a_numeric_column = tf.feature_column.numeric_column("latitude")
    latitude_boundaries = list(
        np.arange(
            int(min(train_df["latitude"])),
            int(max(train_df["latitude"])),
            resolution_in_degrees,
        )
    )
    latitude = tf.feature_column.bucketized_column(
        latitude_as_a_numeric_column, latitude_boundaries
    )

    # 创建一个数字特征列来表示经度
    longitude_as_a_numeric_column = tf.feature_column.numeric_column("longitude")
    longitude_boundaries = list(
        np.arange(
            int(min(train_df["longitude"])),
            int(max(train_df["longitude"])),
            resolution_in_degrees,
        )
    )
    longitude = tf.feature_column.bucketized_column(
        longitude_as_a_numeric_column, longitude_boundaries
    )

    # 创建经纬度交叉的特征
    latitude_x_longitude = tf.feature_column.crossed_column(
        [latitude, longitude], hash_bucket_size=100
    )
    crossed_feature = tf.feature_column.indicator_column(latitude_x_longitude)
    feature_columns.append(crossed_feature)

    # 将特征列表转换为最终将成为模型一部分的图层
    feature_cross_feature_layer = layers.DenseFeatures(feature_columns)

    def create_model(my_learning_rate, feature_layer):
        # Most simple tf.keras models are sequential.
        model = tf.keras.models.Sequential()

        # 将包含特征列的图层添加到模型
        model.add(feature_layer)

        # 在模型中添加一个线性层以产生简单的线性回归
        model.add(tf.keras.layers.Dense(units=1, input_shape=(1,)))

        # 将这些层构建为TensorFlow可以执行的模型
        model.compile(
            optimizer=tf.keras.optimizers.RMSprop(lr=my_learning_rate),
            loss="mean_squared_error",
            metrics=[tf.keras.metrics.RootMeanSquaredError()],
        )

        return model

    def train_model(model, dataset, epochs, batch_size, label_name):
        features = {name: np.array(value) for name, value in dataset.items()}
        label = np.array(features.pop(label_name))
        history = model.fit(
            x=features, y=label, batch_size=batch_size, epochs=epochs, shuffle=True
        )

        # The list of epochs is stored separately from the rest of history.
        epochs = history.epoch

        # Isolate the mean absolute error for each epoch.
        hist = pd.DataFrame(history.history)
        rmse = hist["root_mean_squared_error"]

        return epochs, rmse

    def plot_the_loss_curve(epochs, rmse):
        plt.figure()
        plt.xlabel("Epoch")
        plt.ylabel("Root Mean Squared Error")

        plt.plot(epochs, rmse, label="Loss")
        plt.legend()
        plt.ylim([rmse.min() * 0.94, rmse.max() * 1.05])
        plt.show()

    learning_rate = 0.03
    epochs = 100
    batch_size = 100
    label_name = "median_house_value"

    my_model = create_model(learning_rate, feature_cross_feature_layer)
    epochs, rmse = train_model(my_model, train_df, epochs, batch_size, label_name)
    plot_the_loss_curve(epochs, rmse)

    print("\nEvaluate the new model against the test set:")
    test_features = {name: np.array(value) for name, value in test_df.items()}
    test_label = np.array(test_features.pop(label_name))
    my_model.evaluate(x=test_features, y=test_label, batch_size=batch_size)

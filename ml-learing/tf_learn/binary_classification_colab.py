# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @author : saltfish
# @Filename : binary_classification_colab.py
# @Date : 2020/4/2
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import feature_column
from tensorflow.keras import layers
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
    # shuffle the training set
    train_df = train_df.reindex(np.random.permutation(train_df.index))
    # 计算训练集中各列的Z-score，并将这些Z-score写入名为train_df_norm的新DataFrame中
    train_df_mean = train_df.mean()
    train_df_std = train_df.std()
    train_df_norm = (train_df - train_df_mean) / train_df_std
    print(train_df_norm.head())

    test_df_mean = test_df.mean()
    test_df_std = test_df.std()
    test_df_norm = (test_df - test_df_mean) / test_df_std

    threshold = 265000
    train_df_norm["median_house_value_is_high"] = (
        train_df["median_house_value"] > threshold
    ).astype(float)
    test_df_norm["median_house_value_is_high"] = (
        test_df["median_house_value"] > threshold
    ).astype(float)
    print(train_df_norm["median_house_value_is_high"].head(8000))

    feature_columns = []
    median_income = tf.feature_column.numeric_column("median_income")
    feature_columns.append(median_income)
    tr = tf.feature_column.numeric_column("total_rooms")
    feature_columns.append(tr)
    feature_layer = layers.DenseFeatures(feature_columns)
    print(feature_layer(dict(train_df_norm)))

    def create_model(my_learning_rate, feature_layer, my_metrics):
        model = tf.keras.models.Sequential()

        # 将特征层（特征列表及其表示方式）添加到模型中
        model.add(feature_layer)  # 输入层

        # 通过S型函数将回归值集中
        model.add(
            tf.keras.layers.Dense(units=1, input_shape=(1,), activation=tf.sigmoid),
        )

        # 使用分类的loss function
        model.compile(
            optimizer=tf.keras.optimizers.RMSprop(lr=my_learning_rate),
            loss=tf.keras.losses.BinaryCrossentropy(),
            metrics=my_metrics,
        )

        return model

    def train_model(model, dataset, epochs, label_name, batch_size=None, shuffle=True):
        """Feed a dataset into the model in order to train it."""

        # The x parameter of tf.keras.Model.fit can be a list of arrays, where
        # each array contains the data for one feature.  Here, we're passing
        # every column in the dataset. Note that the feature_layer will filter
        # away most of those columns, leaving only the desired columns and their
        # representations as features.
        features = {name: np.array(value) for name, value in dataset.items()}
        label = np.array(features.pop(label_name))
        history = model.fit(
            x=features, y=label, batch_size=batch_size, epochs=epochs, shuffle=shuffle
        )

        epochs = history.epoch
        hist = pd.DataFrame(history.history)

        return epochs, hist

    def plot_curve(epochs, hist, list_of_metrics):
        plt.figure()
        plt.xlabel("Epoch")
        plt.ylabel("Value")

        for m in list_of_metrics:
            x = hist[m]
            plt.plot(epochs[1:], x[1:], label=m)

        plt.legend()
        plt.show()

    # # The following variables are the hyperparameters.
    # learning_rate = 0.001
    # epochs = 20
    # batch_size = 100
    # label_name = "median_house_value_is_high"
    # classification_threshold = 0.5
    #
    # # Establish the metrics the model will measure.
    # METRICS = [
    #     tf.keras.metrics.BinaryAccuracy(
    #         name="accuracy", threshold=classification_threshold
    #     ),
    #     tf.keras.metrics.Precision(
    #         thresholds=classification_threshold, name="precision"
    #     ),
    #     tf.keras.metrics.Recall(thresholds=classification_threshold, name="recall"),
    # ]

    learning_rate = 0.001
    epochs = 20
    batch_size = 100
    label_name = "median_house_value_is_high"

    METRICS = [
        tf.keras.metrics.AUC(num_thresholds=100, name="auc"),
    ]

    # Establish the model's topography.
    my_model = create_model(learning_rate, feature_layer, METRICS)
    # Train the model on the training set.
    epochs, hist = train_model(my_model, train_df_norm, epochs, label_name, batch_size)
    # Plot a graph of the metric(s) vs. epochs.
    list_of_metrics_to_plot = ["auc"]
    plot_curve(epochs, hist, list_of_metrics_to_plot)

    # 测试
    features = {name: np.array(value) for name, value in test_df_norm.items()}
    label = np.array(features.pop(label_name))
    my_model.evaluate(x=features, y=label, batch_size=batch_size)

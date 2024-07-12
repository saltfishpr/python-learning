# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @author: SaltFish
# @file: first.py
# @date: 2020/05/27
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# %%

museum_path = "datasets/visualization/museum_visitors.csv"
museum_data = pd.read_csv(museum_path, index_col="Date", parse_dates=True)
# 折线图
plt.figure(figsize=(14, 6))  # 调整图表大小
plt.title("museum visitors")  # 图表标题
plt.xlabel("Date")  # 坐标轴名
sns.lineplot(data=museum_data)
plt.show()

# %%

ign_path = "datasets/visualization/ign_scores.csv"
ign_data = pd.read_csv(ign_path, index_col="Platform")
# 条形图
# 设置图形的宽度和高度
plt.figure(figsize=(8, 6))
# 条形图显示了按平台划分的赛车游戏的平均得分
sns.barplot(x=ign_data["Racing"], y=ign_data.index)
plt.xlabel("")
plt.title("Average Score for Racing Games, by Platform")
plt.show()

# 热图
# 设置图形的宽度和高度
plt.figure(figsize=(10, 10))
# 热图显示按平台和类型划分的平均游戏得分
sns.heatmap(ign_data, annot=True)
# 为横轴添加标签
plt.xlabel("Genre")
# 为纵轴添加标签
plt.title("Average Game Score, by Platform and Genre")
plt.show()

# %%

insurance_filepath = "datasets/visualization/insurance.csv"
insurance_data = pd.read_csv(insurance_filepath)

# scatter plots 散点图
sns.scatterplot(x=insurance_data["bmi"], y=insurance_data["charges"])

# regression line 回归线
sns.regplot(x=insurance_data["bmi"], y=insurance_data["charges"])
plt.show()

# 彩色散点图 描述两个群组
sns.scatterplot(
    x=insurance_data["bmi"], y=insurance_data["charges"], hue=insurance_data["smoker"]
)
plt.show()

# 绘制散点图和两个群组的斜率
sns.lmplot(x="bmi", y="charges", hue="smoker", data=insurance_data)
plt.show()

# swarmplot 分簇散点图
sns.swarmplot(x=insurance_data["smoker"], y=insurance_data["charges"])
plt.show()

# %%
iris_path = "datasets/visualization/Iris.csv"
iris_data = pd.read_csv(iris_path)

# 直方图
sns.distplot(a=iris_data["PetalLengthCm"], kde=False)
plt.show()

# KDE plot (核密度估计)
sns.kdeplot(data=iris_data["PetalLengthCm"], shade=True)
plt.show()

# 2D KDE plot
sns.jointplot(x=iris_data["PetalLengthCm"], y=iris_data["SepalWidthCm"], kind="kde")
plt.show()

iris_set_data = iris_data.loc[iris_data["Species"] == "Iris-setosa"]
iris_ver_data = iris_data.loc[iris_data["Species"] == "Iris-versicolor"]
iris_vir_data = iris_data.loc[iris_data["Species"] == "Iris-virginica"]

# 每个物种的直方图
sns.distplot(a=iris_set_data["PetalLengthCm"], label="Iris-setosa", kde=False)
sns.distplot(a=iris_ver_data["PetalLengthCm"], label="Iris-versicolor", kde=False)
sns.distplot(a=iris_vir_data["PetalLengthCm"], label="Iris-virginica", kde=False)
# 添加标题
plt.title("Histogram of Petal Lengths, by Species")
# 强制图例出现
plt.legend()
plt.show()

# KDE plots for each species
sns.kdeplot(data=iris_set_data["PetalLengthCm"], label="Iris-setosa", shade=True)
sns.kdeplot(data=iris_ver_data["PetalLengthCm"], label="Iris-versicolor", shade=True)
sns.kdeplot(data=iris_vir_data["PetalLengthCm"], label="Iris-virginica", shade=True)
# Add title
plt.title("Distribution of Petal Lengths, by Species")
plt.show()

# %%

spotify_path = "datasets/visualization/spotify.csv"
spotify_data = pd.read_csv(spotify_path, index_col="Date", parse_dates=True)

# Change the style of the figure to the "dark" theme
sns.set_style("ticks")
# Line chart
plt.figure(figsize=(12, 6))
sns.lineplot(data=spotify_data)
plt.show()

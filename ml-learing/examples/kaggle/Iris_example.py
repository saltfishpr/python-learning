# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @author: SaltFish
# @file: Iris_example.py
# @date: 2020/05/29
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn import metrics
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

sns.set_palette("husl")
data = pd.read_csv("datasets/visualization/Iris.csv")

#%%

data.head()
data.info()
data.describe()
data["Species"].value_counts()

#%%

tmp = data.drop("Id", axis=1)
g = sns.pairplot(tmp, hue="Species", markers="+")
plt.show()

#%%

g = sns.violinplot(y="Species", x="SepalLengthCm", data=data, inner="quartile")
plt.show()
g = sns.violinplot(y="Species", x="SepalWidthCm", data=data, inner="quartile")
plt.show()
g = sns.violinplot(y="Species", x="PetalLengthCm", data=data, inner="quartile")
plt.show()
g = sns.violinplot(y="Species", x="PetalWidthCm", data=data, inner="quartile")
plt.show()

#%%
# Modeling with scikit-learn
X = data.drop(["Id", "Species"], axis=1)
y = data["Species"]
# print(X.head())
print(X.shape)
# print(y.head())
print(y.shape)

# experimenting with different n values
k_range = list(range(1, 26))
scores = []
for k in k_range:
    knn = KNeighborsClassifier(n_neighbors=k)
    knn.fit(X, y)
    y_pred = knn.predict(X)
    scores.append(metrics.accuracy_score(y, y_pred))

plt.plot(k_range, scores)
plt.xlabel("Value of k for KNN")
plt.ylabel("Accuracy Score")
plt.title("Accuracy Scores for Values of k of k-Nearest-Neighbors")
plt.show()

logreg = LogisticRegression()
logreg.fit(X, y)
y_pred = logreg.predict(X)
print(metrics.accuracy_score(y, y_pred))


#%%

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4, random_state=5)
# experimenting with different n values
k_range = list(range(1, 26))
scores = []
for k in k_range:
    knn = KNeighborsClassifier(n_neighbors=k)
    knn.fit(X_train, y_train)
    y_pred = knn.predict(X_test)
    scores.append(metrics.accuracy_score(y_test, y_pred))

plt.plot(k_range, scores)
plt.xlabel("Value of k for KNN")
plt.ylabel("Accuracy Score")
plt.title("Accuracy Scores for Values of k of k-Nearest-Neighbors")
plt.show()

logreg = LogisticRegression()
logreg.fit(X_train, y_train)
y_pred = logreg.predict(X_test)
print(metrics.accuracy_score(y_test, y_pred))

knn = KNeighborsClassifier(n_neighbors=12)
knn.fit(X, y)
# make a prediction for an example of an out-of-sample observation
knn.predict([[6, 3, 4, 2]])

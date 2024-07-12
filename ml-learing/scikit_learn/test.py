# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @author: saltfish
# @file: test.py
# @date: 2020/05/23
from sklearn import datasets
import matplotlib.pyplot as plt
import tensorflow as tf

digits = datasets.load_digits()
data = digits.images.reshape((digits.images.shape[0], -1))  # 将图像变成一维特征向量

if __name__ == "__main__":
    pass

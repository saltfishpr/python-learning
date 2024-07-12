# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @author: SaltFish
# @file: intro_pandas.py
# @date: 2020/05/25
import pandas as pd

reviews = pd.read_csv("datasets/winemag-data-130k-v2.csv")
canadian_youtube = pd.read_csv("datasets/trending_youtube/CAvideos.csv")
british_youtube = pd.read_csv("datasets/trending_youtube/GBvideos.csv")


#%%


pd.DataFrame({"Yes": [50, 21], "No": [131, 2]})
pd.DataFrame(
    {"Bob": ["I liked it.", "It was awful."], "Sue": ["Pretty good.", "Bland."]}
)
pd.DataFrame(
    {"Bob": ["I liked it.", "It was awful."], "Sue": ["Pretty good.", "Bland."]},
    index=["Product A", "Product B"],
)
pd.Series([1, 2, 3, 4, 5])
pd.Series(
    [30, 35, 40], index=["2015 Sales", "2016 Sales", "2017 Sales"], name="Product A"
)

# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @author: saltfish
# @file: test_factory.py
# @date: 2020/05/21
from flaskr import create_app


def test_config():
    assert not create_app().testing
    assert create_app({"TESTING": True}).testing


# def test_hello(client):
#     response = client.get("/hello")
#     assert response.data == b"Hello, World!"

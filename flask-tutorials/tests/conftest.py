# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @author: saltfish
# @file: conftest.py
# @date: 2020/05/21
import os
import tempfile

import pytest
from flaskr import create_app
from flaskr.db import get_db, init_db

with open(os.path.join(os.path.dirname(__file__), "data.sql"), "rb") as f:
    _data_sql = f.read().decode("utf8")


@pytest.fixture
def app():
    # 创建并打开一个临时文件，返回该文件对象和路径。
    # DATABASE 路径被重载，这样它会指向临时路径，而不是实例文件夹。
    # 设置好路径之后，数据库表被创建，然后插入数据。测试结束后，临时文件会被关闭并删除。
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({"TESTING": True, "DATABASE": db_path})

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username="test", password="test"):
        return self._client.post(
            "/auth/login", data={"username": username, "password": password}
        )

    def logout(self):
        return self._client.get("/auth/logout")


@pytest.fixture
def auth(client):
    return AuthActions(client)

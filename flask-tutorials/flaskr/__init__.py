# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @author: saltfish
# @file: __init__.py.py
# @date: 2020/05/20
import os

from flask import Flask
from . import auth, blog
from . import db


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev", DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)  # 注册命令
    app.register_blueprint(auth.bp)  # 注册认证蓝图
    app.register_blueprint(blog.bp)  # 注册博客蓝图

    # 关联端点名称 'index' 和 / URL
    # 这样 url_for('index') 或 url_for('blog.index') 都会有效
    # 会生成同样的 / URL
    app.add_url_rule("/", endpoint="index")

    return app

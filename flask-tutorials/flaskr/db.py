# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @author: saltfish
# @file: db.py
# @date: 2020/05/20
import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    """
    返回一个数据库连接
    :return: 数据库连接
    """
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))


@click.command("init-db")  # 定义一个名为 init-db 命令行，它调用 init_db 函数
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")


def init_app(app):
    app.teardown_appcontext(close_db)  # 告诉 Flask 在返回响应后进行清理的时候调用此函数
    app.cli.add_command(init_db_command)  # 添加一个新的可以与 flask 一起工作的命令

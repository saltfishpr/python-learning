# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @author: saltfish
# @file: auth.py
# @date: 2020/05/20
"""
认证蓝图 Blueprint
认证蓝图将包括注册新用户、登录和注销视图。
"""
import functools

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint("auth", __name__, url_prefix="/auth")  # url_prefix 会添加到所有与该蓝图关联的 URL 前面


@bp.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None

        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."
        elif (
            db.execute(
                "SELECT id FROM user WHERE username = '{}'".format(username)
            ).fetchone()
            is not None
        ):
            error = "User {} is already registered.".format(username)

        if error is None:
            db.execute(
                "INSERT INTO user (username, password) VALUES (?, ?)",
                (username, generate_password_hash(password)),
            )
            db.commit()
            return redirect(url_for("auth.login"))

        flash(error)  # 用于储存在渲染模块时可以调用的信息

    return render_template("auth/register.html")  # 渲染一个包含 HTML 的模板


@bp.route("/login", methods=("GET", "POST"))
def login():
    """
    进行登录验证
    :return:
    """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None
        user = db.execute(
            "SELECT * FROM user WHERE username = '{}'".format(username)
        ).fetchone()

        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user["password"], password):
            error = "Incorrect password."

        if error is None:
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("index"))

        flash(error)

    return render_template("auth/login.html")


@bp.before_app_request  # 注册一个在视图函数之前运行的函数，不论其 URL 是什么
def load_logged_in_user():
    """
    检查用户 id 是否已经储存在 session 中，并从数据库中获取用户数据，然后储存在 g.user 中。
    g.user 的持续时间比请求要长。如果没有用户 id ，或者 id 不存在，那么 g.user 将会是 None 。
    :return: Nothing
    """
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = (
            get_db()
            .execute("SELECT * FROM user WHERE id = {}".format(user_id))
            .fetchone()
        )


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


def login_required(view):
    """
    装饰器 用于身份验证
    :param view:
    :return:
    """

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))
        return view(**kwargs)

    return wrapped_view

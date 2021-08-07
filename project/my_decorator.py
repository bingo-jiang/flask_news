# coding=gbk
from flask import redirect, request, session, current_app, g
from functools import wraps
from project.models import User


# 自定义用户对象实现登录校验
def login_auth(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if not request.user:
            return redirect("/login")
        return function(*args, **kwargs)

    return wrapper


# 配合flask的g对象实现登录校验
def login_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        # 获取session中的user_id
        user_id = session.get("user_id")
        user_mobile = session.get("user_mobile")
        # 获取用户对象
        user_obj = None
        if user_id and user_mobile:
            try:
                user_obj = User.query.filter(User.id == user_id, User.mobile == user_mobile).first()
            except Exception as e:
                current_app.logger(e)
        g.user = user_obj
        if not g.user:
            return redirect("/login")
        return function(*args, **kwargs)

    return wrapper


# 管理员登录校验
def admin_auth(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not request.admin:
            return redirect("/admin/index")
        return view_func(*args, **kwargs)
    return wrapper

from flask import Flask, request, session, render_template
from project.models import db
from flask_session import Session
from flask_wtf.csrf import CSRFProtect, generate_csrf  # csrf配置(防止csrf攻击)
import logging
from logging.handlers import RotatingFileHandler
import setting
from redis import Redis

redis_connect = None


def create_app(config_name):
    app = Flask(__name__)
    # 配置设置
    config = setting.config_dict.get(config_name)
    app.config.from_object(config)
    # 定义redis连接
    global redis_connect
    redis_connect = Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, password=config.REDIS_PASSWORD)
    # 日志
    log_file(config.LEVEL_NAME)
    # session
    Session(app)
    # csrf防护
    CSRFProtect(app)
    # 数据库
    db.init_app(app)
    # 自定义过滤器注册（参数1：函数名，参数2：过滤器名字）
    from project.template_tag import class_filter, transfer_time, to_category,digest_format,flask_url_deal
    app.add_template_filter(class_filter, "my_tag")
    app.add_template_filter(transfer_time, "transfer_time")
    app.add_template_filter(to_category, "to_category")
    app.add_template_filter(digest_format, "digest_format")
    app.add_template_filter(flask_url_deal, "flask_url_deal")
    # 蓝图注册
    from project.views import account, news_category, news_details, user,admin
    app.register_blueprint(account.ac)
    app.register_blueprint(news_category.nc)
    app.register_blueprint(news_details.details)
    app.register_blueprint(user.user)
    app.register_blueprint(admin.admin)

    @app.before_request
    def before_request():
        request.user = None
        request.category = None
        mobile = session.get("user")
        if not mobile:
            mobile = session.get("admin")
        user_obj = models.User.query.filter(models.User.mobile == mobile).first()
        category_obj = models.Category.query.all()
        if category_obj:
            request.category = category_obj
        if mobile and user_obj:
            request.user = user_obj
            return
        return

    @app.after_request
    def after_request(response):
        csrf_token = generate_csrf()
        response.set_cookie('csrf_token', csrf_token)
        return response

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404

    return app


def log_file(LEVEL_NAME):
    logging.basicConfig(level=LEVEL_NAME)
    file_handler = RotatingFileHandler('logs/log', maxBytes=1024*1024*10, backupCount=100)
    formatter = logging.Formatter(fmt="%(asctime)s->%(levelname)s->%(filename)s第%(lineno)d行: %(message)s")
    file_handler.setFormatter(formatter)
    logging.getLogger().addHandler(file_handler)

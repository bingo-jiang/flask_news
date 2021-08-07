import datetime
import random
from flask import Blueprint, render_template, session, request, jsonify, url_for, redirect
from flask import current_app, send_file

from project.script.get_param_list import flask_get_per_param_list
from project.script.pic_code import check_code
from io import BytesIO
from project import my_forms
from project import models
from project import redis_connect
from project.models import db
import logging

# from flask_wtf.csrf import generate_csrf
# from sqlalchemy import or_, and_, text

ac = Blueprint('ac', __name__, template_folder='news/templates', static_folder='news/static')


@ac.route('/')
def redirect_to_index():
    # status_list = flask_get_per_param_list(request.url,"status")
    # category_id_list = flask_get_per_param_list(request.url,"category_id")
    # # # 允许的筛选条件
    # # allow_filter_name = ['status', 'category_id']
    # if status_list and category_id_list:
    #     print("all")
    #     objs=models.News.query.filter(models.News.status.in_(status_list),models.News.category_id.in_(category_id_list)).all()
    # elif status_list and not category_id_list:
    #     print("status")
    #     objs = models.News.query.filter(models.News.status.in_(status_list)).all()
    # elif not status_list and category_id_list:
    #     print("category")
    #     objs = models.News.query.filter(models.News.category_id.in_(category_id_list)).all()
    # else:
    #     print("none")
    #     objs=models.News.query.all()
    # print(status_list,category_id_list,objs[0:5])
    # return "666"
    return redirect(url_for("ac.index"))


@ac.route('/index', methods=['GET', 'POST'], endpoint='index')
def index():
    # 查询点击量多的10条资讯
    hot_news = None
    latest_news = None
    data = {}
    try:
        hot_news = models.News.query.order_by(models.News.clicks.desc()).limit(10).all()
        suggestions = models.News.query.order_by(models.News.collected_counts.desc()).limit(10).all()
        # latest_notice = models.Notice.query.order_by(models.Notice.update_time.desc()).first()
    except Exception as e:
        logging.error(e)
        data['news-error'] = "无法访问数据库"
        hot_news = []
        suggestions = []
        # latest_notice = None
    data['hot_news'] = hot_news
    data['suggestions'] = suggestions
    # data['latest_notice'] = latest_notice
    return render_template('index.html', request=request, data=data)


@ac.route('/favicon.ico', methods=['GET', 'POST'], endpoint='logo')
def logo():
    return current_app.send_static_file('images/02.ico')


@ac.route('/login', methods=['GET', 'POST'], endpoint='login')
def login():
    if request.method == 'GET':
        return render_template('login.html', request=request)
    # 获取请求参数
    mobile = request.form.get('mobile')
    password = request.form.get('password')
    pic_code = request.form.get('pic_code')
    img_id = request.form.get('img_id')
    # 校验图片验证码
    redis_code = str(redis_connect.get(img_id), encoding='utf-8')
    if str(pic_code).upper() != str(redis_code).upper():
        return jsonify(status=False, error=[{"for_pic_code": "验证码错误"}])
    try:
        user_obj = models.User.query.filter(models.User.mobile == mobile).first()
    except Exception as e:
        logging.info(e)
        return jsonify(status=False, error=[{"db_error": "数据库请求错误"}])
    if not user_obj:
        logging.info(mobile + "账号错误或还没有注册")
        return jsonify(status=False, error=[{"for_mobile": "账号错误或还没有注册"}])
    if not user_obj.check_password(password):
        logging.info(mobile + "密码错误")
        return jsonify(status=False, error=[{"for_password": "密码错误"}])
    session['user_id'] = user_obj.id
    session['user'] = mobile
    try:
        user_obj.last_login = datetime.datetime.now()
        db.session.commit()
    except Exception as e:
        logging.info(e)
    return jsonify(status=True, data='/')


@ac.route('/logout', methods=['GET'], endpoint='logout')
def logout():
    session.pop("user_id", None)
    session.pop("user", None)
    return redirect('/login')


@ac.route('/register', methods=['GET', 'POST'], endpoint='register')
def register():
    if request.method == 'GET':
        form = my_forms.RegisterForm()
        return render_template('register.html', form=form, request=request)
    else:
        form = my_forms.RegisterForm(formdata=request.form)
        logging.info(request.form)
        if form.validate():
            mobile = request.form.get("mobile")
            password_hash = request.form.get("password_hash")
            post_code = request.form.get("sms_code")
            sms_code = str(redis_connect.get(mobile), encoding='utf-8')
            if not sms_code:
                logging.error(mobile + "短信验证码过期")
                return jsonify({'status': False, 'sms_error': "短信验证码过期"})
            if str(post_code) != sms_code:
                logging.error(mobile + "短信验证码错误")
                return jsonify({'status': False, 'sms_error': "短信验证码错误"})

            user_obj = models.User()
            user_obj.nick_name = mobile
            user_obj.password = password_hash
            user_obj.mobile = mobile
            user_obj.signature = "该用户很懒，什么都没写..."
            try:
                db.session.add(user_obj)
                db.session.commit()
            except Exception as e:
                logging.info(e)
                return jsonify({'status': False, 'db_error': "注册失败"})
            redis_connect.delete(mobile)
            return jsonify(status=True, data="/login")
        else:
            logging.info(form.errors)
            return jsonify({'status': False, 'error': form.errors})


@ac.route('/code', endpoint='code')
def code():
    try:
        img_id = request.args.get('img_id')
        img_obj, code = check_code('project/script/font_file/Monaco.ttf')
        redis_connect.set(name=img_id, value=code, ex=300)
        stream = BytesIO()
        img_obj.save(stream, 'png')
    except Exception as e:
        logging.error(e)
        return jsonify(staus=False, error=e)
    return stream.getvalue()


@ac.route('/send/sms', endpoint='send_sms')
def send_sms():
    mobile = request.args.get('mobile')
    img_code = request.args.get('img_code')
    img_id = request.args.get('img_id')
    pic_code = str(redis_connect.get(img_id), encoding='utf-8')
    # 生成验证码并存储到Redis
    sms_code = random.randrange(100000, 999999)
    redis_connect.set(mobile, sms_code)
    # 校验手机号格式、是否注册过
    import re
    pattern = r'^1[3456789]\d{9}$'
    res = re.search(pattern, str(mobile))
    if not res:
        logging.info("手机格式错误")
        return jsonify(status=False, error="手机格式错误")
    user_obj = models.User.query.filter(models.User.mobile == mobile).first()
    logging.info(user_obj)
    if user_obj:
        return jsonify(status=False, error="该手机已经注册过了")
    # 校验图片验证码
    if str(img_code).upper() != pic_code.upper():
        logging.info("图片验证码错误")
        return jsonify(status=False, error="图片验证码错误")
    # return jsonify(status=True)
    return jsonify(status=True,code=sms_code)

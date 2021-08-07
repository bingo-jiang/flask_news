from flask import Blueprint, render_template, session, request, jsonify, url_for, redirect
from project import models
import logging
from flask_wtf.csrf import generate_csrf

nc = Blueprint("nc", __name__)


@nc.route('/get_news')
def news():
    # 获取参数
    category_id = request.args.get('cid', "1")
    page = request.args.get('page', "1")
    per_page = request.args.get('per_page', "10")
    # 参数类型转换
    try:
        page = int(page)
        per_page = int(per_page)
    except Exception as e:
        logging.error(e)
        page = 1
        per_page = 10
    try:
        if category_id == "1":
            news_obj = models.News.query.filter(models.News.status == 1).order_by(
                models.News.create_time.desc())
        else:
            news_obj = models.News.query.filter(models.News.category_id == category_id,
                                                models.News.status == 1).order_by(
                models.News.create_time.desc())
        paginate_obj = news_obj.paginate(page, per_page, False)
    except Exception as e:
        logging.error(e)
        return jsonify(status=False, error="请求错误：%s" % e)
    # 获取分页对象的属性
    total_page = paginate_obj.pages
    current_page = paginate_obj.page
    all_objs = paginate_obj.items
    logging.info("分类ID:" + str(category_id) + ";数据集:" + str(news_obj.all()))
    news_list = []
    for item in all_objs:
        news_list.append(item.to_dict())
    if news_list.__len__() == 0:
        error_url = url_for('static', filename='images/loading.gif', _external=True)
        logging.info(error_url)
        return jsonify(status=False, error=error_url)
    return jsonify(status=True, totalPage=total_page, newsList=news_list)


@nc.route('/notice/list', endpoint="notice_list")
def notice_list():
    data = {}
    try:
        notice_list = models.Notice.query.order_by(models.Notice.update_time.desc()).all()
        hot_news = models.News.query.order_by(models.News.clicks.desc()).limit(10).all()
        suggestions = models.News.query.order_by(models.News.collected_counts.desc()).limit(10).all()
        data['hot_news'] = hot_news
        data['suggestions'] = suggestions
    except Exception as e:
        notice_list = []
        logging.error(e)
    res_list = []
    for item in notice_list:
        res_list.append(item.to_dict())
    data["notice_list"] = res_list
    return render_template("notice_list.html", data=data)


@nc.route('/notice/<int:nid>', endpoint="notice_scan")
def notice_scan(nid):
    data = {}
    url = url_for("nc.notice_list")
    try:
        notice_obj = models.Notice.query.get(int(nid))
        if not notice_obj:
            return redirect(url)
        else:
            notice_obj=notice_obj.to_dict()
        hot_news = models.News.query.order_by(models.News.clicks.desc()).limit(10).all()
        suggestions = models.News.query.order_by(models.News.collected_counts.desc()).limit(10).all()
        data['hot_news'] = hot_news
        data['suggestions'] = suggestions
    except Exception as e:
        logging.error(e)
        return redirect(url)
    data["notice_obj"] = notice_obj
    return render_template("notice_scan.html", data=data)

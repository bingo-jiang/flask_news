# coding=gbk
from . import details
from flask import render_template, request, jsonify, abort
from project import models
from project.models import db
import logging


@details.route('/<int:nid>', endpoint="detail")
def detail(nid):
    data = {}
    comments = []
    try:
        news_obj = models.News.query.filter(models.News.id == nid).first()
        # news_obj = models.News.query.get(nid)
    except Exception as e:
        logging.error(e)
        return render_template("404.html", request=request)
    if not news_obj:
        abort(404)
    data["news_obj"] = news_obj.to_dict()
    # 获取热门资讯
    try:
        hot_news = models.News.query.order_by(models.News.clicks.desc()).limit(10).all()
        data['hot_news'] = hot_news
    except Exception as e:
        logging.error(e)
        data['news-error'] = "无法访问数据库"
    # 判断登录用户是否已收藏该资讯
    is_collected = False
    if request.user:
        if news_obj in request.user.collection_news:
            is_collected = True
        else:
            is_collected = False
    data["is_collected"] = is_collected
    # 判断登录用户是否已关注该资讯作者
    is_follow = False
    try:
        author_obj = models.User.query.filter(models.User.id == news_obj.user_id).first()
    except Exception as e:
        logging.error(e)
        author_obj = None
    if request.user:
        if request.user in author_obj.followers:
            is_follow = True
        else:
            is_follow = False
    data["is_follow"] = is_follow
    # 获取用户点赞过的所有评论编号
    praised_comments = []
    if request.user:
        comment_like_objs = models.CommentLike.query.filter(models.CommentLike.user_id == request.user.id).all()
        for item in comment_like_objs:
            praised_comments.append(item.comment_id)
    # 获取所有评论
    comment_objs = models.Comment.query.filter(models.Comment.news_id == nid).order_by(
        models.Comment.create_time.desc()).all()
    for obj in comment_objs:
        obj_dict = obj.to_dict()
        # 判断用户给哪些评论点赞过
        if obj.id in praised_comments:
            obj_dict["is_praise"] = True
        else:
            obj_dict["is_praise"] = False
        comments.append(obj_dict)
    data["comments"] = comments
    return render_template("detail.html", request=request, data=data)


@details.route('/collect', endpoint="collect", methods=["POST"])
def collect():
    news_id = request.form.get("nid")
    user_id = request.form.get("user_id")
    deal_type = request.form.get("deal_type")
    if not user_id:
        return jsonify(status=False, login="/login")
    try:
        news_obj = models.News.query.get(news_id)
        user_obj = models.User.query.get(user_id)
    except Exception as e:
        logging.error(e)
        return jsonify(status=False, error="数据库请求错误！")
    if not news_obj:
        return jsonify(status=False, error="请求错误，数据库未检索到该资讯！")
    if deal_type not in ["collecting", "collected"]:
        return jsonify(status=False, error="请求错误，数据操作类型错误！")
    # 未收藏
    if deal_type == "collecting":
        if news_obj not in user_obj.collection_news:
            try:
                user_obj.collection_news.append(news_obj)
                news_obj.collected_counts += 1
                db.session.commit()
            except Exception as e:
                logging.error(e)
                return jsonify(status=False, error="数据库请求错误！")
    # 已收藏
    else:
        if news_obj in user_obj.collection_news:
            try:
                user_obj.collection_news.remove(news_obj)
                news_obj.collected_counts -= 1
                db.session.commit()
            except Exception as e:
                logging.error(e)
                return jsonify(status=False, error="数据库请求错误！")
    return jsonify(status=True)


@details.route('/comment', endpoint="comment", methods=["POST"])
def comment():
    # 获取参数
    news_id = request.form.get("nid")
    user_id = request.form.get("user_id")
    parent_id = request.form.get("parent_id")
    content = request.form.get("content")
    # 校验用户登录
    if not user_id:
        return jsonify(status=False, login="/login")
    # 校验content
    if not content:
        return jsonify(status=False, error="内容不能为空！")
    # 获取用户对象、新闻对象
    try:
        news_obj = models.News.query.get(news_id)
        user_obj = models.User.query.get(user_id)
    except Exception as e:
        logging.error(e)
        return jsonify(status=False, error="数据库请求错误！")
    # 校验新闻对象
    if not news_obj:
        return jsonify(status=False, error="请求错误，数据库未检索到该资讯！")
    # 保存评论到数据库
    comment_obj = models.Comment()
    comment_obj.user_id = user_id
    comment_obj.news_id = news_id
    comment_obj.content = content
    if parent_id:
        comment_obj.parent_id = parent_id
    try:
        db.session.add(comment_obj)
        db.session.commit()
    except Exception as e:
        logging.error(e)
        return jsonify(status=False, error="请求失败！")
    return jsonify(status=True)


@details.route('/praise', methods=['POST'], endpoint="praise")
def praise():
    # 判断用户登录状态
    if not request.user:
        return jsonify(status=False, login="/login")
    # 获取参数
    comment_id = request.json.get("comment_id")
    action = request.json.get("action")
    # 校验参数
    if not comment_id and not action:
        return jsonify(status=False, error="请求错误!没有请求参数!")
    if action not in ["add", "del"]:
        return jsonify(status=False, error="请求参数错误!")
    try:
        comment_obj = models.Comment.query.get(comment_id)
    except Exception as e:
        logging.error(e)
        return jsonify(status=False, error="数据库请求错误!")
    if not comment_obj:
        return jsonify(status=False, error="请求错误。数据库未检索到该评论!")
    try:
        if action == "add":
            up_obj = models.CommentLike.query.filter(models.CommentLike.user_id == request.user.id,
                                                     models.CommentLike.comment_id == comment_id).first()
            if not up_obj:
                comment_like_obj = models.CommentLike()
                comment_like_obj.comment_id = comment_id
                comment_like_obj.user_id = request.user.id
                db.session.add(comment_like_obj)
                comment_obj.like_count += 1
                db.session.commit()
            else:
                return jsonify(status=False, error="数据库操作错误!")
        else:
            up_obj = models.CommentLike.query.filter(models.CommentLike.user_id == request.user.id,
                                                     models.CommentLike.comment_id == comment_id).first()
            if up_obj:
                db.session.delete(up_obj)
                if comment_obj.like_count > 0:
                    comment_obj.like_count -= 1
                db.session.commit()
            else:
                return jsonify(status=False, error="数据库操作错误!")
    except Exception as e:
        logging.error(e)
        return jsonify(status=False, error="数据库操作错误!")
    return jsonify(status=True)


@details.route('/author/follow', methods=['GET', 'POST'], endpoint="follow")
def follow():
    if not request.user:
        return jsonify(status=False, error="请登录后再操作!")
    # 1.获取参数并转换数据类型
    followed_id = request.json.get("followed_id")
    deal_type = request.json.get("deal_type")
    if not all([followed_id, deal_type]):
        return jsonify(status=False, error="请求参数错误!")
    if deal_type not in ["follow", "cancel"]:
        return jsonify(status=False, error="请求参数错误!")
    try:
        author_obj = models.User.query.filter(models.User.id == int(followed_id)).first()
    except Exception as e:
        logging.error(e)
        return jsonify(status=False, error="数据库请求错误!")
    if not author_obj:
        return jsonify(status=False, error="数据库中不存在该作者!")
    user_obj = models.User.query.filter(models.User.id == request.user.id).first()
    # 未关注
    if deal_type == "follow":
        if user_obj not in author_obj.followers:
            try:
                author_obj.followers.append(user_obj)
            except Exception as e:
                logging.error(e)
                return jsonify(status=False, error="数据库请求错误!")
    # 已关注
    else:
        if user_obj in author_obj.followers:
            try:
                author_obj.followers.remove(user_obj)
            except Exception as e:
                logging.error(e)
                return jsonify(status=False, error="数据库请求错误!")
    return jsonify(status=True)

# coding=gbk
from . import admin
from flask import render_template, request, jsonify, abort, session, redirect, url_for
from project import models
from project.models import db
import logging
import datetime
from project.my_decorator import admin_auth
import os
from project.script.filename_format import filename_format
from project.script.pagination import FlakPagination
from project.script.get_param_list import flask_get_per_param_list
from project.script.get_param_list import flask_get_per_param_dict, generate_param_url, FlaskCheckFilter


@admin.before_request
def before_request():
    request.admin = None
    mobile = session.get("admin")
    user_obj = models.User.query.filter(models.User.mobile == mobile).first()
    if mobile and user_obj.is_admin:
        request.admin = user_obj
        request.user = user_obj
        return
    else:
        return


@admin.route('')
def index_none():
    return redirect("/admin/index")


@admin.route('/')
def index_():
    return redirect("/admin/index")


@admin.route('/index', methods=['GET', 'POST'], endpoint="index")
def index():
    if request.method == "GET":
        return render_template("admin/index.html", request=request)
    else:
        return jsonify(status=True)


@admin.route('/login', methods=['GET', 'POST'], endpoint='login')
def login():
    # 获取请求参数
    mobile = request.form.get('name')
    password = request.form.get('pwd')
    logging.info(mobile)
    logging.info(password)
    try:
        user_obj = models.User.query.filter(models.User.mobile == mobile).first()
    except Exception as e:
        logging.error(e)
        return jsonify(status=False, error="数据库请求错误")
    if not user_obj:
        logging.error("账号错误或还没有注册")
        return jsonify(status=False, error="账号错误或还没有注册")
    if not user_obj.is_admin:
        return jsonify(status=False, error="非管理员用户!")
    if not user_obj.check_password(password):
        logging.error(mobile + "密码错误")
        return jsonify(status=False, error="密码错误")
    session['admin_id'] = user_obj.id
    session['admin'] = mobile
    try:
        user_obj.last_login = datetime.datetime.now()
        db.session.commit()
    except Exception as e:
        logging.info(e)
    return jsonify(status=True, data='/admin/manage')


@admin.route('/logout', methods=['GET'], endpoint='logout')
def logout():
    session.pop("admin_id", None)
    session.pop("admin", None)
    return redirect('/admin/index')


@admin.route('/manage', methods=['GET', 'POST'], endpoint="manage")
@admin_auth
def manage():
    if request.method == "GET":
        return render_template("admin/manage.html", request=request)
    else:
        return jsonify(status=True)


@admin.route('/manage/user', methods=['GET', 'POST'], endpoint="manage_user")
@admin_auth
def manage_user():
    if request.method == "GET":
        per_page = 10
        data = {}
        # 1.获取参数
        page = request.args.get("page", "1")
        # 2.参数类型转换
        try:
            page = int(page)
            all_user = models.User.query.filter(models.User.is_admin == False).all()
        except Exception as e:
            page = 1
            all_user = []
        if len(all_user) < int(per_page):
            page = 1
        if len(all_user) > int(per_page):
            if page > int(len(all_user) / int(per_page)):
                page = 1
        try:
            queryset = all_user
            pagination_obj = FlakPagination(
                current_page=request.args.get('page'),
                all_count=len(all_user),
                base_url=request.url,
                per_page=per_page
            )
            final_list = queryset[pagination_obj.start:pagination_obj.end]
        except Exception as e:
            return render_template("admin/manage_user.html", data=data)
        all_list = []
        for item in final_list:
            all_list.append(item.to_admin_dict())
        data = {"all_list": all_list, 'page_html': pagination_obj.page_html(), }
        logging.info(data)
        return render_template("admin/manage_user.html", request=request, data=data)
    else:
        return jsonify(status=True)


@admin.route('/manage/news', methods=['GET', 'POST'], endpoint="manage_news")
@admin_auth
def manage_news():
    if request.method == "GET":
        status_list = flask_get_per_param_list(request.url, "status")
        category_id_list = flask_get_per_param_list(request.url, "category_id")
        per_page = 5
        data = {}
        # 1.获取参数
        page = request.args.get("page", "1")
        # 2.参数类型转换
        try:
            page = int(page)
            if status_list and category_id_list:
                all_news = models.News.query.filter(models.News.status.in_(status_list),
                                                    models.News.category_id.in_(category_id_list)).all()
            elif status_list and not category_id_list:
                all_news = models.News.query.filter(models.News.status.in_(status_list)).all()
            elif not status_list and category_id_list:
                all_news = models.News.query.filter(models.News.category_id.in_(category_id_list)).all()
            else:
                all_news = models.News.query.all()
            logging.info(all_news[0:5])
        except Exception as e:
            logging.error(e)
            page = 1
            all_news = []
        try:
            if int(len(all_news) / int(per_page)) > 1:
                if page > int(len(all_news) / int(per_page)):
                    return abort(404)
        except IndexError as e:
            logging.error(e)
        try:
            queryset = all_news
            pagination_obj = FlakPagination(
                current_page=request.args.get('page'),
                all_count=len(all_news),
                base_url=request.url,
                per_page=per_page
            )
            final_list = queryset[pagination_obj.start:pagination_obj.end]
            data['page_html'] = pagination_obj.page_html()
        except Exception as e:
            logging.error(e)
            data['page_html'] = None
            final_list = []
        all_list = []
        for item in final_list:
            all_list.append(item.to_dict())
        data['all_list'] = all_list
        category = models.Category.query.all()
        category_data_list = []
        for j in category:
            category_data_list.append(j.to_tuple())
        status_data_list = [(0, "审核中"), (1, "通过"), (-1, "未通过")]
        param_dict = flask_get_per_param_dict(request.url, ['status', 'category_id'])
        status_check_filter = FlaskCheckFilter('status', status_data_list, request, param_dict)
        category_check_filter = FlaskCheckFilter('category_id', category_data_list, request, param_dict)
        data['filter'] = [
            {"title": "审核状态", 'check_filter': status_check_filter},
            {"title": "新闻分类", 'check_filter': category_check_filter},
        ]
        return render_template("admin/manage_news.html", request=request, data=data, category=category)
    else:
        return jsonify(status=True)


@admin.route('/news/verify', methods=['GET', 'POST'], endpoint="news_verify")
@admin_auth
def news_verify():
    nid = request.form.get("nid")
    deal_type = request.form.get("deal_type")
    if not all([nid, deal_type]):
        return jsonify(status=False, error="参数缺失")
    if deal_type not in ["drawback", "agree", "reject"]:
        return jsonify(status=False, error="参数错误")
    try:
        news_obj = models.News.query.filter(models.News.id == nid).first()
        if request.admin:
            if deal_type == "agree":
                news_obj.status = 1
            elif deal_type == "drawback":
                news_obj.status = 0
            elif deal_type == "reject":
                reason = request.form.get("reason")
                if not all([nid, deal_type, reason]):
                    return jsonify(status=False, error="参数缺失")
                news_obj.status = -1
                news_obj.reason = reason
            else:
                news_obj.status = 0
        else:
            return jsonify(status=False, error="非管理员")
        db.session.commit()
    except Exception as e:
        logging.error(e)
        jsonify(status=False, error="数据库操作失败")
    return jsonify(status=True)


@admin.route('/manage/category', methods=['GET', 'POST'], endpoint="news_category")
@admin_auth
def news_category():
    if request.method == "GET":
        status_list = flask_get_per_param_list(request.url, "status")
        per_page = 10
        data = {}
        # 1.获取参数
        page = request.args.get("page", "1")
        # 2.参数类型转换
        try:
            page = int(page)
            if status_list:
                all_category = models.Category.query.filter(models.Category.status.in_(status_list)).all()
            else:
                all_category = models.Category.query.all()
        except Exception as e:
            logging.error(e)
            page = 1
            all_category = []
        try:
            if int(len(all_category) / int(per_page)) > 1:
                if page > int(len(all_category) / int(per_page)):
                    return abort(404)
        except IndexError as e:
            logging.error(e)
        try:
            queryset = all_category
            pagination_obj = FlakPagination(
                current_page=request.args.get('page'),
                all_count=len(all_category),
                base_url=request.url,
                per_page=per_page
            )
            final_list = queryset[pagination_obj.start:pagination_obj.end]
            data['page_html'] = pagination_obj.page_html()
        except Exception as e:
            logging.error(e)
            data['page_html'] = None
            final_list = []
        all_list = []
        for item in final_list:
            all_list.append(item.to_dict())
        data['all_list'] = all_list
        category_data_list = [(0, "禁用"), (1, "使用中")]
        allow_filter_name = ['status']
        param_dict = flask_get_per_param_dict(request.url, allow_filter_name)
        category_check_filter = FlaskCheckFilter('status', category_data_list, request, param_dict)
        data['filter'] = [
            {"title": "使用状态", 'check_filter': category_check_filter},
        ]
        return render_template("admin/manage_category.html", request=request, data=data)
    else:
        cid = request.form.get("cid")
        name = request.form.get("name")
        operate_type = request.form.get("deal_type")
        if operate_type not in ["edit", "delete", "add"]:
            return jsonify(status=False, error="参数错误")
        if operate_type == "add":
            if not all([operate_type, name]):
                return jsonify(status=False, error="参数缺失")
            try:
                new_category_obj = models.Category()
                new_category_obj.name = name
                new_category_obj.status = True
                db.session.add(new_category_obj)
                db.session.commit()
            except Exception as e:
                logging.error(e)
                jsonify(status=False, error="数据库操作失败")
            return jsonify(status=True)
        else:
            if not all([cid, name, operate_type]):
                return jsonify(status=False, error="参数缺失")
            try:
                category_obj = models.Category.query.filter(models.Category.id == cid).first()
                if request.admin:
                    if operate_type == "edit":
                        category_obj.name = name
                        category_obj.update_time = datetime.datetime.now()
                    if operate_type == "delete":
                        if not category_obj.status:
                            category_obj.status = True
                            category_obj.update_time = datetime.datetime.now()
                        else:
                            category_obj.status = False
                            category_obj.update_time = datetime.datetime.now()
                else:
                    return jsonify(status=False, error="非管理员")
                db.session.commit()
            except Exception as e:
                logging.error(e)
                jsonify(status=False, error="数据库操作失败")
            return jsonify(status=True)


@admin.route('/manage/comment', methods=['GET', 'POST'], endpoint="manage_comment")
@admin_auth
def manage_comment():
    if request.method == "GET":
        per_page = 10
        data = {}
        # 1.获取参数
        page = request.args.get("page", "1")
        # 2.参数类型转换
        try:
            page = int(page)
            all_comments = models.Comment.query.all()
        except Exception as e:
            logging.error(e)
            page = 1
            all_comments = []
        try:
            if int(len(all_comments) / int(per_page)) > 1:
                if page > int(len(all_comments) / int(per_page)):
                    return abort(404)
        except IndexError as e:
            logging.error(e)
        try:
            queryset = all_comments
            pagination_obj = FlakPagination(
                current_page=request.args.get('page'),
                all_count=len(all_comments),
                base_url=request.url,
                per_page=per_page
            )
            final_list = queryset[pagination_obj.start:pagination_obj.end]
            data['page_html'] = pagination_obj.page_html()
        except Exception as e:
            logging.error(e)
            data['page_html'] = None
            final_list = []
        all_list = []
        for item in final_list:
            all_list.append(item.to_dict())
        data['all_list'] = all_list
        return render_template("admin/manage_comment.html", request=request, data=data)
    else:
        cid = request.form.get("cid")
        content = request.form.get("content")
        operate_type = request.form.get("deal_type")
        if operate_type not in ["edit", "delete"]:
            return jsonify(status=False, error="参数错误")
        if operate_type == "edit":
            if not all([cid, content, operate_type]):
                return jsonify(status=False, error="参数缺失")
        if operate_type == "delete":
            if not all([cid, operate_type]):
                return jsonify(status=False, error="参数缺失")
        try:
            comment_obj = models.Comment.query.filter(models.Category.id == cid).first()
            if request.admin:
                if operate_type == "edit":
                    comment_obj.content = content
                    comment_obj.update_time = datetime.datetime.now()
                if operate_type == "delete":
                    comment_obj.delete()
            else:
                return jsonify(status=False, error="非管理员")
            db.session.commit()
        except Exception as e:
            logging.error(e)
            jsonify(status=False, error="数据库操作失败")
        return jsonify(status=True)


@admin.route('/manage/notice', methods=['GET', 'POST'], endpoint="manage_notice")
@admin_auth
def manage_notice():
    if request.method == "GET":
        per_page = 10
        data = {}
        # 1.获取参数
        page = request.args.get("page", "1")
        # 2.参数类型转换
        try:
            page = int(page)
            all_notices = models.Notice.query.order_by(models.Notice.update_time.desc()).all()
        except Exception as e:
            logging.error(e)
            page = 1
            all_notices = []
        try:
            if int(len(all_notices) / int(per_page)) > 1:
                if page > int(len(all_notices) / int(per_page)):
                    return abort(404)
        except IndexError as e:
            logging.error(e)
        try:
            queryset = all_notices
            pagination_obj = FlakPagination(
                current_page=request.args.get('page'),
                all_count=len(all_notices),
                base_url=request.url,
                per_page=per_page
            )
            final_list = queryset[pagination_obj.start:pagination_obj.end]
            data['page_html'] = pagination_obj.page_html()
        except Exception as e:
            logging.error(e)
            data['page_html'] = None
            final_list = []
        all_list = []
        for item in final_list:
            all_list.append(item.to_dict())
        data['all_list'] = all_list
        return render_template("admin/manage_notice.html", request=request, data=data)
    else:
        nid = request.form.get("nid")
        operate_type = request.form.get("deal_type")
        if operate_type not in ["delete"]:
            return jsonify(status=False, error="参数错误")
        if operate_type == "delete":
            if not all([nid, operate_type]):
                return jsonify(status=False, error="参数缺失")
        try:
            notice_obj = models.Notice.query.filter(models.Notice.id == nid).first()
            if request.admin:
                if operate_type == "delete":
                    notice_obj.delete()
            else:
                return jsonify(status=False, error="非管理员")
            db.session.commit()
        except Exception as e:
            logging.error(e)
            jsonify(status=False, error="数据库操作失败")
        return jsonify(status=True)


@admin.route('/manage/notice/edit', methods=['GET', 'POST'], endpoint="notice_edit")
@admin_auth
def manage_notice_edit():
    if request.method == 'GET':
        data = {}
        from project.my_forms import NoticeForm
        nid=request.args.get("nid")
        if nid:
            try:
                notice_obj=models.Notice.query.get(nid)
                form=NoticeForm(obj=notice_obj)
            except Exception as e:
                logging.error(e)
        else:
            form = NoticeForm()
        data["form"] = form
        return render_template("admin/notice_edit.html", data=data)
    else:
        title = request.form.get("title")
        content = request.form.get("content")
        if not all([title, content]):
            return jsonify(status=False, error="参数不全")
        try:
            notice_obj = models.Notice()
            if request.admin:
                notice_obj.title = title
                notice_obj.content = content
                notice_obj.admin_id = request.admin.id
                db.session.add(notice_obj)
                db.session.commit()
            else:
                return jsonify(status=False, error="数据库错误")
        except Exception as e:
            logging.error(e)
            return jsonify(status=False, error="数据库错误")
        url = url_for("admin.manage_notice")
        return jsonify(status=True, data=url)


@admin.route('/manage/author/register', methods=['GET', 'POST'], endpoint="manage_author_register")
@admin_auth
def manage_author_register():
    if request.method == "GET":
        per_page = 10
        data = {}
        # 1.获取参数
        page = request.args.get("page", "1")
        # 2.参数类型转换
        try:
            page = int(page)
            all_author_infos = models.AuthorRegister.query.all()
        except Exception as e:
            logging.error(e)
            page = 1
            all_author_infos = []
        # 页数校验
        try:
            if int(len(all_author_infos) / int(per_page)) > 1:
                if page > int(len(all_author_infos) / int(per_page)):
                    return abort(404)
        except IndexError as e:
            logging.error(e)
        # 分页处理
        try:
            queryset = all_author_infos
            pagination_obj = FlakPagination(
                current_page=request.args.get('page'),
                all_count=len(all_author_infos),
                base_url=request.url,
                per_page=per_page
            )
            final_list = queryset[pagination_obj.start:pagination_obj.end]
            data['page_html'] = pagination_obj.page_html()
        except Exception as e:
            logging.error(e)
            data['page_html'] = None
            final_list = []
        # 结果转字典类型
        all_list = []
        for item in final_list:
            all_list.append(item.to_dict())
        data['all_list'] = all_list
        return render_template("admin/manage_author_register.html", request=request, data=data)
    else:
        nid = request.form.get("nid")
        deal_type = request.form.get("deal_type")
        if not all([nid, deal_type]):
            return jsonify(status=False, error="参数缺失")
        if deal_type not in ["drawback", "agree", "reject"]:
            return jsonify(status=False, error="参数错误")
        try:
            author_obj = models.AuthorRegister.query.filter(models.AuthorRegister.id == nid).first()
            related_user = models.User.query.get(author_obj.user_id)
            if request.admin:
                if deal_type == "agree":
                    author_obj.status = 1
                    related_user.is_author = True
                elif deal_type == "drawback":
                    author_obj.status = 0
                    related_user.is_author = False
                elif deal_type == "reject":
                    reason = request.form.get("reason")
                    if not all([nid, deal_type, reason]):
                        return jsonify(status=False, error="参数缺失")
                    author_obj.status = -1
                    author_obj.reason = reason
                    related_user.is_author = False
                else:
                    author_obj.status = 0
            else:
                return jsonify(status=False, error="非管理员")
            db.session.commit()
        except Exception as e:
            logging.error(e)
            jsonify(status=False, error="数据库操作失败")
        return jsonify(status=True)


@admin.route('/news/rewrite/<int:news_id>', methods=['GET', 'POST'], endpoint="news_rewrite")
@admin_auth
def news_rewrite(news_id):
    if request.method == "GET":
        data = {}
        try:
            news_obj = models.News.query.get(int(news_id))
            if not request.admin:
                url = url_for("admin.login")
                return redirect(url)
            category_objs = models.Category.query.all()
            category_choices = []
            for i in category_objs:
                if i.id == 1:
                    continue
                category_choices.append(i.to_dict())
            data["category_choices"] = category_choices
        except Exception as e:
            news_obj = None
            logging.error(e)
            data['error'] = "没有该文章"
        from project.my_forms import NewsForm
        form = NewsForm(obj=news_obj)
        data['form'] = form
        data['news_obj'] = news_obj
        return render_template("admin/news_edit.html", data=data,request=request)
    else:
        try:
            news_obj = models.News.query.get(news_id)
        except:
            return jsonify(status=False, error="数据库操作失败!")
        if not request.admin:
            return jsonify(status=False, error="非管理员!")
        index_pic = request.files.get("index_pic")
        title = request.form.get("title")
        digest = request.form.get("digest")
        content = request.form.get("content")
        category = request.form.get("category")
        source = request.form.get("source")
        # print(request.form)
        if not all([title, digest, content, category, source]):
            return jsonify(status=False, error="参数为空!")
        if index_pic:
            index_pic.filename = filename_format(request.user.id, request.user.mobile, index_pic.filename)
            # 拼接完整文件目录路径
            try:
                # 手动拼接存储文件的路径
                from manage import app
                base_path = app.root_path
                base_path = base_path.replace("\\", '/')
                author_file_dir = "news_picture/{}".format(
                    str(request.user.id) + "_" + str(request.user.nick_name))  # 为每个用户创建一个文件夹
                static_path = url_for("static", filename=author_file_dir)
                file_dir = (base_path + static_path)
            except Exception as e:
                logging.error(e)
                return jsonify(status=False, error="文件保存目录不存在")
            # 创建文件目录
            try:
                # 文件目录校验
                if not os.path.exists(file_dir):
                    os.makedirs(file_dir)
            except FileNotFoundError as e:
                logging.error(e)
                return jsonify(status=False, error="文件保存目录不存在且创建失败")
            # 拼接完整文件保存路径
            index_pic_path = os.path.join(file_dir, index_pic.filename)
            logging.info(index_pic_path)
            # 保存图片到本地
            try:
                # with open(index_pic_path, 'wb') as f:
                #     for line in index_pic:
                #         f.write(line)
                index_pic.save(index_pic_path)
            except Exception as e:
                logging.error(e)
                return jsonify(status=False, error="文件保存错误!")
        else:
            static_path = None
        try:
            category_ = models.Category.query.filter(models.Category.name == category).first()
            news_obj.title = title
            news_obj.digest = digest
            news_obj.content = content
            news_obj.category_id = category_.id
            news_obj.source = source
            if index_pic:
                news_obj.index_image_url = static_path + "/" + index_pic.filename
            db.session.commit()
        except Exception as e:
            logging.error(e)
            return jsonify(status=False, error="数据库操作失败!")
        return jsonify(status=True)

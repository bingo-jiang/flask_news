# coding=gbk
from flask_wtf import csrf
from . import user
from flask import render_template, request, jsonify, abort, session, redirect, url_for
from project import models
from project.models import db
import logging
from project.my_decorator import login_auth, login_required
import os
from project.script.filename_format import filename_format
from project.script.pagination import FlakPagination
from project.script.get_param_list import flask_get_per_param_list
from project.script.get_param_list import flask_get_per_param_dict, generate_param_url, FlaskCheckFilter


@user.route('/center', endpoint="center")
@login_auth
def center():
    return render_template("user.html", request=request)


@user.route('/base/info', methods=['GET', 'POST'], endpoint="base_info")
@login_auth
def user_info():
    if request.method == "GET":
        return render_template("user_info.html", request=request)
    else:
        nick_name = request.form.get("nick_name")
        signature = request.form.get("signature")
        gender = request.form.get("gender")
        if not request.user:
            return jsonify(status=False, error="���¼!")
        if not all([nick_name, signature, gender]):
            return jsonify(status=False, error="�������,������ȫ!")
        if gender not in ["MAN", "WOMAN"]:
            return jsonify(status=False, error="�����������!")
        user_obj = models.User.query.filter(models.User.id != request.user.id,
                                            models.User.nick_name == nick_name).first()
        if user_obj:
            return jsonify(status=False, error="�ǳ��ѱ�ʹ��!")
        try:
            obj = models.User.query.filter(models.User.id == request.user.id,
                                           models.User.mobile == request.user.mobile).first()
            obj.nick_name = nick_name
            obj.signature = signature
            obj.gender = gender
            db.session.commit()
        except Exception as e:
            logging.error(e)
            return jsonify(status=False, error="���ݿ����ʧ��!")
        return jsonify(status=True)


@user.route('/avatar', methods=['GET', 'POST'], endpoint="avatar")
@login_auth
def user_avatar():
    if request.method == "GET":
        return render_template("user_avatar.html", request=request)
    else:
        # ��ȡ�ļ�����
        file = request.files.get('avatar')
        file.filename = filename_format(request.user.id, request.user.mobile, file.filename)
        logging.info(file.filename)
        # ƴ�������ļ�Ŀ¼·��
        try:
            # �ֶ�ƴ�Ӵ洢�ļ���·��
            from manage import app
            base_path = app.root_path
            base_path = base_path.replace("\\", '/')
            static_path = url_for("static", filename="upload_files/avatar")
            file_dir = (base_path + static_path)
            logging.info("�ļ�·��:" + file_dir)
        except Exception as e:
            logging.error(e)
            return jsonify(status=False, error="�ļ�����Ŀ¼������")
        # �����ļ�Ŀ¼
        try:
            # �ļ�Ŀ¼У��
            if not os.path.isdir(file_dir):
                os.mkdir(file_dir)
        except FileNotFoundError as e:
            logging.error(e)
            return jsonify(status=False, error="�ļ�����Ŀ¼�������Ҵ���ʧ��")
        # ƴ������ͷ�񱣴�·��
        file_path = os.path.join(file_dir, file.filename)
        logging.info("file_path:" + file_path)
        # ����ͷ��ͼƬ������
        try:
            with open(file_path, 'wb') as f:
                for line in file:
                    f.write(line)
        except Exception as e:
            logging.error(e)
            return jsonify(status=False, error="ͼƬ�������")
        # �޸��û���avatar_url
        avatar_url = static_path + "/" + file.name
        try:
            user_obj = models.User.query.filter(models.User.id == request.user.id).first()
            user_obj.avatar_url = avatar_url
            db.session.commit()
        except Exception as e:
            logging.error(e)
        return jsonify(status=True)


@user.route('/password', methods=['GET', 'POST'], endpoint="password")
@login_auth
def user_password():
    if request.method == "GET":
        return render_template("user_password.html", request=request)
    else:
        # 1.��ȡ����
        old_pwd = request.form.get("old_pwd")
        new_pwd = request.form.get("new_pwd")
        confirm_pwd = request.form.get("confirm_pwd")
        logging.info(request.form)
        # 2.��¼У��
        if not request.user:
            return jsonify(status=False, error="���¼!")
        # 3.����У��
        if not all([old_pwd, new_pwd, confirm_pwd]):
            return jsonify(status=False, error="���������ȫ!")
        # 4.ԭ����У��
        flags = request.user.check_password(old_pwd)
        if not flags:
            return jsonify(status=False, error="ԭ�������!")
        # 5.��������������У��
        if new_pwd != confirm_pwd:
            return jsonify(status=False, error="�����������벻һ��!")
        # 6.����������
        try:
            obj = models.User.query.filter(models.User.id == request.user.id).first()
            obj.password = new_pwd
            db.session.commit()
        except Exception as e:
            logging.error(e)
            return jsonify(status=False, error="���ݿ��������!")
        session.pop("user_mobile", None)
        return jsonify(status=True)


@user.route('/collections', endpoint="my_collections")
@login_auth
def collections():
    data = {}
    # 1.��ȡ����
    page = request.args.get("page", "1")
    # 2.��������ת��
    try:
        page = int(page)
    except Exception as e:
        page = 1
    # 3.��ҳ��ѯ�����ղ�
    try:
        collections_objs = request.user.collection_news.order_by(models.News.create_time.desc()).all()
    except Exception as e:
        logging.error(e)
        data["error"] = "���ݿ��������!"
        return render_template("user_collections.html", data=data)
    if not collections_objs:
        return render_template("user_collections.html", data=data)
    # 5.�ж��������page�Ƿ�С��total_page
    if page > int(int(len(collections_objs)) / 10) + 1:
        return abort(404)
    res = request.url.split("?")
    base_url = res[0]
    try:
        query_params = res[1]
        if int(len(collections_objs) / 10) > 1:
            if page > int(len(collections_objs) / 10):
                return render_template("user_collections.html", data=data)
    except IndexError as e:
        query_params = None
    try:
        pagination_obj = FlakPagination(
            current_page=request.args.get('page'),
            all_count=len(collections_objs),
            base_url=base_url,
            query_params=query_params,
        )
    except Exception as e:
        return render_template("user_collections.html", data=data)
    # 6.�������б�ת��Ϊ�ֵ�
    news_list = []
    for item in collections_objs:
        news_list.append(item.to_dict())
    data = {"newsList": news_list, 'page_html': pagination_obj.page_html(), }
    logging.info(data)
    return render_template("user_collections.html", data=data)


@user.route('/news/edit', methods=['GET', 'POST'], endpoint="news_edit")
@login_auth
def news_edit():
    if request.method == "GET":
        data = {}
        if not request.user.is_author:
            url = url_for("user.center")
            return redirect(url)
        try:
            category_objs = models.Category.query.all()
            category_choices = []
            for i in category_objs:
                if i.id == 1:
                    continue
                category_choices.append(i.to_dict())
            data["category_choices"] = category_choices
        except Exception as e:
            logging.error(e)
        return render_template("news_edit.html", data=data)
    else:
        if not request.user.is_author:
            return jsonify(status=False, error="���������ע��!")
        index_pic = request.files.get("index_pic")
        title = request.form.get("title")
        digest = request.form.get("digest")
        content = request.form.get("md_editor-markdown-doc")
        category = request.form.get("category")
        source = request.form.get("source")
        if not all([index_pic, title, digest, content, category, source]):
            return jsonify(status=False, error="����Ϊ��!")
        index_pic.filename = filename_format(request.user.id, request.user.mobile, index_pic.filename)
        # ƴ�������ļ�Ŀ¼·��
        try:
            # �ֶ�ƴ�Ӵ洢�ļ���·��
            from manage import app
            base_path = app.root_path
            base_path = base_path.replace("\\", '/')
            author_file_dir = "news_picture/{}".format(
                str(request.user.id) + "_" + str(request.user.nick_name))  # Ϊÿ���û�����һ���ļ���
            static_path = url_for("static", filename=author_file_dir)
            file_dir = (base_path + static_path)
        except Exception as e:
            logging.error(e)
            return jsonify(status=False, error="�ļ�����Ŀ¼������")
        # �����ļ�Ŀ¼
        try:
            # �ļ�Ŀ¼У��
            if not os.path.exists(file_dir):
                os.makedirs(file_dir)
        except FileNotFoundError as e:
            logging.error(e)
            return jsonify(status=False, error="�ļ�����Ŀ¼�������Ҵ���ʧ��")
        # ƴ�������ļ�����·��
        index_pic_path = os.path.join(file_dir, index_pic.filename)
        logging.info(index_pic_path)
        # ����ͼƬ������
        try:
            with open(index_pic_path, 'wb') as f:
                for line in index_pic:
                    f.write(line)
        except Exception as e:
            logging.error(e)
            return jsonify(status=False, error="�ļ��������!")
        try:
            category_ = models.Category.query.filter(models.Category.name == category).first()
            news_obj = models.News()
            news_obj.title = title
            news_obj.digest = digest
            news_obj.content = content
            news_obj.category_id = category_.id
            news_obj.source = source
            news_obj.user_id = request.user.id
            news_obj.status = 0
            news_obj.index_image_url = static_path + "/" + index_pic.filename
            db.session.add(news_obj)
            db.session.commit()
        except Exception as e:
            logging.error(e)
            return jsonify(status=False, error="���ݿ����ʧ��!")
        # return jsonify(status=False, error="����")
        return jsonify(status=True)


@user.route('/news/issues', methods=['GET', 'POST'], endpoint="news_issues")
@login_auth
def news_issues():
    if request.method == "GET":
        status_list = flask_get_per_param_list(request.url, "status")
        category_id_list = flask_get_per_param_list(request.url, "category_id")
        per_page = 5
        data = {}
        # 1.��ȡ����
        page = request.args.get("page", "1")
        # 2.��������ת��
        try:
            page = int(page)
            if status_list and category_id_list:
                all_news = models.News.query.filter(models.News.status.in_(status_list),
                                                    models.News.user_id == request.user.id,
                                                    models.News.category_id.in_(category_id_list)).all()
            elif status_list and not category_id_list:
                all_news = models.News.query.filter(models.News.user_id == request.user.id,
                                                    models.News.status.in_(status_list)).all()
            elif not status_list and category_id_list:
                all_news = models.News.query.filter(models.News.user_id == request.user.id,
                                                    models.News.category_id.in_(category_id_list)).all()
            else:
                all_news = models.News.query.filter(models.News.user_id == request.user.id, ).order_by(
                    models.News.create_time.desc()).all()
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
        status_data_list = [(0, "�����"), (1, "ͨ��"), (-1, "δͨ��")]
        param_dict = flask_get_per_param_dict(request.url, ['status', 'category_id'])
        status_check_filter = FlaskCheckFilter('status', status_data_list, request, param_dict)
        category_check_filter = FlaskCheckFilter('category_id', category_data_list, request, param_dict)
        data['filter'] = [
            {"title": "���״̬", 'check_filter': status_check_filter},
            {"title": "���ŷ���", 'check_filter': category_check_filter},
        ]
        return render_template("news_issues.html", request=request, data=data, category=category)
    else:
        nid = request.form.get("nid")
        operate_type = request.form.get("deal_type")
        if operate_type not in ["edit", "delete", "add"]:
            return jsonify(status=False, error="��������")
        if not all([nid, operate_type]):
            return jsonify(status=False, error="����ȱʧ")
        try:
            news_obj = models.News.query.filter(models.News.id == nid, models.News.user_id == request.user.id).first()
            if operate_type == "delete":
                if request.user.id == news_obj.user_id:
                    models.News.query.filter(models.News.id == nid, models.News.user_id == request.user.id).delete()
                else:
                    return jsonify(status=False, error="����������!")
            db.session.commit()
        except Exception as e:
            logging.error(e)
            return jsonify(status=False, error="���ݿ����ʧ��")
        return jsonify(status=True)


@user.route('/my_idols', methods=['GET', 'POST'], endpoint="my_idols")
@login_auth
def my_idols():
    if request.method == "GET":
        data = {}
        # 1.��ȡ����
        page = request.args.get("page", "1")
        # 2.��������ת��
        try:
            page = int(page)
        except Exception as e:
            page = 1
        # 3.��ҳ��ѯ�����ղ�
        try:
            user_obj = models.User.query.filter(models.User.id == request.user.id).first()
            followers_objs = user_obj.followed.all()
        except Exception as e:
            logging.error(e)
            data["error"] = "���ݿ��������!"
            return render_template("my_idols.html", data=data)
        if not followers_objs:
            return render_template("my_idols.html", data=data)
        # 5.�ж��������page�Ƿ�С��total_page
        if page > int(int(len(followers_objs)) / 10) + 1:
            return abort(404)
        res = request.url.split("?")
        base_url = res[0]
        try:
            query_params = res[1]
            if int(len(followers_objs) / 10) > 1:
                if page > int(len(followers_objs) / 10):
                    return render_template("user_collections.html", data=data)
        except IndexError as e:
            query_params = None
        try:
            pagination_obj = FlakPagination(
                current_page=request.args.get('page'),
                all_count=len(followers_objs),
                base_url=base_url,
                query_params=query_params,
            )
        except Exception as e:
            return render_template("my_idols.html", data=data)
        # 6.����˿�����б�ת��Ϊ�ֵ�
        followers_list = []
        for item in followers_objs:
            followers_list.append(item.to_dict())
        data = {"followers_list": followers_list, 'page_html': pagination_obj.page_html(), }
        logging.info(data)
        return render_template("my_idols.html", request=request, data=data)
    else:
        author_id = request.form.get("author_id")
        if not author_id:
            return jsonify(status=False, error="�������Ϊ��!")
        try:
            author_obj = models.User.query.get(author_id)
            user_obj = models.User.query.get(request.user.id)
            logging.info(author_obj)
            logging.info(user_obj)
        except Exception as e:
            logging.error(e)
            return jsonify(status=False, error="���ݿ����ʧ��!")
        if user_obj in author_obj.followers:
            logging.debug(author_obj.followers)
            author_obj.followers.remove(user_obj)
        else:
            return jsonify(status=False, error="���ݿ����ʧ��!")
        return jsonify(status=True)


@user.route('/author/register', methods=['GET', 'POST'], endpoint="author_register")
@login_auth
def author_register():
    if request.method == "GET":
        data = {}
        author_obj = None
        try:
            author_obj = models.AuthorRegister.query.filter(models.AuthorRegister.user_id == request.user.id).first()
        except Exception as e:
            logging.error(e)
        data["author_obj"] = author_obj
        return render_template("author_register.html", request=request, data=data)
    else:
        # ��ȡ���ļ�����
        name = request.form.get('name')
        id_card = request.form.get('id_card')
        email = request.form.get('email')
        address = request.form.get('address')
        logging.info(request.form)
        # ��ȡ�ļ�����
        file_positive = request.files.get('positive')
        file_negative = request.files.get('negative')
        file_positive.filename = filename_format(request.user.id, request.user.mobile, file_positive.filename)
        file_negative.filename = filename_format(request.user.id, request.user.mobile, file_negative.filename)
        logging.info(file_positive.filename)
        logging.info(file_negative.filename)
        # У�����
        if not all([name, id_card, email, address, file_negative, file_positive]):
            return jsonify(status=False, error="������ȫ!")
        # ƴ�������ļ�Ŀ¼·��
        try:
            # �ֶ�ƴ�Ӵ洢�ļ���·��
            from manage import app
            base_path = app.root_path
            base_path = base_path.replace("\\", '/')
            author_file_dir = "author_register/{}".format(
                str(request.user.id) + "_" + str(request.user.nick_name))  # Ϊÿ���û�����һ���ļ���
            static_path = url_for("static", filename=author_file_dir)
            file_dir = (base_path + static_path)
            logging.info("�ļ�·��:" + file_dir)
        except Exception as e:
            logging.error(e)
            return jsonify(status=False, error="�ļ�����Ŀ¼������")
        # �����ļ�Ŀ¼
        try:
            # �ļ�Ŀ¼У��
            if not os.path.exists(file_dir):
                os.makedirs(file_dir)
        except FileNotFoundError as e:
            logging.error(e)
            return jsonify(status=False, error="�ļ�����Ŀ¼�������Ҵ���ʧ��")
        # ƴ�������ļ�����·��
        file_positive_path = os.path.join(file_dir, file_positive.filename)
        file_negative_path = os.path.join(file_dir, file_negative.filename)
        # ����ͷ��ͼƬ������
        try:
            with open(file_positive_path, 'wb') as f1:
                for line in file_positive:
                    f1.write(line)
            with open(file_negative_path, 'wb') as f2:
                for line in file_negative:
                    f2.write(line)
        except Exception as e:
            logging.error(e)
            return jsonify(status=False, error="�ļ��������!")
        # ���浽���ݿ�
        try:
            author_obj = models.AuthorRegister()
            author_obj.name = name
            author_obj.email = email
            author_obj.address = address
            author_obj.id_card = id_card
            author_obj.user_id = request.user.id
            author_obj.status = 0
            author_obj.positive_ID_card_url = static_path + "/" + file_positive.filename
            author_obj.take_ID_card_url = static_path + "/" + file_negative.filename
            db.session.add(author_obj)
            db.session.commit()
        except Exception as e:
            logging.error(e)
            return jsonify(status=False, error="���ݿ����ʧ��!")
        return jsonify(status=True)


@user.route('/pic_upload', methods=['GET', 'POST'], endpoint="pic_upload")
def pic_upload():
    # ��ʼ�����ؽ��
    result = {'success': 0, 'message': None, 'url': None}  # MarkdownҪ��Ĺ̶��ķ��ؽ����ʽ
    img_obj = request.files.get('editormd-image-file')  # ��ȡ�ϴ����ļ�����
    # ����ļ��ϴ�ʧ��
    if not img_obj:
        result['message'] = "�ļ�������"
        return jsonify(result)

    img_obj.filename = filename_format(request.user.id, request.user.mobile, img_obj.filename)
    # ƴ�������ļ�Ŀ¼·��
    try:
        # �ֶ�ƴ�Ӵ洢�ļ���·��
        from manage import app
        base_path = app.root_path
        base_path = base_path.replace("\\", '/')
        author_file_dir = "news_picture/{}".format(
            str(request.user.id) + "_" + str(request.user.nick_name))  # Ϊÿ���û�����һ���ļ���
        static_path = url_for("static", filename=author_file_dir)
        file_dir = (base_path + static_path)
    except Exception as e:
        logging.error(e)
        return jsonify(status=False, error="�ļ�����Ŀ¼������")
    # �����ļ�Ŀ¼
    try:
        # �ļ�Ŀ¼У��
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)
    except FileNotFoundError as e:
        logging.error(e)
        return jsonify(status=False, error="�ļ�����Ŀ¼�������Ҵ���ʧ��")
    # ƴ�������ļ�����·��
    index_pic_path = os.path.join(file_dir, img_obj.filename)
    logging.info(index_pic_path)
    # ����ͼƬ������
    try:
        # with open(index_pic_path, 'wb') as f:
        #     for line in img_obj:
        #         f.write(line)
        img_obj.save(index_pic_path)
    except Exception as e:
        logging.error(e)
        return jsonify(status=False, error="�ļ��������!")
    img_url = request.host_url + static_path + "/" + img_obj.filename
    # print(img_url)
    result['success'] = 1
    result['url'] = img_url
    return jsonify(result)


@user.route('/news/rewrite/<int:news_id>', methods=['GET', 'POST'], endpoint="news_rewrite")
@login_auth
def news_rewrite(news_id):
    if request.method == "GET":
        data = {}
        try:
            news_obj = models.News.query.get(int(news_id))
            if not request.user.id == news_obj.user_id:
                url = url_for("user.center")
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
            data['error'] = "û�и�����"
        from project.my_forms import NewsForm
        form = NewsForm(obj=news_obj)
        data['form'] = form
        data['news_obj'] = news_obj
        return render_template("news_rewrite.html", data=data)
    else:
        try:
            news_obj = models.News.query.get(news_id)
        except:
            return jsonify(status=False, error="���ݿ����ʧ��!")
        if not request.user.id == news_obj.user_id:
            return jsonify(status=False, error="����������!")
        if not request.user.is_author:
            return jsonify(status=False, error="���������ע��!")
        index_pic = request.files.get("index_pic")
        title = request.form.get("title")
        digest = request.form.get("digest")
        content = request.form.get("content")
        category = request.form.get("category")
        source = request.form.get("source")
        print(request.form)
        if not all([title, digest, content, category, source]):
            return jsonify(status=False, error="����Ϊ��!")
        if index_pic:
            index_pic.filename = filename_format(request.user.id, request.user.mobile, index_pic.filename)
            # ƴ�������ļ�Ŀ¼·��
            try:
                # �ֶ�ƴ�Ӵ洢�ļ���·��
                from manage import app
                base_path = app.root_path
                base_path = base_path.replace("\\", '/')
                author_file_dir = "news_picture/{}".format(
                    str(request.user.id) + "_" + str(request.user.nick_name))  # Ϊÿ���û�����һ���ļ���
                static_path = url_for("static", filename=author_file_dir)
                file_dir = (base_path + static_path)
            except Exception as e:
                logging.error(e)
                return jsonify(status=False, error="�ļ�����Ŀ¼������")
            # �����ļ�Ŀ¼
            try:
                # �ļ�Ŀ¼У��
                if not os.path.exists(file_dir):
                    os.makedirs(file_dir)
            except FileNotFoundError as e:
                logging.error(e)
                return jsonify(status=False, error="�ļ�����Ŀ¼�������Ҵ���ʧ��")
            # ƴ�������ļ�����·��
            index_pic_path = os.path.join(file_dir, index_pic.filename)
            logging.info(index_pic_path)
            # ����ͼƬ������
            try:
                # with open(index_pic_path, 'wb') as f:
                #     for line in index_pic:
                #         f.write(line)
                index_pic.save(index_pic_path)
            except Exception as e:
                logging.error(e)
                return jsonify(status=False, error="�ļ��������!")
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
            return jsonify(status=False, error="���ݿ����ʧ��!")
        return jsonify(status=True)

"""
分页组件应用：
1. 在视图函数中
    queryset = models.Issues.objects.filter(project_id=project_id)
    page_object = Pagination(
        current_page=request.GET.get('page'),
        all_count=queryset.count(),
        base_url=request.path_info,
        query_params=request.GET
    )
    object_list = queryset[page_object.start:page_object.end]

    context = {
        'object_list': object_list,
        'page_html': page_object.page_html()
    }
    return render(request, 'issues.html', context)
2. 前端
    {% for item in issues_object_list %}
        {{item.xxx}}
    {% endfor %}

     <nav aria-label="...">
        <ul class="pagination" style="margin-top: 0;">
            {{ page_html|safe }}
        </ul>
    </nav>
"""


class Pagination(object):
    def __init__(self, current_page, all_count, base_url, query_params, per_page=10, pager_page_count=7):
        """
        分页初始化
        :param current_page: 当前页码
        :param per_page: 每页显示数据条数
        :param all_count: 数据库中总条数
        :param base_url: 基础URL
        :param query_params: QueryDict对象，内部含所有当前URL的原条件
        :param pager_page_count: 页面上最多显示的页码数量
        """
        self.base_url = base_url
        try:
            self.current_page = int(current_page)
            if self.current_page <= 0:
                self.current_page = 1
        except Exception as e:
            self.current_page = 1
        query_params = query_params.copy()
        query_params._mutable = True
        self.query_params = query_params
        self.per_page = per_page
        self.all_count = all_count
        self.pager_page_count = pager_page_count
        pager_count, b = divmod(all_count, per_page)
        if b != 0:
            pager_count += 1
        self.pager_count = pager_count

        half_pager_page_count = int(pager_page_count / 2)
        self.half_pager_page_count = half_pager_page_count

    @property
    def start(self):
        """
        数据获取值起始索引
        :return:
        """
        return (self.current_page - 1) * self.per_page

    @property
    def end(self):
        """
        数据获取值结束索引
        :return:
        """
        return self.current_page * self.per_page

    def page_html(self):
        """
        生成HTML页码
        :return:
        """
        if self.all_count == 0:
            return ""

        # 如果数据总页码pager_count<11 pager_page_count
        if self.pager_count < self.pager_page_count:
            pager_start = 1
            pager_end = self.pager_count
        else:
            # 数据页码已经超过11
            # 判断： 如果当前页 <= 5 half_pager_page_count
            if self.current_page <= self.half_pager_page_count:
                pager_start = 1
                pager_end = self.pager_page_count
            else:
                # 如果： 当前页+5 > 总页码
                if (self.current_page + self.half_pager_page_count) > self.pager_count:
                    pager_end = self.pager_count
                    pager_start = self.pager_count - self.pager_page_count + 1
                else:
                    pager_start = self.current_page - self.half_pager_page_count
                    pager_end = self.current_page + self.half_pager_page_count

        page_list = []

        if self.current_page <= 1:
            prev = '<li><a href="#"><span aria-hidden="true">&laquo;</span></a></li>'
        else:
            self.query_params['page'] = self.current_page - 1
            prev = '<li><a href="%s?%s"><span aria-hidden="true">&laquo;</span></a></li>' % (
                self.base_url, self.query_params.urlencode())
        page_list.append(prev)
        for i in range(pager_start, pager_end + 1):
            self.query_params['page'] = i
            if self.current_page == i:
                tpl = '<li class="active"><a href="%s?%s">%s</a></li>' % (
                    self.base_url, self.query_params.urlencode(), i,)
            else:
                tpl = '<li><a href="%s?%s">%s</a></li>' % (self.base_url, self.query_params.urlencode(), i,)
            page_list.append(tpl)

        if self.current_page >= self.pager_count:
            nex = '<li><a href="#"><span aria-hidden="true">&raquo;</span></a></li>'
        else:
            self.query_params['page'] = self.current_page + 1
            nex = '<li><a href="%s?%s"><span aria-hidden="true">&raquo;</span></a></li>' % (
                self.base_url, self.query_params.urlencode(),)
        page_list.append(nex)

        if self.all_count:
            tpl = "<li class='disabled'><a>共%s条数据，页码%s/%s页</a></li>" % (
                self.all_count, self.current_page, self.pager_count,)
            page_list.append(tpl)
        page_str = "".join(page_list)
        return page_str


class MyPagination(object):
    def __init__(self, current_page, all_count, base_url, query_params, browser_param=None, per_page=5,
                 pager_page_count=7):
        self.base_url = base_url
        self.browser_param = browser_param
        try:
            self.current_page = int(current_page)
            if self.current_page <= 0:
                self.current_page = 1
        except Exception:
            self.current_page = 1
        query_params = query_params.copy()
        query_params._mutable = True
        self.query_params = query_params
        self.per_page = per_page
        self.all_count = all_count
        self.pager_page_count = pager_page_count
        pager_count, b = divmod(all_count, per_page)
        if b != 0:
            pager_count += 1
        self.pager_count = pager_count

        half_pager_page_count = int(pager_page_count / 2)
        self.half_pager_page_count = half_pager_page_count

    @property
    def start(self):
        """
        数据获取值起始索引
        :return:
        """
        return (self.current_page - 1) * self.per_page

    @property
    def end(self):
        """
        数据获取值结束索引
        :return:
        """
        return self.current_page * self.per_page

    def page_html(self):
        if self.all_count == 0:
            return ""

        # 如果数据总页码pager_count<11 pager_page_count
        if self.pager_count < self.pager_page_count:
            pager_start = 1
            pager_end = self.pager_count
        else:
            # 数据页码已经超过11
            # 判断： 如果当前页 <= 5 half_pager_page_count
            if self.current_page <= self.half_pager_page_count:
                pager_start = 1
                pager_end = self.pager_page_count
            else:
                # 如果： 当前页+5 > 总页码
                if (self.current_page + self.half_pager_page_count) > self.pager_count:
                    pager_end = self.pager_count
                    pager_start = self.pager_count - self.pager_page_count + 1
                else:
                    pager_start = self.current_page - self.half_pager_page_count
                    pager_end = self.current_page + self.half_pager_page_count

        page_list = []

        if self.current_page <= 1:
            prev = '<li><a href="#"><span aria-hidden="true">&laquo;</span></a></li>'
        else:
            self.query_params['page'] = self.current_page - 1
            prev = '<li><a href="%s?%s#%s"><span aria-hidden="true">&laquo;</span></a></li>' % (
                self.base_url, self.query_params.urlencode(), self.browser_param)
        page_list.append(prev)
        for i in range(pager_start, pager_end + 1):
            self.query_params['page'] = i
            if self.current_page == i:
                tpl = '<li class="active"><a href="%s?%s#%s">%s</a></li>' % (
                    self.base_url, self.query_params.urlencode(), self.browser_param, i,)
            else:
                tpl = '<li><a href="%s?%s#%s">%s</a></li>' % (
                    self.base_url, self.query_params.urlencode(), self.browser_param, i,)
            page_list.append(tpl)

        if self.current_page >= self.pager_count:
            nex = '<li><a href="#"><span aria-hidden="true">&raquo;</span></a></li>'
        else:
            self.query_params['page'] = self.current_page + 1
            nex = '<li><a href="%s?%s#%s"><span aria-hidden="true">&raquo;</span></a></li>' % (
                self.base_url, self.query_params.urlencode(), self.browser_param)
        page_list.append(nex)

        if self.all_count:
            tpl = "<li class='disabled'><a>共%s条数据，页码%s/%s页</a></li>" % (
                self.all_count, self.current_page, self.pager_count,)
            page_list.append(tpl)
        page_str = "".join(page_list)
        return page_str


class FlakPagination(object):
    def __init__(self, current_page, all_count, base_url,  per_page, pager_page_count=7):
        """
        分页初始化
        :param current_page: 当前页码
        :param per_page: 每页显示数据条数
        :param all_count: 数据库中总条数
        :param base_url: URL(request.url)
        :param pager_page_count: 页面上最多显示的页码数量
        """

        def flask_url_deal(flask_url):
            '''
            :param flask_url: 使用request.url获取
            :return:
            '''
            res0 = flask_url.split("?")
            param_name = {}
            if len(res0) > 1:
                res1 = res0[1].split("&")
                res1 = [i for i in res1 if i != '']
                for item in res1:
                    res = item.split("=")
                    param_name[res[0]] = res[1]
            if "page" in param_name.keys():
                param_name.pop("page")
            final_url = res0[0] + "?"
            for item in param_name:
                final_url += item
                final_url += "="
                final_url += param_name.get(item)
                final_url += "&"
            return final_url
        self.base_url = flask_url_deal(base_url)
        try:
            self.current_page = int(current_page)
            if self.current_page <= 0:
                self.current_page = 1
        except Exception as e:
            self.current_page = 1
        self.per_page = per_page
        self.all_count = all_count
        self.pager_page_count = pager_page_count
        pager_count, b = divmod(all_count, per_page)
        if b != 0:
            pager_count += 1
        self.pager_count = pager_count

        half_pager_page_count = int(pager_page_count / 2)
        self.half_pager_page_count = half_pager_page_count

    @property
    def start(self):
        """
        数据获取值起始索引
        :return:
        """
        return (self.current_page - 1) * self.per_page

    @property
    def end(self):
        """
        数据获取值结束索引
        :return:
        """
        return self.current_page * self.per_page

    def page_html(self):
        """
        生成HTML页码
        :return:
        """
        if self.all_count == 0:
            return ""

        # 如果数据总页码pager_count<11 pager_page_count
        if self.pager_count < self.pager_page_count:
            pager_start = 1
            pager_end = self.pager_count
        else:
            # 数据页码已经超过11
            # 判断： 如果当前页 <= 5 half_pager_page_count
            if self.current_page <= self.half_pager_page_count:
                pager_start = 1
                pager_end = self.pager_page_count
            else:
                # 如果： 当前页+5 > 总页码
                if (self.current_page + self.half_pager_page_count) > self.pager_count:
                    pager_end = self.pager_count
                    pager_start = self.pager_count - self.pager_page_count + 1
                else:
                    pager_start = self.current_page - self.half_pager_page_count
                    pager_end = self.current_page + self.half_pager_page_count

        page_list = []

        if self.current_page <= 1:
            prev = '<li><a href="#"><span aria-hidden="true">&laquo;</span></a></li>'
        else:
            prev = '<li><a href="%spage=%s"><span aria-hidden="true">&laquo;</span></a></li>' % (
                self.base_url, self.current_page - 1)
        page_list.append(prev)
        for i in range(pager_start, pager_end + 1):
            if self.current_page == i:
                tpl = '<li class="active"><a href="%spage=%s">%s</a></li>' % (
                    self.base_url, i, i,)
            else:
                tpl = '<li><a href="%spage=%s">%s</a></li>' % (self.base_url, i, i,)
            page_list.append(tpl)

        if self.current_page >= self.pager_count:
            nex = '<li><a href="#"><span aria-hidden="true">&raquo;</span></a></li>'
        else:
            nex = '<li><a href="%spage=%s"><span aria-hidden="true">&raquo;</span></a></li>' % (
                self.base_url, self.current_page + 1)
        page_list.append(nex)

        if self.all_count:
            tpl = "<li class='disabled'><a>共%s条数据，页码%s/%s页</a></li>" % (
                self.all_count, self.current_page, self.pager_count,)
            page_list.append(tpl)
        page_str = "".join(page_list)
        return page_str

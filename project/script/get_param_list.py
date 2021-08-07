# coding=gbk
from flask import Markup


def flask_get_per_param_list(flask_url, param_name):
    '''
    :param flask_url: URL（http://***.com?status=0&status=1&category_id=1)
    :param param_name: 参数名称
    :return: param_name的所有值的列表对象
    '''
    url_params = flask_url.split("?")  # 分离URL？前后的数据，获取？后面的get请求参数
    if len(url_params) > 1:
        res_list = []
        res1 = url_params[1].split("&")
        res1 = [i for i in res1 if i != '']  # 去除空元素
        for item in res1:
            res = item.split("=")
            if "page" in res:
                continue
            if res[0] == param_name:
                res_list.append(res[1])
        return res_list
    else:
        return []


def flask_get_per_param_dict(flask_url, param_name_list):
    '''
    :param flask_url: URL（http://***.com?status=0&status=1&category_id=1)
    :param param_name_list: 参数名称列表
    :return: result_dict-->{'status': ['0'], 'category': []}
    '''
    url_params = flask_url.split("?")  # 分离URL？前后的数据，获取？后面的get请求参数
    result_dict = {}
    for i in param_name_list:
        result_dict[i] = []
    if len(url_params) > 1:
        res1 = url_params[1].split("&")
        res1 = [i for i in res1 if i != '']  # 去除空元素
        for item in res1:
            res = item.split("=")
            if "page" in res:
                continue
            flag = type(result_dict.get(res[0]))
            if flag == list:
                result_dict.get(res[0]).append(res[1])
        return result_dict
    else:
        return result_dict


def generate_param_url(param_dict):
    key_list = param_dict.keys()
    param_url = ''
    for i in key_list:
        values = param_dict.get(i)
        for j in values:
            param_url += str(i) + "=" + str(j) + "&"
    return param_url


class FlaskCheckFilter(object):
    def __init__(self, name, data_list, request, param_dict):
        '''
        :param name: such as "status"
        :param data_list: such as status_list=[0,1,-1]
        :param request:
        '''
        self.name = name
        self.data_list = data_list
        self.request = request
        self.param_dict = param_dict
        self.base_url = request.url.split("?")[0]

    def __iter__(self):
        for item in self.data_list:
            key = str(item[0])
            text = item[1]
            ck = ""
            # 如果当前用户请求的URL中status和当前循环key相等
            import copy
            param_dict = copy.deepcopy(self.param_dict)
            value_list = param_dict.get(self.name)  # {'status': ['0'], 'category': []}.get('status')
            if key == "1" and text == "最新":
                ck = 'checked'
            if key in value_list:
                ck = 'checked'
                value_list.remove(key)
            else:
                value_list.append(key)
            param_url = generate_param_url(param_dict)
            if param_url:
                url = "{}?{}".format(self.base_url, param_url)  # status=1&status=2&status=3&xx=1
            else:
                url = self.base_url
            tpl = '<a class="cell" href="{url}"><input type="checkbox" {ck} /><label>{text}</label></a>'
            html = tpl.format(url=url, ck=ck, text=text)
            # print(self.base_url, param_url)
            # return html
            yield Markup(html)

    def get_name(self):
        return self.name

    def get_result(self):
        res = [generate_param_url(self.param_dict), self.param_dict]
        return res

# res = flask_get_per_param_dict("http://10.210.53.162:5000/admin/manage/news?category_id=4", ['status', 'category_id'])
# print(res)

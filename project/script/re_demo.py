# coding=gbk
def get_per_param_dict(flask_url, param_name_list):
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
            res=item.split("=")
            if "page" in res:
                continue
            result_dict.get(res[0]).append(res[1])
        return result_dict
    else:
        return result_dict
def generate_param_url(param_dict):
    key_list=param_dict.keys()
    param_url=''
    for i in key_list:
        values=param_dict.get(i)
        for j in values:
            param_url+=str(i)+"="+str(j)+"&"
    return param_url
# url="http://10.210.53.162:5000/admin/manage/news?status=0&status=1&status=-1&category=0"
# res=flask_get_per_param_list(url,["status","category"])
# param=generate_param_url(res)
# print(res,param)

# def flask_get_per_param_list(flask_url, param_name):
#     '''
#     :param flask_url: URL（http://***.com?status=0&status=1&category_id=1)
#     :param param_name: 参数名称
#     :return: param_name的所有值的列表对象
#     '''
#     url_params = flask_url.split("?")  # 分离URL？前后的数据，获取？后面的get请求参数
#     if len(url_params) > 1:
#         res_list = []
#         res1 = url_params[1].split("&")
#         res1 = [i for i in res1 if i != '']  # 去除空元素
#         for item in res1:
#             res = item.split("=")
#             if "page" in res:
#                 continue
#             if res[0] == param_name:
#                 res_list.append(res[1])
#         return res_list
#     else:
#         return []

first={'status': ['1', '-1', '0'], 'category_id': ['5', '1', '2']}
status_list=first.get("status")
status_list.remove("1")
print(first,status_list)
# coding=gbk
def class_filter(index):
    if index == 1:
        return "first"
    elif index == 2:
        return "second"
    elif index == 3:
        return "third"
    else:
        return "hot-other"


def transfer_time(value):
    res = value.strftime("%Y-%m-%d %H:%M")
    return res


def to_category(value):
    if value == 1:
        return "latest"
    elif value == 2:
        return "#"
    else:
        return "company"


def digest_format(digest):
    if len(digest) < 128:
        return digest
    else:
        return digest[0:128] + "..."


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

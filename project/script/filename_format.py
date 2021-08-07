import datetime


def filename_format(user_id, user_mobile, file_name):
    current_datetime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    old_name = str(file_name).split(".")[0]
    file_type = str(file_name).split(".")[-1]
    final_name = str(user_id) + '_' + str(user_mobile) + '_' + current_datetime + '_' + old_name + '.' + file_type
    return final_name

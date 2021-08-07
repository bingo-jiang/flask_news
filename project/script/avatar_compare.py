# -*-coding:utf-8-*-
import os


def compare(target_dirs):
    dir_list = []
    file_list = []
    for root, dirs, files in os.walk("f:\\"):
        if dirs:
            for item in dirs:
                dir_res = os.path.join(root, item).decode('gbk').encode('utf-8')
                dir_list.append(dir_res)
        if files:
            for file in files:
                file_res = os.path.join(root, file).decode('gbk').encode('utf-8')
                file_list.append(file_res)
    return dir_list,file_list


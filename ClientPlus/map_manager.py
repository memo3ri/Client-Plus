import os
import time
import difflib


def ver_analysis(amm_path, file_name, file_name_a):  # 对有表示的对比版本号
    # 有提示情况下进行获取版本
    # 需要考虑各种因素

    if file_name.split(".")[0].find("v") > 0 and file_name_a.split(".")[0].find("v") > 0:

        # 父版本号
        v_count = file_name.split("v")[1].count(".")

        # 添加版本数字至列表
        str_v = file_name.split("v")[1].split(".")[0]
        for i in range(0, v_count - 1):
            str_v = str_v + file_name.split("v")[1].split(".")[i + 1]

        # 判断版本
        str_a = file_name_a.split("v")[1].split(".")[0]
        for i in range(0, v_count - 1):
            str_a = str_a + file_name_a.split("v")[1].split(".")[i + 1]
        if str_v.isdigit() and str_a.isdigit():
            if int(str_v) > int(str_a):
                # 删除低版本
                os.remove(amm_path + file_name_a)


def map_(amm_path, keywords):
    lists = os.listdir(amm_path)
    for i in lists:
        file_name = str(i)
        for j in lists:
            file_name_a = j
            # 文件不同时才进行处理
            if file_name != file_name_a:
                # 判断前缀是否相同
                if file_name.find(f"{keywords}") != -1 and file_name_a.find(f"{keywords}") != -1:
                    prefix = file_name.split(keywords)[0]
                    if file_name_a.find(f"{keywords}") != -1:
                        prefix_a = file_name_a.split(keywords)[0]
                        # 当前缀都吻合时，开始判断地图名称
                        if prefix == prefix_a:
                            # 有关键字处理
                            if difflib.SequenceMatcher(None, file_name.split(keywords)[1],
                                                       file_name_a.split(keywords)[1]).quick_ratio() > 0.7:
                                # 当被对比文件小于对比文件时，判断日期
                                if os.path.getsize(amm_path + file_name) > os.path.getsize(amm_path
                                                                                           + file_name_a):
                                    if time.ctime(os.path.getmtime(amm_path + file_name)) > time.ctime(
                                            os.path.getmtime(amm_path + file_name_a)):
                                        os.remove(amm_path + file_name_a)
                                elif os.path.getsize(amm_path + file_name) == os.path.getsize(amm_path
                                                                                              + file_name_a):
                                    ver_analysis(amm_path, file_name, file_name_a)
                                    # 如果仍然无法判断出，则保留最新修改的文件
                                    if time.ctime(os.path.getmtime(amm_path + file_name)) > time.ctime(
                                            os.path.getmtime(amm_path + file_name_a)):
                                        os.remove(amm_path + file_name_a)

                else:
                    if file_name_a.find(f"{keywords}") == -1:
                        # 无关键字处理
                        if difflib.SequenceMatcher(None, file_name, file_name_a).quick_ratio() > 0.7:
                            if os.path.getsize(amm_path + file_name) > os.path.getsize(amm_path
                                                                                       + file_name_a):
                                if time.ctime(os.path.getmtime(amm_path + file_name)) > time.ctime(
                                        os.path.getmtime(amm_path + file_name_a)):
                                    os.remove(amm_path + file_name_a)
                            elif os.path.getsize(amm_path + file_name) == os.path.getsize(amm_path
                                                                                          + file_name_a):
                                ver_analysis(amm_path, file_name, file_name_a)
                                # 如果仍然无法判断出，则保留最新修改的文件
                                if time.ctime(os.path.getmtime(amm_path + file_name)) > time.ctime(
                                        os.path.getmtime(amm_path + file_name_a)):
                                    os.remove(amm_path + file_name_a)


if __name__ == "__main__":
    map_("./Custom/", "]")

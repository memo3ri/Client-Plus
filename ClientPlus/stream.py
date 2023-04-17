# 增量更新模块
# 您可以在此优化逻辑

import json
import os.path
import datetime
import requests
import threading

from urllib.request import urlopen

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                         ' like Gecko) Chrome/107.0.0.0 Safari/537.36'}


def mkdir(lists):
    # 基础文件夹生成
    for i in lists:
        if not os.path.exists(i):
            os.makedirs(i)


def multi_thread(url_list, thread, path):
    # 多线程下载
    # 设置下载线程, 默认为3个
    if not isinstance(thread, int):
        thread = 3

    # 下载列表大于线程数时则分批次下载
    if len(url_list) > int(thread):
        # 格式化列表
        new_list = []
        while len(url_list) >= thread:
            new_list.append(url_list[:thread])
            url_list = url_list[thread:]
        if len(url_list) > 0:
            new_list.append(url_list)

        # 启动线程
        for elements in new_list:
            threads = []
            for j in elements:
                t = threading.Thread(target=download, args=(j, path))
                t.start()
                threads.append(t)

            # 等待线程结束
            for t in threads:
                t.join()

    else:

        # 当所需下载文件数量 < 线程数时按文件数量生成线程
        threads = []
        for j in url_list:
            t = threading.Thread(target=download, args=(j, path))
            t.start()
            threads.append(t)

        # 等待线程结束
        for t in threads:
            t.join()

    return True


def url_encode(string):
    # URL转码
    result = ""
    for char in string:
        if char == " ":
            result += "%20"
        elif ord(char) < 128:
            result += char
        else:
            encoded_char = char.encode('utf-8')
            hex_str = ''.join([f'%{byte:02X}' for byte in encoded_char])
            result += hex_str
    return result


def download(download_url, path):
    # 下载资源并保存
    try:
        file_size = int(urlopen(download_url).info().get('Content-Length', -1))  # 获取下载文件的总大小
        if os.path.exists(path):
            first_byte = os.path.getsize(path)  # 获取已经下载部分文件的大小
        else:
            first_byte = 0
        header = {"Range": "bytes=%s-%s" % (first_byte, file_size)}  # 设置下载头
        req = requests.get(download_url, headers=header, stream=True)  # 请求下载文件剩下的部分
        with(open(path, 'ab')) as f:
            for chunk in req.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        return True

    except:
        print("资源更新_连接url或保存失败")
        return False


def master_data(data_path, var, url):
    # 将主文件夹内容先写入配置文件
    if os.path.exists(f"{data_path}Update/{var}/download/stream/data/master"):
        with open(f"{data_path}Update/{var}/download/stream/data/master/data.ini",
                  'w') as configfile:
            configfile.write(
                str(get_data(url + "/-/refs/master/logs_tree/?format=json&offset=0")))


def get_data(url_):
    # 获取gitcode仓库信息
    res = requests.get(url_, headers=headers)
    res.encoding = "utf-8"
    data = json.loads(res.content)

    gitcode_data = []
    for gitcode in data:
        gitcode_data.append(gitcode["file_name"])
        gitcode_data.append(gitcode["type"])
        gitcode_data.append(str(gitcode["commit"]).split("committed_date\': \'")[1].split("\'")[0])

    return gitcode_data


def save_information(data_path, var, path, url):
    # 写入时间信息
    if os.path.exists(f"{data_path}Update/{var}/download/stream/data/{path}"):
        with open(f"{data_path}Update/{var}/download/stream/data/{path}/data.ini",
                  'w') as configfile:
            configfile.write(
                str(get_data(url + "/-/refs/" + path + "/logs_tree/?format=json&offset=0")))


def merge(list1, list2): # 远程 本地
    # 合并列表
    val_ = list2
    for i in range(0, int(len(list1) / 2)):

        validation_name = i * 2
        validation_date = i * 2 + 1
        if list2.count(list1[validation_name]):

            # 获取validation列表元素在val中的位置
            lists = list2.index(list1[validation_name])
            # 取validation的时间信息
            val_[lists + 1] = list1[validation_date]

        else:
            val_.append(list1[validation_name])
            val_.append(list1[validation_date])

    return val_


def main(url, data_path, var):
    # 使用队列存储待遍历的文件夹
    global validation_info
    queue = ["master"]
    update_list, update_list_, validation = [], [], []
    var_ = 0

    # 读取本地验证信息
    if os.path.exists(f"{data_path}Update/{var}/download/stream/data_validation/data.ini"):
        with open(f"{data_path}Update/{var}/download/stream/data_validation/data.ini", "r") as f:
            validation_info = f.read()
        file_update_validation = True
        try:
            validation_info = eval(validation_info)
        except:
            # 验证集为空，且存在导致错误
            validation_info = []
            file_update_validation = False

    else:
        validation_info = []
        file_update_validation = False

    while queue:
        var_ += 1
        if var_ == 2:
            # 保存主目录数据
            master_data(data_path, var, url)

        if os.path.exists(f"{data_path}Update/{var}/download/stream/data.txt"):
            with open(f"{data_path}Update/{var}/download/stream/data.txt", "r") as f:
                data_old = f.read()
            data = json.loads(data_old)
            data_old_list = []
            for data_old_ in data:
                data_old_list.append(data_old_["file_name"])
                data_old_list.append(data_old_["type"])
                data_old_list.append(str(data_old_["commit"]).split("committed_date\': \'")[1].split("\'")[0])

        # 弹出队首元素，即将要遍历的文件夹
        current_dir = queue.pop(0)
        resource = get_data(url + "/-/refs/" + current_dir + "/logs_tree/?format=json&offset=0")

        # 读取本地保存的文件信息文件
        if os.path.exists(f"{data_path}Update/{var}/download/stream/data/{current_dir}/data.ini"):
            with open(f"{data_path}Update/{var}/download/stream/data/{current_dir}/data.ini", "r") as f:
                info = f.read()
            file_update = True
            info = eval(info)

        else:
            info = []
            file_update = False

        # 写入时间信息
        save = str(resource)
        if os.path.exists(f"{data_path}Update/{var}/download/stream/data/{current_dir}/data.ini"):
            with open(f"{data_path}Update/{var}/download/stream/data/{current_dir}/data.ini") as f:
                read_ = f.read()
            if read_ != save:
                with open(f"{data_path}Update/{var}/download/stream/data/{current_dir}/data.ini",
                          'w') as configfile:
                    configfile.write(save)
        else:
            # 创建文件更新信息存储文件夹
            mkdir([f"{data_path}Update/{var}/download/stream/data_validation/{current_dir}",
                   f"{data_path}Update/{var}/download/stream/data/{current_dir}"])
            with open(f"{data_path}Update/{var}/download/stream/data/{current_dir}/data.ini",
                      'w') as configfile:
                configfile.write(save)

        # 遍历当前Gitcode文件夹中的所有文件和文件夹
        for content in range(0, int(len(resource) / 3)):
            file_name = resource[content * 3]
            file_type = resource[content * 3 + 1]
            file_date = resource[content * 3 + 2]

            # 拼接文件/文件夹的路径
            # URL文件路径
            path = current_dir + "/" + resource[content * 3]
            # 如果是文件，则存储至更新列表
            if file_type == "blob":

                if file_update or file_update_validation:
                    # 存在数据文件开始对比时间信息进行判断是否更新，并等待验证

                    if info.count(file_name) != 0:

                        info_number = info.index(file_name)
                        # 当前文件的本地日期
                        get_date = str(info[info_number + 2])
                        # 存在时继续比较信息,本地文件信息格式化
                        update_data_file = datetime.datetime.strptime(get_date, "%Y-%m-%dT%H:%M:%S.000+08:00")

                        # 远程文件信息格式化
                        time_data = datetime.datetime.strptime(file_date, "%Y-%m-%dT%H:%M:%S.000+08:00")

                        # 本地验证文件信息格式化
                        if validation_info.count(file_name) != 0:

                            # 遍历验证数据，获取时间信息
                            for j in range(0, int(len(validation_info) / 2)):
                                if path == validation_info[j * 2]:
                                    validation_info = datetime.datetime.strptime(validation_info[j * 2 + 1],
                                                                                 "%Y-%m-%dT%H:%M:%S.000+08:00")

                            # 当远程时间 = 本地文件首次下载日期的时间 > 本地文件下载确定后的时间，则此文件或许为上次下载中
                            # 断的文件，且远程仓库已更新，予以加入更新，并删除原文件
                            if time_data == update_data_file > validation_info:
                                update_list.append(path)
                                update_list.append(file_date)

                            # 当远程时间 > 本地文件首次下载日期的时间 > 本地文件下载确定后的时间，则此文件或许为上次下载中
                            # 断的文件，予以加入更新
                            elif time_data > update_data_file > validation_info:
                                update_list_.append(path)
                                update_list.append(file_date)

                        else:
                            # 远程时间大于本地时间，加入更新列表
                            if time_data > update_data_file:
                                update_list.append(path)
                                update_list.append(file_date)

                    else:
                        # 不存在时则加入更新列表
                        update_list.append(path)
                        update_list.append(file_date)

                else:
                    # 不存在上次获取的数据列表，则本文件夹所有文件进行更新
                    update_list.append(path)
                    update_list.append(file_date)

            # 如果是文件夹，则将其加入队列尾部
            elif file_type == "tree":
                queue.append(path)

    # 正常进行更新或继续更新的文件列表
    for i in range(0, int(len(update_list) / 2)):
        # path_ = i[:i.rfind("/") + 1]
        path_ = os.path.dirname(update_list[i * 2])
        if not os.path.exists(f"{data_path}Update/{var}/download/stream/{path_}"):
            os.makedirs(f"{data_path}Update/{var}/download/stream/{path_}")
        if download(url_encode(url + "/-/raw/" + update_list[i * 2] + "?inline=false"),
                    f"{data_path}Update/{var}/download/stream/{update_list[i * 2]}"):
            validation.append(update_list[i * 2])
            validation.append(update_list[i * 2 + 1])

    # 没下载完成且远程仓库也已更新的文件处理
    for i in range(0, int(len(update_list_) / 2)):
        path_ = os.path.dirname(update_list_[i * 2])
        if not os.path.exists(f"{data_path}Update/{var}/download/stream/{path_}"):
            os.makedirs(f"{data_path}Update/{var}/download/stream/{path_}")
        # 删除存在的文件
        if os.path.exists(f"{data_path}Update/{var}/download/stream/{i}"):
            os.remove(f"{data_path}Update/{var}/download/stream/{i}")
        if download(url_encode(url + "/-/raw/" + update_list_[i * 2] + "?inline=false"),
                    f"{data_path}Update/{var}/download/stream/{update_list[i * 2]}"):
            validation.append(update_list_[i * 2])
            validation.append(update_list_[i * 2 + 1])

    # 写入验证数据
    if validation:
        if os.path.exists(f"{data_path}Update/{var}/download/stream/data_validation/data.ini"):
            with open(f"{data_path}Update/{var}/download/stream/data_validation/data.ini",
                      "r") as configfile:
                val = eval(configfile.read())
            # 合并时间信息
            date = merge(validation, val)
            with open(f"{data_path}Update/{var}/download/stream/data_validation/data.ini",
                      'w') as configfile:
                configfile.write(str(date))
        else:
            with open(f"{data_path}Update/{var}/download/stream/data_validation/data.ini",
                      'w') as configfile:
                configfile.write(str(validation))


if __name__ == "__main__":
    main("https://gitcode.net/qq_41194307/client_lib", "./Resources/Client/manager/", "try")

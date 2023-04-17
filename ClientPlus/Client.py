# By：Bt（Bilibili：Bt_Asker）
# 适用于所有基于DTA客户端的RA2

import os
import time
import random
import shutil
import datetime
import requests
import threading
import subprocess
import configparser

from sys import exit
from PIL import Image
from bs4 import BeautifulSoup
from urllib.request import urlopen

from map_manager import map_  # 导入地图处理模块
from random_cache import random_cache  # 导入远程随机化模块
from stream import main as stream_download  # 导入增量更新（流式传输）模块
# from random_cache import main as random_cache  # 导入远程随机化模块
from clientplus_update import clientplus_update  # 导入Client+自动更新模块
from processes import clientplus_process, clientdx_process  # 导入进程检测模块


def get_config(file, name, value):
    # 初始化配置文件
    i = file.get(f"{name}", f"{value}")
    return i


def move_folder(src, dst):
    # 批量移动文件
    if os.path.exists(src):
        for root, dirs, files in os.walk(src):
            # 创建目标文件夹中对应的文件夹
            for d in dirs:
                dir_path = os.path.join(root, d).replace(src, dst)
                os.makedirs(dir_path, exist_ok=True)
            # 移动文件
            for f in files:
                src_file_path = os.path.join(root, f)
                dst_file_path = src_file_path.replace(src, dst)
                shutil.move(src_file_path, dst_file_path)
        for folder in os.listdir(src):
            shutil.rmtree(f"{src}/{folder}")
    else:
        return False


def unpack(zippack, out_filepath):
    # 解压压缩包
    zipexe = data_path.replace("/", "\\") + "Lib\\7z.exe"
    os.system("\"" + zipexe + "\"" + " x " + "\"" + zippack + "\"" + " -o" + "\"" + out_filepath + "\"")


# 排序
def bubblesort(time_list):
    n = len(time_list)
    # 遍历所有数组元素
    for i in range(n):
        for j in range(0, n - i - 1):
            if time_list[j] > time_list[j + 1]:
                time_list[j], time_list[j + 1] = time_list[j + 1], time_list[j]


# 读取基本配置
def read_basic_path():
    base = configparser.ConfigParser()
    if not os.path.exists("./base.ini"):
        # 生成基本路径配置文件
        base['Path'] = {'base_path': "./Resources/",
                        'data_path': "./Resources/Client/manager/"}
        base["Author"] = {"bilibili": "Bt_Asker",
                          "Bt": "https://space.bilibili.com/326134780"}
        base["Version"] = {"version": "v0.6Beta",
                           "channels": "default"}
        with open('base.ini', 'w') as configfile:
            base.write(configfile)
        base.read('./base.ini')
    else:
        # 不存在值则添加
        base.read('./base.ini')
        if 'channels' not in base['Version']:
            base['Version']['channels'] = 'sta'
        with open('./base.ini', 'w') as configfile:
            base.write(configfile)

    global base_path, data_path, channels
    base_path = get_config(base, "Path", "base_path")
    data_path = get_config(base, "Path", "data_path")
    channels = get_config(base, "Version", "channels")


# 读取配置
def read_config():
    config = configparser.ConfigParser()

    if not os.path.exists(f"{data_path}config.ini"):
        config['Main'] = {'Enable': 'True'}

        config['Randomization'] = {'random_fiwwle_name': "",
                                   "random_output_path": "",
                                   "random_data_storage": ""}

        config['Update'] = {"update": "True"}

        config["DTA_Priority"] = {"level": "high"}

        config["Log"] = {"log_level": "none"}

        config["Developer_Options"] = {"RSN": "1", "Cnc_master_list_log": "False"}
        with open(f'{data_path}config.ini', 'w') as config_build:
            config.write(config_build)
    try:
        # 生成配置文件
        if os.path.exists(f"{data_path}config.ini"):
            config.read(f'{data_path}config.ini')

            # 添加 更新 中的键值
            if not config.has_option('Update', 'streaming_download'):
                config.set('Update', 'streaming_download', 'True')
                config.set('Update', 'random', 'True')
                with open(f'{data_path}config.ini', 'w') as config_build:
                    config.write(config_build)

            # 自定义地图处理
            if not 'Automatic_map_management' in config.sections():
                config.add_section('Automatic_map_management')
                config.set('Automatic_map_management', 'Enable', 'False')
                config.set('Automatic_map_management', 'path', './Maps/Custom')
                config.set('Automatic_map_management', 'name_repair', 'True')
                config.set('Automatic_map_management', 'Keep_the_latest_version', 'True')

                with open(f'{data_path}config.ini', 'w') as config_build:
                    config.write(config_build)

            # 图片优化
            if not 'Optimization' in config.sections():
                config.add_section('Optimization')
                config.set('Optimization', 'image_optimization', 'False')
                config.set('Optimization', 'quality', '95')

                with open(f'{data_path}config.ini', 'w') as config_build:
                    config.write(config_build)

            # Client+自动更新
            if not 'ClientPlus_update' in config.sections():
                config.add_section('ClientPlus_update')
                config.set('ClientPlus_update', 'update', 'True')
                config.set('ClientPlus_update', 'update_channels', 'Stable')

                with open(f'{data_path}config.ini', 'w') as config_build:
                    config.write(config_build)

    except:
        print("读取文件失败")

    config.read(f'{data_path}/config.ini', encoding="UTF-8")
    global Enable, update, log_level, RSN, Cnc_master_list_log, Cnc_master_list_log, DTA_Priority, random_fiwwle_name, \
        random_output_path, client_path, AMM_Enable, AMM_path, AMM_name_repair, AMM_Keep_the_latest_version, \
        clientplus_update_info, update_channels_info, image_optimization_, Optimization_quality
    Enable = get_config(config, "Main", "Enable")

    # Random
    try:
        random_fiwwle_name = get_config(config, "Randomization", "random_fiwwle_name").split(",")
        random_output_path = get_config(config, "Randomization", "random_output_path").split(",")
        client_path = get_config(config, "Randomization", "random_data_storage").split(",")
    except:
        print("随机化读取失败")
    # Update
    try:
        update = get_config(config, "Update", "update")
    except:
        print("自动更新读取失败")
    # Automatic_map_management
    try:
        AMM_Enable = get_config(config, "Automatic_map_management", "Enable")
        AMM_path = get_config(config, "Automatic_map_management", "path")
        AMM_name_repair = get_config(config, "Automatic_map_management", "name_repair")
        AMM_Keep_the_latest_version = get_config(config, "Automatic_map_management", "Keep_the_latest_version")
    except:
        print("自定义地图处理读取失败")

    # Log
    try:
        log_level = get_config(config, "Log", "log_level")
    except:
        print("日志处理读取失败")
    # Developer_Options
    try:
        RSN = get_config(config, "Developer_Options", "RSN")
        Cnc_master_list_log = get_config(config, "Developer_Options", "Cnc_master_list_log")
    except:
        print("进阶设置读取失败")
    # DTA_Priority
    try:
        DTA_Priority = get_config(config, "DTA_Priority", "level")
    except:
        print("Cncnet服务器获取信息读取失败")
    # Optimization
    try:
        image_optimization_ = get_config(config, "Optimization", "image_optimization")
        Optimization_quality = get_config(config, "Optimization", "quality")
    except:
        print("图像优化读取失败")

    # ClientPlus_Update
    try:
        clientplus_update_info = get_config(config, "ClientPlus_update", "update")
        update_channels_info = get_config(config, "ClientPlus_update", "update_channels")
    except:
        print("Client+更新读取错误")


client_folder = ["temp", "Lib", "Update"]


def mkdir(list):
    # 基础文件夹生成
    for i in list:
        if not os.path.exists(f'{data_path}%s' % i):
            os.makedirs(f'{data_path}%s' % i)


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

    except:
        print("资源更新_连接url或保存失败")


def randomization():
    # Client+ 图片/音频随机化\
    # 列表诺为空停止执行
    try:
        mkdir(client_path)
        if client_path[0] != "":
            for i in range(0, len(random_fiwwle_name)):
                filedir = os.listdir(data_path + client_path[i])
                # print(filedir)
                try:
                    random_file = random.randint(int(RSN), len(filedir))
                except:
                    print("随机化似乎没有目标文件")
                    exit()
                file_name = filedir[random_file - 1]
                # 复制随机化最终文件到目标目录
                shutil.copyfile(data_path + client_path[i] + "/" + file_name,
                                base_path + random_output_path[i] + random_fiwwle_name[i])
    except:
        pass


def read_url():
    # 获取本地存储URL
    global download_url_master
    update_list = os.listdir(f"{data_path}/Update/")
    if len(update_list) >= 1:
        update_config = configparser.ConfigParser()
        for i in update_list:
            # 生成配置列表
            if not os.path.exists(f"{data_path}/Update/{i}/update.ini"):
                update_config['Update'] = {"update": "False", 'url_type': "agit",
                                           "Streaming_download": "False", "url": "", "notes": "none"}
                with open(f"{data_path}/Update/{i}/update.ini", 'w') as update_ini:
                    update_config.write(update_ini)

            # 读取配置
            update_config.read(f"{data_path}/Update/{i}/update.ini", encoding='utf-8')
            update_switch = get_config(update_config, "Update", "update")
            if update_switch.lower() == "true":
                url_type = get_config(update_config, "Update", "url_type").lower()
                Streaming_download = get_config(update_config, "Update", "Streaming_download")
                url_ = get_config(update_config, "Update", "url")
                if url_type == "auto":
                    # 尝试识别
                    url_type = url_.split("https://")[1].split(".")[0]
                if url_type == "github":
                    url = url_.split("github.com/")[1]
                    download_url_master = "https://github.com/" + url + "/archive/master.zip"
                    github_update_url = "https://api.github.com/repos/" + url
                elif url_type == "agit":
                    url = url_.split("agit.ai/")[1]
                    download_url_master = "https://agit.ai/" + url + "/archive/master.zip"
                    agit_update_url = ""
                elif url_type == "gitcode":
                    url = url_.split("gitcode.net/")[1]
                    download_url_master = "https://gitcode.net/" + url + "/-/archive/master/" + url.split("/")[1] \
                                          + "-master.zip"
                    # 增量更新URL
                    stream_url = url_
                    url_ = url_ + "/-/refs/master/logs_tree/?format=json&offset=0"

                else:
                    print("未知的更新仓库")
                    return "Url类型无法识别"

                # 伪装
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                                         ' like Gecko) Chrome/107.0.0.0 Safari/537.36'}
                try:
                    html = requests.get(url_, headers=headers)
                except:
                    print(f"无法链接到{url_type}，可能是网络问题")
                    return 1
                html.encoding = "utf-8"
                soup = BeautifulSoup(html.text, "html.parser")
                data = configparser.ConfigParser()

                # 对比时间信息
                if os.path.exists(f"{data_path}/Update/{i}/data.ini"):
                    data.read(f"{data_path}/Update/{i}/data.ini")
                    try:
                        update_data_file = datetime.datetime.strptime(get_config(data, "Data", "date_utc"),
                                                                      "%Y-%m-%d %H:%M:%S")
                    except:
                        return f"{i}_Data信息出错"

                # 对比校验信息
                if os.path.exists(f"{data_path}/Update/{i}/data_validation.ini"):
                    data.read(f"{data_path}/Update/{i}/data_validation.ini")
                    try:
                        update_data_new_file = datetime.datetime.strptime(get_config(data, "Data", "date_utc"),
                                                                          "%Y-%m-%d %H:%M:%S")
                    except:
                        print(f"{i}_data_validation信息出错")
                        exit()

                # 开始判断使用平台
                # Agit
                if url_type == "agit":
                    out = soup.find_all("th", class_="text grey right age")
                    time_str = str(out).split("title=")[1].split("UTC")[0].split(",")[1]

                    # 提前8H
                    time_data = datetime.datetime.strptime(time_str, ' %d %b %Y %H:%M:%S ')
                    if not os.path.exists(f"{data_path}/Update/{i}/data.ini"):
                        # 生成基本路径配置文件
                        data['Data'] = {'date_utc': f"{time_data}"}
                        with open(f"{data_path}/Update/{i}/data.ini", 'w') as configfile:
                            data.write(configfile)
                        update_download(url_type, download_url_master, i)

                    elif time_data > update_data_file:
                        data['Data'] = {'date_utc': f"{time_data}"}
                        with open(f"{data_path}/Update/{i}/data.ini", 'w') as configfile:
                            data.write(configfile)
                        update_download(url_type, download_url_master, i)

                # Gitcode
                elif url_type == "gitcode":
                    if Streaming_download.lower() == "true":
                        # 开始进行增量更新
                        stream_download(stream_url, data_path, i)
                        # 如果不为空则复制下载文件至游戏目录
                        if os.path.exists(f"{data_path}Update/{i}/download/stream/master"):
                            if len(os.listdir(f"{data_path}Update/{i}/download/stream/master/")) != 0:
                                move_folder(f"{data_path}Update/{i}/download/stream/master/", './')

                    else:
                        # 获取时间信息
                        time_list = []
                        commit_count = str(soup).count("committed_date")
                        # 存在则对比时间信息
                        try:
                            # 获取Gitcode文件时间
                            for j in range(0, int(commit_count)):
                                time_data = datetime.datetime.strptime(
                                    str(soup).split("""committed_date":""")[j + 1].split(""","committer_name""")[
                                        0].strip("""
                                ""
                                """), "%Y-%m-%dT%H:%M:%S.000+08:00")
                                time_list.append(time_data)
                                bubblesort(time_list)
                            time_data = time_list[int(commit_count) - 1]
                        except:
                            print("GItcode仓库文件不存在或获取时间信息错误")
                            exit()
                        # 不存在配置文件，生成更新配置文件
                        if not os.path.exists(f"{data_path}/Update/{i}/data.ini"):
                            data['Data'] = {'date_utc': f"{time_data}"}
                            with open(f"{data_path}/Update/{i}/data.ini", 'w') as configfile:
                                data.write(configfile)
                            update_download(url_type, download_url_master, i)
                            data['Data'] = {'date_utc': f"{time_data}"}
                            with open(f"{data_path}/Update/{i}/data_validation.ini", 'w') as configfile:
                                data.write(configfile)
                        else:
                            data.read(f"{data_path}/Updateupdate_data_file/{i}/data.ini", "rb")

                            # 验证文件不存在时的操作
                            if not os.path.exists(
                                    f"{data_path}/Update/{i}/data_validation.ini") and time_data == update_data_file:
                                # 当不存在验证信息，且仓库更新时间=本地首次下载时间时，文件尚未下载完成，继续下载
                                update_download(url_type, download_url_master, i)

                                # 写入下载时间数据
                                data['Data'] = {'date_utc': f"{time_data}"}
                                with open(f"{data_path}/Update/{i}/data_validation.ini", 'w') as configfile:
                                    data.write(configfile)

                            elif not os.path.exists(
                                    f"{data_path}/Update/{i}/data_validation.ini") and time_data > update_data_file:
                                # 当不存在验证信息，且仓库更新时间＞本地首次下载时间时，即用户还没下载完成仓库就已更新
                                os.remove(f"{data_path}/Update/{i}/download/data.zip")
                                update_download(url_type, download_url_master, i)

                                # 写入下载时间数据
                                data['Data'] = {'date_utc': f"{time_data}"}
                                with open(f"{data_path}/Update/{i}/data_validation.ini", 'w') as configfile:
                                    data.write(configfile)


                            # 验证文件存在时的操作
                            elif os.path.exists(f"{data_path}/Update/{i}/data_validation.ini"):
                                # 仓库时间 = 本地存储时间时继续下载所需数据，未下载完成，继续下载
                                if time_data == update_data_file > update_data_new_file:
                                    update_download(url_type, download_url_master, i)

                                    # 写入验证数据
                                    data['Data'] = {'date_utc': f"{time_data}"}
                                    with open(f"{data_path}/Update/{i}/data_validation.ini", 'w') as configfile:
                                        data.write(configfile)

                                # 如果上次下载数据和本次下载数据不匹配，则重新下载
                                elif time_data > update_data_file > update_data_new_file:
                                    # 写入下载时间数据
                                    data['Data'] = {'date_utc': f"{time_data}"}
                                    with open(f"{data_path}/Update/{i}/data.ini", 'w') as configfile:

                                        data.write(configfile)
                                    os.remove(f"{data_path}/Update/{i}/download/data.zip")
                                    update_download(url_type, download_url_master, i)

                                    # 写入验证数据
                                    data['Data'] = {'date_utc': f"{time_data}"}
                                    with open(f"{data_path}/Update/{i}/data_validation.ini", 'w') as configfile:
                                        data.write(configfile)

                                elif time_data > update_data_file == update_data_new_file:
                                    # 开始更新
                                    data['Data'] = {'date_utc': f"{time_data}"}
                                    with open(f"{data_path}/Update/{i}/data.ini", 'w') as configfile:
                                        data.write(configfile)
                                    update_download(url_type, download_url_master, i)

                                    # 写入验证数据
                                    data['Data'] = {'date_utc': f"{time_data}"}
                                    with open(f"{data_path}/Update/{i}/data_validation.ini", 'w') as configfile:
                                        data.write(configfile)


def update_download(url_type, download_url_master, i):
    # 非流式传输
    # 从github/agit上获取必要的库
    libs = ["7z.exe", "7z.dll"]
    for j in libs:
        if not os.path.exists(f"{data_path}" + "/Lib/%s" % j):
            if url_type == "agit":
                lib = "https://agit.ai/Bt_Asker/DTAClient--Lib/raw/branch/master/"
            elif url_type == "github":
                lib = "https://github.com/AskeBt/client--libs/raw/main/"
            elif url_type == "gitcode":
                lib = "https://gitcode.net/qq_41194307/client_lib/-/raw/master/"
            else:
                print("更新源错误！")
                exit()
            download(f"{lib}%s" % j, f"{data_path}/Lib/%s" % j)

    if not os.path.exists(f"{data_path}Update/{i}/download"):
        os.makedirs(f"{data_path}Update/{i}/download")
    if not os.path.exists(f"{data_path}Update/{i}/temp"):
        os.makedirs(f"{data_path}Update/{i}/temp")
    try:
        download(download_url_master, f"{data_path}/Update/{i}/download/data.zip")
    except:
        print("下载错误_可能是URL目标不正确")
        return "下载错误_可能是URL目标不正确"
    # 解压安装资源
    if os.path.exists(f"{data_path}/Update/{i}/download/data.zip"):
        unpack(f"{data_path}/Update/{i}/download/data.zip", f"./{data_path}/Update/{i}/temp")
    else:
        print("无解压资源")
    time.sleep(2)
    if len(os.listdir(f"./{data_path}Update/{i}/temp/")) == 1:
        zip_path = os.listdir(f"./{data_path}Update/{i}/temp/")[0]
        # 移动解压后的内容至游戏目录
        move_folder(f"{data_path}Update/{i}/temp/{zip_path}/", './')
        os.system('taskkill /f /im %s' % '7z.exe')
        time.sleep(4)
        # 删除下载资源
        if os.path.exists(f"{data_path}Update/{i}/download/data.zip"):
            os.remove(f"{data_path}Update/{i}/download/data.zip")
    else:
        # 移动解压后的内容至游戏目录
        move_folder(f"{data_path}Update/{i}/temp/", './')
        os.system('taskkill /f /im %s' % '7z.exe')
        time.sleep(4)
        if os.path.exists(f"{data_path}Update/{i}/download/data.zip"):
            os.remove(f"{data_path}Update/{i}/download/data.zip")


def image_optimization():
    # 图片大小优化以转移IO压力
    image_path, file_names = ["./Resources/", "./Resources/MainMenu/"], []
    for i in image_path:
        for j in os.listdir(i):
            # 判断是否为PNG或JPG
            if j.endswith(".png"):
                jpg_magic_number = open(i + j, "rb").read(2)
                if jpg_magic_number == b"\x89\x50":
                    with Image.open(i + j) as img:
                        # 先检查模式，再检查是否有透明像素
                        if 'A' in img.mode and img.getextrema()[3][0] >= 255:
                            # 转换为RGB模式
                            img = img.convert('RGB')
                            # 保存图片
                            img.save(f'{i}/{j}', 'JPEG', quality=Optimization_quality)

                    # elif jpg_magic_number == b"\xff\xd8":
                    #     pass


def maps_fix():
    if AMM_path[-1] != "/":
        AMM_path += "/"

    # 地图拓展名修复
    def amm_name_repair_(AMM_path):
        if os.path.exists(AMM_path):
            # 纠正文件名
            for name in os.listdir(AMM_path):
                portion = name.split(".")
                if portion[1] == "yrm" or portion[1] == "mpr":
                    os.rename(AMM_path + "/" + name, AMM_path + "/" + portion[0] + ".map")

    # 地图拓展名修复
    if AMM_name_repair.lower():
        amm_name_repair_(AMM_path)
    # 自动地图版本处理
    if AMM_Keep_the_latest_version.lower():
        amm_name_repair_(AMM_path)
        map_(AMM_path, "]")


def debug_level(level):
    level = level.lower()
    # debug目标路径
    debug_path = "./debug"
    if os.path.exists(debug_path):
        match level:
            case "none":
                # 无保留清理
                shutil.rmtree(debug_path)

            case "info":
                # 保留信息
                for root, dirs, files in os.walk('./debug/'):
                    for name in files:
                        if name.endswith(".dmp"):
                            os.remove(os.path.join(root, name))

            case "warning":
                # 保留警告和错误信息
                    for filename in os.listdir(debug_path):
                        if filename.endswith(".log"):
                            with open(os.path.join(debug_path, filename), 'r') as file:
                                lines = file.readlines()
                                if not lines or lines[0].lower() == "[level: warning]\n":
                                    continue

                            with open(os.path.join(debug_path, filename), 'w') as file:
                                file.write('[Level: warning]\n')
                                for line in lines:
                                    if 'warning' in line:
                                        file.write(line)


def cnc_info():
    download("http://cncnet.org/master-list", f"{data_path}server_info.log")


def run_game():
    # os.system(f"start /{DTA_Priority} "" .\Resources\clientdx.exe")
    if os.path.exists(".\Resources\clientdx.exe"):
        subprocess.Popen(f"start /{DTA_Priority} "" .\Resources\clientdx.exe", shell=True)


def user_command():
    # 用户指令
    if os.path.exists("./command.ini"):
        try:
            command = configparser.ConfigParser()
            command.read("./command.ini", encoding="UTF-8")
            del_file = get_config(command, "Command", "del").split(",")
            for i in del_file:
                if os.path.isdir(i):
                    shutil.rmtree(i)
                else:
                    os.remove(i)
            os.remove("./command.ini")

        except:
            current_dir = os.getcwd()
            with open('file.txt', 'r') as f:
                for line in f:
                    if 'delfile:' in line:
                        line_ = line.split("\"")
                        try:
                            del_file = line_[1].replace("/", "\\")
                            os.remove(current_dir + del_file)
                        except:
                            # 格式有误
                            pass

                    elif 'deltree:' in line:
                        line_ = line.split("\"")
                        try:
                            del_tree = line_[1].replace("/", "\\")
                            shutil.rmtree(current_dir + del_tree)
                        except:
                            # 格式有误
                            pass


def clientupdate_script(data_path):
    # 判断Client+是否进行更新
    if os.path.exists("./script.bat"):
        # 打开脚本
        subprocess.Popen(f"start \"\" .\\script.bat", shell=True)

        while 1:
            # 检查文件锁
            if os.path.exists(f"{data_path}\\lock.l"):
                os.remove(f"{data_path}\\lock.l")
                os.remove("./script.bat")
                break
            time.sleep(0.1)
        exit(0)


if __name__ == "__main__":

    # 创建基本保存数据目录
    read_basic_path()

    if not os.path.exists(data_path):
        os.makedirs(data_path)
    read_config()

    # Client+ 总控
    if Enable.lower() == "true":
        # 判断Client+是否进行更新
        clientupdate_script(data_path)

        # 判断Client+进程是否已经存在，存在则不运行Client+
        if not clientplus_process():
            os.system("start "" .\Resources\clientdx.exe")
            exit(0)

        mkdir(client_folder)

        # 随机化运行
        randomization()

        # 地图检测运行
        try:
            if AMM_Enable.lower() == "true":
                maps_fix()
        except:
            pass

        # 判断DTA客户端是否在运行
        if not clientdx_process("clientdx.exe"):
            # 开始游戏，等待后续步骤
            run_game()
            time.sleep(6)
        else:
            # 已有一个实例在运行，仅执行保留客户端只执行脚本内容
            pass

        # 选择清理debug
        try:
            debug_level(log_level)
        except:
            pass


        def update_t1():
            # 进行更新
            try:
                if update.lower() == "true":
                    read_url()
            except:
                pass
            user_command()


        def image_optimization_t2():

            # 图片优化
            if image_optimization_.lower() == "true":
                image_optimization()


        def cnc_master_list_log_t3():
            try:
                # 获取服务器列表
                if Cnc_master_list_log.lower() == "true":
                    cnc_info()
            except:
                pass


        def clientplus_update_t4():
            # 检查Client+更新
            try:
                if clientplus_update_info.lower() == "true":
                    # 此处更改你的Client+更新源
                    clientplus_update("https://gitcode.net/qq_41194307/client_lib/-/raw/master/ClientPlus", channels,
                                      data_path)
            except:
                pass


        # 创建并运行线程
        thread_list = [update_t1, image_optimization_t2, cnc_master_list_log_t3, clientplus_update_t4]
        threads = []
        for i in thread_list:
            t = threading.Thread(target=i)
            t.start()
            threads.append(t)

        for t in threads:
            t.join()
        exit(0)

    else:
        os.system("start "" .\Resources\clientdx.exe")
        exit(0)

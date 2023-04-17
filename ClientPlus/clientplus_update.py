# Client+ 自身更新模块

import os
import sys
import requests
import configparser

from bs4 import BeautifulSoup
from urllib.request import urlopen


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
        return 0
    except:
        print("资源更新_连接url或保存失败", download_url)
        return "error"


def update(url, data_path, type_):
    # 下载新版本
    if download(f"{url}Client+.exe?inline=false", f"{data_path}Temp/Client+.exe") == "error":
        return "没有更新内容"
    else:
        # 修改当前版本信息
        ver = configparser.ConfigParser()
        ver.read("./base.ini")
        ver.set('Version', 'version', f'{type_}')
        with open('base.ini', 'w') as f:
            ver.write(f)


def clientplus_update(url, update_channels, data_path):
    ver = configparser.ConfigParser()
    try:
        ver.read("./base.ini")
        version = ver.get("Version", "version")
    except:
        return "缺少版本信息文件"

    # 判断版本号
    try:
        version = version.split("Beta")[0]
    except:
        pass
    try:
        version = version.split("v")[1]
    except:
        # 格式错误或未知则退出
        if isinstance(version, int) or isinstance(version, float):
            pass
        else:
            return 1

    # 操作系统判断
    if update_channels.lower() == "beta":
        # Beta版
        if os.path.exists("C:\Program Files (x86)"):
            # 64位
            url += "/Beta/86_64x/"
            type_ = "Beta"
        else:
            # 32位
            url += "/Beta/86/"
            type_ = "Beta"
    else:
        # 正式版
        if os.path.exists("C:\Program Files (x86)"):
            # 64位
            url += "/86_64x/"
            type_ = ""
        else:
            # 32位
            url += "/86/"
            type_ = ""

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                             ' like Gecko) Chrome/107.0.0.0 Safari/537.36'}
    version_info = url + "versioninfo.txt"
    res = requests.get(version_info, headers=headers)
    res.encoding = "utf-8"
    soup = BeautifulSoup(res.text, "html.parser")
    # 获取最新的版本号用于对比
    txt = str(soup).split("version=")[1].split(";")[0]

    type_ = "v" + txt + type_
    if float(version) < float(txt):
        # 开始更新
        if download(f"{url}script.bat", f"{data_path}Temp/script.bat") == "error":
            # 如果没有更新脚本则执行默认操作
            # 获取当前进程名
            exe_ = sys.argv[0].split("\\")[-1]
            # 格式化路径
            data_path_ = data_path.replace("/", "\\")
            if not os.path.exists(f"{data_path}Temp/"):
                os.makedirs(f"{data_path}Temp")
            with open("script.bat", "w") as f:
                # 写入一个移动文件用的bat
                f.write(
f"""::这是Client+的更新脚本 一般它会在下次启动游戏更新后自动删除
title Client+ 更新脚本，稍后会自行关闭
mode con cols=20 lines=1
echo off
ping 127.0.0.1 -n 5 >nul
move "{data_path_}Temp\\Client+.exe" "{exe_}"
start "" "{exe_}"
echo 1 > "{data_path_}\\lock.l"
exit"""
                )
            info = update(url, data_path, type_)

        else:
            # 有更新脚本则使用远程仓库下载的脚本
            info = update(url, data_path, type_)

        return info
    return "当前为最新版本"


if __name__ == "__main__":
    # 获取更新的来源
    print(clientplus_update("https://gitcode.net/qq_41194307/client_lib/-/raw/master/ClientPlus", "none",
                      "./Resources/Client/manager/"))

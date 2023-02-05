# Client+ v0.4
# By：Bt（Bilibili：Bt_Asker）
# 适用于所有基于DTA客户端的RA2

import os
import time
import random
import shutil
import datetime
import requests
import configparser


from sys import exit
from bs4 import BeautifulSoup

def get_config(file,name,value):
    # 初始化配置文件
    i = file.get(f"{name}", f"{value}")
    return i

def bubbleSort(time_list):
    n = len(time_list)
    # 遍历所有数组元素
    for i in range(n):
        for j in range(0, n-i-1):
            if time_list[j] > time_list[j+1] :
                time_list[j], time_list[j+1] = time_list[j+1], time_list[j]

def read_basic_path():
    base = configparser.ConfigParser()
    if not os.path.exists("./base.ini"):
            # 生成基本路径配置文件
            base['Path'] = {'base_path' : "./Resources/",
                        'data_path' : "./Resources/Client/manager/"}
            base["Author"] = {"bilibili" : "Bt_Asker",
                        "Bt" : "https://space.bilibili.com/326134780"}
            base["Version"] = {"version": "v0.4Beta"}
            with open('base.ini', 'w') as configfile:
                base.write(configfile)
    base.read('./base.ini')
    global base_path,data_path
    base_path = get_config(base,"Path","base_path")
    data_path = get_config(base,"Path","data_path")

def read_config():
    config = configparser.ConfigParser()
    
    if not os.path.exists(f"{data_path}config.ini"):
        config['Main'] = {'Enable' : 'True'}

        config['Randomization'] = {'random_fiwwle_name' : "",
        "random_output_path" : "",
        "random_data_storage" : ""}

        config['Update'] = {"update" : "True"}

        config["DTA_Priority"] = {"level" : "high"}

        config["Log"] = {"log_level" : "none"}

        config["Developer_Options"] = {"RSN" : "1","Cnc_master_list_log" : "False"}
        with open(f'{data_path}config.ini', 'w') as configfile:
                    config.write(configfile)

    config.read(f'{data_path}/config.ini', encoding="UTF-8")
    global Enable,update,log_level,RSN,Cnc_master_list_log,Cnc_master_list_log,DTA_Priority,random_fiwwle_name,\
        random_output_path,client_path
    Enable = get_config(config,"Main", "Enable")

    #Random
    random_fiwwle_name = get_config(config,"Randomization","random_fiwwle_name").split(",")
    random_output_path = get_config(config,"Randomization","random_output_path").split(",")
    client_path = get_config(config,"Randomization","random_data_storage").split(",")
    #Update
    update = get_config(config,"Update", "update")
    #Log
    log_level = get_config(config,"Log","log_level")
    #Developer_Options
    RSN = get_config(config,"Developer_Options","RSN")
    Cnc_master_list_log = get_config(config,"Developer_Options","Cnc_master_list_log")
    #DTA_Priority
    DTA_Priority = get_config(config,"DTA_Priority","level")

client_folder = ["temp","Lib","Update"]

def mkdir(list):
    # 基础文件夹生成
    for i in list:
        if not os.path.exists(f'{data_path}%s' % i):
            os.makedirs(f'{data_path}%s' % i)      

def download(download_url,path):
    # 下载资源并保存
    try:
        r = requests.get(download_url) 
        with open(path, "wb") as code:
            code.write(r.content)
    except:
        print("资源更新_连接url或保存失败")

def unpack(zippack,out_filepath):
    # 解压压缩包
    zipexe = data_path.replace("/", "\\") + "Lib\\7z.exe"
    os.popen("\""+zipexe+"\""+" x "+"\""+zippack+"\""+" -o"+"\""+out_filepath+"\"")

def movefile():
    # Client+ 图片/音频随机化\
    # 列表诺为空停止执行
    try:
        mkdir(client_path)
        list = len(random_fiwwle_name)
        for i in range(0,list):
            filedir = os.listdir(data_path + client_path[i])
            try:
                random_file = random.randint(int(RSN),int(len(filedir)))
            except:
                print("随机化似乎没有目标文件")
                exit()
            file_name = filedir[random_file - 1]
            shutil.copyfile(data_path + client_path[i] + "/" + file_name,
                            base_path + random_output_path[i] + random_fiwwle_name[i])
    except:
        print("出错")
        pass

def read_url():
    # 获取本地存储URL
    global download_url_master
    if len(os.listdir(f"{data_path}/Update/")) >= 1:
        update_config = configparser.ConfigParser()
        for i in os.listdir(f"{data_path}/Update/"):
            # 生成配置列表
            if not os.path.exists(f"{data_path}/Update/{i}/update.ini"):
                update_config['Update'] = {"update" : "False",'url_type' : "agit",
                                           "Streaming_download" : "False","url" : "","notes" : "none"}
                with open(f"{data_path}/Update/{i}/update.ini", 'w') as configfile:
                    update_config.write(configfile)
            # 读取配置
            update_config.read(f"{data_path}/Update/{i}/update.ini" ,encoding='utf-8')
            update_switch = get_config(update_config,"Update","update")
            if update_switch == "True":
                url_type = get_config(update_config,"Update","url_type").lower()
                Streaming_download = get_config(update_config,"Update","Streaming_download")
                url_ = get_config(update_config,"Update","url")

                try:
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
                        # qq_41194307/client_lib
                        download_url_master = "https://gitcode.net/" + url + "/-/archive/master/" + url.split("/")[1] + "-master.zip"
                        # https://gitcode.net/qq_41194307/client_lib/-/archive/master/client_lib-master.zip
                        url_ = url_ + "/-/refs/master/logs_tree/?format=json&offset=0"
                    else:
                        print("未知的更新仓库")
                        exit()
                except:
                    print("URL错误，或许是不支持的URL")
                    exit()

                # 伪装
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                                         ' like Gecko) Chrome/107.0.0.0 Safari/537.36'}
                try:
                    html=requests.get(url_,headers=headers)
                except:
                    print(f"无法链接到{url_type}，可能是网络问题")
                    exit()
                html.encoding = "utf-8"
                soup = BeautifulSoup(html.text,"html.parser")
                data = configparser.ConfigParser()

                # 对比时间信息
                data.read(f"{data_path}/Update/{i}/data.ini")
                try:
                    if os.path.exists(f"{data_path}/Update/{i}/data.ini"):
                        update_data_file = datetime.datetime.strptime(get_config(data,"Data","date_utc"),
                                                                        "%Y-%m-%d %H:%M:%S")
                except:
                    print(f"{i}_Data信息出错")
                    exit()


                # 开始判断使用平台
                # Agit
                if url_type == "agit":
                    out = soup.find_all("th",class_="text grey right age")
                    time_str = str(out).split("title=")[1].split("UTC")[0].split(",")[1]

                    # 提前8H
                    time_data= datetime.datetime.strptime(time_str,' %d %b %Y %H:%M:%S ')
                    if not os.path.exists(f"{data_path}/Update/{i}/data.ini"):
                        # 生成基本路径配置文件
                        data['Data'] = {'date_utc' : f"{time_data}"}
                        with open(f"{data_path}/Update/{i}/data.ini", 'w') as configfile:
                                data.write(configfile)
                        update_download(url_type,download_url_master)

                    if time_data > update_data_file:
                        data['Data'] = {'date_utc': f"{time_data}"}
                        with open(f"{data_path}/Update/{i}/data.ini", 'w') as configfile:
                            data.write(configfile)
                        update_download(url_type,download_url_master)
                        

                # Gitcode
                if url_type == "gitcode":
                    # 获取时间信息
                    time_list = []
                    commit_count = str(soup).count("committed_date")
                    # 存在则对比时间信息
                    try:
                        # 获取Gitcode文件时间
                        for j in range(0, int(commit_count)):
                            time_data = datetime.datetime.strptime(
                                str(soup).split("""committed_date":""")[j + 1].split(""","committer_name""")[0].strip("""
                            ""
                            """), "%Y-%m-%dT%H:%M:%S.000+08:00")
                            time_list.append(time_data)
                            bubbleSort(time_list)
                        time_data = time_list[int(commit_count)-1]
                    except:
                        print("GItcode仓库文件不存在或获取时间信息错误")
                        exit()

                    # 不存在配置文件，生成更新配置文件
                    if not os.path.exists(f"{data_path}/Update/{i}/data.ini"):
                        data['Data'] = {'date_utc' : f"{time_data}"}
                        with open(f"{data_path}/Update/{i}/data.ini", 'w') as configfile:
                                data.write(configfile)
                        update_download(url_type,download_url_master)
                    else:

                        # 存在则对比时间，判断是否进行更新
                        data.read(f"{data_path}/Update/{i}/data.ini")
                        if Streaming_download.lower() == "false":
                            if time_data > update_data_file:
                                data['Data'] = {'date_utc': f"{time_data}"}
                                with open(f"{data_path}/Update/{i}/data.ini", 'w') as configfile:
                                    data.write(configfile)
                                update_download(url_type, download_url_master)
                            pass


def update_download(url_type,download_url_master):
    # 非流式传输
    # 从github/agit上获取必要的库
    libs = ["7z.exe","7z.dll"]
    for i in libs:
        if not os.path.exists(f"{data_path}" + "/Lib/%s" % i):
            if url_type == "agit":
                lib = "https://agit.ai/Bt_Asker/DTAClient--Lib/raw/branch/master/"
            elif url_type == "github":
                lib = "https://github.com/AskeBt/client--libs/raw/main/"
            elif url_type == "gitcode":
                lib = "https://gitcode.net/qq_41194307/client_lib/-/raw/master/"
            else:
                print("更新源错误！")
                exit()
            download(f"{lib}%s" % i,f"{data_path}/Lib/%s" % i)

    try:
        download(download_url_master,f"{data_path}/data.zip")
    except:
        print("下载错误_可能是URL目标不正确")

    # 解压安装资源
    if os.path.exists(f"{data_path}/data.zip"):
        unpack(f"{data_path}/data.zip",f"./{data_path}/temp/")
    else:
        print("无解压资源")
    time.sleep(2)
    if len(os.listdir(f"./{data_path}/temp/")) == 1:
        zip_path = os.listdir(f"./{data_path}/temp/")[0]
    shutil.copytree(f"{data_path}temp/{zip_path}/", './', dirs_exist_ok=True)
    url="https://agit.ai/Bt_Asker/Client-P"
    
    # 删除下载资源
    os.system('taskkill /f /im %s' % '7z.exe')
    time.sleep(4)
    if os.path.exists(f"{data_path}data.zip"):
        os.remove(f"{data_path}data.zip")
    if os.path.exists(f"{data_path}temp/{zip_path}"):
        shutil.rmtree(f"{data_path}temp/{zip_path}")
    print("更新完成")

def debug_level(level):
    if level == "none":
        # 无保留清理
        if os.path.exists("./debug"):
            shutil.rmtree("./debug")
    elif level == "info":
        # 保留文本文件
        for root, dirs, files in os.walk('./debug/'):
            for name in files:
                if(name.endswith(".dmp")):
                    os.remove(os.path.join(root, name))
    else:
        pass

def cnc_info():
    download("http://cncnet.org/master-list",data_path)

def start_game():
    os.system(f"start /{DTA_Priority} "" .\Resources\clientdx.exe")


def user_command():
    if os.path.exists("./command.ini"):
        command = configparser.ConfigParser()
        command.read("./command.ini", encoding="UTF-8")
        del_file = get_config(command, "Command", "del").split(",")
        for i in del_file:
            try:
                if os.path.isdir(i):
                    shutil.rmtree(i)
                else:
                    os.remove(i)
            except:
                pass
        os.remove("./command.ini")
        
    

if __name__ == "__main__":
    # 创建基本保存数据目录
    read_basic_path()
    if not os.path.exists(data_path):
        os.makedirs(data_path)
    read_config()

    # Client+ 总控
    if Enable == "True":
        mkdir(client_folder)

        # 随机化运行
        movefile()

        # 开始游戏，等待后续步骤
        start_game()
        time.sleep(6)

        # 选择清理debug
        debug_level(log_level)
        if update == "True":
            read_url()

        # 获取服务器列表
        if Cnc_master_list_log == "True":
            cnc_info()
        user_command()
        exit()

    else:
        os.system("start "" .\Resources\clientdx.exe")
        exit()
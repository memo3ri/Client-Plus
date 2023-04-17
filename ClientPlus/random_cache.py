# 远程随机化缓存模块
import os
import json
import shutil
import random
import requests
import configparser

from PIL import Image
from urllib.request import urlopen

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                         ' like Gecko) Chrome/107.0.0.0 Safari/537.36'}


def layer_overlay(overlay_path, path):
    # 图片叠加
    # 打开底层图片
    background = Image.open(path)
    # 打开覆盖图片
    overlay = Image.open(overlay_path)
    # 粘贴覆盖图片到底层图片上
    background.paste(overlay, (0, 0), overlay)
    # 保存结果
    background.save(path)


def download(download_url, path):
    # 下载资源并保存
    try:
        if os.path.exists(path):
            os.remove(path)
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
        return False


def get_data(url):
    # 获取指定文件和类型
    data = url.replace("tree", "refs", 1) + "/logs_tree/?format=json&offset=0"
    res = requests.get(data, headers=headers)
    res.encoding = "utf-8"
    data = json.loads(res.content)

    gitcode_data = []
    for gitcode in data:
        gitcode_data.append(gitcode["file_name"])
        gitcode_data.append(gitcode["type"])
    return gitcode_data


def random_cache(data_path, url, path, cache_max):
    # 将随机化文件添加至列表
    lists = []
    data = get_data(url)
    for i in range(0, int(len(data) / 2)):
        if data[i * 2 - 1] == "blob":
            lists.append(data[i * 2])

    # 随机文件
    try:
        random_file = lists[random.randint(0, len(lists) - 1)]
    except:
        print("无法进行远程随机化，可能是由于远程随机化的配置文件错误导致")
    # 合成url

    # print(os.path.dirname(path)[1])
    if "\\" in url:
        url = url.replace("\\", "/")

    if "./" in url:
        file_path = os.path.dirname(path).split("./")[1]
    else:
        file_path = os.path.dirname(path)

    file_name = os.path.basename(path)

    dl_url = url.split("/-/tree/")[0] + "/-/raw/" + url.split("/-/tree/")[1] + "/" + random_file + "?inline=false"

    # 创建缓存文件夹
    if not os.path.exists(f"{data_path}.cache/random/{file_path}/{os.path.splitext(file_name)[0]}"):
        os.makedirs(f"{data_path}.cache/random/{file_path}/{os.path.splitext(file_name)[0]}")

    # 下载并缓存到文件夹
    cache_file_list = os.listdir(f"{data_path}.cache/random/{file_path}/{os.path.splitext(file_name)[0]}/")
    cache_number = len(os.listdir(f"{data_path}.cache/random/{file_path}/{os.path.splitext(file_name)[0]}/"))
    if download(dl_url, f"{data_path}.cache/random/{file_path}/{os.path.splitext(file_name)[0]}/{random_file}"):
        # 缓存成功，随机删除源文件

        # 当缓存文件数小于最大缓存数时继续缓存
        if cache_number < cache_max:
            # 小于最大缓存，存储文件
            shutil.copyfile(f"{data_path}.cache/random/{file_path}/{os.path.splitext(file_name)[0]}/{random_file}",
                            path)

        else:
            # 获取将删除的文件
            while 1:
                del_file = cache_file_list[random.randint(0, cache_number - 1)]
                # 如果删除的文件=随机到的文件，重新随机选择
                if del_file != random_file:
                    break
            # 删除文件
            os.remove(f"{data_path}.cache/random/{file_path}/{os.path.splitext(file_name)[0]}/{del_file}")
            shutil.copyfile(f"{data_path}.cache/random/{file_path}/{os.path.splitext(file_name)[0]}/{random_file}",
                            path)

    else:
        # 当前无法连接到仓库，不删除文件，并随机选择本地缓存的文件进行随机化
        random_file = cache_file_list[random.randint(0, cache_number - 1)]
        shutil.copyfile(f"{data_path}.cache/random/{file_path}/{os.path.splitext(file_name)[0]}/{random_file}",
                        path)
    return random_file


def main(data_path, path, cache_max):
    lists = os.listdir(f"{data_path}Update/")

    for i in lists:
        config = configparser.ConfigParser()
        if os.path.exists(f"{data_path}Update/{i}/random/config.ini"):
            try:
                config.read(f'{data_path}Update/{i}/random/config.ini', encoding='UTF-8')
            except:
                return "更新/随机化文件错误"

            # 读取配置文件
            enable = config.get("random", "enable")

            def get_config_items(config, section, prefix):
                return [config.get(section, key) for key in config.options(section) if key.startswith(prefix)]

            urls = get_config_items(config, "random", "url")
            file_path = get_config_items(config, "random", "file")
            image_overlay_urls = get_config_items(config, "image_overlay", "url")

            image_overlay_enable = config.get('image_overlay', 'enable')

            if enable.lower() == "true":
                # 开始下载随机图片
                for count in range(len(urls)):
                    random_cache(data_path, urls[count], file_path[count], cache_max)

            if image_overlay_enable.lower() == "true":
                # 开始进行图片叠加
                if os.path.exists(f"{path}/.cache/overlay_path"):
                    os.makedirs(f"{path}/.cache/overlay_path")
                for count in range(len(urls)):
                    file = os.path.splitext(file_path[count])[0]
                    # 创建叠加图片的缓存文件夹
                    if not os.path.exists(f"{path}/.cache/overlay_path/{file}"):
                        os.makedirs(f"{path}/.cache/overlay_path/{file}")
                    # 开始下载叠加图片
                    random_cache(data_path, image_overlay_urls[count], f"{path}/.cache/overlay_path/{file}", cache_max)
                    layer_overlay(f"{path}/.cache/overlay_path/{file}", path)

        else:
            # 生成配置文件
            if not os.path.exists(f"{data_path}Update/{i}/random"):
                os.makedirs(f"{data_path}Update/{i}/random")
            config['random'] = {'enable': 'False',
                                'url': "",
                                'file': "", }

            config['image_overlay'] = {"enable": "False",
                                       "url": ""}

            config["cache"] = {"cache_max": "10"}

            with open(f"{data_path}Update/{i}/random/config.ini", 'w') as configfile:
                config.write(configfile)


if __name__ == '__main__':
    print(main("./Resources/Client/manager/", "./Resources/1.png", 10))

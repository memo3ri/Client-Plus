import json
import os
import random
import shutil
from urllib.parse import urlparse
from urllib.request import urlopen

import requests
from PIL import Image


class Config:
    def __init__(self):
        self.resources_path = '.\\Resources'
        self.main_path = '.\\Resources\\Client'

        self.src_url = 'https://gitcode.net/qq_41194307/endpoint_line'

        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                                      ' like Gecko) Chrome/107.0.0.0 Safari/537.36'}


class RandomFile(Config):
    def __init__(self):
        super().__init__()

    def randomFile(self, src: str, dst: str):
        main_menu_src_path = os.path.join(self.main_path, src)
        main_menu_dst_path = os.path.join(self.resources_path, dst)

        files = os.listdir(main_menu_src_path)
        file = files[random.randint(0, len(files) - 1)]
        shutil.copy2(os.path.join(main_menu_src_path, file), main_menu_dst_path)


class Resource(Config):
    def __init__(self):
        super().__init__()

    @staticmethod
    def _download(url: str, path: str):
        """
        下载资源并保存
        :param path:
        :param url:
        :return:
        """
        file_name = os.path.basename(urlparse(url).path)  # 从 URL 中获取文件名
        save_path = os.path.join(path, file_name)  # 将当前工作目录和文件名合并为保存路径

        file_size = int(urlopen(url).info().get('Content-Length', -1))  # 获取下载文件的总大小
        if os.path.exists(save_path):
            first_byte = os.path.getsize(save_path)  # 获取已经下载部分文件的大小
        else:
            first_byte = 0
        header = {"Range": "bytes=%s-%s" % (first_byte, file_size)}  # 设置下载头
        try:
            req = requests.get(url, headers=header, stream=True)  # 请求下载文件剩下的部分
        except Exception as e:
            print(e)
            return False
        with(open(save_path, 'ab')) as f:
            for chunk in req.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        return True

    def getRandomResources(self, file_type: str):
        """
        url: url + "/-/refs/" + path + "/logs_tree/?format=json&offset=0"))
        获取随机资源
        :param file_type:
        :return:
        """

        def getInfo():
            depository_info = f'{self.src_url}/-/refs/master/random/{file_type.lower()}/logs_tree/?format=json&offset=0'
            try:
                res = requests.get(depository_info, headers=self.headers)
            except Exception as e:
                print(e)
                return {}
            res.encoding = "utf-8"
            try:
                data = json.loads(res.content)
            except Exception as e:
                print(e)
                return {}
            result = {}
            for m_file in data:
                if m_file["file_name"] == '.gitkeep':
                    continue
                result[m_file["file_name"]] = {
                    'type': m_file["type"],
                    'date': str(m_file["commit"]).split("\': \'")[1].split("\'")[0]
                }
            return result

        file_list = []
        for file, value in getInfo().items():
            file_list.append(file)

        if not file_list:
            return {}
        print(file_list)
        file = file_list[random.randint(0, len(file_list) - 1)]
        dl_url = f'{self.src_url}/-/raw/master/{file_type.lower()}/{file}?inline=false'
        return self._download(dl_url, os.path.join(self.main_path, file_type))

    @staticmethod
    def layer_overlay(src_image_path: str, overlay_path: str):
        """
        叠加图片
        :param src_image_path: 底图片
        :param overlay_path: 覆盖图片
        :return:
        """
        background = Image.open(src_image_path).convert('RGBA')
        # 打开覆盖图片
        overlay = Image.open(overlay_path).convert('RGBA')
        # 粘贴覆盖图片到底层图片上
        background.paste(overlay, (0, 0), overlay)
        # 如果图像模式是RGBA或P，将其转换为RGB
        if background.mode in ("RGBA", "P"):
            background = background.convert("RGB")
        # 保存结果
        background.save(src_image_path)


class Run(RandomFile, Resource):
    def __init__(self):
        super().__init__()
        self.randomFile('mainmenubg', 'MainMenu\\mainmenubg.png')
        self.randomFile('loadingscreen', 'loadingscreen.png')

        files = os.listdir(os.path.join(self.main_path, 'UI\\'))
        file = files[random.randint(0, len(files) - 1)]

        self.layer_overlay(os.path.join(self.resources_path, 'loadingscreen.png'),
                           os.path.join(self.main_path, 'UI', file))

        self.randomFile('chaoticimpulse', 'chaoticimpulse.wma')

        os.system('start /high \".\\Resources\\clientdx.exe\"')

        self.getRandomResources('mainmenubg')
        self.getRandomResources('loadingscreen')
        self.getRandomResources('chaoticimpulse')
        self.getRandomResources('UI')


if __name__ == '__main__':
    run = Run()
# r = RandomFile()
# r.run()

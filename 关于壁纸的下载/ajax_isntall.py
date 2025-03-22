# -*- conding:utf-8 -*-
# !usr/bin/env python
#
#   ajax_install.py
#
# 创建时间 2025/3/20   19:16
# TUGE ( *^-^)ρ(*╯^╰)
# 从属于 IMG 项目

import typing
import requests
import uuid
import hashlib
from pathlib import Path as path
from abc import ABCMeta, abstractmethod
import pickle

TIME_OUT = 10
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
}
FILE_END = 'jpg'
SAVE_TUGE = 'save.TUGE'
LOCALHOST = 'localhost'


class Img_Task(metaclass=ABCMeta):
    """下载图片必须遵守的接口"""

    @abstractmethod
    def install_img(self):
        """下载图片的逻辑"""
        pass

    @abstractmethod
    def __str__(self):
        """显示任务对象"""
        pass

    @abstractmethod
    def save(self):
        """用于缓存数据"""
        pass

    @abstractmethod
    def get_dir_path(self) -> path:
        pass


class Img:
    def __init__(self, img_path: path, md5: str) -> None:
        """下载后的文件处理

        * `img_path`: 图片保存路径 `path` 类型
        * `md5`: 图片的md5值"""
        self.img_path = img_path
        self.md5 = self.in_md5_set(md5)

    def in_md5_set(self, md5: str):
        """用于判断图片是否合法"""
        if md5 in MD5_SET.ALL_MD5_SET:  # 判断文件md5值是否存在
            print(f"Remove img: {str(self.img_path)}")
            self.img_path.unlink()
            return None
        elif self.img_path.stat().st_size > 1000:  # 判断 文件是否合法
            print(f"Remove img: {str(self.img_path)}")
            self.img_path.unlink()
            return None
        else:
            return md5

    def __str__(self) -> str:
        return f"{self.img_path}\t{self.md5}"


class MD5_SET:
    """全局 md5 值"""
    ALL_MD5_SET: typing.Set[str] = set()
    """全局 Task 任务对象"""
    __Task: typing.Set[Img_Task] = set()
    task_个数: int = 0

    @staticmethod
    def add_taste(task: Img_Task):
        MD5_SET.task_个数 += 1
        MD5_SET.__Task.add(task)

    @staticmethod
    def remove_taste(task: Img_Task):
        MD5_SET.task_个数 -= 1
        MD5_SET.__Task.remove(task)

    @staticmethod
    def Task() -> typing.Iterable[Img_Task]:
        MD5_SET.task_个数 = len(set(MD5_SET.__Task))
        new_tast = set(MD5_SET.__Task)
        for i in new_tast:
            yield i


class install_工具类:

    @staticmethod
    def install_img(url: str, Download_path: path, time_out: int = None) -> typing.Union[None, Img]:
        """下载单张图片
        * `url`: 下载的 url
        * `Download_path`: 下载位置
        * `time_out`: 超时时间"""
        try:
            return install_工具类._install_img(url, Download_path, time_out)
        except requests.exceptions.Timeout as error_time:
            print(f"访问超时! Message: {error_time}")
            return None
        except Exception as error_exception:
            print(f"未知错误! Message: {error_exception}")
            return None

    @staticmethod
    def install_json(url: str, Download_path: path, select: typing.List[typing.Union[str, int]],
                     time_out: int = None) -> typing.Union[None, Img]:
        """下载单张图片
        只有下载成功才会返回 `Img` 对象,否则返回 `None`
        * `url`: 下载的 url
        * `Download_path`: 下载位置
        * `select`: json选择器
        * `time_out`: 超时时间"""
        try:
            return install_工具类._install_json(url, Download_path, select, time_out)
        except requests.exceptions.Timeout as error_time:
            print(f"访问超时! Message: {error_time}")
        except requests.exceptions as error_exception:
            print(f"未知错误! Message: {error_exception}")
        finally:
            return None

    @classmethod
    def _install_img(cls, url: str, Download_path: path, time_out: int = None) -> Img:
        """通过 `url` 下载图片,并返回图片的 md5 值
        * `url`: 图片下载链接
        * `Download_path`: 下载路径,要求 `path` 对象"""
        file_name = uuid.uuid1()
        img = requests.get(url=url, headers=HEADERS, timeout=time_out)
        with open(f'{Download_path}\\{file_name}.{FILE_END}', mode='bw') as file:
            file.write(img.content)
            readable_hash = hashlib.md5(img.content).hexdigest()
        print(f"Download\t{file_name}\t100%")
        return Img(path(f'{Download_path}\\{file_name}.{FILE_END}'), readable_hash)

    @classmethod
    def _install_json(cls, url: str, Download_path: path, select: typing.List[str] = None,
                      time_out: int = None) -> Img:
        """通过下载 `json` 数据取出其 img_url 并下载,并返回图片的 md5 值

            * `url`:下载链接
            * `Download_path`:下载路径 'path' 对象类型
            * `select`:`json`的选择路径
            * `time_out`:等待时间,默认5秒"""
        if time_out is None:
            time_out = TIME_OUT
        json_data = requests.get(url=url, headers=HEADERS, timeout=time_out).json()
        for i in select:
            json_data = json_data[i]
        img_url = json_data
        return install_工具类._install_img(url=img_url,
                                           Download_path=Download_path,
                                           time_out=time_out, )

    @staticmethod
    def get_img_md5(img_path: path):
        """返回文件的md5值
        * `img_path`: 图片路径"""
        with open(img_path, mode='rb') as file:
            readable_hash = hashlib.md5(file.read()).hexdigest()
        return readable_hash

    @staticmethod
    def read_二进制数据(file_path: path) -> typing.Set[str]:
        """读取二进制数据
        * `file_path`: 二进制文件路径"""
        if file_path.is_dir():
            raise ValueError(f"{str(file_path)} 不是一个文件!")
        try:
            with open(file_path, mode='rb') as file:
                return pickle.load(file)
        except EOFError:
            file_path.unlink()
            print(f"{str(file_path)} 数据错误,重新制作")
            install_工具类.make_SAVE_TUGE(file_path.parent)
            return install_工具类.read_二进制数据(file_path)

    @staticmethod
    def write_二进制数据(file_path: path, data: set) -> None:
        """将二进制数据保存到指定文件
        * `file_path`: 文件保存路径
        * `data`: 保存数据
        """
        if file_path.is_dir():
            raise ValueError(f"{str(file_path)} 不是一个文件!")
        with open(file_path, mode='wb') as file:
            pickle.dump(data, file)

    @staticmethod
    def is_save_TUGE_init(dir_path: path) -> bool:
        """判断文件夹里 `SAVE_TUGE` 缓存文件是否在里面
        * `dir_path`: 判断目录
        """
        for i in dir_path.glob('*.TUGE'):
            if i.name == SAVE_TUGE:
                return True
        return False

    @staticmethod
    def get_dir_md5_set(dir_path: path) -> typing.Set[str]:
        """返回指定文件夹里 `FILE_END` 的 md5 值
        会顺带删除不符合和多余的
        配合全局变量一起"""
        img_set = set()

        for i in dir_path.glob(f"*.{FILE_END}"):
            file_md5 = install_工具类.get_img_md5(i)
            if file_md5 in img_set or file_md5 in MD5_SET.ALL_MD5_SET:  # 用于判断是否在这个文件夹里或全局变量里
                print(f"Remove img {str(i)}")
                i.unlink()
            elif i.stat().st_size < 1000:
                print(f"Remove img {str(i)}")
                i.unlink()
            else:
                img_set.add(file_md5)
        MD5_SET.ALL_MD5_SET |= img_set  # 配合全局变量一起
        return img_set

    @staticmethod
    def make_SAVE_TUGE(dir_path: path) -> typing.Set[str]:
        """制作指定 `dir_path` 的 `SAVE_TUGE` 并返回 md5集合
        会顺带删除不符合和多余的"""
        data = install_工具类.get_dir_md5_set(dir_path)
        install_工具类.write_二进制数据(dir_path / SAVE_TUGE, data)
        print(f"创建成功: {str(dir_path / SAVE_TUGE)}")
        return data


class Json_Task(Img_Task):
    """用于下载 `json` 格式的图片"""
    _TIME_OUT = 5

    def __init__(self, dir_name: path, ):
        """* `dir_name` 下载路径

        下载路径里请放入 `readme`
        选择器一行一条"""
        self._json_url: str
        self._select: list
        self._readme_path: path
        self._select = []
        self._dir_path: path = dir_name
        self._find_readme_txt()
        self._install_set: typing.Set[str]
        self._get_img_md5_set()

    def _get_img_md5_set(self) -> None:
        """尝试读取 `SAVE_TUGE`
        失败则创建 `SAVE_TUGE`
        """
        if install_工具类.is_save_TUGE_init(self._dir_path):
            self._install_set = install_工具类.read_二进制数据(self._dir_path / SAVE_TUGE)  # 读取
            MD5_SET.ALL_MD5_SET = MD5_SET.ALL_MD5_SET | self._install_set
            print(f"{self._json_url}读取成功!")
        else:
            self._install_set = install_工具类.make_SAVE_TUGE(self._dir_path)  # 创建
            print(f"已创建日志文件: {SAVE_TUGE}")

    def get_dir_path(self) -> path:
        return self._dir_path

    def _find_readme_txt(self):
        """寻找任务文件 readme.txt"""
        for i in self._dir_path.glob("*.txt"):
            if i.is_file() and i.stem == "readme":
                self._readme_path = i
                self.__set_self()

    def __set_self(self):
        """设置任务的 url 和 select 选择器"""
        with open(self._readme_path, mode='r', encoding='utf-8') as file:
            self._json_url = file.readline().removesuffix("\n")
            file_r = file.readlines()
            for line in file_r:
                if line.removesuffix("\n") != '':
                    if line.removesuffix("\n").isdigit() and int(line) < 10:
                        self._select.append(int(line))
                    else:
                        self._select.append(line.removesuffix("\n"))

    def __str__(self) -> str:
        return f'mode: Json_url - url: {self._json_url}\t{str(self._dir_path)}'

    @staticmethod
    def is_json_task(dir_path: path) -> bool:
        """用于判断指定文件是否是`Json_Task`任务"""
        for i in dir_path.glob("*txt"):
            if i.stem == 'readme':
                with open(i, mode='r', encoding='utf-8') as file:
                    len_file = 0
                    for line in file:
                        if line != '\n':
                            len_file += 1
                    if len_file > 1:
                        return True
        return False

    def install_img(self):
        if self._json_url != LOCALHOST:
            """下载图片"""
            img = install_工具类.install_json(url=self._json_url, Download_path=self._dir_path, select=self._select)
            if img is None:  # 判断是否合法
                pass
            else:
                if img.md5 is not None:
                    self._install_set.add(img.md5)  # 添加到自己的缓存目录
                    MD5_SET.ALL_MD5_SET.add(img.md5)  # 更新全局的 md5
        else:
            MD5_SET.remove_taste(self)

    def save(self):
        """最后保存缓存文件 `SAVE_TUGE` 到下载目录"""
        save_path = self._dir_path / SAVE_TUGE
        print(f"任务{self._json_url}结束,保存到{save_path}")
        install_工具类.write_二进制数据(save_path, self._install_set)


class Ajax_Task(Img_Task):
    _TIME_OUT = 5

    def save(self):
        """最后保存缓存文件 `SAVE_TUGE` 到下载目录"""
        save_path = self._dir_path / SAVE_TUGE
        print(f"任务{self._url}结束,保存到{save_path}", end='')
        install_工具类.write_二进制数据(save_path, self._install_set)

    def __init__(self, dir_name: path):
        """* `dir_name` 下载路径

        下载路径里请放入 `readme` """
        self._url: str
        self._readme_path: path
        self._dir_path: path = dir_name
        self._find_readme_txt()
        self._install_set: typing.Set[str]
        self._get_img_md5_set()

    def get_dir_path(self) -> path:
        return self._dir_path

    def _get_img_md5_set(self) -> None:
        """尝试读取 `SAVE_TUGE`
        失败则创建 `SAVE_TUGE`
        """
        if install_工具类.is_save_TUGE_init(self._dir_path):
            self._install_set = install_工具类.read_二进制数据(self._dir_path / SAVE_TUGE)  # 读取
            MD5_SET.ALL_MD5_SET = MD5_SET.ALL_MD5_SET | self._install_set
            print(f"{self._url}读取成功!")
        else:
            self._install_set = install_工具类.make_SAVE_TUGE(self._dir_path)  # 创建
            print(f"已创建日志文件: {SAVE_TUGE}")

    def _find_readme_txt(self):
        """寻找任务文件 readme 并设置相应信息"""
        for i in self._dir_path.glob("*.txt"):
            if i.is_file() and i.stem == "readme":
                self._readme_path = i
                self.__set_self()

    def __set_self(self):
        """读取下载配置并设置 `url`"""
        with open(self._readme_path, mode='r', encoding='utf-8') as file:
            self._url = file.readline().removesuffix("\n")

    def __str__(self) -> str:
        return f'mode: Ajax_url - url: {self._url}\t{str(self._dir_path)}'

    @staticmethod
    def is_ajax_task(dir_path: path) -> bool:
        """用于判断是否是 `Ajax_Task` 任务"""
        for i in dir_path.glob("*txt"):
            if i.stem == 'readme':
                with open(i, mode='r', encoding='utf-8') as file:
                    len_file = 0
                    for line in file.readlines():
                        if line != '\n' and line != 'localhost\n':
                            len_file += 1
                    if len_file == 1:
                        return True
        return False

    def install_img(self):
        if self._url != LOCALHOST:
            """下载图片"""
            img = install_工具类.install_img(url=self._url, Download_path=self._dir_path)
            if img is None:
                pass
            else:
                if img.md5 is not None:
                    self._install_set.add(img.md5)  # 添加到自己的缓存目录
                    MD5_SET.ALL_MD5_SET.add(img.md5)  # 更新全局的 md5
        else:
            MD5_SET.remove_taste(self)


def CS_install_json(url: str) -> typing.Union[dict, list]:
    """这是一个测试获取 `json` 数据000"""
    json_data = requests.get(url=url, headers=HEADERS).json()
    print(json_data)
    return json_data


def CS_get_img_url(data: typing.Union[dict, list], select_: typing.List[str]) -> None:
    """Json 选择器的尝试"""
    for i in select_:
        data = data[i]
    img_url = data
    print(img_url)
    for i in select_:
        print(i)


def 任务收集(dir_path: path) -> None:
    """深度搜寻所有合法任务
    并将合法缓存加载到全局中
    * `dir_path`: 任务目录"""
    for i in dir_path.glob('*'):
        if i.is_dir():
            if Ajax_Task.is_ajax_task(i):
                MD5_SET.add_taste(Ajax_Task(i))  # 加载 Ajax_Task 任务
            elif Json_Task.is_json_task(i):
                MD5_SET.add_taste(Json_Task(i))  # 加载 Json_Task 任务
            elif install_工具类.is_save_TUGE_init(i):
                MD5_SET.ALL_MD5_SET |= install_工具类.read_二进制数据(i / SAVE_TUGE)  # 自动添加之前下载过的任务
                print(f"{str(i)}\t缓存读取成功!")
            else:
                任务收集(i)


def main(dir_path: str, mode: str = None) -> None:
    """自动下载测试的开始函数
    * `dir_path`: 操作目录
    * 'time_sleep`: 等待时间
    * `mode`: install -> 开始下载,'try`-> 尝试下载,'' -> None"""
    任务收集(path(dir_path))
    for i in MD5_SET.Task():  # 输出任务信息
        print(i)
    if mode == 'install':  # 开始下载
        while True:
            if MD5_SET.task_个数 == 0:
                break
            for i in MD5_SET.Task():
                i.install_img()
    else:
        print("*" * 100)


def 全局任务保存() -> None:
    """退出并保存缓存信息"""
    for i in MD5_SET.Task():
        i.save()

    print(f"一共{len(MD5_SET.ALL_MD5_SET)}")


def init(dir_path: str) -> None:
    """初始化 `dir_path` 的全部合法任务
    也就是说有 readme.txt 的合法任务
    * `dir_path`: 任务集目录"""
    dir_path = path(dir_path)
    sum_Data = 0
    for i in dir_path.glob("*"):
        if i.is_dir():
            if Ajax_Task.is_ajax_task(i) or Json_Task.is_json_task(i):
                sum_Data += len(install_工具类.make_SAVE_TUGE(i))
            else:
                init(str(i))


def __重复文件测试(dir_path: str) -> None:
    """任务集 `dir_path` 下载重复测试"""
    dir_path = path(dir_path)
    data = {}
    for i in dir_path.glob("*"):
        for j in i.glob(f"*{FILE_END}"):
            print(j)
            md5 = install_工具类.get_img_md5(j)
            if md5 in data:
                print(str(j), data[md5])
            else:
                data[md5] = str(j)


def 去除重复内容(dir_path: str) -> None:
    """重新制作所有满足合法任务对象 `readme.txt` 或有缓存文件 `SAVE_TUGE` 的任务目录
    深度搜索"""
    dir_path = path(dir_path)
    for i in dir_path.glob("*"):
        if i.is_dir():
            if install_工具类.is_save_TUGE_init(i):
                install_工具类.make_SAVE_TUGE(i)
            elif Ajax_Task.is_ajax_task(i) or Json_Task.is_json_task(i):
                install_工具类.make_SAVE_TUGE(i)
            else:
                去除重复内容(str(i))


if __name__ == "__main__":
    任务收集(path(r'T:\PY3.12\IMG'))
    for i in MD5_SET.Task():
        print(i)
    # main(r"T:\img", mode="install")

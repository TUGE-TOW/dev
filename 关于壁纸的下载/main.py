import ajax_install as aj
import sys
import typing
from pathlib import Path as path

__help__ = """
此程序会读取输入路径下(不包括当前路径)的所有合法任务
合法任务: 有 readme.txt or save.TUGE 的文件夹

readme.txt -> 输入您想要下载的图片的 url,如果是 json 格式的,在其后添加选择器,一行一个

示例:
--------------------------------------------------------------------------------------------
随机图片 url 示例 -> readme.txt
           https://install_for_img
--------------------------------------------------------------------------------------------
Json 格式示例   ->  readme.txt
           https://install_for_json  #假设返回{"img":["img_name","https://install_for_img"]}
           
           img
           2
           ... ...
--------------------------------------------------------------------------------------------
如果您像加入本地信息,可以使用如下格式
本地格式       ->  readme.txt:
            localhost
            ... ...
--------------------------------------------------------------------------------------------

install [path] -> 开始 path 下的所有下载目录
init [path] -> 重置 path 下的所有合法任务,会读取缓存
print [path] -> 显示当前 path 下的所有合法任务信息
set_localhost -> 将 path 下的所有任务信息改为 localhost 不在下载
un_localhost -> 将 path 下的所有任务信息改为需要下载
reset_localhost -> 将 path 下的所有任务信息单个更改
--------------------------------------------------------------------------------------------

"""


def set_one_localhost(dir_path: path) -> None:
    """设置为本地 `localhost` ,不要下载"""
    with open(dir_path / "readme.txt", 'r', encoding='utf-8') as file:
        data = [i for i in file.readlines() if i != '\n']
        if len(data) == 0:
            file.write("localhost\n")
            print(f"{str(dir_path)}\t修改为 localhost")
            return
        elif "http" in data[0]:
            with open(dir_path / "readme.txt", 'w', encoding='utf-8') as w_file:
                w_file.write('localhost\n')
                for line in data:
                    w_file.write(line)
            print(f"{str(dir_path)}\t修改为 localhost")
        elif data[0].removesuffix("\n") == 'localhost':
            print(f"{str(dir_path)}\t原本为 localhost 所以未修改")
        else:
            print(f"{str(dir_path)}\t未知格式")


def un_one_localhost(dir_path: path) -> None:
    """设置为下载 `install` ,要下载"""
    with open(dir_path / "readme.txt", 'r', encoding='utf-8') as file:
        data = [i for i in file.readlines() if i != '\n']
        if len(data) == 0:
            print(f"{str(dir_path)}\t原本为 install_task 所以未修改")
            pass
        if "localhost" == data[0].removesuffix("\n"):
            data.pop(0)
            with open(dir_path / "readme.txt", 'w', encoding='utf-8') as w_file:
                for line in data:
                    w_file.write(line)
            print(f"{str(dir_path)}\t修改为 install_task")
        elif "http" in data[0]:
            print(f"{str(dir_path)}\t原本为 install_task 所以未修改")
        else:
            print(f"{str(dir_path)}\t未知格式")


def set_localhost(dir_path: str) -> None:
    """设置所有为 `localhost`"""
    dir_path = path(dir_path)

    for one_dir in dir_path.glob("*"):
        if one_dir.is_dir():
            if aj.Ajax_Task.is_ajax_task(one_dir) or aj.Json_Task.is_json_task(one_dir):
                set_one_localhost(one_dir)
            else:
                set_localhost(str(one_dir))


def un_localhost(dir_path: str) -> None:
    """设置所有为 `install`"""
    dir_path = path(dir_path)

    for one_dir in dir_path.glob("*"):
        if one_dir.is_dir():
            if aj.Ajax_Task.is_ajax_task(one_dir) or aj.Json_Task.is_json_task(one_dir):
                un_one_localhost(one_dir)
            else:
                un_localhost(str(one_dir))


def reset_localhost(dir_path: path):
    """为每个指定设置"""
    aj.任务收集(dir_path)
    print("-" * 100)
    for one_task in aj.MD5_SET.Task():
        print(one_task)
        user_input = input(f"Install?(Y,n) >>>\t")
        if user_input == "y" or user_input == "Y":
            un_one_localhost(one_task.get_dir_path())
        else:
            set_one_localhost(one_task.get_dir_path())
    print("-" * 100)


def main_user_input(user_input: typing.List[str]) -> None:
    """命令行界面"""
    data = iter(user_input)
    next(data)
    任务 = next(data, None)
    dir_path = next(data, None)
    if dir_path is None:
        dir_path = path.cwd()
    if 任务 is not None:
        print(f"Install task for {str(dir_path)}")
        if 任务 == 'install':
            aj.main(dir_path, mode='install')
            print(f"一共\t{len(aj.MD5_SET.ALL_MD5_SET)}\t张图片")
        elif 任务 == 'init':
            aj.去除重复内容(dir_path)
            print(f"一共\t{len(aj.MD5_SET.ALL_MD5_SET)}\t张图片")
        elif 任务 == 'print':
            aj.main(dir_path)
            print(f"一共\t{len(aj.MD5_SET.ALL_MD5_SET)}\t张图片")
        elif 任务 == 'set_localhost':
            set_localhost(dir_path)
        elif 任务 == 'un_localhost':
            un_localhost(dir_path)
        elif 任务 == 'reset_localhost':
            reset_localhost(path(dir_path))
            print(f"一共\t{len(aj.MD5_SET.ALL_MD5_SET)}\t张图片")
        else:
            print(__help__)
    else:
        print(__help__)


if __name__ == "__main__":
    try:
        if len(sys.argv) == 1:
            print(f"Install task for {path(__file__).parent.absolute()}")
            aj.main(str(path.cwd()), mode='install')
            print(f"一共\t{len(aj.MD5_SET.ALL_MD5_SET)}\t张图片")
        else:
            main_user_input(sys.argv)
        input("键入任何内容退出>>>")
    except KeyboardInterrupt:
        print("退出中!正在保存缓存信息,请稍后 ... ...")
        aj.全局任务保存()
        print(f"一共\t{len(aj.MD5_SET.ALL_MD5_SET)}\t张图片")
        input("键入任何内容退出>>>")

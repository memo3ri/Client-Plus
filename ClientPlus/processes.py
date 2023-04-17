import os
import sys
import subprocess


def clientplus_process():
    # 当进程出现大于等于两个时禁止Client+运行

    # 使用tasklist命令获取进程列表
    tasklist = subprocess.check_output(['tasklist']).decode('gbk')
    # 将进程列表按行分割
    lines = tasklist.split('\n')
    # 遍历每一行，获取pid和进程名
    process_list = []
    client_name = sys.argv[0].split("\\")[-1]
    for line in lines:
        if line:
            try:
                pid = line.split(None, 1)
                if len(pid) != 0:
                    if client_name == pid[0]:
                        process_list.append(pid[0])
            except ValueError:
                continue

    # 当进程 >= 3时 Client+则运行有两个实例
    if len(process_list) >= 3:
        return False
    else:
        # 当未运行Client+时则返回True
        return True


def clientdx_process(process_name):
    # 判断指定进程是否在运行
    # 读取系统进程列表
    process_list = os.popen('tasklist').readlines()

    # 遍历进程列表，查找进程名对应的进程
    for process in process_list:
        if process_name in process:
            return True

    # 如果没有找到进程，则返回 False
    return False


if __name__ == "__main__":
    print(clientdx_process("clientdx.exe"))

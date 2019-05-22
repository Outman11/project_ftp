"""
    ftp文件传输服务端
"""

from socket import *
from threading import Thread
import os, sys
from time import sleep

#  全局变量
HOST = "0.0.0.0"
POST = 9529
ADDR = (HOST, POST)
FTP = "/home/tarena/学习知识点/month02/Concurr/project_ftp/FTP/"  # 文件库路径
s = socket(AF_INET, SOCK_STREAM)


#  将客户端请求功能封装为类
class FtpServer(object):
    def __init__(self, connfd, FTP_PATH):
        self.connfd = connfd
        self.FTP_PATH = FTP_PATH

    def do_list(self):
        # 获取文件列表
        files = os.listdir(self.FTP_PATH)
        if not files:
            self.connfd.send("该文件类别为空!")
            return
        else:
            self.connfd.send(b"OK")
            sleep(0.1)
        fs = ""  # 新建一个空字符串,将列表内容全部写到一个字符串里,这样就不会出现粘包情况
        for file in files:
            if file[0] != "." and os.path.isfile(self.FTP_PATH + file):  # "."是判断隐藏文件
                fs += file + "\n"
        self.connfd.send(fs.encode())

    def do_get(self, filename):
        try:
            fd = open(self.FTP_PATH + filename, "rb")
        except Exception:
            self.connfd.send("文件不存在".encode())
            return
        else:
            self.connfd.send(b"OK")
            sleep(0.1)
        # 发送文件
        while True:
            data = fd.read(1024)
            if not data:  # 文件结束
                sleep(0.1)
                self.connfd.send(b"##")
                break
            self.connfd.send(data)

    def do_put(self, filename):
        if os.path.exists(self.FTP_PATH + filename):
            self.connfd.send("该文件已存在".encode())
            return
        self.connfd.send(b"OK")
        fd = open(self.FTP_PATH + filename, "wb")
        # 接收文件
        while True:
            data = self.connfd.recv(1024)
            if data == "##":
                break
            fd.write(data)
        fd.close()


#  网络搭建
def main():
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s.bind(ADDR)
    s.listen(5)
    print("Listen the post 9529...")
    while True:
        try:
            connfd, addr = s.accept()
        except KeyboardInterrupt:
            sys.exit("退出服务器")
        except Exception as e:
            print(e)
            continue
        print("连接的客户端:", connfd.getpeername())
        # 创建线程处理请求
        t = Thread(target=handle, args=(connfd,))
        t.setDaemon(True)
        t.start()


#  处理客户端请求
def handle(connfd):
    #  选择文件夹
    cls = connfd.recv(1024).decode()
    FTP_PATH = FTP + cls + "/"
    ftp = FtpServer(connfd, FTP_PATH)  # 创建对象
    while True:
        # 接收客户端请求
        data = connfd.recv(1024).decode()
        # 如果客户端断开返回data为空
        if not data or data[0] == "Q":
            return
        elif data[0] == "L":
            ftp.do_list()
        elif data[0] == "G":
            filename = data.split(" ")[-1]
            ftp.do_get(filename)
        elif data[0] == "P":
            filename = data.split(" ")[-1]
            ftp.do_put(filename)


if __name__ == "__main__":
    main()

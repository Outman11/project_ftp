"""
    ftp文件传输客户端
"""

from socket import *
import sys
from time import sleep


#  具体功能
class FtpClient(object):
    def __init__(self, sockfd):
        self.sockfd = sockfd

    def do_list(self):
        self.sockfd.send(b"L")  # 发送请求
        # 等待回复
        data = self.sockfd.recv(4096).decode()
        # OK表示请求成功
        if data == "OK":
            # 接收文件列表
            data = self.sockfd.recv(4096)
            print(data.decode())
        else:
            print(data)

    def do_quit(self):
        self.sockfd.send(b"Q")
        self.sockfd.close()
        sys.exit("感谢使用!")

    def do_get(self, filename):
        # 发送请求
        self.sockfd.send(("G " + filename).encode())
        # 等待回复
        data = self.sockfd.recv(128).decode()
        if data == "OK":
            fd = open(filename, "wb")
            # 接收内容写入文件
            while True:
                data = self.sockfd.recv(1024)
                if data == b"##":
                    break
                fd.write(data)
            fd.close()
        else:
            print(data)

    def do_put(self, filename):
        try:
            f = open(filename, "rb")
        except Exception:
            print("没有该文件")
            return
            # 发送请求
        filename = filename.split("/")[-1]
        self.sockfd.send(("P " + filename).encode())
        # 等待回复
        data = self.sockfd.recv(128).decode()
        if data == "OK":
            while True:
                data = f.read(1024)
                if not data:
                    sleep(0.1)
                    self.sockfd.send(b"##")
                    break
                self.sockfd.send(data)
            f.close()
        else:
            print(data)


#  发起请求
def do_request(sockfd):
    ftp = FtpClient(sockfd)

    while True:
        print("\n**********命令选项**********")
        print("\n*==========list===========*")
        print("\n*=========get file========*")
        print("\n*=========put file========*")
        print("\n*===========quit==========*")
        print("\n***************************")

        cmd = input("输入命令:")
        if cmd.strip() == "list":
            ftp.do_list()
        elif cmd[:3] == "get":
            filename = cmd.strip().split(" ")[-1]
            ftp.do_get(filename)
        elif cmd[:3] == "put":
            filename = cmd.strip().split(" ")[-1]
            ftp.do_put(filename)
        elif cmd.strip() == "quit":
            ftp.do_quit()


#  网络连接
def main():
    sockfd = socket(AF_INET, SOCK_STREAM)
    try:
        sockfd.connect(("172.40.71.158", 9529))
    except Exception as e:
        print(e)
        sys.exit("连接服务器失败")
    else:
        print("""
        ***************************
          Data    File    Image
        ***************************
        """)
        cls = input("请输入文件种类:")
        if cls not in ["Data", "File", "Image"]:
            print("Sorry input Error!")
            return
        else:
            sockfd.send(cls.encode())
            do_request(sockfd)


if __name__ == "__main__":
    main()

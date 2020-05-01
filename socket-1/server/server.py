import socket
import argparse
import os
import json
import socketserver
import time
import threading
import queue

FLAG = "success"
BUFFER_SIZE = 4096
SERVER_IP = "0.0.0.0"
SERVER_SEND_PORT = "5002"
SERVER_RECV_PORT = "5001"

client_sockets = dict()
prog_info = dict()
#lock = threading.Lock()

config = json.load(open("config.json","r"))
SERVER_IP = config["serverIp"]
SERVER_SEND_PORT = config["serverSendPort"]     #发送文件到服务器的端口
SERVER_RECV_PORT = config["serverRecvPort"]     #从该端口接收来自服务器的数据
SERVER_DIR = config["serverDir"]
SERVER_TMP_DIR = config["serverTmpDir"]

def startServers(progInfo):
    global prog_info
    prog_info = progInfo

    global SERVER_DIR
    global SERVER_TMP_DIR
    SERVER_DIR = os.path.join(SERVER_DIR, prog_info["progname"])
    SERVER_TMP_DIR = os.path.join(SERVER_TMP_DIR, prog_info["progname"])
    
    if not os.path.exists(SERVER_DIR):
        os.makedirs(SERVER_DIR)
    if not os.path.exists(SERVER_TMP_DIR):
        os.makedirs(SERVER_TMP_DIR)

    send_server_thread = threading.Thread(target=startSendServer)
    recv_server_thread = threading.Thread(target=startRecvServer)
    sync_files_thread = threading.Thread(target=sync_files, args=(progInfo,))
    send_server_thread.start()
    recv_server_thread.start()
    sync_files_thread.start()

def startSendServer():
    send_server = socketserver.ThreadingTCPServer((SERVER_IP, int(SERVER_SEND_PORT)), sendServer)
    send_server.serve_forever()

def startRecvServer():
    recv_server = socketserver.ThreadingTCPServer((SERVER_IP, int(SERVER_RECV_PORT)), recvServer)
    recv_server.serve_forever()

def sync_files(progInfo):
    #检测文件变化
    curr_id = -1
    def sendFile(filename):
        #lock.acquire()
        for client_socket, q in client_sockets.items():
            if client_socket.client_address == filename.split("1")[-1]:
                continue
            q.put(filename)
        #lock.release()

    while True:
        #是否存在新测试用例
        files = os.listdir(SERVER_DIR)
        max_id = curr_id
        for filename in files:
            if filename.startswith("id:"):
                fileId = int(filename.split(":")[1])
                if curr_id < fileId:
                    sendFile(os.join(SERVER_DIR, filename))
                    max_id = max(fileId,max_id)
        curr_id = max_id
        time.sleep(1)

class sendServer(socketserver.BaseRequestHandler):
    def handle(self):
        q = queue.Queue()
        global client_sockets
        global prog_info
        #lock.acquire()
        client_sockets[self.request] = q
        #lock.release()
        command = json.dumps(prog_info)

        #确定程序名
        self.send_command(command, seed = True)

        #发送种子测试用例
        self.send_seed_files(prog_info["seeddir"])

        #开始执行
        self.send_command(command)
        
        while True:
            filename = q.get()
            self.send_file(filename)
            q.task_done()
            #data = self.request.recv(1024).decode() #阻塞socket
    
    def send_command(self, command, seed = False):
        if seed:
            self.request.send("SC".encode())
        else:
            self.request.send("C".encode())
        if self.request.recv(BUFFER_SIZE).decode()==FLAG: #开始接受命令
            self.request.send(command.encode())

    def send_file(self, filename, seed = False):
        if seed:
            self.request.send("SF".encode())
        else:
            self.request.send("F".encode())
        if self.request.recv(BUFFER_SIZE).decode()==FLAG: #开始接受命令
            self.request.send(os.path.basename(filename).encode())
            print("send {}".format(filename, ))
            if self.request.recv(BUFFER_SIZE).decode() == FLAG:   #开始传输文件内容
                with open(filename, "rb") as f:
                    while True:
                        bytes_read = f.read(BUFFER_SIZE)
                        if not bytes_read:
                            break
                        self.request.sendall(bytes_read)
    
    def send_seed_files(self, filedir):
        files = os.listdir(filedir)
        for filename in files:
            filename = os.path.join(filedir, filename)
            if os.path.isfile(filename):
                print("seed : " + filename)
                self.send_file(filename, seed=True)

class recvServer(socketserver.BaseRequestHandler):
    def handle(self):
        global prog_info
        while True :
            tran_type = self.request.recv(BUFFER_SIZE).decode()
            if tran_type == "C":
                self.request.send(FLAG.encode())
                command = self.request.recv(BUFFER_SIZE).decode()
                print(command)
            elif tran_type == "F":
                self.request.send(FLAG.encode())
                fileinfo_size = struct.calcsize('128sl')
                # 接收文件名与文件大小信息
                buf = self.request.recv(fileinfo_size)
                # 判断是否接收到文件头信息
                if buf:
                    # 获取文件名和文件大小
                    filename, filesize = struct.unpack('128sl', buf)
                    fn = filename.strip(b'\00')
                    fn = fn.decode()
                    print ('file new name is {0}, filesize if {1}'.format(str(fn),filesize))
        
                    recvd_size = 0  # 定义已接收文件的大小
                    # 存储在该脚本所在目录下面
                    fp = open('./' + str(fn), 'wb')
                    print ('start receiving...')
                    
                    # 将分批次传输的二进制流依次写入到文件
                    while not recvd_size == filesize:
                        if filesize - recvd_size > 1024:
                            data = s.recv(1024)
                            recvd_size += len(data)
                        else:
                            data = s.recv(filesize - recvd_size)
                            recvd_size = filesize
                        fp.write(data)
                    fp.close()
                    print ('end receive...')


if __name__ == "__main__":
    prog_info["seeddir"] = "/home/wen/seed"
    prog_info["outdir"] = "fuzz_test2"
    prog_info["progname"] = "nasm"
    prog_info["progInput"] = "-elf64"
    prog_info["timelimit"] = ""
    prog_info["memorylimit"] = "none"
    startServers(prog_info)
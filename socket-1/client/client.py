import socket
import argparse
import os
import json
import threading
import time

FLAG = "success"
BUFFER_SIZE = 4096 # send 4096 bytes each time step

prog_info = {"progname":"default"}
config = json.load(open("config.json","r"))
SERVER_IP = config["serverIp"]
CLIENT_SEND_PORT = config["clientSendPort"]     #发送文件到服务器的端口
CLIENT_RECV_PORT = config["clientRecvPort"]     #从该端口接收来自服务器的数据
ROOT_DIR = config["rootDir"]

def receiveFromServer(server_ip, server_port): 
    recv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("[+] Connecting to {}:{}".format(server_ip,server_port,))
    recv_socket.connect((server_ip, server_port))
    print("[+] Connected.")

    init_seed_dir = os.path.join(ROOT_DIR, prog_info["progname"], "input")
    server_dir = os.path.join(ROOT_DIR, prog_info["progname"], "output", "server", "queue")

    def writeToDir(filedir):
        recv_socket.send(FLAG.encode())
        filename = recv_socket.recv(BUFFER_SIZE).decode()
        print(filename)
        filename = os.path.join(filedir,filename)
        recv_socket.send(FLAG.encode())
        with open(filename, "wb") as f:
            while True:
                bytes_read = recv_socket.recv(BUFFER_SIZE)
                if not bytes_read:    
                    print("Finished")
                    break
                f.write(bytes_read)
    
    while True :
        tran_type = recv_socket.recv(BUFFER_SIZE).decode()
        if tran_type == "SC":
            recv_socket.send(FLAG.encode())
            command = recv_socket.recv(BUFFER_SIZE).decode()
            #获得程序信息
            print("SC : " + command)
            init_seed_dir, server_dir = processInitCommand(command)
        elif tran_type == "C":
            recv_socket.send(FLAG.encode())
            command = recv_socket.recv(BUFFER_SIZE).decode()
            #执行模糊测试
            print("C : " + command)
        elif tran_type == "F":
            print("receive F")
            writeToDir(server_dir)      #server文件夹
        elif tran_type == "SF":
            print("receive SF")
            writeToDir(init_seed_dir)    #初始种子文件夹
    recv_socket.close()

def processInitCommand(command):
    global prog_info
    prog_info = json.loads(command)
    prog_name = prog_info["progname"]
    
    prog_dir = os.path.join(ROOT_DIR, prog_name)
    init_seed_dir = os.path.join(prog_dir, "input")
    out_dir = os.path.join(prog_dir, "output")
    server_dir = os.path.join(prog_dir, "output", "server")
    target_dir = os.path.join(prog_dir, "target")
    
    if not os.path.exists(init_seed_dir):
        os.makedirs(init_seed_dir)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    if not os.path.exists(server_dir):
        os.makedirs(server_dir)
        os.makedirs(os.path.join(server_dir,"queue"))
        os.makedirs(os.path.join(server_dir,"crashes"))
        os.makedirs(os.path.join(server_dir,"hangs"))

    server_dir = os.path.join(server_dir,"queue")
    send_thread = threading.Thread(target=syncFileWithServer, args=(SERVER_IP, int(CLIENT_SEND_PORT),))
    send_thread.start()

    return init_seed_dir, server_dir

def syncFileWithServer(server_ip, server_port):
    # while prog_name == "":
    #     time.sleep(5)
    send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("[+] Connecting to {}:{}".format(server_ip,server_port,))
    send_socket.connect((server_ip, server_port))
    print("[+] Connected.")
    
    #检测文件变化
    global prog_info
    prefix = os.path.join(ROOT_DIR, prog_info["progname"], "output")
    fuzzdir = ["queue", "hangs", "crashes"]
    outdir = os.listdir(prefix)
    fuzzers = {}
    #os.chdir(prefix)
    for fuzzerName in outdir:
        if fuzzerName != "server" and os.path.isdir(prefix + fuzzerName):
            fuzzers[os.path.join(prefix, fuzzerName, fuzzdir[0])] = -1
            fuzzers[os.path.join(prefix, fuzzerName, fuzzdir[1])] = -1
            fuzzers[os.path.join(prefix, fuzzerName, fuzzdir[2])] = -1

    while True:
        for fuzzerName, curr_id in fuzzers:
            files = os.listdir(fuzzerName)
            max_id = curr_id
            for fileName in files:
                if fileName.startswith("id:") and not fileName.find("server"):
                    fileId = int(fileName.split(":")[1])
                    if curr_id < fileId:
                        send_file(send_socket, os.path.join(fuzzerName, fileName))
                        max_id = max(fileId, max_id)
            fuzzers[fuzzerName] = max_id
        time.sleep(1)
    
    send_socket.close()
import struct
def send_file(send_socket, filepath):
    send_socket.send("F".encode())
    if send_socket.recv(BUFFER_SIZE).decode()==FLAG: #开始接受命令
        if os.path.isfile(filepath):
            # 定义定义文件信息。128s表示文件名为128bytes长，l表示一个int或log文件类型，在此为文件大小
            fileinfo_size = struct.calcsize('128sl')
            # 定义文件头信息，包含文件名和文件大小
            fhead = struct.pack('128sl', os.path.basename(filepath).encode('utf-8'), os.stat(filepath).st_size)
            # 发送文件名称与文件大小
            send_socket.send(fhead)

            # 将传输文件以二进制的形式分多次上传至服务器
            fp = open(filepath, 'rb')
            while 1:
                data = fp.read(1024)
                if not data:
                    print ('{0} file send over...'.format(os.path.basename(filepath)))
                    break
                send_socket.send(data)
            # 关闭当期的套接字对象
            send_socket.close()
    
def send_command(send_socket, command):
    send_socket.send("C".encode())
    if send_socket.recv(BUFFER_SIZE).decode()==FLAG: #开始接受命令
        send_socket.send(command.encode())

def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--command", help="the command to transport")
    parser.add_argument("-f", "--filename", help="the file to transport")
    parser.add_argument("-s", "--serverip", help="server ip")
    parser.add_argument("-p", "--clinetSendPort", help="send data to this server port")
    parser.add_argument("-r", "--clientRecvPort", help="recieve data from this server port")
    parser.add_argument("-d", "--daemon", action="store_true", help="daemon process used to sync files with server")
    # parser.add_argument("-F", "--folder", help="the files in folder to transport")
    return parser

if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()

    if(args.serverip != None):
        SERVER_IP = args.serverip
    if(args.clinetSendPort != None):
        CLIENT_SEND_PORT = args.serverSendPort
    if(args.clientRecvPort != None):
        CLIENT_RECV_PORT = args.serverRecvPort
    if(args.command != None or args.filename != None):
        send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("[+] Connecting to {}:{}".format(SERVER_IP,CLIENT_SEND_PORT,))
        send_socket.connect((SERVER_IP, CLIENT_SEND_PORT))

        if(args.command != None):
            send_command(send_socket, args.command)
        if(args.filename != None):
            send_file(send_socket, args.filename)
    if(args.daemon != None and args.daemon):
        recv_thread = threading.Thread(target=receiveFromServer, args=(SERVER_IP, int(CLIENT_RECV_PORT),))
        #send_thread = threading.Thread(target=syncFileWithServer, args=(SERVER_IP, int(CLIENT_SEND_PORT),))
        recv_thread.start()
        #send_thread.start()

        recv_thread.join()
        #send_thread.join()

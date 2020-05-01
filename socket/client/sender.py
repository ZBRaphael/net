import socket
import argparse
import os
import struct
FLAG = "success"
BUFFER_SIZE = 4096 # send 4096 bytes each time step
# the ip address or hostname of the server, the receiver
hosts = []
with open("config.txt","r") as config:
    for line in config.readlines():
        # print(line,end="") 
        if(line.find("END") >= 0):
            break
        if(line.find('\n') >= 0):
            hosts.append(line[:line.find('\n')])
# the port, let's use 5001
# host = "192.168.1.101"
# the port, let's use 5001
port = 5001

def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-C", "--command", help="the command to transport")
    parser.add_argument("-F", "--filename", help="the file to transport")
    # parser.add_argument("-F", "--folder", help="the files in folder to transport")
    return parser

def send_command(command):
    s.send("C".encode())
    if s.recv(BUFFER_SIZE).decode()==FLAG: #开始接受命令
        s.send(command.encode())
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

if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    for host in hosts:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"[+] Connecting to {host}:{port}")
        s.connect((host, port))
        print("[+] Connected.")
        if args.command != None:
            send_command(args.command)
        elif args.filename != None:
            if args.filename.find(host)>=0 :
                continue
            else:
                send_file(s, args.filename)
        print("finished")
        s.close()
    
    # print(args.command,args.filename,args.folder)
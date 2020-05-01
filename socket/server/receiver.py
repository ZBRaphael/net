import socket
import os
import time
import struct
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 5001
# receive 4096 bytes each time
BUFFER_SIZE = 4096
FLAG = "success"
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# bind the socket to our local address
s.bind((SERVER_HOST, SERVER_PORT))
# enabling our server to accept connections
# 5 here is the number of unaccepted connections that
# the system will allow before refusing new connections
s.listen(5)

while True:
    print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")
    # accept connection if there is any
    client_socket, address = s.accept()
    # if below code is executed, that means the sender is connected
    print(f"[+] {address} is connected.")
    # receive the file infos
    # receive using client socket, not server socket
    tran_type = client_socket.recv(BUFFER_SIZE).decode()
    if tran_type == "C":
        client_socket.send(FLAG.encode())
        command = client_socket.recv(BUFFER_SIZE).decode()
        print(command)
    elif tran_type == "F":
        client_socket.send(FLAG.encode())
        fileinfo_size = struct.calcsize('128sl')
        # 接收文件名与文件大小信息
        buf = client_socket.recv(fileinfo_size)
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
                    data = client_socket.recv(1024)
                    recvd_size += len(data)
                else:
                    data = client_socket.recv(filesize - recvd_size)
                    recvd_size = filesize
                fp.write(data)
            fp.close()
            print ('end receive...')

s.close()

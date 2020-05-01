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
                            data = self.request.recv(1024)
                            recvd_size += len(data)
                        else:
                            data = self.request.recv(filesize - recvd_size)
                            recvd_size = filesize
                        fp.write(data)
                    fp.close()
                    print ('end receive...')


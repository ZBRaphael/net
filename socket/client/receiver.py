import socket
import os
import time
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

while True :
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
        filename = client_socket.recv(BUFFER_SIZE).decode()
        print(filename)
        client_socket.send(FLAG.encode())
        # 
        # received = received.decode()
        # filename, filesize = received.split(SEPARATOR)
        # # remove absolute path if there is
        # filename = os.path.basename(filename)
        # # convert to integer
        # filesize = int(filesize)
        # start receiving the file from the socket
        # and writing to the file stream
        with open(filename, "wb") as f:
            while True:
                # read 1024 bytes from the socket (receive)
                bytes_read = client_socket.recv(BUFFER_SIZE)
                if not bytes_read:    
                    # nothing is received
                    # file transmitting is done
                    print("Finished")
                    break
                # write to the file the bytes we just received
                f.write(bytes_read)
        # time.sleep(1)
        # close the client socket
        client_socket.close()
        # close the server socket
    
s.close()
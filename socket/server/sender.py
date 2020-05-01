import socket
import argparse
import os

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
def send_file(filename):
    s.send("F".encode())
    if s.recv(BUFFER_SIZE).decode()==FLAG: #开始接受命令
        # filename = input("filename:\n")
        # get the file size
        # send the filename and filesize
        s.send(filename.encode())
        # start sending the file
        if s.recv(BUFFER_SIZE).decode() == FLAG:   #开始传输文件内容
            # progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
            with open(filename, "rb") as f:
                while True:
                    # read the bytes from the file
                    bytes_read = f.read(BUFFER_SIZE)
                    if not bytes_read:
                        # file transmitting is done
                        break
                    # we use sendall to assure transimission in 
                    # busy networks
                    s.sendall(bytes_read)
                    # update the progress bar
            # close the socket
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
                send_file(args.filename)
        print("finished")
        s.close()
    
    # print(args.command,args.filename,args.folder)
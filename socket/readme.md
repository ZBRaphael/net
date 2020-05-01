# 使用说明

这里分别有两个文件夹，分别为server和client，这分别是部署在server和client上的。

两个文件夹中有sender.py和receiver.py和 config.txt

server中config.txt中是所有客户端的ip地址
client中config.txt中是服务端的IP地址

开始服务端和客户端的receiver都打开，命令如下：

```shell
python recevier.py
```

服务端和客户端如果要发送消息都是用如下命令

```shell
python sender.py -C 要传送的命令 -F 要传输的文件名称（使用相对路径）
```

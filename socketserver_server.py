#coding=utf-8
#!/usr/bin/python
'''
Created on 2016-6-11
@author: bestlan
Function:
   简单ssh功能的服务端程序，与远程ssh客户建立socket连接，并接收命令执行后返回结果给客户端。可返回文件内容。
实现：利用SocketServer模块来实现。
遗留问题：服务端执行后没有返回结果，客户端会处于一直等待状态，不能再次接受用户输入
'''
import SocketServer
from SocketServer import BaseRequestHandler
import commands
import re
import os

pattern="\s+"
file_data=""
#新建一个handle类，继承SocketServer模块中的BaseRequestHandler类，用来定义请求处理的逻辑。
class myhandler(BaseRequestHandler): 
    def handle(self):
        while True:
            data=self.request.recv(1024).strip() #self.request是套接字对象，self.client_address是客户端的套接字地址和端口
            if not data:continue
            print "Received data from host %s,the data:%s" %(self.client_address[0],data)
            data=data.strip()
            command_list=re.split(pattern,data) #将收到的字符，用空格分隔成列表
            if len(command_list)>1:
                #将列表中的第2个元素当作文件名，组合成绝对路径
                file_path=os.path.join(os.path.abspath('.'),command_list[1]) 
            if command_list[0]=="get": #如果第一个字符串为get
                print "catch get..."
                if re.match("\w+?:\\\\",command_list[1]): #如果第2个字符串带有路径
                    if os.path.isfile(command_list[1]):   #判断是否是文件且是否存在
                        with open(command_list[1],'r') as f_handle:#打开文件
                            file_data=f_handle.read() #读取文件内容
                            self.request.sendall(file_data) #发送文件内容到客户端
                        print "The file content is:\n%s" %file_data
                    else: #文件不存在时的处理
                        print "There is no file %s." %command_list[1];
                        self.request.sendall("The file doesn't existed")
                else:#如果第2个字符串不带路径，直接打开文件，返回内容给客户端
                    if os.path.isfile(file_path):
                        with open(file_path,'r') as f_handle:
                            file_data=f_handle.read()
                            self.request.sendall(file_data)
                        print "Thr file content is:\n%s" %file_data
                    else: 
                        print "The file doesn't existed.";
                        self.request.sendall("The file doesn't existed")
            else:#如果是普通字符，执行命令，判断执行的结果
                status,result=commands.getstatusoutput(data)
                if status!=0:
                    self.request.sendall("Error input.")
                else:
                    if len(result)!=0:
                        self.request.sendall(result.strip())
                    else:
                        self.request.sendall("Done")
                print "status:%s" %status
                print "result:%s" %result
    
if __name__ == '__main__':
    # myserver=SocketServer.TCPServer(('',6000), myhandler)
    print "Waiting for connect from client...."
    #实例化一个server，将自定义的handler类作为参数传递进来。
    myserver=SocketServer.ThreadingTCPServer(('',6000), myhandler)     
    #myserver.handle_request()  #处理单个请求后退出
    myserver.serve_forever()    #循环处理多个请求，直到shutdown()
    print "exec this statment at the end."

#echo -ne "GET / HTTP/1.1\r\nHost: www.baidu.com\r\n\r\n" |python3.7 ./bhnet.py -t www.baidu.com -p 80
#只能对www.baidu.com进行测试
#!/usr/bin/python3.7
#coding:utf-8
"""
  Author:   --<>
  Purpose: 
  Created: 04/26/2019
"""

import sys
import socket
import getopt
import  threading
import subprocess

listen =False
command = False
upload = False
execute = ""
target = ""
upload_destination =""
port =0
def run_command(command):
    command = command.rstrip()
    try :
        output = subprocess.check_output(command,stderr = subprocess.STDOUT,shell = True)
    except:
        output = b"Failed to execute command. \r\n"
    return output
def client_handler(client_socket):
    global upload
    global execute
    global command
    #print("hey gays")
    if len(upload_destination):
        #print('upload_destination')
        file_buffer =""
        while True :
            data =client_socket.recv(1024)
            data = data.decode()
            if not data :
                break
            else:
                file_buffer  +=data
        try :
            file_descriptor = open(upload_destination,"wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()
            client_socket.send(b"Seccesessfully saved file to %s\r\n" %upload_destination)
        except:
            client_socket.send(b"Failed to save file to %s\r\n" %upload_destination)
    if len(execute):
        #print("abc")
        output = run_command(execute)
        client_sender.send(output.encode())
    #print("command:",command)
    if command:
        #print(command)
        while True:
            #print("here command")
            res ="<BHP:#> "
            client_socket.send(res.encode())
            cmd_buffer=""
            while "\n" not in cmd_buffer:  
                c = client_socket.recv(1024)
                #print(c)
                cmd_buffer += c.decode()
            #print(cmd_buffer)
            response =run_command(cmd_buffer)
            client_socket.send(response.encode())
def server_loop():
    global target
    global port
    if not  len(target):
        target ="0.0.0.0"
    server =  socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.bind((target,port))
    server.listen(5)
    while True:
        client_socket, addr = server.accept()
        client_thread = threading.Thread(target=client_handler, args=(client_socket,))
        #print("here")
        client_thread.start()

def client_sender(buffer):
    print("buffer:",buffer)
    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try :
        client.connect((target,port))
        print((target,port))
        if len(buffer):
            #print("len(buffer):",len(buffer))
            client.send(buffer.encode()) 
        #print(len(buffer))
        while True:
            recv_len =1
            response = ""
            while recv_len:
                #print("recv_len here")
                data = client.recv(4096)
                #print(data)
                recv_len = len(data)
                #print(recv_len)
                data = data.decode()
                #print(data)
                response+=data
                #print(response)
                if recv_len<4096:
                    break                
            #print("here response")
            print (response,end=" ")   #python3中end=“”不换行
            buffer = input("")
            buffer +="\n" 
            #print(buffer)
            client.send(buffer.encode())
    except:
        #print("except here")
        print ("[*] Exception! Exiting.")
        client.close()

def usage():
    print ("BHP Net Tool")
    print ()
    print ("Usage: bhpnet.py -t target_host -p port")
    print ("-l --listen   -listen on [Host] : [port] for - incoming connections ")
    print ("-e --execute = file_to_fun -execute the given file upon - receiving a connection")
    print ("-c --command -initialize a command shell")
    print ("-u --upload_destination - upon receiving connection upload a file and write to [destination]")
    print()
    print()
    print ("Examples :")
    print("bhpnet.py -t 192.168.0.1 -p 5555 -l -c")
    print("bhpnet.py -t 192.168.0.1 -p 5555 -l -u =c:\\target.exe")
    print("bhpnet.py -t 192.168.0.1 -p 5555 -l -e = \"cat /etc passwd\"")
    print ("echo 'ABCDEFGHI' | ./bhpent.py -t 192.168.11.12 -p 135")
    sys.exit(0)
    
def main():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target
    #s = "-l -p 9999 -c"
    #s=['-t','localhost','-p', '9999']
    if not len(sys.argv[1:]):
        usage()
    
    try :
        opts , args = getopt.getopt(sys.argv[1:], "hle:t:p:cu", ["help", "listen", "execute", "target","port", "command", "upload"])
    except getopt.GetoptError as err:
        print (str(err))
        usage()
    for o ,a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-l","--listen"):
            listen = True
        elif o in ("-e","--execute"):
            execute =a
        elif o in ("-c", "--commandshell"):
            command = True
        elif o in ("-u","--upload"):
            upload_destination = a
        elif o in ("-t","--target"):
            target =a
        elif o in ("-p","--port"):
            port = int(a)
        else:
            assert False, "Unhandled Option"
    if not listen and len(target) and port >0:
        #print("here")
        buffer = sys.stdin.read()
        #print("yes")
        client_sender(buffer)
    if listen:
        server_loop()
main()

    

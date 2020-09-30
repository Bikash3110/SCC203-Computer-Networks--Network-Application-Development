#!/usr/bin/python
# -*- coding: UTF-8 -*-
 
import sys
import socket 
import thread
import os

MAX_DATA_RECV = 999999                     

def start():
    # check the length of command running
    if (len(sys.argv)<2):
      try:
        port = int(raw_input("[*]ENTER PORT NUMBER: "))         # Enter Port
      except KeyboardInterrupt:
        print"PORT FAILURE"
        sys.exit()
    else:
        port = int(sys.argv[1]) # port from argument

    # host and port info.
    host = ''               # blank for localhost
    print "Proxy Server Running on ",host,":",port

    try:
        # create a socket,bind,listening
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host, port))
        s.listen(50)
    except socket.error as e:
          if e.errno == 1:
              e.msg = e.msg + ("ICMP messages can only be sent from root user processes")
              raise socket.error(e.msg)
          raise

    # get the connection from client
    while 1:
        conn, addr = s.accept()
        
        # create a thread to handle request
        thread.start_new_thread(proxy, (conn, addr))    
    s.close()  

def printout(type,request,address):
    if "Block" in type:
        col_num = 1
    elif "Request" in type:
        col_num = 2
    elif "Reset" in type:
        col_num = 3

    print "\033[",col_num,"o",address[0],"\t",type,"\t",request,"\033[0m"


def proxy(conn,addr):
    # get the request from browser
    req = conn.recv(MAX_DATA_RECV)
    # parse the first line
    line = req.split('\n')[0]
    # get url
    url = line.split(' ')[1]
            
    printout("Request",line,addr)

    # find the webserver and port
    http_pos = url.find("://")          # find pos of ://
    if (http_pos==-1):
        temp = url
    else:
        temp = url[(http_pos+3):]       # get the rest of url
        
    port_pos = temp.find(":")           # find the port pos (if any)

    # find end of web server
    webserver_pos = temp.find("/")
    if webserver_pos == -1:
        webserver_pos = len(temp)

    webserver = "127.0.0.7"
    port = -1
    if (port_pos==-1 or webserver_pos < port_pos):      # default port
        port = 80
        webserver = temp[:webserver_pos]
    else:       # specific port
        port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
        webserver = temp[:port_pos]

    try:
        # create a socket to connect to the web server
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
        s.connect((webserver, port))
        s.send(req)         # send request to webserver
        
        while 1:
            # receive data from web server
            data = s.recv(9999)
            
            if (len(data) > 0):
                # send to browser
                conn.send(data)
            else:
                break
        s.close()
        conn.close()
    except socket.error, (value, message):
        if s:
            s.close()
        if conn:
            conn.close()
        printout("Reset",line,addr)
        sys.exit(1)

if __name__ == '__main__':
    start()

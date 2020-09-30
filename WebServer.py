#!/usr/bin/python
# -*- coding: UTF-8 -*-

from socket import * 
import sys
import socket 

def handleRequest(tcpSocket):
	# 1. Receive request message from the client on connection socket
	# 2. Extract the path of the requested object from the message (second part of the HTTP header)
	# 3. Read the corresponding file from disk
	# 4. Store in temporary buffer
	# 5. Send the correct HTTP response error
	# 6. Send the content of the file to the socket
	# 7. Close the connection socket 
	print 'Client Connected'
        try:
           while True:
              client_req = tcpSocket.recv(1024)
              filename = client_req.split()[1]
              f = open(filename[1:])
              outputdata = f.read()
              f.close()
              
              tcpSocket.send('HTTP/1.0 200 OK\r\n\r\n')
             
              for i in range(0,len(outputdata)):
                  tcpSocket.send(outputdata[i])
              tcpSocket.close()
        except IOError:
              tcpSocket.send('404 Not Found')
              tcpSocket.close() 

def startServer(serverAddress, serverPort):
	# 1. Create server socket
	# 2. Bind the server socket to server address and server port
	# 3. Continuously listen for connections to server socket
	# 4. When a connection is accepted, call handleRequest function, passing new connection socket (see https://docs.python.org/2/library/socket.html#socket.socket.accept)
	# 5. Close server socket
        try:
         serverSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
         serverSocket.bind((serverAddress, serverPort))
         serverSocket.listen(1) 
        except socket.error as e:
          if e.errno == 1:
              e.msg = e.msg + ("ICMP messages can only be sent from root user processes")
              raise socket.error(e.msg)
          raise

        while 1:
         tcpSocket , addr = serverSocket.accept()
         handleRequest(tcpSocket)
            
        serverSocket.close()


startServer("127.0.0.1", 8000)

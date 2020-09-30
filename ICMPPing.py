#!/usr/bin/python
# -*- coding: UTF-8 -*-

from socket import *
import os
import sys
import struct
import time
import select
import binascii
import socket 
import signal 


ICMP_ECHO_REQUEST = 8 #ICMP type code for echo request messages
ICMP_ECHO_REPLY = 0 #ICMP type code for echo reply messages


def checksum(string): 
	csum = 0
	countTo = (len(string) // 2) * 2  
	count = 0

	while count < countTo:
		thisVal = ord(string[count+1]) * 256 + ord(string[count]) 
		csum = csum + thisVal 
		csum = csum & 0xffffffff  
		count = count + 2
	
	if countTo < len(string):
		csum = csum + ord(string[len(string) - 1])
		csum = csum & 0xffffffff 
	
	csum = (csum >> 16) + (csum & 0xffff)
	csum = csum + (csum >> 16)
	answer = ~csum 
	answer = answer & 0xffff 
	answer = answer >> 8 | (answer << 8 & 0xff00)
	
	if sys.platform == 'darwin':
		answer = htons(answer) & 0xffff		
	else:
		answer = htons(answer)

	return answer 
	
def receiveOnePing(icmpSocket, destinationAddress, ID, timeout):
    # 1. Wait for the socket to receive a reply    
        timeLeft = timeout
        while True:
           started = time.time() 
           ready = select.select([icmpSocket],[],[],timeLeft)
           print ready
           wait = time.time() - started   # wait_time for the socket to recieve reply 
    # 2. Once received, record time of receipt, otherwise, handle a timeout       
           if ready[0] == [ ]: #TimeOut
              return
           time_received = time.time()
    # 3. Compare the time of receipt to time of sending, producing the total network delay
           delay = time_received - started
    # 4. Unpack the packet header for useful information, including the ID       
           rec_packet, address = icmpSocket.recvfrom(4028)
           icmp_header = rec_packet[20:28]   
           type, code, checksum, p_id, seq = struct.unpack('!BBHHH',icmp_header)
    # 5. Check that the ID matches between the request and reply
           if p_id == ID:
	# 6. Return total network delay    
               return delay
 
	
def sendOnePing(icmpSocket, destinationAddress, ID):
        my_csum = 0
    # 1. Build ICMP header    
        icmpHeader = struct.pack("!BBHHH", ICMP_ECHO_REQUEST, 0, my_csum, ID, 1)
        bytesDouble = struct.calcsize("d")
        data = (192 - bytesDouble)*"a"
        data = struct.pack("d", time.time()) + data
    # 2. Checksum ICMP packet using given function
        my_csum = checksum(icmpHeader + data)
    # 3. Insert checksum into packet
        icmpHeader = struct.pack("!BBHHH", ICMP_ECHO_REQUEST, 0, socket.htons(my_csum), ID, 1)
        packet = icmpHeader + data
    # 4. Send packet using socket
        icmpSocket.sendto(packet, (destinationAddress,1))
	# 5. Record time of sending                      
        time_send = time.time() 
            
def doOnePing(destinationAddress, timeout):	
	# 1. Create ICMP socket 
        icmp = socket.getprotobyname("icmp")
        try:
          icmpSocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp) 
        except socket.error as e:
          if e.errno == 1:
              e.msg = e.msg + ("ICMP messages can only be sent from root user processes")
              raise socket.error(e.msg)
          raise
      
        ID = os.getpid() & 0xFFFF             # get Operating Sys ID
    # 2. Call sendOnePing function    
        sendOnePing(icmpSocket, destinationAddress, ID)
	# 3. Call receiveOnePing function        
        delay = receiveOnePing(icmpSocket, destinationAddress, ID, timeout)
	# 4. Close ICMP socket        
        icmpSocket.close()
	# 5. Return total network delay        
        return delay

	
def ping(host, timeout=1):	
	# 1. Look up hostname, resolving it to an IP address	
        host = socket.gethostbyname(host)
        
        for i in range(0,10):
           print('ping{}...'.format(host))
           try: 
	# 2. Call doOnePing function, approximately every second			   
              delay = doOnePing(host, timeout)
           except socket.gaierror,e:
              print("failed.(socket error: '%s')" %e[1])
              break 
	# 3. Print out the returned delay 
           if delay == None:
              print('failed.(TImeout within {} seconds)'.format(timeout))
           else:
              delay = round(delay*1000.0, 4)
              time.sleep(1)
              print('get ping in {} milliseconds'.format(delay))
        print('') 
	# 4. Continue this process until stopped

ping("lancaster.ac.uk")
ping("bbc.co.uk")
ping("www.ed.gov")



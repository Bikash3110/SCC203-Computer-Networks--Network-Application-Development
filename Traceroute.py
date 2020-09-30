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
	# 6. Return total network delay        
    # 1. Wait for the socket to receive a reply   
        timeLeft = timeout
        while True:
           started = time.time() 
           ready = select.select([icmpSocket],[],[],timeLeft)
           print ready
    # 2. Once received, record time of receipt, otherwise, handle a timeout        
           wait = time.time() - started
           if ready[0] == [ ]: #TimeOut
              return
           time_received = time.time()
    # 3. Compare the time of receipt to time of sending, producing the total network delay
           delay = time_received - started 
    # 4. Unpack the packet header for useful information, including the ID           
           rec_packet, address = icmpSocket.recvfrom(4028)
           icmp_header = rec_packet[20:28]   
           type, code, checksum, p_id, seq = struct.unpack('!BBHHH',icmp_header)
	# 5. Check type
           if type == 11:
              return (delay,address,0)
           elif type == 0:
              return (delay,address,1)     
         
	
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
	    #time_send = time.time()
            
def doOnePing(destinationAddress, timeout,ttl):
	# 1. Create ICMP socket	 
        icmp = socket.getprotobyname("icmp")
        try:
          icmpSocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
          icmpSocket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
          icmpSocket.settimeout(timeout)  
        except socket.error as e:
          if e.errno == 1:
              e.msg = e.msg + ("ICMP messages can only be sent from root user processes")
              raise socket.error(e.msg)
          raise
      
        ID = os.getpid() & 0xFFFF
	# 2. Call sendOnePing function        
        sendOnePing(icmpSocket, destinationAddress, ID)
    # 3. Call receiveOnePing function
        delay,address,info = receiveOnePing(icmpSocket, destinationAddress, ID, timeout)
	# 4. Close ICMP socket        
        icmpSocket.close()
   	# 5. Return total network delay
        return delay,address,info

	
def traceroute(host,timeout,maxHops):
        
        hostID = socket.gethostbyname(host)
        print("traceroute to %s (%s), %d hops max"%(host,hostID,maxHops))
        
        for ttl in range(1,maxHops+1):                       # hopes
           print ttl
           add = None
           for i in range(3):                                # 3 delays from same host
               try: 
                 delay,address,info = doOnePing(hostID,timeout,ttl)
               except TypeError:                             # for lost packets 
                 delay = 0
                 address = None
                 info = 0  
               add = address
               print add
               if delay == None:
                 print('failed.(TImeout within {} seconds)'.format(timeout))
               else:
                 delay = round(delay*1000.0, 4)
                 time.sleep(1)
                 print('get ping in {} milliseconds'.format(delay))
           print('')

           if info == 1:
             break
         	

traceroute("lancaster.ac.uk",1,5)
traceroute("bbc.co.uk",1,5)
traceroute("www.ed.gov",1,5)


#!/usr/bin/env python
#  Author:
#  Muhammad Shahbaz (muhammad.shahbaz@gatech.edu)

import sys
import os
import getopt
from multiprocessing import Process
from multiprocessing.connection import Listener

''' bgp server '''
class bgp_server():
    
    def __init__(self):
        listener = Listener(('localhost', 6000), authkey='sdx')
        self.conn = listener.accept()
        print 'Connection accepted from', listener.last_accepted
    
    ''' send '''
    def send(self, line):
        self.conn.send(line)
        
    ''' receive '''
    def recv(self):
        return self.conn.recv()
	
''' main '''	
if __name__ == '__main__':
    while True:
        server = bgp_server()
    
        while True:
            try:
                print server.recv()
                server.send('announce route %s next-hop %s as-path [ %s ]' % ('200.0.0.0/16','172.0.0.1','100'))
            except:
                print 'thread ended'
                break
        
    


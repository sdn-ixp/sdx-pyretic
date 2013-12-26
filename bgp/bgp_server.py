#!/usr/bin/env python
#  Author:
#  Muhammad Shahbaz (muhammad.shahbaz@gatech.edu)

from threading import Thread
from multiprocessing import Queue
from multiprocessing.connection import Listener

''' bgp server '''
class bgp_server():
    
    def __init__(self):
        listener = Listener(('localhost', 6000), authkey='sdx')
        self.conn = listener.accept()
        print 'Connection accepted from', listener.last_accepted
        
        self.sender_queue = Queue()
        sender = Thread(target=_sender, args=(self.conn,self.sender_queue))
        sender.start()
        
        self.receiver_queue = Queue()
        receiver = Thread(target=_receiver, args=(self.conn,self.receiver_queue))
        receiver.start()
    
''' sender '''
def _sender(conn,queue):
    while True:
        try:
            line = queue.get()
            conn.send(line)
        except:
            pass
        
''' receiver '''
def _receiver(conn,queue):
    while True:
        try:
            line = conn.recv()
            queue.put(line)
        except:
            pass

''' main '''	
if __name__ == '__main__':
    while True:
        server = bgp_server()
    
        while True:
            try:
                print server.receiver_queue.get()
                server.sender_queue.put('announce route %s next-hop %s as-path [ %s ]' % ('200.0.0.0/16','172.0.0.1','100'))
            except:
                print 'thread ended'
                break
        

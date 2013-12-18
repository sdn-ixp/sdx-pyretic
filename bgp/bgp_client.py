#!/usr/bin/env python
#  Author:
#  Muhammad Shahbaz (muhammad.shahbaz@gatech.edu)

import sys
import os
import getopt
from threading import Thread
from multiprocessing.connection import Client
sys.path.append(r'/home/sdx/pyretic/pyretic/sdx/bgp')

'''Write output to stdout'''
def _write(stdout,data):
    stdout.write(data + '\n')
    stdout.flush()

''' Sender function '''
def _sender(conn,stdin,log):
	# Warning: when the parent dies we are seeing continual newlines, so we only access so many before stopping
	counter = 0

	while True:
		try:
			line = stdin.readline().strip()
	
			if line == "":
				counter += 1
				if counter > 100:
					break
				continue
			counter = 0

			conn.send(line)
						
			#log.write(line + '\n')
			#log.flush()
		
		except KeyboardInterrupt:
			pass
		except IOError:
			# most likely a signal during readline
			pass
	
''' Receiver function '''
def _receiver(conn,stdout,log):
	
	while True:
		try:
			line = conn.recv()
	
			if line == "":
				continue
			
			_write(stdout, line) 
			''' example: announce route 1.2.3.4 next-hop 5.6.7.8 as-path [ 100 200 ] '''
            			
			#log.write(line + '\n')
			#log.flush()
		
		except KeyboardInterrupt:
			pass
		except IOError:
			# most likely a signal during readline
			pass

''' main '''	
if __name__ == '__main__':
	
	logfile = '/home/sdx/pyretic/pyretic/sdx/bgp/bgp-client.log'
	log = open(logfile, "w")
		
	conn = Client(('localhost', 6000), authkey='sdx')
	
	sender = Thread(target=_sender, args=(conn,sys.stdin,log))
	sender.start()
    
	receiver = Thread(target=_receiver, args=(conn,sys.stdout,log))
	receiver.start()
	
	sender.join()
	receiver.join()
	
	log.close()


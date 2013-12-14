#!/usr/bin/env python
#  Author:
#  Muhammad Shahbaz (muhammad.shahbaz@gatech.edu)

import sys
sys.path.append(r'/usr/lib/eclipse/plugins/org.python.pydev_3.0.0.201311051910/pysrc')
sys.path.append(r'~/exabgp/etc/exabgp/rs')

import pydevd
import json
from util import getArgs, write

logfile = '/home/sdx/exabgp/etc/exabgp/rs/rs.log'
log = open(logfile, "w")

# Warning: when the parent dies we are seeing continual newlines, so we only access so many before stopping
counter = 0

while True:
	try:
		line = sys.stdin.readline().strip()
	
		if line == "":
			counter += 1
			if counter > 100:
				break
			continue
		counter = 0

		log.write(line + '\n')
		log.flush()
		
		# Set debug point
		#pydevd.settrace()
		
		bgp_message = json.loads(line)
		
		ip = ''
		as_path = ''
		route = ''
		next_hop = ''
		
		for k,v in bgp_message.iteritems():
			if (k=='neighbor'):
				for k1,v1 in v.iteritems():
					if (k1=='ip'):
						ip = v1
					
					if (k1=='update'):
						if ('attribute' in v1):
							for k2,v2 in v1['attribute'].iteritems():
								if (k2=='as-path'):
									for v3 in v2:
										as_path += ' '.join([str(x) for x in v3])				
						
						if ('announce' in v1):
							for k2,v2 in v1['announce'].iteritems():
								if (k2=='ipv4 unicast'):
									for k3,v3 in v2.iteritems():
										route = k3
										next_hop = v3['next-hop']
									
										log.write('announce route %s next-hop %s as-path [ %s ]' % (route,next_hop,as_path))
										log.write('\n')
										log.flush()
									
										write('announce route %s next-hop %s as-path [ %s ]' % (route,next_hop,as_path))
						
						if ('withdraw' in v1):
							for k2,v2 in v1['withdraw'].iteritems():
								if (k2=='ipv4 unicast'):
									for k3,v3 in v2.iteritems():
										route = k3
									
										log.write('withdraw route %s next-hop %s' % (route,ip))
										log.write('\n')
										log.flush()
									
										write('withdraw route %s next-hop %s' % (route,ip))
		
		#write('announce route %s next-hop %s as-path [ %s ]' % ('100.0.0.0/16','172.0.0.1','100')) 
		#write('announce route %s next-hop %s as-path [ %s ]' % ('110.0.0.0/16','172.0.0.1','100')) 
		#write('announce route %s next-hop %s as-path [ %s ]' % ('120.0.0.0/16','172.0.0.11','200')) 
		#write('announce route %s next-hop %s as-path [ %s ]' % ('130.0.0.0/16','172.0.0.11','200'))
	except KeyboardInterrupt:
		pass
	except IOError:
		# most likely a signal during readline
		pass

file.close()

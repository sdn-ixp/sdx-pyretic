################################################################################
#
#  <website link>
#
#  File:
#        main.py
#
#  Project:
#        Software Defined Exchange (SDX)
#
#  Author:
#        Muhammad Shahbaz
#        Arpit Gupta (glex.qsd@gmail.com)
#        Laurent Vanbever
#
#  Copyright notice:
#        Copyright (C) 2012, 2013 Georgia Institute of Technology
#              Network Operations and Internet Security Lab
#
#  License:
#        This file is part of the SDX development base package.
#
#        This file is free code: you can redistribute it and/or modify it under
#        the terms of the GNU Lesser General Public License version 2.1 as
#        published by the Free Software Foundation.
#
#        This package is distributed in the hope that it will be useful, but
#        WITHOUT ANY WARRANTY; without even the implied warranty of
#        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#        Lesser General Public License for more details.
#
#        You should have received a copy of the GNU Lesser General Public
#        License along with the SDX source package.  If not, see
#        http://www.gnu.org/licenses/.
#

## General imports
import os
from threading import Thread,Event
from multiprocessing import Process,Queue

## Pyretic-specific imports
from pyretic.lib.corelib import *
from pyretic.lib.std import *
from pyretic.modules.mac_learner import *

## SDX-specific imports
from pyretic.sdx.utils import *
from pyretic.sdx.utils.arp import *
from pyretic.sdx.utils.inet import *
from pyretic.sdx.lib.core import *
from pyretic.sdx.lib.bgp_interface import *
from pyretic.sdx.bgp.route_server import route_server

''' Get current working directory ''' 
cwd = os.getcwd()

class sdx_policy(DynamicPolicy):
    """Standard MAC-learning logic"""
    def __init__(self,arp_policy):
        
        ''' list of IP to MAC mapping '''
        self.arp_policy = arp_policy
        
        print "Initialize SDX"
        super(sdx_policy,self).__init__()
        
        print "SDX:",self.__dict__
        
        self.sdx = sdx_parse_config(cwd+'/pyretic/sdx/sdx_global.cfg')
        
        ''' Event handling for dynamic policy compilation '''  
        event_queue=Queue()
        ready_queue=Queue()
        
        ''' Dynamic update policy thread '''
        dynamic_update_policy_thread = Thread(target=dynamic_update_policy_event_hadler,args=(event_queue,ready_queue,self.update_policy))
        dynamic_update_policy_thread.daemon = True
        dynamic_update_policy_thread.start()   
        
        ''' Router Server interface thread '''
        # TODO: confirm if we need RIBs per participant or per peer!
        rs = route_server(event_queue,ready_queue,self.sdx)
        
        rs_thread = Thread(target=rs.start)
        rs_thread.daemon = True
        rs_thread.start()
        
        ''' Update policies'''
        event_queue.put("init")
        #TODO: Should we send the loaded routes on bootup to the participants?
    
        ''' Announce custom routes '''
        sdx_parse_announcements(cwd+'/pyretic/sdx/sdx_announcements.cfg',self.sdx)
        sdx_annouce_custom_routes(self.sdx)
        
    def update_policy(self):
        
        # TODO: why are we running sdx_parse_polcieis for every update_policy (this is a serious bottleneck in policy compilation time) - MS
        sdx_parse_policies(cwd+'/pyretic/sdx/sdx_policies.cfg',self.sdx)
        
        ''' Get updated policy '''
        self.policy = sdx_platform(self.sdx)
        
        print 'Final Policy'
        print self.policy
        
        ''' Get updated IP to MAC list '''
        # TODO: Maybe we won't have to update it that often - MS
        #       Need efficient implementation of this ...
        self.arp_policy.mac_of = get_ip_mac_list(self.sdx.VNH_2_IP,self.sdx.VNH_2_MAC)
    
'''' Dynamic update policy handler '''
def dynamic_update_policy_event_hadler(event_queue,ready_queue,update_policy):
    
    while True:
        event_source=event_queue.get()
        
        ''' Compile updates '''
        update_policy()
        
        if ('bgp' in event_source):
            ready_queue.put(event_source)

        
''' Main '''
def main():
    
    arp_policy = arp()
    
    policy = sdx_policy(arp_policy)
    
    return if_(ARP,
                   arp_policy,
                   if_(BGP,
                           identity,
                           policy
                   )
               ) >> mac_learner()

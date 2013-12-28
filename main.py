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
from pyretic.sdx.bgp.route_server import route_server

''' Get current working directory ''' 
cwd = os.getcwd()

class sdx_policy(DynamicPolicy):
    """Standard MAC-learning logic"""
    def __init__(self):
        
        print "Initialize SDX"
        super(sdx_policy,self).__init__()
        
        print "SDX:",self.__dict__
        
        (self.base,self.participants) = sdx_parse_config(cwd+'/pyretic/sdx/sdx_global.cfg')
        
        ''' Get updated policy'''
        self.update_policy()
        
        ''' Event handling for dynamic policy compilation '''  
        event_queue=Queue()
        
        ''' Dynamic update policy thread '''
        dynamic_update_policy_thread = Thread(target=dynamic_update_policy_event_hadler,args=(event_queue,self.update_policy))
        dynamic_update_policy_thread.daemon = True
        dynamic_update_policy_thread.start()   
        
        ''' Router Server interface thread '''
        #TODO: need to clean up this logic by updating the core.py - MS
        
        peers_list=[]
        
        for participant_name in self.participants:
            for port in self.participants[participant_name].phys_ports:
                peers_list.append(str(port.ip))
                
        rs = route_server(peers_list)
        
        rs_thread = Thread(target=rs.start,args=(event_queue,self.base))
        rs_thread.daemon = True
        rs_thread.start()
        
    def update_policy(self):
        
        # TODO: why are we running sdx_parse_polcieis for every update_policy (this is a serious bottleneck in policy compilation time) - MS
        sdx_parse_policies(cwd+'/pyretic/sdx/sdx_policies.cfg',self.base,self.participants)
        
        ''' Get updated policy '''
        self.policy = sdx_platform(self.base)
        
        ''' Get updated IP to MAC list '''
        # TODO: Maybe we won't have to update it that often - MS
        self.ip_mac_list = get_ip_mac_list(self.base.VNH_2_IP,self.base.VNH_2_mac)
    
'''' Dynamic update policy handler '''
def dynamic_update_policy_event_hadler(event_queue,update_policy):
    
    while True:
        event_queue.get()
        
        ''' Compile updates '''
        update_policy()
        
''' Main '''
def main():
    
    policy = sdx_policy()
    
    return if_(ARP,
                   arp(policy.ip_mac_list),
                   if_(BGP,
                           identity,
                           policy
                   )
               ) >> mac_learner()

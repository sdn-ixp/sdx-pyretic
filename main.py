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

import pyretic.sdx.QuaggaInterface.quagga_interface as qI

''' Get current working directory ''' 
cwd = os.getcwd()

class sdx_policy(DynamicPolicy):
    """Standard MAC-learning logic"""
    def __init__(self):
        
        print "Initialize SDX"
        super(sdx_policy,self).__init__()
        
        print "SDX:",self.__dict__
        
        (self.base,self.participants)=sdx_parse_config(cwd+'/pyretic/sdx/sdx_global.cfg')
        
        ''' Get updated policy'''
        self.update_policy()
        
        ''' Event handling for dynamic policy compilation '''  
        event=Event()
        
        ''' Dynamic update policy thread '''
        dynamic_update_policy_thread=Thread(target=dynamic_update_policy_event_hadler,args=(event,self.update_policy))
        dynamic_update_policy_thread.daemon = True
        dynamic_update_policy_thread.start()   
        
        ''' Router Server interface thread '''
        # TODO: replace this with route server handler (still in progress) - MS
        route_server_thread=Thread(target=qI.main,args=(event,self.base))
        route_server_thread.daemon=True
        route_server_thread.start()
        
    def update_policy(self):
        
        # TODO: why are we running sdx_parse_polcieis for every update_policy (this is a serious bottleneck in policy compilation time) - MS
        sdx_parse_policies(cwd+'/pyretic/sdx/sdx_policies.cfg',self.base,self.participants)
        
        ''' Get updated policy '''
        self.policy=sdx_platform(self.base)
        
        # Maybe we won't have to update it that often - MS
        ''' Get updated IP to MAC list '''
        self.ip_mac_list=get_ip_mac_list(self.base.VNH_2_IP,self.base.VNH_2_mac)
    
'''' Dynamic update policy handler '''
def dynamic_update_policy_event_hadler(event,update_policy):
    
    while True:
        ''' Wait for the update event '''
        event.wait()
        
        ''' Compile updates '''
        update_policy()
        
        ''' Clear the event '''
        event.clear()

### Main ###
def main():
    
    policy=sdx_policy()
    
    return if_(ARP,
                   arp(policy.ip_mac_list),
                   if_(BGP,
                           identity,
                           policy
                   )
               ) >> mac_learner()

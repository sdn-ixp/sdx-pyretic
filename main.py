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
#        Arpit Gupta (glex.qsd@gmail.com)
#        Muhammad Shahbaz
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

## Pyretic-specific imports
from pyretic.lib.corelib import *
from pyretic.lib.std import *

from pyretic.modules.arp import *
from pyretic.modules.mac_learner import *

## SDX-specific imports
from pyretic.sdx.lib.core import *
import pyretic.sdx.QuaggaInterface.quagga_interface as qI

## General imports
import os
import thread,threading
from multiprocessing import Process, Queue

cwd = os.getcwd()

BGP_PORT = 179
BGP = match(srcport=BGP_PORT) | match(dstport=BGP_PORT)


class SDX_Policies(DynamicPolicy):
    """Standard MAC-learning logic"""
    def __init__(self):
        print "SDX init called"
        super(SDX_Policies,self).__init__()
        print "SDX:",self.__dict__
        (base,participants) = sdx_parse_config(cwd + '/pyretic/sdx/sdx_global.cfg')
        self.sdx=base
        self.participants=participants 
        self.update_policy(True)
        
        queue=Queue()  
        # Starting the thread to catch transition signals
        t1 = threading.Thread(target=self.transition_signal_catcher, args=(queue,))
        t1.daemon = True
        t1.start()   
        
        # Starting the Quagga Interface thread
        t2 = threading.Thread(target=qI.main, args=(self.sdx,queue,))
        t2.daemon = True
        t2.start()
        
        # TODO: Explore if we thread (current) or Process makes more sense here,
        # especially for BGP (Quagga Thread)
        
        print "Done with init"
        
    def compose_policies(self,init):
        # Update the sdx and participant data structures
        # Get the VNH assignment
        print "Compose policy function called with init: ",init
        if init==True:
            print "INIT: Parsing Policies"
            sdx_parse_policies(cwd + '/pyretic/sdx/sdx_policies.cfg', self.sdx, self.participants)
            self.policy=sdx_platform(self.sdx)
            # Get the time to compile initial set of policies
            start_comp=time.time()
            #self.policy.compile()
            #print "INIT: dict: ",self.__dict__
            print  'INIT: Aggregate Compilation',time.time() - start_comp, "seconds"
                   
        else:
            self.policy=drop
            sdx_update_policies(cwd + '/pyretic/sdx/sdx_policies.cfg',self.sdx, self.participants)
            self.policy=sdx_platform(self.sdx)
            #print "UPDATE: policy returned: ",self.policy 

        print "Done with compose"
        return self.policy
        
    def update_policy(self,init):
        self.policy=self.compose_policies (init)
    
    def transition_signal_catcher(self,queue):
        print "Transition signal catcher called"
        while 1:
            try:  
                line = queue.get(timeout=.1)
            except:
                continue
            else: # Got line 
                self.update_policy(False)
       
def getMacList(VNH_2_IP,VNH_2_MAC):
    ip_mac_list={}
    for vnh in VNH_2_IP:
        #print VNH_2_IP[vnh],VNH_2_mac[vnh]
        ip_mac_list[IPAddr(VNH_2_IP[vnh])]=EthAddr(VNH_2_mac[vnh])
    return ip_mac_list

### Main ###
def main():
    
    p=SDX_Policies()
    ip_mac_list=getMacList(p.sdx.VNH_2_IP,p.sdx.VNH_2_mac)
    print "ip_mac_list: ",ip_mac_list
    return if_(ARP, arp(ip_mac_list), if_(BGP, identity, p)) >> mac_learner()

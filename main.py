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

from pyretic.modules.mac_learner import *

## SDX-specific imports
from pyretic.sdx.lib.core import *
from pyretic.sdx.utils.arp import *
import pyretic.sdx.QuaggaInterface.quagga_interface as qI

## General imports
import os
import thread

cwd = os.getcwd()

BGP_PORT = 179
BGP = match(srcport=BGP_PORT) | match(dstport=BGP_PORT)

### SDX Platform ###
def sdx():
    ####
    #### Initialize SDX
    ####
    print "Parsing Global Config ....."
    (base, participants) = sdx_parse_config(cwd + '/pyretic/sdx/sdx_global.cfg')
    
    ####
    #### Apply policies from each participant
    ####
    print "Parsing Participant's policies ..."
    sdx_parse_policies(cwd + '/pyretic/sdx/sdx_policies.cfg', base, participants)
    #print base

    return ({IPAddr('172.0.0.172'): EthAddr('08:00:27:8b:e4:7b')},sdx_platform(base),base)
    # {} is the list of local IP-to-MAC addresses used with VNH. Will be extracted from the sdx_platform()

### Main ###
def main():
    """Handle ARPs, BGPs, SDX and then do MAC learning"""
    print "Parsing Configurations"
    
    start_parse=time.time()
    (ip_mac_list,sdx_policy,sdx_base) = sdx()
    
    print  time.time() - start_parse, "seconds"
    #print sdx_policy
    #for participant in sdx_base.participants:
    #    print participant.id_
    print "Compiled SDX Policies"
    start_comp=time.time()
    sdx_policy.compile()
    print  'Aggregate Compilation',time.time() - start_comp, "seconds"
    
    # Start the Quagga Interface
    thread.start_new_thread(qI.main(sdx_base))
    
    return if_(ARP, arp(ip_mac_list), if_(BGP, identity, sdx_policy)) >> mac_learner()

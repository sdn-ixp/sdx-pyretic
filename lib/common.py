################################################################################
#
#  <website link>
#
#  File:
#        core.py
#
#  Project:
#        Software Defined Exchange (SDX)
#
#  Author:
#        Laurent Vanbever
#        Muhammad Shahbaz
#        Arpit Gupta
#
#  Copyright notice:
#        Copyright (C) 2012, 2013 Georgia Institute of Technology
#              Network Operations and Internet Security Lab
#
#  Licence:
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

###
### SDX classes
###

class Port(object):
    """Represents a switch port"""
    def __init__(self, mac='', participant=None, ip=''):
        self.mac = mac
        self.participant = participant
        self.ip=ip

class PhysicalPort(Port):
    """Abstract class that represents a physical port"""
    def __init__(self, id_, *args, **kwargs):
        super(PhysicalPort, self).__init__(*args, **kwargs)
        self.id_ = id_

class VirtualPort(Port):
    """Abstract class that represents a virtual port"""
    def __init__(self, *args, **kwargs):
        super(VirtualPort, self).__init__(*args, **kwargs)

class SDXParticipant(object):
    """Represent a particular SDX participant"""
    def __init__(self, id_, vport, phys_ports, peers={}, policies=None, rs_client=None, custom_routes=[]):
        self.id_ = id_
        self.vport = vport
        self.phys_ports = phys_ports
        self.peers = peers
        self.policies = policies 
        self.original_policies=None       
        self.vport.participant = self ## set the participant
        self.n_policies=0
        self.rs_client=rs_client
        self.custom_routes=custom_routes
    
    def init_policy(self,new_policy):
        self.policies=new_policy
        self.n_policies=1
        
    def add_policy(self,new_policy):
        self.policies=parallel([self.policies,new_policy])
        self.n_policies+=1
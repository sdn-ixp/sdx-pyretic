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
#        Arpit Gupta
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

## General imports
import os

cwd = os.getcwd()

### SDX Platform ###
def sdx():
    ####
    #### Initialize SDX
    ####
    (base, participants) = sdx_parse_config(cwd + '/pyretic/sdx/sdx_global.cfg')
    
    ####
    #### Apply policies from each participant
    ####
    sdx_parse_policies(cwd + '/pyretic/sdx/sdx_policies.cfg', base, participants)
    
    return sdx_platform(base)

### Main ###
def main():
    """Handle ARPs, SDX and do MAC learning"""
    sdx_policy = sdx()
    print sdx_policy
    return if_(ARP, arp(), sdx_policy) # >> mac_learner)
    #return sdx()

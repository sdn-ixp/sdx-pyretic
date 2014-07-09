#!/usr/bin/env python
#  Author:
#  Muhammad Shahbaz (muhammad.shahbaz@gatech.edu)

from pyretic.lib.corelib import *
from pyretic.lib.std import *

''' BGP filter policy '''
BGP_PORT = 179
BGP = match(srcport=BGP_PORT) | match(dstport=BGP_PORT)

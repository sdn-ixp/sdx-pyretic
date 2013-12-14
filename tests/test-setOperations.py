################################################################################
#
#  <website link>
#
#  File:
#        test-setOperations.py
#        To stress test the set operation functionality with data from AMS-IX collector
#
#  Project:
#        Software Defined Exchange (SDX)
#
#  Author:
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


# SDX specific imports
from pyretic.sdx.lib.setOperation import *

# General imports
import os,sys
from ipaddr import IPv4Network

def initializeData():
    print "Initializing data for stress test"

def main():
    print "Starting the setOperations stress test"
    initializeData()

if __name__ == '__main__':
    main()

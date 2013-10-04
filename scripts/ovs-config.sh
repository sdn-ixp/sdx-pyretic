#!/bin/bash
################################################################################
#
#  <website link>
#
#  File:
#        ovs-config.sh
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

case "$1" in
   start)
      echo "Starting Open vSwitch ..." 
      # Clear eth1
      ifconfig eth1 0
      ifconfig eth1 promisc
      # Clear eth2
      ifconfig eth2 0
      ifconfig eth2 promisc
      # Clear eth0
      ifconfig eth0 0
      ifconfig eth0 promisc
      # Configure bridge 0
      ovs-vsctl add-br br0 
      ovs-vsctl add-port br0 eth1
      ovs-vsctl add-port br0 eth2
      ovs-vsctl add-port br0 eth0
      # Bring up bridge 0
      ifconfig br0 up
      # Assign remote controller
      ovs-vsctl set-controller br0 tcp:127.0.0.1:6633
      ovs-vsctl set-fail-mode br0 secure
   ;;
   stop)
      echo "Stopping Open vSwitch ..."
      # Delete remote controller
      ovs-vsctl del-controller br0
      ovs-vsctl del-fail-mode br0
      # Turn down bridge 9
      ifconfig br0 down
      # Delete bridge 0
      ovs-vsctl del-br br0      
      # Restart Network Service
      ifconfig eth1 -promisc
      ifconfig eth1 down
      ifconfig eth2 -promisc
      ifconfig eth2 down
      ifconfig eth0 -promisc
      ifconfig eth0 down
   ;;
   *)
      echo "Usage: of-swtich {start|stop}"
   ;;
esac

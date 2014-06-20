#!/bin/bash
######################################
# SDX: Software Defined Exchange
# Author: Muhammad.Shahbaz@gatech.edu
######################################

case "$1" in 
  start) 
    echo "Starting SDX ..."
    # Clear eth2 (RS), eth3 (AS-A), eth4 (AS-B), eth5 (AS-C1), eth6 (AS-C2), and eth7 (AS-D)
    ifconfig eth2 0
    ifconfig eth2 promisc
    ifconfig eth3 0
    ifconfig eth3 promisc
    ifconfig eth4 0
    ifconfig eth4 promisc
    ifconfig eth5 0
    ifconfig eth5 promisc
    ifconfig eth6 0
    ifconfig eth6 promisc
    ifconfig eth7 0
    ifconfig eth7 promisc
    # Cofigure bridge (br0)
    ovs-vsctl add-br br0
    ovs-vsctl add-port br0 eth2
    ovs-vsctl add-port br0 eth3
    ovs-vsctl add-port br0 eth4
    ovs-vsctl add-port br0 eth5
    ovs-vsctl add-port br0 eth6
    ovs-vsctl add-port br0 eth7
    # Setup remote interface (eth1)
    ifconfig eth1 0
    ifconfig eth1 192.168.1.2 netmask 255.255.255.0
    ifconfig eth1 up
    # Assign remote controller to bridge (br0)
    ovs-vsctl set-controller br0 tcp:192.168.1.1:6633
    ovs-vsctl set-fail-mode br0 secure
    # Bring up bridge (br0)
    ifconfig br0 up
  ;;
  stop)
    echo "Stopping SDX ..."
    # Detach remote controller from bridge (br0)
    ovs-vsctl del-controller br0
    ovs-vsctl del-fail-mode br0
    # Turn down and delete bridge (br0)
    ifconfig br0 down
    ovs-vsctl del-br br0
    # Turn down other interfaces
    ifconfig eth2 0
    ifconfig eth3 0
    ifconfig eth4 0
    ifconfig eth5 0
    ifconfig eth6 0
    ifconfig eth7 0
    ifconfig eth1 0
    ifconfig eth1 down
  ;;
  *)
    echo "Usage: ixp-setup {start|stop}"
  ;;
esac
     

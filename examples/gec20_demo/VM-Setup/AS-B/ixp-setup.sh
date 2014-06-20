#!/bin/bash
######################################
# SDX: Software Defined Exchange
# Author: Muhammad.Shahbaz@gatech.edu
######################################

case "$1" in
  start)
    echo "Starting SDX ..."
    # Setup remote interface (eth2)
    ifconfig eth2 172.0.0.11 netmask 255.255.0.0 up
    #ifconfig eth3 172.200.0.2 netmask 255.255.255.0 up
    # Setup loopback interfaces
    ifconfig lo:140 140.0.0.1 netmask 255.255.255.0 up
    ifconfig lo:150 150.0.0.1 netmask 255.255.255.0 up
  ;;
  stop)
    echo "Stopping SDX ..."
    # Clear remote and loopback interface interface
    ifconfig eth2 down
    #ifconfig eth3 down
    ifconfig lo:140 down
    ifconfig lo:150 down
  ;;
  *)
    echo "Usage: ixp-setup {start|stop}"
  ;;
esac


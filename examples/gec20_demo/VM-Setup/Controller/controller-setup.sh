#!/bin/bash
######################################
# SDX: Software Defined Exchange
# Author: Muhammad.Shahbaz@gatech.edu
######################################

case "$1" in
  start)
    echo "Starting SDX ..."
    # Setup remote interface (eth2)
    ifconfig eth2 0
    ifconfig eth2 192.168.1.1 netmask 255.255.255.0
    ifconfig eth2 up
    # Setup remote interface (eth3) for BGP participants
    ifconfig eth3 172.0.255.254 netmask 255.255.0.0
    ifconfig eth3 up
  ;;
  stop)
    echo "Stopping SDX ..."
    # Clear remote interface (eth2)
    ifconfig eth2 0
    ifconfig eth2 down
    # Clear remote interface (eth3)
    ifconfig eth3 down
;;
exabgp)
   echo "Starting ExaBGP ..."
   if [ "$(id -u)" == "0" ]; then
      echo "Do not perform this operation as root (run as user = sdx)" 1>&2
      exit 1
   fi
   /home/mininet/pyretic/pyretic/sdx/exabgp/sbin/exabgp --env /home/mininet/pyretic/pyretic/sdx/exabgp/etc/exabgp/exabgp.env /home/mininet/pyretic/pyretic/sdx/bgp/bgp.conf
  ;;
 pyretic)
   echo "Starting Pyretic ..."
   if [ "$(id -u)" == "0" ]; then
      echo "Do not perform this operation as root (run as user = sdx)" 1>&2
      exit 1
   fi
   (cd /home/mininet/pyretic/ && ./pyretic.py pyretic.sdx.main)
  ;;
 clearrib)
   echo "Clearing RIB ..."
   rm -rf /home/mininet/pyretic/pyretic/sdx/ribs/*
  ;;
 pushconfig)
   echo "SDX Config File: Pushing (sdx_global.cfg, sdx_policies.cfg)...."
   cp -r /home/sdx/pyretic/pyretic/sdx/examples/sigcomm14/Controller-Setup/SDX-Config/* /home/sdx/pyretic/pyretic/sdx
;; 
*)
    echo "Usage: ixp-setup {start|stop|exabgp|pyretic|clearrib|pushconfig}"
  ;;
esac


#!/bin/bash
######################################
# SDX: Software Defined Exchange
# Author: Arpit Gupta
######################################

case "$1" in
exabgp)
   echo "Starting ExaBGP ..."
   if [ "$(id -u)" == "0" ]; then
      echo "Do not perform this operation as root" 1>&2
      exit 1
   fi
   $HOME/pyretic/pyretic/sdx/exabgp/sbin/exabgp --env $HOME/pyretic/pyretic/sdx/exabgp/etc/exabgp/exabgp.env $HOME/pyretic/pyretic/sdx/bgp/bgp.conf
  ;;
 pyretic)
   echo "Starting Pyretic ..."
   if [ "$(id -u)" == "0" ]; then
      echo "Do not perform this operation as root" 1>&2
      exit 1
   fi
   (cd $HOME/pyretic/ && ./pyretic.py pyretic.sdx.main)
  ;;
 mininet)
EXAMPLE_NAME=$2
   if [ -d "$HOME/pyretic/pyretic/sdx/examples/$EXAMPLE_NAME" ]; then
   	echo "Starting Mininet ..."
   	if [ "$(id -u)" == "0" ]; then
      		echo "Do not perform this operation as root" 1>&2
      		exit 1
   	fi
   (sudo $HOME/pyretic/pyretic/sdx/examples/$EXAMPLE_NAME/mininet/sdx_mininext.py)
   else
	echo "Directory does not exists: $HOME/pyretic/pyretic/sdx/examples/$EXAMPLE_NAME"
   fi 
  ;;
 demo)
EXAMPLE_NAME=$2
   if [ -d "$HOME/pyretic/pyretic/sdx/examples/$EXAMPLE_NAME" ]; then
   	echo "Starting Mininet ..."
   	if [ "$(id -u)" == "0" ]; then
      		echo "Do not perform this operation as root" 1>&2
      		exit 1
   	fi
   (sudo python $HOME/pyretic/pyretic/sdx/examples/$EXAMPLE_NAME/mininet/demo.py)
   else
	echo "Directory does not exists: $HOME/pyretic/pyretic/sdx/examples/$EXAMPLE_NAME"
   fi 
  ;;
 clearrib)
   echo "Clearing RIB ..."
   rm -rf $HOME/pyretic/pyretic/sdx/ribs/*
  ;;
 init)
   EXAMPLE_NAME=$2
   if [ -d "$HOME/pyretic/pyretic/sdx/examples/$EXAMPLE_NAME" ]; then
  	echo "SDX Config File: Pushing (sdx_global.cfg, sdx_policies.cfg, bgp.conf)...."
   	cp -r $HOME/pyretic/pyretic/sdx/examples/$EXAMPLE_NAME/controller/sdx_config/sdx_* $HOME/pyretic/pyretic/sdx
   	cp -r $HOME/pyretic/pyretic/sdx/examples/$EXAMPLE_NAME/controller/sdx_config/bgp.conf $HOME/pyretic/pyretic/sdx/bgp/
   else
	echo "Directory does not exists: $HOME/pyretic/pyretic/sdx/examples/$EXAMPLE_NAME"
   fi
;; 
*)
    echo "Usage: ixp-setup {exabgp|pyretic|mininet <example_name>|clearrib|pushconfig|init <example_name>}"
  ;;
esac


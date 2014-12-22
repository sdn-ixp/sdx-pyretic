#!/bin/sh
################################################################################
# Flavio Castro
# Software Defined Exchange
# Georgia Institute of Technology   
# December 2014
################################################################################
BGPD="/etc/quagga/bgpd.conf"

if [ ! -f $BGPD ]
then
    case "$1" in
    exabgp)
       echo "Starting ExaBGP ..."
       sudo apt-get -y install wireshark
       sudo setcap 'CAP_NET_RAW+eip CAP_NET_ADMIN+eip' /usr/bin/dumpcap
       # git clone https://github.com/sdn-ixp/sdx
       # cd sdx
       # git checkout FlavioGeni
       # sudo cp examples/GeniIxp/exabgp/* bgp
       # $HOME/sdx/exabgp/sbin/exabgp --env $HOME/sdx/exabgp/etc/exabgp/exabgp.env $HOME/sdx/bgp/bgp.conf
      ;;
     quagga)
        ROUTER=$2
        echo "Configuring Quagga..."
        #install quagga, wireshark and nmap
        sudo apt-get -y install quagga wireshark iperf
        #Adding permissions to wireshark
        sudo setcap 'CAP_NET_RAW+eip CAP_NET_ADMIN+eip' /usr/bin/dumpcap
        cd /home/
        git clone https://github.com/sdn-ixp/sdx
        cd sdx
        git checkout FlavioGeni
        sudo cp examples/GeniIXP/quaggacfgs/$ROUTER/* /etc/quagga
        sudo /etc/init.d/quagga restart
      ;;
    *)
        echo "Usage: geni-setup {exabgp|quagga <router>}"
      ;;
    esac
else
    echo "False"
fi












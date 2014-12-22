#!/bin/sh
################################################################################
# Flavio Castro
# Software Defined Exchange
# Georgia Institute of Technology   
# December 2014
################################################################################
BGPD="/etc/quagga/bgpd.conf"
ROUTER=$1
if [ ! -f $BGPD ]
then
    #install quagga, wireshark and nmap
    sudo apt-get -y install quagga wireshark
    #Adding permissions to wireshark
    sudo setcap 'CAP_NET_RAW+eip CAP_NET_ADMIN+eip' /usr/bin/dumpcap
    cd ~/
    git clone https://github.com/sdn-ixp/sdx
    cd sdx
    git checkout FlavioGeni
    sudo cp examples/GeniIXP/quaggacfgs/$ROUTER/* /etc/quagga
    sudo /etc/init.d/quagga restart
else
    echo "False"
fi












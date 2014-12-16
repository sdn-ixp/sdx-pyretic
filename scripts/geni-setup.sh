#!/bin/bash
######################################
# SDX: Software Defined Exchange
# Author: Flavio Castro
######################################

#`sudo apt-get update`
#`sudo apt-get install -y wireshark quagga`
sudo setcap 'CAP_NET_RAW+eip CAP_NET_ADMIN+eip' /usr/bin/dumpcap
#`git clone https://github.com/sdn-ixp/sdx`
#`cd sdx`
#`git checkout FlavioGeni`
sudo cp examples/GeniIXP/quaggacfgs/a1/* /etc/quagga
#`cd ..`
#`sudo apt-get install -y python-dev python-pip python-netaddr screen hping3 ml-lpt graphviz ruby1.9.1-dev`
#`sudo apt-get install -y libboost-dev libboost-test-dev libboost-program-options-dev libevent-dev automake`
#`sudo apt-get install -y libtool flex bison pkg-config g++ libssl-dev python-all python-all-dev python-all-dbg`
echo "Installing stuff pyretic dependencies"
`sudo pip install networkx bitarray netaddr ipaddr pytest ipdb yappi sphinx pyparsing==1.5.7`
`sudo gem install jekyll`
echo "asynchat"
`wget https://raw.github.com/frenetic-lang/pyretic/master/pyretic/backend/patch/asynchat.py`
`sudo mv asynchat.py /usr/lib/python2.7/`
`sudo chown root:root /usr/lib/python2.7/asynchat.py`
echo "Installing git pox"
`git clone http://www.github.com/noxrepo/pox`

##Configuring Route Server
`sudo apt-get update`
`sudo apt-get install -y git`
`git clone https://github.com/sdn-ixp/sdx`
`cd sdx`
`git checkout FlavioGeni`
chown user name client/log



def addInterfacesForSDXNetwork( net ):
    hosts=net.hosts
    print "Configuring participating ASs\n\n"
    for host in hosts:
        print "Host name: ", host.name
        if host.name=='a1':
                host.cmd('sudo ifconfig lo:1 100.0.0.1 netmask 255.255.255.0 up')
                host.cmd('sudo ifconfig lo:2 100.0.0.2 netmask 255.255.255.0 up')
                host.cmd('sudo ifconfig lo:110 110.0.0.1 netmask 255.255.255.0 up')
        if host.name=='b1':
                host.cmd('sudo ifconfig lo:140 140.0.0.1 netmask 255.255.255.0 up')
                host.cmd('sudo ifconfig lo:150 150.0.0.1 netmask 255.255.255.0 up')
        if host.name=='c1':
                host.cmd('sudo ifconfig lo:140 140.0.0.1 netmask 255.255.255.0 up')
                host.cmd('sudo ifconfig lo:150 150.0.0.1 netmask 255.255.255.0 up')
        if host.name=='c2':
                host.cmd('sudo ifconfig lo:140 140.0.0.1 netmask 255.255.255.0 up')
                host.cmd('sudo ifconfig lo:150 150.0.0.1 netmask 255.255.255.0 up')
        if host.name == "exabgp":
                host.cmd( 'route add -net 172.0.0.0/16 dev exabgp-eth0')

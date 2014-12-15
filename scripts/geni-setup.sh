#!/bin/bash
######################################
# SDX: Software Defined Exchange
# Author: Flavio Castro
######################################

#`sudo apt-get update`
#`sudo apt-get install -y wireshark`
#`sudo git checkout https://github.com/sdn-ixp/sdx`
#`cd sdx`
#`git checkout FlavioGeni`
#`cd ..`
#`sudo apt-get install -y python-dev python-pip python-netaddr screen hping3 ml-lpt graphviz ruby1.9.1-dev`
#`sudo apt-get install -y libboost-dev libboost-test-dev libboost-program-options-dev libevent-dev automake`
#`sudo apt-get install -y libtool flex bison pkg-config g++ libssl-dev python-all python-all-dev python-all-dbg`
echo "Installing stuff pyretic dependencies"
`sudo pip install networkx bitarray netaddr ipaddr pytest ipdb sphinx pyparsing==1.5.7`
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
`sudo git clone https://github.com/sdn-ixp/sdx`
`cd sdx`
`git checkout FlavioGeni`

#!/usr/bin/python
################################################################################
#
#  <website link>
#
#  File:
#        sdx_mininet_simple.py
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
#  License:
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

import sys, getopt
from mininet.topo import SingleSwitchTopo
from mininet.net import Mininet
from mininet.log import setLogLevel
from mininet.node import RemoteController
from mininet.cli import CLI

def getArgs():
    cli = False;
    controller = '127.0.0.1'
    
    try:
        opts, args = getopt.getopt(sys.argv[1:],"h",["help", "cli", "controller="])
    except getopt.GetoptError:
        print 'sdx_mininet_simple.py [--cli --controller <ip address>]'
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            
            print 'sdx_mininet_simple.py [--cli --controller <ip address>]'
            sys.exit()
        elif opt == '--cli':
            cli = True
        elif opt == '--controller':
            controller = arg
    return (cli, controller)
   
def simple(cli, controllerIP):
    "Create and test SDX Simple Module"
    print "Creating the topology with one IXP switch and three participating ASs\n\n" 
    topo = SingleSwitchTopo(k=3)
    net = Mininet(topo, controller=lambda name: RemoteController( 'c0', controllerIP ), autoSetMacs=True) #, autoStaticArp=True)
    net.start()
    hosts=net.hosts
    print "Configuring participating ASs\n\n"
    for host in hosts:
        if host.name=='h1':
            host.cmd('ifconfig lo:40 110.0.0.1 netmask 255.255.255.0 up')
            host.cmd('route add -net 120.0.0.0 netmask 255.255.255.0 gw 10.0.0.2 h1-eth0')
            host.cmd('route add -net 130.0.0.0 netmask 255.255.255.0 gw 10.0.0.2 h1-eth0')
        if host.name=='h2':
            host.cmd('route add -net 110.0.0.0 netmask 255.255.255.0 gw 10.0.0.1 h2-eth0')
            host.cmd('ifconfig lo:40 120.0.0.1 netmask 255.255.255.0 up')
            host.cmd('route add -net 130.0.0.0 netmask 255.255.255.0 gw 10.0.0.3 h2-eth0')
        if host.name=='h3':
            host.cmd('route add -net 110.0.0.0 netmask 255.255.255.0 gw 10.0.0.2 h3-eth0')
            host.cmd('route add -net 120.0.0.0 netmask 255.255.255.0 gw 10.0.0.2 h3-eth0')
            host.cmd('ifconfig lo:40 130.0.0.1 netmask 255.255.255.0 up')
    if (cli): # Running CLI
        CLI(net)
    else:
        print "Running the Ping Tests\n\n"
        for host in hosts:
            if host.name=='h1':
                host.cmdPrint('ping -c 5 -I 110.0.0.1 130.0.0.1')

    net.stop()
    print "\n\nExperiment Complete !\n\n"

if __name__ == '__main__':
    # Tell mininet to print useful information
    setLogLevel('info')
    # Parse arguments
    (cli, controller) = getArgs() 
    
    simple(cli, controller) 
#!/usr/bin/python

"Create a network consisting of Quagga routers"

import inspect, os, atexit
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.service import QuaggaService
from mininet.node import Node
from mininet.link import Link
from collections import namedtuple
from mininet.node import RemoteController
from mininet.term import makeTerm, cleanUpScreens
QuaggaHost = namedtuple("QuaggaHost", "name ip mac port")
net = None

class QuaggaTopo( Topo ):
    "Quagga topology example."

    def __init__( self ):

        "Initialize topology"
        Topo.__init__( self )

        "Directory where this file / script is located"
        scriptdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) # script directory
        "Initialize a service helper for Quagga with default options"
        quaggaSvc = QuaggaService()

        "Path configurations for mounts"
        quaggaBaseConfigPath=scriptdir + '/quaggacfgs/'

        "List of Quagga host configs"
        quaggaHosts = []
        quaggaHosts.append(QuaggaHost(name = 'a1', ip = '172.0.0.1/16', mac = '08:00:27:89:3b:9f', port = 2))
        quaggaHosts.append(QuaggaHost(name = 'b1', ip = '172.0.0.11/16', mac ='08:00:27:92:18:1f', port = 3))
        quaggaHosts.append(QuaggaHost(name = 'c1', ip = '172.0.0.21/16', mac = '08:00:27:54:56:ea', port = 4))
        quaggaHosts.append(QuaggaHost(name = 'c2', ip = '172.0.0.22/16', mac = '08:00:27:bd:f8:b2', port = 5))

        "Add switch for IXP fabric"
        ixpfabric = self.addSwitch( 's1' )

        "Setup each legacy router, add a link between it and the IXP fabric"
        for host in quaggaHosts:
            "Set Quagga service configuration for this node"
            quaggaSvcConfig = \
            { 'quaggaConfigPath' : scriptdir + '/quaggacfgs/' + host.name }

            "Add services to the list for handling by service helper"
            services = {}
            services[quaggaSvc] = quaggaSvcConfig
            "Create an instance of a host, called a quaggaContainer"
            quaggaContainer = self.addHost( name=host.name,
                                            ip=host.ip,
					    mac=host.mac,
                                            services=services,
                                            privateLogDir=True,
                                            privateRunDir=True,
                                            inMountNamespace=True,
                                            inPIDNamespace=True)
            "Attach the quaggaContainer to the IXP Fabric Switch"
            self.addLink( quaggaContainer, ixpfabric , port2=host.port)

def connectToRootNS( network, switch, ip, routes ):
    """Connect hosts to root namespace via switch. Starts network.
      network: Mininet() network object
      switch: switch to connect to root namespace
      ip: IP address for root namespace node
      routes: host networks to route to"""
    # Create a node in root namespace and link to switch 0
    root = Node( 'exabgp', inNamespace=False )
    intf = Link( root, switch ).intf1
    root.setIP( ip, intf=intf )
    # Start network that now includes link to root namespace
    network.start()
    # Add routes from root ns to hosts
    for route in routes:
        root.cmd( 'route add -net ' + route + ' dev ' + str( intf ) )



def addInterfacesForSDXNetwork( net ):
    hosts=net.hosts
    print "Configuring participating ASs\n\n"
    for host in hosts:
	if host.name=='a1':
		host.cmdPrint('sudo ifconfig lo:1 100.0.0.1 netmask 255.255.255.0 up')
		host.cmdPrint('sudo ifconfig lo:2 100.0.0.2 netmask 255.255.255.0 up')
		host.cmdPrint('sudo ifconfig lo:110 110.0.0.1 netmask 255.255.255.0 up')
		host.cmdPrint('sudo ifconfig -a')  
	if host.name=='b1':
		host.cmdPrint('sudo ifconfig lo:140 140.0.0.1 netmask 255.255.255.0 up')
		host.cmdPrint('sudo ifconfig lo:150 150.0.0.1 netmask 255.255.255.0 up')
		host.cmdPrint('sudo ifconfig -a')  
	if host.name=='c1':
		host.cmdPrint('sudo ifconfig lo:140 140.0.0.1 netmask 255.255.255.0 up')
		host.cmdPrint('sudo ifconfig lo:150 150.0.0.1 netmask 255.255.255.0 up')
		host.cmdPrint('sudo ifconfig -a')  
	if host.name=='c2':
		host.cmdPrint('sudo ifconfig lo:140 140.0.0.1 netmask 255.255.255.0 up')
		host.cmdPrint('sudo ifconfig lo:150 150.0.0.1 netmask 255.255.255.0 up')
		host.cmdPrint('sudo ifconfig -a')  


def startNetwork():
    info( '** Creating Quagga network topology\n' )
    topo = QuaggaTopo()
    global net
    net = Mininet(topo=topo, 
		controller=lambda name: RemoteController( name, ip='127.0.0.1' ),listenPort=6633)

    info( '** Starting the network\n' )
    net.start()
    
    info( '** Dumping host connections\n' )
    dumpNodeConnections(net.hosts)

    info( '** psaux dumps on all hosts\n' )
    for lr in net.hosts:
        lr.cmdPrint("ps aux")
    #    lr.cmdPrint("xterm &")
    info( '** Dumping host connections\n' )
    dumpNodeConnections(net.hosts)

    info( '**Adding Network Interfaces for SDX Setup\n' )    
    addInterfacesForSDXNetwork(net)
    
    switch = net.switches[ 0 ]
    info( '** Adding SDX Controller ') 
    connectToRootNS( net, switch,'172.0.255.254/16', [ '172.0.0.0/16' ] )
 
    info( '** Running CLI\n' )
    CLI( net )

def stopNetwork():
    if net is not None:
        info( '** Tearing down Quagga network\n' )
        net.stop()

if __name__ == '__main__':
    # Force cleanup on exit by registering a cleanup function
    atexit.register(stopNetwork)

    # Tell mininet to print useful information
    setLogLevel('info')
    startNetwork()

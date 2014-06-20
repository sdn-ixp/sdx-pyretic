#!/bin/bash
if [ -z "$1" ]; then
        echo "Usage: $0 pushVM"
        exit 1
fi

if [ "$1" = "pushVM" ]; then
	#Script to Create N/W Interfaces
	echo "Pushing Setup Files..."
	sshpass -p "sdx" scp OVS/ixp-setup.sh sdx@192.168.56.101:/home/sdx/scripts/
	echo "Virtual Switch : Done"
	sshpass -p "sdx" scp AS-A/ixp-setup.sh sdx@192.168.56.102:/home/sdx/scripts/	
	echo "AS-A : Done"
	sshpass -p "sdx" scp AS-B/ixp-setup.sh sdx@192.168.56.103:/home/sdx/scripts/
        echo "AS-B : Done"
	sshpass -p "sdx" scp AS-C1/ixp-setup.sh sdx@192.168.56.104:/home/sdx/scripts/
        echo "AS-C1 : Done"
	sshpass -p "sdx" scp AS-C2/ixp-setup.sh sdx@192.168.56.105:/home/sdx/scripts/
        echo "AS-C2 : Done"
	sshpass -p "sdx" scp Controller/ixp-setup.sh sdx@192.168.56.106:/home/sdx/scripts/
        echo "Controller : Done"
	
	#BGP Configuration file
        echo "Pushing BGP Configuration Files..."
	sshpass -p "sdx" scp AS-A/bgpd.conf sdx@192.168.56.102:/etc/quagga/
        echo "AS-A : Done"
	sshpass -p "sdx" scp AS-B/bgpd.conf sdx@192.168.56.103:/etc/quagga/       
	echo "AS-B : Done"
	sshpass -p "sdx" scp AS-C1/bgpd.conf sdx@192.168.56.104:/etc/quagga/
        echo "AS-C1 : Done"
	sshpass -p "sdx" scp AS-C2/bgpd.conf sdx@192.168.56.105:/etc/quagga/
        echo "AS-C2 : Done"
fi

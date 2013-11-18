#############################################
# SDX-Quagga Integration                    #
# author: Arpit Gupta (glex.qsd@gmail.com)  #
#############################################

import socket
import threading
import SocketServer
import json
from bgp_update import*
from json_coders import*

## SDX-specific imports
from pyretic.sdx.lib.common import *
from pyretic.sdx.lib.core import *


def process_update(bgp_update):
    return 'OK'

def update_info(info1,info2):
    # Make note of update replacing a previous entry
    return info1

def update_rib(jmesg,sdx_base):
    print "RIB Update function called"
    # get the participants name
    neighbor_list=[]
    sender_name=sdx_base.get_participantName(jmesg.update.peer)
    print sender_name
    if sender_name=='':
        print "Error: Participant not found"
    else:
        neighbor_list=sdx_base.get_neighborList(sender_name)
    print "neighbor list: ",neighbor_list
    for participant in sdx_base.participants:
        if participant.id_ in neighbor_list:
            print "update: ",participant.id_
            if (jmesg.prefix.address,jmesg.prefix.prefixlen) not in participant.rib:
                participant.rib[(jmesg.prefix.address,jmesg.prefix.prefixlen)]={}
            participant.rib[(jmesg.prefix.address,jmesg.prefix.prefixlen)][jmesg.update.peer]=jmesg.update
            print "Rib:", participant.rib

        
    """
    for participant in sdx_base.participants:
        for participant_name in participant.peers:
            print participant.peers[participant_name].ip
        
        if jmesg.update.peer in participant.peers:
            if (jmesg.prefix.address,jmesg.prefix.prefixlen) not in participant.rib:
                participant.rib[(jmesg.prefix.address,jmesg.prefix.prefixlen)]={}   
            participant.rib[(jmesg.prefix.address,jmesg.prefix.prefixlen)][jmesg.update.peer]=jmesg.update
        
        print participant.rib
    """
def process_json(message,sdx_base):
    print message
    jmesg=MyDecoder().decode(message)
    #print 'Decoded Update Object: ',update_msg
    # Apply the logic to analyse this BGP Update and

    update_rib(jmesg,sdx_base)
    print jmesg.prefix.address,jmesg.prefix.prefixlen

    return json.dumps(jmesg,cls=ComplexEncoder,
            default=convert_to_builtin_type)

def main(sdx_base):
    message = ''
    print "Quagga Interface Started"
    for participant in sdx_base.participants:
        print participant.rib
    # Set up the Server
    HOST,port="localhost",9998
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST,port))
    s.listen(1)

    while True:
        message=''

        conn,addr = s.accept()
        print 'Received connection from ',addr

        while True:
            data = conn.recv(1024)

            if not data:
                conn.close()
                break

            message = message + data
            return_value = process_json(message,sdx_base)
            #return_value = "OK"
            #print return_value
            conn.sendall(return_value)
            print "Sent the message back"
            #parse_message(message)



if __name__ == "__main__":
    main()


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
from multiprocessing import Process, Queue
## SDX-specific imports
from pyretic.sdx.lib.common import *
from pyretic.sdx.lib.core import *

participant_to_ebgp_nh_received1={
        'A' : {'p1':'D','p2':'D','p3':'D','p4':'C','p5':'C','p6':'C'}
    }
participant_to_ebgp_nh_received2={
        'A' : {'p1':'D','p2':'D','p3':'D','p4':'B','p5':'C','p6':'C'}
    }


def update_info(info1,info2):
    # Make note of update replacing a previous entry
    
    return info2

def update_rib(jmesg,sdx_base):
    print "RIB Update called"
    neighbor_list=[]
    # get the participants name    
    sender_name=sdx_base.get_participantName(jmesg.update.peer)
    new_update=jmesg.update
    prefix_curr=(jmesg.prefix.address,jmesg.prefix.prefixlen)
    peer_curr=jmesg.update.peer
    #print sender_name
    if sender_name=='':
        print "Error: Participant not found"
    else:
        neighbor_list=sdx_base.get_neighborList(sender_name)
    #print "neighbor list: ",neighbor_list
    for participant in sdx_base.participants:
        if participant.id_ in neighbor_list:
            #print "update: ",participant.id_
            if prefix_curr not in participant.rib:
                participant.rib[prefix_curr]={}
            elif peer_curr in participant.rib[prefix_curr]:
                info1=participant.rib[prefix_curr][peer_curr]
                new_update=update_info(info1,jmesg.update)
            
            participant.rib[prefix_curr][peer_curr]=new_update
            #print "Rib:", participant.rib

def VNH_assignment(jmesg,sdx):
    print "VNH Assignment Called"
    print "part_2_vnh: ",sdx.part_2_VNH
    vnh_flag=False
    jmesg_updated=jmesg
    prefix=IPv4Network(str(jmesg.prefix.address)+'/'+str(jmesg.prefix.prefixlen))
    prefix_str=''
    for pfx in sdx.prefixes:
        if sdx.prefixes[pfx]==prefix:
            prefix_str=pfx
    announcer=sdx.get_participantName(jmesg.update.peer).encode('ascii','ignore')
    for vnh in sdx.part_2_VNH[announcer]:
        if prefix_str in sdx.part_2_VNH[announcer][vnh]:
            vnh_flag=True
            jmesg_updated.update.attr.nexthop=VNH_2_IP[vnh]
            print "VNH Selected: ",vnh
    
    return vnh_flag,jmesg_updated

def process_json(message,sdx,queue):
    print message
    jmesg=MyDecoder().decode(message)
    # Check this BGP Update for VNH assignment
    flag_vnh,jmesg_new=VNH_assignment(jmesg,sdx)
    if flag_vnh==True:
        print "BGP Update Modified with VNH Assignment"
        print "New NH: ",jmesg_new.update.attr.nexthop 
        if sdx.participant_to_ebgp_nh_received==participant_to_ebgp_nh_received1:
            sdx.participant_to_ebgp_nh_received=participant_to_ebgp_nh_received2
        else:
            sdx.participant_to_ebgp_nh_received=participant_to_ebgp_nh_received1
        queue.put('transition')
    # Update the rib with this new BGP Update    
    update_rib(jmesg_new,sdx)    
    return json.dumps(jmesg_new,cls=ComplexEncoder,
            default=convert_to_builtin_type)

def main(sdx,queue):
    message = ''
    print "Quagga Interface Started"
    print "best path info",sdx.participant_to_ebgp_nh_received
    print "VNH-NH mappings",sdx.VNH_2_IP
    print "VNH-prefix mappings",sdx.part_2_VNH
    
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
            return_value = process_json(message,sdx,queue)
            conn.sendall(return_value)
            print "Sent the message back"

if __name__ == "__main__":
    main()


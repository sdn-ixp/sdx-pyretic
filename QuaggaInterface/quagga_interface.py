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

c1='140.0.0.0/16'
c2='150.0.0.0/16'

VNH_map={'VNHB':'172.0.0.201','VNHC':'172.0.0.301','VNHA':'172.0.0.101'}

# prefix_2_policy={c1:{'C':{'C':'policy1'},'B':{'B':'policy1','A':'policy1'}},
#                       c2:{'C':{'C':'policy1'},'B':{'B':'policy1','A':'policy1'}}
#                       }

# policy_2_VNH={'A':{'policy1':{}},
#                    'B':{'policy1':{'B':{c1:'VNHB',c2:'VNHB'}}},
#                    'C':{'policy1':{'C':{}}} # No VNH assigned
#                    }
# 
# policy_2_prefix={'A':{'policy1':[c1,c2]},
#                    'B':{'policy1':[c1,c2]},
#                    'C':{'policy1':[c1,c2]}
#                    }
# 
# VNH_2_participant={'VNHB':{'A':([c1,c2],'B','policy1'),
#                            'B':([c1,c2],'B','policy1')},
#                    'VNHC':{'C':([c1,c2],'C','policy1')}
#                    }


# prefix_2_policy={c1:{'C':{'A':'policy1'},'B':{'B':'policy1','A':'policy1'}},
#                       c2:{'C':{'A':'policy1'},'B':{'B':'policy1','A':'policy1'}}
#                       }
# 
# policy_2_VNH={'A':{'policy1':{}},
#                    'B':{'policy1':{}}
#                    }
# 
# policy_2_prefix={'A':{'policy1':[c1,c2]},
#                  'B':{'policy1':[c1,c2]}
#                 }

VNH_2_participant={'VNHB':{'A':([c1,c2],'B','policy1'),
                           'B':([c1,c2],'B','policy1')},
                   'VNHC':{'C':([c1,c2],'C','policy1')}
                   }



def process_update(bgp_update):
    return 'OK'

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

def getNew_VNH(peer,policy):
    # Very naiive logic for now, we can improve it later    
    base='VNH'+peer
    pn=int(policy.split('policy')[1])
    VNH=('VNH'+peer+'_'+str(pn)).encode('ascii','ignore') # unicode to ascii encoding, not important
    print VNH
    if VNH not in VNH_map:
        # Need to update the VNH_map
        if base in VNH_map:
            last=int(VNH_map[base].split('.')[3])
            nlast=last+pn*10            
            new_ip=VNH_map[base].split(str(last))[0]+str(nlast)        
            VNH_map[VNH]=new_ip
    print "Updated VNH Map: ",VNH_map            
    return VNH

def VNH_assignment(jmesg,sdx_base):
    print "VNH Assignment Called"
    vnh_flag=False
    jmesg_updated=jmesg
    prefix_curr=str(jmesg.prefix.address)+'/'+str(jmesg.prefix.prefixlen)
    peer_curr=sdx_base.get_participantName(jmesg.update.peer).encode('ascii','ignore')
    VNH_new=''
    nparticipant=''
    print prefix_curr
    if prefix_curr in sdx_base.prefix_2_policy:
        vnh_flag=True
        
        if peer_curr in sdx_base.prefix_2_policy[prefix_curr].keys():
            print 'Update Sender requires VNH assignment for this prefix'
            affected_participants=sdx_base.prefix_2_policy[prefix_curr][peer_curr]
            if peer_curr in affected_participants:
                #print "Other affected participants",affected_participants   
                nparticipant=peer_curr
            else:
                #Case where we'll look for first element in the key and make VNH assignment accordingly
                print "Sender itself has no policies for this prefix"
                nparticipant=affected_participants.keys()[0]
                print nparticipant
                                
            policy_curr=sdx_base.prefix_2_policy[prefix_curr][peer_curr][nparticipant] 
            if policy_curr not in sdx_base.policy_2_VNH[nparticipant]:
                sdx_base.policy_2_VNH[nparticipant][policy_curr]={}
            if peer_curr not in sdx_base.policy_2_VNH[nparticipant][policy_curr]:
                sdx_base.policy_2_VNH[nparticipant][policy_curr][peer_curr]={}  
            if prefix_curr in sdx_base.policy_2_VNH[nparticipant][policy_curr][peer_curr]:
                VNH_new=sdx_base.policy_2_VNH[nparticipant][policy_curr][peer_curr][prefix_curr]                
            else:
                print "assign a new VNH"
                VNH_new=getNew_VNH(nparticipant,policy_curr)
                
            print "New VNH Assignment: ",VNH_map[VNH_new]            
            # Update the other affected participants
            print "Update the affected participants/Prefixes"
            for participant in affected_participants:
                #if participant !=peer_curr:
                print 'Updating for the participant: ',participant
                policy_temp=sdx_base.prefix_2_policy[prefix_curr][peer_curr][participant]
                prefix_list=sdx_base.policy_2_prefix[participant][policy_temp]
                if policy_temp not in sdx_base.policy_2_VNH[participant]:
                    sdx_base.policy_2_VNH[participant][policy_temp]={}
                if peer_curr not in sdx_base.policy_2_VNH[participant][policy_temp]:
                    sdx_base.policy_2_VNH[participant][policy_temp][peer_curr]={}                   
                for temp in prefix_list:
                    sdx_base.policy_2_VNH[participant][policy_temp][peer_curr][temp]=VNH_new
            print "Updated policy_2_VNH: ",sdx_base.policy_2_VNH
                            
        else:
            print "There are no policies for updates from this sender"            
    else:
        print "This prefix does not requires VNH assignment"
                    
    # modify the jmesg if required
    if vnh_flag==True:
        jmesg_updated.update.attr.nexthop=VNH_map[VNH_new]
          
    
    return vnh_flag,jmesg_updated

def process_json(message,sdx_base):
    print message
    jmesg=MyDecoder().decode(message)
    # Check this BGP Update for VNH assignment
    flag_vnh,jmesg_new=VNH_assignment(jmesg,sdx_base)
    if flag_vnh==True:
        print "BGP Update Modified with VNH Assignment"
        print "New NH: ",jmesg_new.update.attr.nexthop    
    # Update the rib with this new BGP Update    
    update_rib(jmesg_new,sdx_base)    
    return json.dumps(jmesg_new,cls=ComplexEncoder,
            default=convert_to_builtin_type)

def main(sdx_base):
    message = ''
    print "Quagga Interface Started"
    
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
            conn.sendall(return_value)
            print "Sent the message back"

if __name__ == "__main__":
    main()


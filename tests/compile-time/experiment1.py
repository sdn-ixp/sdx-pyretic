#############################################
# Experiment to evaluate the compilation    #
# times for 100 participants                #
# author: Arpit Gupta (glex.qsd@gmail.com)  #
#############################################
"""
100 participants
3 of them advertising p1,p2,p3,p4,p5,p6 with inbound policies
97 of them with outbound policies
"""

import os,json,sys,random
from netaddr import *

## Pyretic-specific imports
from pyretic.lib.corelib import *
from pyretic.lib.std import *

## SDX-specific imports
from pyretic.sdx.lib.common import *
from pyretic.sdx.lib.core import *
from pyretic.sdx.lib.vnhAssignment import *

iplist=list(IPNetwork('182.0.0.1/24'))
macinit='A1:A1:00:00:00:00'


def generate_sdxglobal(ntot,nin):
    sdx_participants={}
    for ind in range(1,ntot+1):
        peers=[]
        for i in range(1,ntot+1):
            if i!=ind:
                peers.append(str(i))
        ports=[]
        count =ind
        ip,mac=str(iplist[count]),str(EUI(int(EUI(macinit))+count))
        ports.append({'Id':count,'MAC':mac,'IP':ip})
        if ind<=nin:         
            for i in range(2):
                count=(ind-1)*2+i+1+ntot
                ip,mac=str(iplist[count]),str(EUI(int(EUI(macinit))+count))
                ports.append({'Id':count,'MAC':mac,'IP':ip})                   
        
        
        sdx_participants[ind]={'Ports':ports,'Peers':peers}
        with open('sdx_global.cfg', 'w') as outfile:
            json.dump(sdx_participants,outfile,ensure_ascii=True)
    return sdx_participants

def update_paramters(sdx,ntot,nin):
    participant_2_port={}
    port_2_participant={}
    prefixes_announced={}
    participant_to_ebgp_nh_received={}
    prefixes_announced['pg1']={}
    peer_groups={'pg1':range(1,ntot+1)}
    for participant in sdx.participants:
        if int(participant.id_)<=nin:
            prefixes_announced['pg1'][participant.id_]=sdx.prefixes.keys()
        else:
            participant_to_ebgp_nh_received[participant.id_]={}
            for pfx in sdx.prefixes.keys():
                participant_to_ebgp_nh_received[participant.id_][pfx]=random.randint(1,nin)
        participant_2_port[participant.id_]={}
        participant_2_port[participant.id_][participant.id_]=[participant.phys_ports[i].id_ 
                                                              for i in range(len(participant.phys_ports))]
        for phyport in participant.phys_ports:
            port_2_participant[phyport.id_]=participant.id_
        for peer in participant.peers:
            participant_2_port[participant.id_][peer]=[participant.peers[peer].participant.phys_ports[0].id_]
    print 'participant_2_port: ',participant_2_port
    print 'port_2_participant: ',port_2_participant
    print 'prefixes_announced: ',prefixes_announced
    print 'participant_to_ebgp_nh_received: ',participant_to_ebgp_nh_received
    # Update SDX's data structure
    sdx.participant_2_port=participant_2_port
    sdx.port_2_participant=port_2_participant
    sdx.prefixes_announced=prefixes_announced
    sdx.participant_to_ebgp_nh_received=participant_to_ebgp_nh_received


def generate_policies(sdx,participants,ntot,nin):
    for participant in sdx.participants:
        print participant.id_
        if int(participant.id_)<=nin:
            print "inbound policies"
            policy=((match(dstport=80) >> sdx.fwd(participant.phys_ports[2]))+
                    (match(dstport=22) >> sdx.fwd(participant.phys_ports[1]))
                   )
        else:
            print "outbound policies"
            policy=((match(dstport=80) >> sdx.fwd(participant.peers['1']))+
                    (match(dstport=22) >> sdx.fwd(participant.peers['2']))+
                    (match(dstport=25) >> sdx.fwd(participant.peers['3']))
                   )
        print policy
        participant.policies=policy
        participant.original_policies=participant.policies
        participant.policies=pre_VNH(participant.policies,sdx,participant.id_,participant)
        print participant.policies
    vnh_assignment(sdx,participants)
    classifier=[]
    for participant_name in participants:
        print participant_name
        participants[participant_name].policies=post_VNH(participants[participant_name].policies,
                                                         sdx,participant_name)        
        #print "After Post VNH: ",participants[participant_name].policies
        start_comp=time.time()
        classifier=(participants[participant_name].policies.compile())
        #print classifier
        print participant_name, time.time() - start_comp, "seconds"
    

     
def main():
    ntot=3
    nin=3   # number of participants with inbound policies
    sdx_participants=generate_sdxglobal(ntot,nin)
    (sdx,participants) = sdx_parse_config('sdx_global.cfg')
    update_paramters(sdx,ntot,nin)
    generate_policies(sdx,participants,ntot,nin)
    aggr_policies=sdx_platform(sdx)
    print "Completed State Machine COmposition"
    print aggr_policies
    start_comp=time.time()
    print aggr_policies.compile()
    print  'Completed Aggregate Compilation',time.time() - start_comp, "seconds"
    

if __name__ == '__main__':
    main()
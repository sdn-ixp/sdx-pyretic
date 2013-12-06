################################################################################
#
#  <website link>
#
#  File:
#        core.py
#
#  Project:
#        Software Defined Exchange (SDX)
#
#  Author:
#        Laurent Vanbever
#        Arpit Gupta
#        Muhammad Shahbaz
#
#  Copyright notice:
#        Copyright (C) 2012, 2013 Georgia Institute of Technology
#              Network Operations and Internet Security Lab
#
#  Licence:
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

## Pyretic-specific imports
from pyretic.lib.corelib import *
from pyretic.lib.std import *

## SDX-specific imports
from pyretic.sdx.lib.common import *
from pyretic.sdx.lib.setOperation import *
from pyretic.sdx.lib.language import *
from pyretic.sdx.lib.policy_converter import *

## General imports
import json
from importlib import import_module
from ipaddr import IPv4Network
###
### SDX classes
###
prefix_2_participant={'100.0.0.0/16':{'A':['B'],'B':['C']},
                      '120.0.0.0/16':{'B':['A','C']},
                      '140.0.0.0/16':{'C':['B'],'B':['A']},
                      '150.0.0.0/16':{'C':['B'],'B':['A']},
                      }


class SDX(object):
    """Represent a SDX platform configuration"""
    def __init__(self):
        self.participants = []
        self.sdx_ports={}
        self.participant_id_to_in_var = {}
        self.out_var_to_port = {}
        self.port_id_to_out_var = {}
        self.policy_2_prefix={}
        self.prefix_2_policy={}
        self.prefix_2_participant=prefix_2_participant # This will be later updated from the BGP RIB table
        self.policy_2_VNH={}
        
    def get_participantName(self,ip):
        pname=''
        #print self.sdx_ports
        #print ip
        for participant_name in self.sdx_ports:
            for port in self.sdx_ports[participant_name]:
                #print port.ip
                if IP(ip)==port.ip:
                    #print "IP matched"
                    pname=participant_name
                    break
        return pname
    def get_neighborList(self,sname):
        #print type(sname)
        neighbor_list=[]
        for participant in self.participants:
            #print participant.peers.keys()
            if sname in participant.peers.keys():
                #print "Neighbor found",participant.id_
                neighbor_list.append(participant.id_) 
        return neighbor_list
    
    def add_participant(self, participant):
        self.participants.append(participant)
        self.participant_id_to_in_var[participant.id_] = "in" + participant.id_.upper()
        i = 0
        for port in participant.phys_ports:
            self.port_id_to_out_var[port.id_] = "out" + participant.id_.upper() + "_" + str(i)
            self.out_var_to_port["out" + participant.id_.upper() + "_" + str(i)] = port
            i += 1
    
    #def return_participant(self,ip):
    
    def fwd(self, port):
        if isinstance(port, PhysicalPort):
            return modify(state=self.port_id_to_out_var[port.id_], dstmac=port.mac)
        else:
            return modify(state=self.participant_id_to_in_var[port.participant.id_])
###
### SDX high-level functions
###

def sdx_from(vport):
    '''
        Helper function that given a vport
        return a match function for all the physical macs behind that vport
        this is useful to avoid communication between two participants
    '''
    match_all_physical_port = no_packets
    for phys_port in vport.participant.phys_ports:
        match_all_physical_port = match_all_physical_port | match(srcmac=phys_port.mac)
    return match_all_physical_port

def sdx_restrict_state(sdx_config, participant):
    '''
        Check if the state is not an end state (i.e., output port). 
        If so return a passthrough policy otherwise 
        prefix a match on the participant's state variable
        before any of the participant's policy to ensure that
        it cannot match on other participant's flowspace
    '''
    match_all_output_var = no_packets
    for output_var in sdx_config.out_var_to_port:
        match_all_output_var = match_all_output_var | match(state=output_var)
    return if_(match_all_output_var, 
               passthrough, 
               match(state=sdx_config.participant_id_to_in_var[participant.id_]) >> 
                    #parallel([sdx_from(participant.peers[peer_name]) for peer_name in participant.peers]) & '''Might not happen, as we are providing limited view to the participants''' 
                        participant.policies
              )

def sdx_preprocessing(sdx_config):
    '''
        Map incoming packets on participant's ports to the corresponding
        incoming state
    '''
    preprocessing_policies = []
    for participant in sdx_config.participants:
        for port in participant.phys_ports:
            preprocessing_policies.append((match(inport=port.id_) >> 
                modify(state=sdx_config.participant_id_to_in_var[participant.id_])))
    return parallel(preprocessing_policies)

def sdx_postprocessing(sdx_config):
    '''
        Forward outgoing packets to the appropriate participant's ports
        based on the outgoing state
    '''
    postprocessing_policies = []
    for output_var in sdx_config.out_var_to_port:
        postprocessing_policies.append((match(state=output_var) >> modify(state=None) >> 
            fwd(sdx_config.out_var_to_port[output_var].id_)))
    return parallel(postprocessing_policies)

def sdx_participant_policies(sdx_config):
    '''
        Sequentially compose the || composition of the participants policy k-times where
        k is the number of participants
    '''
    sdx_policy = passthrough
    for k in sdx_config.participants:
        sdx_policy = sequential([
                sdx_policy,
                parallel(
                    [sdx_restrict_state(sdx_config, participant) for participant in sdx_config.participants]
                )])
    return sdx_policy


###
### SDX primary functions
###

def sdx_parse_config(config_file):
    sdx = SDX()
    
    sdx_config = json.load(open(config_file, 'r'))
    #print sdx_config
    sdx_ports = {}
    sdx_vports = {}
    sdx_participants = {}
    
    ''' 
        Create SDX environment ...
    '''
    for participant_name in sdx_config:
        
        ''' Adding physical ports '''
        participant = sdx_config[participant_name]
        sdx_ports[participant_name] = [PhysicalPort(id_ = participant["Ports"][i]['Id'], mac = MAC(participant["Ports"][i]["MAC"]),ip=IP(participant["Ports"][i]["IP"])) for i in range(0, len(participant["Ports"]))]     
        #print sdx_ports[participant_name][0].ip
        ''' Adding virtual port '''
        sdx_vports[participant_name] = VirtualPort() #Check if we need to add a MAC here
    sdx.sdx_ports=sdx_ports   
    for participant_name in sdx_config:
        peers = {}
        
        ''' Assign peers to each participant '''
        for peer_name in sdx_config[participant_name]["Peers"]:
            peers[peer_name] = sdx_vports[peer_name]
            
        ''' Creating a participant object '''
        sdx_participants[participant_name] = SDXParticipant(id_ = participant_name, vport=sdx_vports[participant_name], phys_ports = sdx_ports[participant_name], peers = peers)
        
        ''' Adding the participant in the SDX '''
        sdx.add_participant(sdx_participants[participant_name])
    
    return (sdx, sdx_participants)



                    
def get_policy_name(policy_2_prefix,participant,prefix):  
    policy_name=''
    for policy in policy_2_prefix[participant]:
        if prefix in policy_2_prefix[participant][policy]:
            policy_name=policy
            break
    return policy_name


def is_Active(policy_in,pnum,participant_name,sdx,prefixes):
    flag_active=True
    participant_name=participant_name.encode('ascii','ignore')
    if participant_name not in sdx.policy_2_prefix:
        sdx.policy_2_prefix[participant_name]={}  
        sdx.policy_2_VNH[participant_name]={}   
    for temp in policy_in.policies:
        pnum+=1
        pname='policy'+str(pnum)
        plist=[]
        for temp2 in temp.policies[0].policies:
            if 'dstip' in temp2.map:
                flag_active=False
                plist.append(str(temp2.map['dstip']))
                prefixes[str(temp2.map['dstip'])]=''
        if flag_active==False:
            sdx.policy_2_prefix[participant_name][pname]=plist
            sdx.policy_2_VNH[participant_name][pname]={}
    #print sdx.policy_2_prefix
    return flag_active

def get_bestPaths(nh_received):
    best_paths={}
    for participant in nh_received:
        best_paths[participant]={}
        for prefix in nh_received[participant].keys():
            if nh_received[participant][prefix] in best_paths[participant]:
                best_paths[participant][nh_received[participant][prefix]].append(prefix)
            else:
                best_paths[participant][nh_received[participant][prefix]]=[prefix]    
    return best_paths

def get_fwdPeer(peers,ind):
    for peer in peers:
        if ind in peers[peer]:
            return peer
    return ''
    
def get_prefix(policy,plist,pfxlist,part,pa,acc=[]):
    if isinstance(policy, parallel):
        for pol in policy.policies:
            pfxlist,acc=get_prefix(pol,plist,pfxlist,part,pa)
    elif isinstance(policy, sequential):
        acc=[]
        for pol in policy.policies:
            pfxlist,acc=get_prefix(pol,plist,pfxlist,part,pa,acc) 
    elif isinstance(policy, if_):
        for pol in policy.policies:
            pfxlist,acc=get_prefix(pol,plist,pfxlist,part,pa)  
    else:
        if isinstance(policy, match):
            #print policy
            if 'dstip' in policy.map:
                acc=list(policy.map['dstip'])
        elif isinstance(policy,match_prefixes_set):
            #print policy
            #if 'dstip' in policy.map:
            acc=list(policy.pfxes)
        elif isinstance(policy, fwd):
            if len(acc)==0:
                peer=get_fwdPeer(plist[part],policy.outport)
                acc=pa['pg1'][peer]
            pfxlist.append(acc)   
    return pfxlist,acc


def get_part2prefixes(policies,plist,pa):
    p2pfx={}
    for participant in policies:
        policy=policies[participant]
        pfxlist=[]
        acc=[]
        pfxlist,acc=get_prefix(policy,plist,pfxlist,participant,pa)
        #print participant,pfxlist
        p2pfx[participant]=pfxlist
    
    return p2pfx
    
def get_vname(prefix_set,vdict):
    vname=''
    for temp in vdict:
        if len(list(set(vdict[temp]).intersection(set(prefix_set))))>0:
            vname=temp    
    return vname

def get_fwdMap(part_2_VNH):
    fwd_map={}
    for participant in part_2_VNH:
        fwd_map[participant]={}
        for vname,pfx in part_2_VNH[participant].items():
            for peer in part_2_VNH:
                if peer!=participant:
                    if peer not in fwd_map[participant]:
                        fwd_map[participant][peer] = {}
                    for vnm in part_2_VNH[peer]:
                        if part_2_VNH[peer][vnm]==pfx and vnm!=vname:
                            fwd_map[participant][peer][vname]=vnm
    print "fwd_map: ",fwd_map
    return fwd_map

def vnh_assignment(sdx,participants):
    # Step 1:
    # Get the expanded policies from participant's input policies
    # Prefixes:
    VNH_2_IP={'VNHB':'172.0.0.201','VNHC':'172.0.0.301','VNHA':'172.0.0.101','VNHD':'172.0.0.401'}
    VNH_2_mac={'VNHA':'A1:A1:A1:A1:A1:00','VNHC':'C1:C1:C1:C1:C1:00','VNHB':'B1:B1:B1:B1:B1:00','VNHD':'D1:D1:D1:D1:D1:00'}
    
    prefixes={'p1':IPv4Network('11.0.0.0/24'),
              'p2':IPv4Network('12.0.0.0/24'),
              'p3':IPv4Network('13.0.0.0/24'),
              'p4':IPv4Network('14.0.0.0/24'),
              'p5':IPv4Network('15.0.0.0/24'),
              'p6':IPv4Network('16.0.0.0/24')
              }
    
    participant_list={'A':{'A':[1],'B':[2],'C':[3],'D':[4]},
                      'B':{'A':[1],'B':[21,22],'C':[3],'D':[4]},
                      'C':{'A':[1],'B':[2],'C':[3],'D':[4]},
                      'D':{'A':[1],'B':[2],'C':[3],'D':[4]}
                      }
    
    port_2_participant = {
        1 : 'A',
        2 : 'B',
        21 : 'B',
        22 : 'B',
        3 : 'C',
        4 : 'D'
    }
    
    peer_group={'pg1':[1,2,3,4]}
    # Set of prefixes for A's best paths
    # We will get this data structure from RIB
    participant_to_ebgp_nh_received = {
        'A' : {'p1':'D','p2':'D','p3':'D','p4':'C','p5':'C','p6':'C'}
    }
    prefixes_announced={'pg1':{
                               'A':['p0'],
                               'B':['p1','p2','p3','p4','p6'],
                               'C':['p3','p4','p5','p6'],
                               'D':['p1','p2','p3','p4','p5','p6'],
                               }
                        }
    
    participants_policies = {
        'A':(
            (match(dstport=80) >> fwd(2)) +
            (match(dstport=22) >> fwd(3)) 
         ),
         'B':(
            (match(dstport= 80) >> fwd(21)) +
            (match(dstport=22) >> fwd(21)) +
            (match_prefixes_set(set(['p1'])) >> fwd(21)) +
            (match_prefixes_set(set(['p4'])) >> fwd(21))+
            (match_prefixes_set(set(prefixes_announced['pg1']['B']).difference(set(['p1','p4']))) >> fwd(22))           
         ),
         'C':(
            (match_prefixes_set(set(prefixes_announced['pg1']['C'])) >> fwd(3))
         ),
         'D':(
            (match_prefixes_set(set(prefixes_announced['pg1']['D'])) >> fwd(4))
         ),
        
    }

    # Step 1:
    #----------------------------------------------------------------------------------------------------#
    # 1. Get the best paths data structure
    # 2. Get the participant_2_prefix data structure from participant's policies

    best_paths=get_bestPaths(participant_to_ebgp_nh_received)
    print 'best_paths: ',best_paths
    # get the participant_2_prefix structure
    # without taking default forwarding policies into consideration
    participant_2_prefix=get_part2prefixes(participants_policies,participant_list,prefixes_announced)
    # Add the prefixes for default forwarding policies now
    for participant in best_paths:
        participant_2_prefix[participant]=participant_2_prefix[participant]+best_paths[participant].values()        
    #----------------------------------------------------------------------------------------------------#

    
    # Step 2 & 3
    #participant_2_prefix={'A':[PB,PC,PA1,PA2],'B':[PB,['p1'],['p4']],'C':[PC],'D':[PD]}
    print 'Before Set operations: ',participant_2_prefix
    part_2_prefix_updated=prefix_decompose(prefixes,participant_2_prefix)
    print 'After Set operations: ',part_2_prefix_updated
    #----------------------------------------------------------------------------------------------------#
    
    
    # Step 4: Assign VNHs
    part_2_VNH={}
    
    # deal with folks without best path policies
    for participant in part_2_prefix_updated:
        part_2_VNH[participant]={}
        count=1
        for prefix_set in part_2_prefix_updated[participant]:
            if participant not in best_paths:
                vname='VNH'+participant+str(count)
                base='VNH'+participant
                if vname not in VNH_2_IP:
                    # Need to update the VNH_2_IP
                    if base in VNH_2_IP:
                        last=int(VNH_2_IP[base].split('.')[3])
                        nlast=last+count*1 
                        nhex=hex(nlast-last)
                        new_mac=VNH_2_mac[base].split('00')[0]+'0'+str(nhex).split('0x')[1]   
                        #print new_mac   
                        new_ip=VNH_2_IP[base].split(str(last))[0]+str(nlast)        
                        VNH_2_IP[vname]=new_ip
                        VNH_2_mac[vname]=new_mac
                part_2_VNH[participant][vname]=prefix_set
                count+=1
    print part_2_VNH
    # Now deal with folks with best path policies
    for participant in part_2_prefix_updated:        
        for prefix_set in part_2_prefix_updated[participant]:
            if participant in best_paths:
                for peer in best_paths[participant]:
                    if len(list(set(best_paths[participant][peer]).intersection(set(prefix_set))))>0:
                        vname=get_vname(prefix_set,part_2_VNH[peer])
                        part_2_VNH[participant][vname]=prefix_set   
    
    fwd_map=get_fwdMap(part_2_VNH)
    print part_2_VNH
    print VNH_2_IP
    print VNH_2_mac
    #----------------------------------------------------------------------------------------------------#
    
    # Step 5
    # Step 5a: Get expanded policies
    for participant in participants_policies:
        print "PARTICIPANT: ",participant
        X_policy=participants_policies[participant]
        print "Original policy:", X_policy
        
        X_a = step5a(X_policy, participant,prefixes_announced,participant_list)
        print "Policy after 5a:\n\n", X_a
        
        X_b = step5b(X_a, participant,part_2_VNH,VNH_2_mac,best_paths,participant_list)
        print "Policy after Step 5b:", X_b
        
        X_c = step5c(X_b, participant, participant_list, port_2_participant, fwd_map)
        print "Policy after Step 5c:\n", (X_b >> X_c)
        
        participants_policies[participant]= (X_b >> X_c)
        
def step5c(policy, participant, participant_list, port_2_participant, fwd_map):
    fwd_neighbors = [port_2_participant[a] for a in extract_all_forward_actions_from_policy(policy)]
    
    rewrite_policy = None
    
    for neighbor in fwd_neighbors:
        if neighbor != participant:
            p = None
            for (a,b) in fwd_map[participant][neighbor].items():
                if not p:
                    p = (match(dstmac=a) >> modify(dstmac=b))
                else:
                    p = p + (match(dstmac=a) >> modify(dstmac=b))
            if rewrite_policy:
                rewrite_policy += match(outport=participant_list[participant][neighbor]) >> (p)
            else:
                rewrite_policy = match(outport=participant_list[participant][neighbor]) >> (p)

    if rewrite_policy:
        return rewrite_policy
    else:
        return passthrough

def get_peerName(port,p_list):
    for peer in p_list:
        if port in p_list[peer]:
            return peer
    return ''
 

def step5b(policy, participant,part_2_VNH,VNH_2_mac,best_paths,participant_list):
    expanded_vnhop_policy = step5b_expand_policy_with_vnhop(policy, participant,part_2_VNH,VNH_2_mac)
    
    policy_matches = extract_all_matches_from_policy(expanded_vnhop_policy)
    if participant in best_paths:
        #print 'BIG Match: ',policy_matches
        bgp = step5b_expand_policy_with_vnhop(get_default_forwarding_policy(best_paths[participant],participant,participant_list),participant,part_2_VNH,VNH_2_mac)
        #print bgp   
        return if_(policy_matches, expanded_vnhop_policy, bgp)
    else:
        return expanded_vnhop_policy
    
    
    #return expanded_vnhop_policy
    
def step5b_expand_policy_with_vnhop(policy, participant_id,part_2_VNH,VNH_2_mac, acc=[]):
    # Recursive call
    if isinstance(policy, parallel):
        return parallel(map(lambda p: step5b_expand_policy_with_vnhop(p, participant_id,part_2_VNH,VNH_2_mac), policy.policies))
    elif isinstance(policy, sequential):
        acc = []
        return sequential(map(lambda p: step5b_expand_policy_with_vnhop(p, participant_id,part_2_VNH,VNH_2_mac, acc), policy.policies))
    elif isinstance(policy, if_):
        return if_(step5b_expand_policy_with_vnhop(policy.pred, participant_id,part_2_VNH,VNH_2_mac), 
                   step5b_expand_policy_with_vnhop(policy.t_branch, participant_id,part_2_VNH,VNH_2_mac), 
                   step5b_expand_policy_with_vnhop(policy.f_branch, participant_id,part_2_VNH,VNH_2_mac))
    else:
        # Base call
        if isinstance(policy, match_prefixes_set):            
            unique_vnhops = set()
            for pfx in policy.pfxes:
                vnhop = return_vnhop(part_2_VNH[participant_id],VNH_2_mac, pfx)
                unique_vnhops.add(vnhop)
            #print unique_vnhops
            acc=list(unique_vnhops)
            match_vnhops=match(dstmac=unique_vnhops.pop())
            for vnhop in unique_vnhops:
                match_vnhops = match_vnhops + match(dstmac=vnhop)
            #print match_vnhops           
            print 'acc1: ',acc
            print policy           
            return match_vnhops
        
        elif isinstance(policy, fwd):
            print 'acc: ',acc
            print 'policy: ',policy
            if len(list(acc)):
                print 'a: ',acc
            
        return policy

def get_default_forwarding_policy(best_path,participant,participant_list):
    #for peer in best_path:
    policy_ip=parallel([match_prefixes_set(set(best_path[peer]))>>fwd(participant_list[participant][peer][0]) 
                        for peer in best_path.keys()]) 
    #print policy_ip
    return policy_ip 

def return_vnhop(vnh_2_prefix,VNH_2_mac, pfx):
    vnhop=EthAddr('A1:A1:A1:A1:A1:A1')
    #print vnh_2_prefix,pfx
    for vname in vnh_2_prefix:
        if pfx in vnh_2_prefix[vname]:
            return VNH_2_mac[vname]
    return vnhop

def step5a(policy, participant, prefixes_announced,participant_list,include_default_policy=False):
    p1 = step5a_expand_policy_with_prefixes(policy, participant,prefixes_announced,participant_list)
    if include_default_policy:
        p1 = p1 >> get_default_forwarding_policy(participant)
    return p1

def step5a_expand_policy_with_prefixes(policy, participant, pa, plist,acc=[]):
    global participants_announcements
    
    # Recursive call
    if isinstance(policy, parallel):
        return parallel(map(lambda p: step5a_expand_policy_with_prefixes(p, participant,pa,plist), policy.policies))
    elif isinstance(policy, sequential):
        acc = []
        return sequential(map(lambda p: step5a_expand_policy_with_prefixes(p, participant,pa, plist,acc), policy.policies))
    elif isinstance(policy, if_):
        return if_(step5a_expand_policy_with_prefixes(policy.pred, participant,pa,plist), 
                   step5a_expand_policy_with_prefixes(policy.t_branch, participant,pa,plist), 
                   step5a_expand_policy_with_prefixes(policy.f_branch, participant,pa,plist))
    else:
        # Base call
        if isinstance(policy, match):
            if 'dstip' in policy.map:
                acc.append('dstip')
        elif isinstance(policy, match_prefixes_set):
            acc.append('dstip')
        elif isinstance(policy, fwd):            
            if 'dstip' not in acc:    
                return match_prefixes_set(pa['pg1'][get_fwdPeer(plist[participant],policy.outport)]) >> policy
        return policy

    
def sdx_parse_policies(policy_file, sdx, participants):

    vnh_assignment(sdx,participants)
    
    """
    sdx_policies = json.load(open(policy_file, 'r'))
     
    ''' 
        Get participants policies
    '''
    cnt=0
    prefixes={}
    for participant_name in sdx_policies:
        participant = participants[participant_name]
        policy_modules = [import_module(sdx_policies[participant_name][i]) for i in range(0, len(sdx_policies[participant_name]))]
        policy_participant=[]
        for i in range(0,len(sdx_policies[participant_name])):
            pnum=cnt+i*100
            policy_in =policy_modules[i].policy(participant, sdx.fwd)
            flag_active=is_Active(policy_in,pnum,participant_name,sdx,prefixes)
            #if flag_active==True:
            policy_participant.append(policy_in)
                 
        participant.policies = parallel([policy_participant[i] for i in range(0, len(policy_participant))])
        print participant.policies
        

    
    # Older logic, might be useful in parts later
    # Now generate the prefix_2_policy from policy_2_prefix
    print prefixes
    for prefix in prefixes:
        sdx.prefix_2_policy[prefix]={}
        if prefix not in sdx.prefix_2_participant:
            print "Error: prefix_2_participant incomplete"
        else:
            for announcer in sdx.prefix_2_participant[prefix]:
                sdx.prefix_2_policy[prefix][announcer]={}
                for participant in sdx.prefix_2_participant[prefix][announcer]:
                    policy_name=get_policy_name(sdx.policy_2_prefix,participant,prefix)
                    if policy_name!='':
                        sdx.prefix_2_policy[prefix][announcer][participant]=policy_name
                     
                # Check for announcer's policy for its advertised prefixes
                policy_name=get_policy_name(sdx.policy_2_prefix,announcer,prefix)
                if policy_name!='':
                    sdx.prefix_2_policy[prefix][announcer][announcer]=policy_name
     
    print "Created relevant Data Structures for VNH Assignments...."
    print "Policy_2_Prefix: ",sdx.policy_2_prefix
    print "Policy_2_VNH: ",sdx.policy_2_VNH
    print "Prefix_2_Policy: ",sdx.prefix_2_policy
    """

    
def sdx_platform(sdx_config):
    '''
        Defines the SDX platform workflow
    '''
    return (
        sdx_preprocessing(sdx_config) >>
        sdx_participant_policies(sdx_config) >>
        sdx_postprocessing(sdx_config)
    )
 
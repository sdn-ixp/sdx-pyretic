################################################################################
#
#  <website link>
#
#  File:
#        vnhAssignment.py
#
#  Project:
#        Software Defined Exchange (SDX)
#
#  Author:
#        Arpit Gupta
#        Laurent Vanbever
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

## General imports
from ipaddr import IPv4Network


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
    print "fwd_map: "
    for item in fwd_map:
        print "  -- %s -> %s" % (item, fwd_map[item])
    return fwd_map

def get_peerName(port,p_list):
    for peer in p_list:
        if port in p_list[peer]:
            return peer
    return ''

def get_default_forwarding_policy(best_path, participant, participant_list):
    #for peer in best_path:
    policy_ip=parallel([match_prefixes_set(set(best_path[peer])) >> fwd(participant_list[participant][peer][0]) 
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


def step5c(policy, participant, participant_list, port_2_participant, fwd_map,VNH_2_mac):
    fwd_neighbors = set([port_2_participant[a] for a in extract_all_forward_actions_from_policy(policy)])

    print "Participant:%s -- forwarding neighbor: %s" % (participant, fwd_neighbors)
    
    rewrite_policy = None
    
    for neighbor in fwd_neighbors:
        if neighbor != participant:
            p = None
            for (a,b) in fwd_map[participant][neighbor].items():
                if not p:
                    p = (if_(match(dstmac=VNH_2_mac[a]), modify(dstmac=VNH_2_mac[b]), passthrough))
                else:
                    p = p + (if_(match(dstmac=VNH_2_mac[a]), modify(dstmac=VNH_2_mac[b]), passthough))
            if rewrite_policy:
                if p:
                    rewrite_policy += match(outport=participant_list[participant][neighbor][0]) >> (p)
            else:
                if p:
                    rewrite_policy = match(outport=participant_list[participant][neighbor][0]) >> (p)

    if rewrite_policy:
        return rewrite_policy
    else:
        return passthrough

def extract_all_forward_actions_from_policy(policy, acc=[]):
    # Recursive call
    if isinstance(policy, parallel) or isinstance(policy, sequential):
        fwd_set = set()
        for sub_policy in policy.policies:
            ans = extract_all_forward_actions_from_policy(sub_policy)
            try:
                iterator = iter(ans)
            except TypeError:
                if ans is not None:
                    fwd_set.add(ans)
            else:
                for elem in ans:
                    if elem is not None:
                        fwd_set.add(elem)
        return fwd_set
    elif isinstance(policy, if_):
        return extract_all_forward_actions_from_policy(policy.t_branch) | extract_all_forward_actions_from_policy(policy.f_branch)
    else:
        # Base call
        if isinstance(policy, fwd):
            return policy.outport
        else:
            return None
    
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

def extract_all_matches_from_policy(policy, acc=[]):
    # Recursive call
    if isinstance(policy, parallel):
        p = extract_all_matches_from_policy(policy.policies[0])
        for sub_policy in policy.policies[1:]:
            ans = extract_all_matches_from_policy(sub_policy)
            if ans:
                p = p | extract_all_matches_from_policy(sub_policy)
        return p
    elif isinstance(policy, sequential):
        p = extract_all_matches_from_policy(policy.policies[0])
        for sub_policy in policy.policies[1:]:
            ans = extract_all_matches_from_policy(sub_policy)
            if ans:
                p = p & extract_all_matches_from_policy(sub_policy)
        return p
    elif isinstance(policy, if_):
        raise NotImplementedError("Compilation of if_ policy is currently not supported")
        sys.exit(-1)
    else:
        # Base call
        if isinstance(policy, fwd):
            return None
        else:
            return policy


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
    
def step5a(policy, participant, prefixes_announced,participant_list,include_default_policy=False):
    p1 = step5a_expand_policy_with_prefixes(policy, participant,prefixes_announced,participant_list)
    if include_default_policy:
        p1 = p1 >> get_default_forwarding_policy(participant)
    return p1
    
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
        'A' : {'p1':'C','p2':'C','p3':'C','p4':'C','p5':'C','p6':'C'}
    }
    prefixes_announced={'pg1':{
                               'A':['p0'],
                               'B':['p1','p2','p3','p4','p5','p6'],
                               'C':['p1','p2','p3','p4','p5','p6'],
                               }
                        }
    
    participants_policies = {
        'A':(
            (match_prefixes_set(set(['p1','p2','p3','p4','p5','p6'])) >> fwd(3))
         ),
         'B':(
            (match_prefixes_set(set(['p1','p2','p3'])) >> fwd(21)) +
            (match_prefixes_set(set(['p4','p5','p6'])) >> fwd(22))
         ),
         'C':(
            (match_prefixes_set(set(prefixes_announced['pg1']['C'])) >> fwd(3))
         )
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
        
        X_c = step5c(X_b, participant, participant_list, port_2_participant, fwd_map,VNH_2_mac)
        print "Policy after Step 5c:\n", (X_b >> X_c)
        
        print "Final classifier: %s" % (X_b >> X_c).compile()
        
        participants_policies[participant]= (X_b >> X_c)
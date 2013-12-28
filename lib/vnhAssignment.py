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


# # Pyretic-specific imports
from pyretic.lib.corelib import *
from pyretic.lib.std import *

# # SDX-specific imports
from pyretic.sdx.lib.common import *
from pyretic.sdx.lib.setOperation import *
from pyretic.sdx.lib.language import *

# # General imports
from ipaddr import IPv4Network
from netaddr import *


def get_policy_name(policy_2_prefix, participant, prefix):  
    policy_name = ''
    for policy in policy_2_prefix[participant]:
        if prefix in policy_2_prefix[participant][policy]:
            policy_name = policy
            break
    return policy_name


def is_Active(policy_in, pnum, participant_name, sdx, prefixes):
    flag_active = True
    participant_name = participant_name.encode('ascii', 'ignore')
    if participant_name not in sdx.policy_2_prefix:
        sdx.policy_2_prefix[participant_name] = {}  
        sdx.policy_2_VNH[participant_name] = {}   
    for temp in policy_in.policies:
        pnum += 1
        pname = 'policy' + str(pnum)
        plist = []
        for temp2 in temp.policies[0].policies:
            if 'dstip' in temp2.map:
                flag_active = False
                plist.append(str(temp2.map['dstip']))
                prefixes[str(temp2.map['dstip'])] = ''
        if flag_active == False:
            sdx.policy_2_prefix[participant_name][pname] = plist
            sdx.policy_2_VNH[participant_name][pname] = {}
    # print sdx.policy_2_prefix
    return flag_active

def get_bestPaths(nh_received):
    best_paths = {}
    for participant in nh_received:
        best_paths[participant] = {}
        for prefix in nh_received[participant].keys():
            if nh_received[participant][prefix] in best_paths[participant]:
                best_paths[participant][nh_received[participant][prefix]].append(prefix)
            else:
                best_paths[participant][nh_received[participant][prefix]] = [prefix]    
    return best_paths

def get_fwdPeer(peers, ind):
    for peer in peers:
        if ind in peers[peer]:
            return peer
    return ''
    
def get_prefix(policy, plist, pfxlist, part, pa, acc=[]):
    if isinstance(policy, parallel):
        for pol in policy.policies:
            pfxlist, acc = get_prefix(pol, plist, pfxlist, part, pa)
    elif isinstance(policy, sequential):
        acc = []
        for pol in policy.policies:
            pfxlist, acc = get_prefix(pol, plist, pfxlist, part, pa, acc) 
    elif isinstance(policy, if_):
        for pol in policy.policies:
            pfxlist, acc = get_prefix(pol, plist, pfxlist, part, pa)  
    else:
        if isinstance(policy, match):
            # print policy
            if 'dstip' in policy.map:
                acc = list(policy.map['dstip'])
        elif isinstance(policy, match_prefixes_set):
            # print policy
            # if 'dstip' in policy.map:
            acc = list(policy.pfxes)
        elif isinstance(policy, fwd):
            if len(acc) == 0:
                peer = get_fwdPeer(plist[part], policy.outport)
                acc = pa['pg1'][peer]
                print peer, acc
            pfxlist.append(acc)   
    return pfxlist, acc


def get_part2prefixes(policies, plist, pa):
    p2pfx = {}
    for participant in policies:
        policy = policies[participant]
        pfxlist = []
        acc = []
        pfxlist, acc = get_prefix(policy, plist, pfxlist, participant, pa)
        # print participant,pfxlist
        p2pfx[participant] = pfxlist
    
    return p2pfx
    
def get_vname(prefix_set, vdict):
    vname = ''
    for temp in vdict:
        if len(list(set(vdict[temp]).intersection(set(prefix_set)))) > 0:
            vname = temp    
    return vname

def get_fwdMap(part_2_VNH):
    fwd_map = {}
    for participant in part_2_VNH:
        fwd_map[participant] = {}
        for vname, pfx in part_2_VNH[participant].items():
            for peer in part_2_VNH:
                if peer != participant:
                    if peer not in fwd_map[participant]:
                        fwd_map[participant][peer] = {}
                    for vnm in part_2_VNH[peer]:
                        if part_2_VNH[peer][vnm] == pfx and vnm != vname:
                            fwd_map[participant][peer][vname] = vnm
    print "fwd_map: ", fwd_map
    return fwd_map

def get_peerName(port, p_list):
    for peer in p_list:
        if port in p_list[peer]:
            return peer
    return ''

def get_default_forwarding_policy(best_path, participant, participant_list):
    # for peer in best_path:
    print best_path,participant,participant_list
    print best_path.keys()
    policy_ip = parallel([match_prefixes_set(set(best_path[peer])) >> fwd(participant_list[participant][unicode(str(peer))][0]) 
                        for peer in best_path.keys()]) 
    # print policy_ip
    return policy_ip 

def return_vnhop(vnh_2_prefix, VNH_2_mac, pfx):
    vnhop = EthAddr('A1:A1:A1:A1:A1:A1')
    # print vnh_2_prefix,pfx
    for vname in vnh_2_prefix:
        if pfx in vnh_2_prefix[vname]:
            return VNH_2_mac[vname]
    return vnhop 


def step5c(policy, participant, participant_list, port_2_participant, fwd_map, VNH_2_mac):
    fwd_neighbors = set([port_2_participant[a] for a in extract_all_forward_actions_from_policy(policy)])
    rewrite_policy = None
    for neighbor in fwd_neighbors:
        if neighbor != participant:
            p = None
            for (a, b) in fwd_map[participant][neighbor].items():
                if not p:
                    p = (if_(match(dstmac=VNH_2_mac[a]), modify(dstmac=VNH_2_mac[b]), passthrough))
                else:
                    p = p >> (if_(match(dstmac=VNH_2_mac[a]), modify(dstmac=VNH_2_mac[b]), passthrough))
            if rewrite_policy and p:
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
    
def step5b_expand_policy_with_vnhop(policy, participant_id, part_2_VNH, VNH_2_mac, acc=[]):
    # Recursive call
    if isinstance(policy, parallel):
        return parallel(map(lambda p: step5b_expand_policy_with_vnhop(p, participant_id, part_2_VNH, VNH_2_mac), policy.policies))
    elif isinstance(policy, sequential):
        acc = []
        return sequential(map(lambda p: step5b_expand_policy_with_vnhop(p, participant_id, part_2_VNH, VNH_2_mac, acc), policy.policies))
    elif isinstance(policy, if_):
        return if_(step5b_expand_policy_with_vnhop(policy.pred, participant_id, part_2_VNH, VNH_2_mac),
                   step5b_expand_policy_with_vnhop(policy.t_branch, participant_id, part_2_VNH, VNH_2_mac),
                   step5b_expand_policy_with_vnhop(policy.f_branch, participant_id, part_2_VNH, VNH_2_mac))
    else:
        # Base call
        if isinstance(policy, match_prefixes_set):            
            unique_vnhops = set()
            for pfx in policy.pfxes:
                vnhop = return_vnhop(part_2_VNH[participant_id], VNH_2_mac, pfx)
                unique_vnhops.add(vnhop)
            # print unique_vnhops
            acc = list(unique_vnhops)
            match_vnhops = match(dstmac=unique_vnhops.pop())
            for vnhop in unique_vnhops:
                match_vnhops = match_vnhops + match(dstmac=vnhop)
            # print match_vnhops           
            # print 'acc1: ',acc
            # print policy           
            return match_vnhops
        
        elif isinstance(policy, fwd):
            # print 'acc: ',acc
            # print 'policy: ',policy
            if len(list(acc)):
                print 'a: ', acc
            
        return policy


def step5b(policy, participant, part_2_VNH, VNH_2_mac, best_paths, participant_list):
    expanded_vnhop_policy = step5b_expand_policy_with_vnhop(policy, participant, part_2_VNH, VNH_2_mac)
    
    policy_matches = extract_all_matches_from_policy(expanded_vnhop_policy)
    if participant in best_paths:
        # print 'BIG Match: ',policy_matches
        bgp = step5b_expand_policy_with_vnhop(get_default_forwarding_policy(best_paths[participant], participant, participant_list), participant, part_2_VNH, VNH_2_mac)
        # print bgp   
        return if_(policy_matches, expanded_vnhop_policy, bgp)
    else:
        return expanded_vnhop_policy
    
    
    # return expanded_vnhop_policy

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


def step4(lcs,part_2_VNH,VNH_2_pfx,VNH_2_IP,VNH_2_mac,part_2_prefix_updated):
    count = 1
    for pset in lcs:
        vname = 'VNH' + str(count)
        if vname not in VNH_2_IP:
            nhex = hex(count)
            VNH_2_IP[vname]=str(VNH_2_IP['VNH'][count])
            VNH_2_mac[vname] = MAC(str(EUI(int(EUI(VNH_2_mac['VNH']))+count)))
        VNH_2_pfx[vname] = pset
        for participant in part_2_prefix_updated:
            #print part_2_prefix_updated
            if pset in part_2_prefix_updated[participant]:
                if participant not in part_2_VNH:
                    part_2_VNH[participant] = {}
                part_2_VNH[participant][vname] = pset
        count += 1      


def step5a_expand_policy_with_prefixes(policy, participant, pa, plist, acc=[]):
    global participants_announcements
    
    # Recursive call
    if isinstance(policy, parallel):
        return parallel(map(lambda p: step5a_expand_policy_with_prefixes(p, participant, pa, plist), policy.policies))
    elif isinstance(policy, sequential):
        acc = []
        return sequential(map(lambda p: step5a_expand_policy_with_prefixes(p, participant, pa, plist, acc), policy.policies))
    elif isinstance(policy, if_):
        return if_(step5a_expand_policy_with_prefixes(policy.pred, participant, pa, plist),
                   step5a_expand_policy_with_prefixes(policy.t_branch, participant, pa, plist),
                   step5a_expand_policy_with_prefixes(policy.f_branch, participant, pa, plist))
    else:
        # Base call
        if isinstance(policy, match):
            if 'dstip' in policy.map:
                acc.append('dstip')
        elif isinstance(policy, match_prefixes_set):
            acc.append('dstip')
        elif isinstance(policy, fwd):            
            if 'dstip' not in acc:    
                return match_prefixes_set(pa['pg1'][get_fwdPeer(plist[participant], policy.outport)]) >> policy
        return policy
    
def step5a(policy, participant, prefixes_announced, participant_list, include_default_policy=False):
    p1 = step5a_expand_policy_with_prefixes(policy, participant, prefixes_announced, participant_list)
    if include_default_policy:
        p1 = p1 >> get_default_forwarding_policy(participant)
    return p1

def vnh_init(sdx, participants):
    VNH_2_IP = sdx.VNH_2_IP    
    VNH_2_mac = sdx.VNH_2_mac
    prefixes = sdx.prefixes
    participant_list = sdx.participant_2_port
    port_2_participant = sdx.port_2_participant    
    peer_groups = sdx.peer_groups
    participant_to_ebgp_nh_received = sdx.participant_to_ebgp_nh_received
    prefixes_announced = sdx.prefixes_announced
    participants_policies = {}
    for participant_name in participants:
        participants_policies[str(participant_name)] = participants[participant_name].policies    
    return VNH_2_IP, VNH_2_mac, prefixes, participant_list, port_2_participant, peer_groups, participant_to_ebgp_nh_received, prefixes_announced, participants_policies

    
    
def vnh_assignment(sdx, participants):
    # Initialize the required data structures
    VNH_2_IP, VNH_2_mac, prefixes, participant_list, port_2_participant, peer_group, participant_to_ebgp_nh_received, prefixes_announced, participants_policies = vnh_init(sdx, participants)
    
    # Step 1:
    #----------------------------------------------------------------------------------------------------#
    # 1. Get the best paths data structure
    # 2. Get the participant_2_prefix data structure from participant's policies

    best_paths = get_bestPaths(participant_to_ebgp_nh_received)
    print 'best_paths: ', best_paths
    # get the participant_2_prefix structure
    # without taking default forwarding policies into consideration
    participant_2_prefix = get_part2prefixes(participants_policies, participant_list, prefixes_announced)
    # Add the prefixes for default forwarding policies now
    for participant in best_paths:
        participant_2_prefix[participant] = participant_2_prefix[participant] + best_paths[participant].values()        
    #----------------------------------------------------------------------------------------------------#
    
    
    # # Update the sdx part_2_prefix_old data structure, it will be used in VNH recompute
    for participant in participant_2_prefix:
        sdx.part_2_prefix_old[participant] = tuple(participant_2_prefix[participant])
                        
    # Step 2 & 3
    print 'Before Set operations: ', participant_2_prefix
    part_2_prefix_updated, lcs = lcs_multiprocess(participant_2_prefix)
    print 'After Set operations: ', part_2_prefix_updated, sdx.part_2_prefix_old
    sdx.part_2_prefix_lcs = part_2_prefix_updated
    sdx.lcs_old = lcs
        
    #----------------------------------------------------------------------------------------------------#
    
    
    # Step 4: Assign VNHs
    part_2_VNH = {}
    VNH_2_pfx = {}
    step4(lcs,part_2_VNH,VNH_2_pfx,VNH_2_IP,VNH_2_mac,part_2_prefix_updated)
    print "After new assignment"                    
    print part_2_VNH
    print VNH_2_pfx
    print VNH_2_IP
    print VNH_2_mac
    sdx.part_2_VNH=part_2_VNH
    sdx.VNH_2_IP=VNH_2_IP
    sdx.VNH_2_mac=VNH_2_mac    
    
    #----------------------------------------------------------------------------------------------------#
    
    # Step 5
    # Step 5a: Get expanded policies
    for participant in participants_policies:
        print "PARTICIPANT: ",participant
        X_policy = participants_policies[participant]
        #print "Original policy:", X_policy
        
        X_a = step5a(X_policy, participant, prefixes_announced, participant_list)
        #print "Policy after 5a:\n\n", X_a
        
        X_b = step5b(X_a, participant, part_2_VNH, VNH_2_mac, best_paths, participant_list)
        #print "Policy after Step 5b:", X_b

        participants_policies[participant] = X_b
        participants[participant].policies = participants_policies[participant]
        print "Policy after Step 5:", participants_policies[participant]
        # classifier=participants_policies[participant].compile()
        # print "Compilation result",classifier


def update_vnh_assignment(sdx, participants):
    print "Update VNH Assignment Called"
    # Initialize the required data structures
    VNH_2_IP, VNH_2_mac, prefixes, participant_list, port_2_participant, peer_group, participant_to_ebgp_nh_received, prefixes_announced, participants_policies = vnh_init(sdx, participants)
    # Step 1:
    #----------------------------------------------------------------------------------------------------#
    # 1. Get the best paths data structure
    # 2. Get the participant_2_prefix data structure from participant's policies
    best_paths = get_bestPaths(participant_to_ebgp_nh_received)
    print 'Updated best_paths: ', best_paths
    print "prefixes_announced: ", sdx.prefixes_announced
    participant_2_prefix = get_part2prefixes(participants_policies, participant_list, prefixes_announced)
    print "p2p: ", participant_2_prefix
    # Add the prefixes for default forwarding policies now
    for participant in best_paths:
        participant_2_prefix[participant] = participant_2_prefix[participant] + best_paths[participant].values()        
    #----------------------------------------------------------------------------------------------------#
    tmp_old = {}
    p2p_old = {}
    for participant in participant_2_prefix:
        tmp_old[participant] = tuple(participant_2_prefix[participant])
        p2p_old[participant] = list(sdx.part_2_prefix_old[participant])
    sdx.part_2_prefix_old = tmp_old
    # Step 2 & 3
    #----------------------------------------------------------------------------------------------------#
    print 'Before Set operations: ', participant_2_prefix
    # part_2_prefix_updated=prefix_decompose(participant_2_prefix)
    part_2_prefix_updated,lcs = lcs_recompute(p2p_old, participant_2_prefix, sdx.part_2_prefix_lcs, sdx.lcs_old)
    sdx.part_2_prefix_lcs = part_2_prefix_updated
    print "TEST: ", sdx.part_2_prefix_old
    print 'After Set operations: ', part_2_prefix_updated
    sdx.lcs_old = lcs
    
    #----------------------------------------------------------------------------------------------------#
        
    # Step 4: Assign VNHs
    part_2_VNH = {}
    VNH_2_pfx = {}
    step4(lcs,part_2_VNH,VNH_2_pfx,VNH_2_IP,VNH_2_mac,part_2_prefix_updated)
    print "After new assignment"                    
    print part_2_VNH
    print VNH_2_pfx
    print VNH_2_IP
    print VNH_2_mac
    sdx.part_2_VNH=part_2_VNH
    sdx.VNH_2_IP=VNH_2_IP
    sdx.VNH_2_mac=VNH_2_mac  
    
    #----------------------------------------------------------------------------------------------------#
    
    # Step 5
    # Step 5a: Get expanded policies
    for participant in participants_policies:
        #print "PARTICIPANT: ",participant
        X_policy = participants_policies[participant]
        #print "Original policy:", X_policy
        
        X_a = step5a(X_policy, participant, prefixes_announced, participant_list)
        #print "Policy after 5a:\n\n", X_a
        
        X_b = step5b(X_a, participant, part_2_VNH, VNH_2_mac, best_paths, participant_list)
        #print "Policy after Step 5b:", X_b

        participants_policies[participant] = X_b
        participants[participant].policies = participants_policies[participant]
        print "Policy after Step 5:", participants_policies[participant]
        # classifier=participants_policies[participant].compile()
        # print "Compilation result",classifier
   
    
def pre_VNH(policy, sdx, participant_name,participant):
    if isinstance(policy, parallel):
        return parallel(map(lambda p: pre_VNH(p, sdx, participant_name,participant), policy.policies))
    elif isinstance(policy, sequential):
        return sequential(map(lambda p: pre_VNH(p, sdx, participant_name,participant), policy.policies))
    elif isinstance(policy, if_):
        return if_(pre_VNH(policy.pred, sdx, participant_name,participant),
                   pre_VNH(policy.t_branch, sdx, participant_name,participant),
                   pre_VNH(policy.f_branch, sdx, participant_name,participant))
    else:
        # Base call
        if isinstance(policy, modify):            
            # print policy.map
            if 'state' in policy.map:    
                # if 'in' in 
                state = policy.map['state'].encode('ascii', 'ignore')
                if 'in' in state:
                    peer = state.split('in')[1]
                    # print peer
                    #return fwd(sdx.participant_2_port[participant_name][peer][0])
                    #print participant.peers
                    return fwd(participant.peers[peer].participant.phys_ports[0].id_)
                    
                else:
                    pn = state.split('out' + participant_name + '_')[1]
                    print "pn: ",pn
                    return fwd(participant.phys_ports[int(pn)].id_)
                    #return fwd(sdx.participant_2_port[participant_name][participant_name][int(pn)])
                                    
        return policy

    
def post_VNH(policy, sdx, participant_name):
    # get port_2_state for this participant
    port_2_state = {}
    port_2_mac={}
    for peer in sdx.participant_2_port[participant_name]:
        if peer != participant_name:
            port_2_state[sdx.participant_2_port[participant_name][peer][0]] = 'in' + peer
        else:
            i = 0
            for port in sdx.participant_2_port[participant_name][peer]:
                port_2_state[port] = 'out' + peer + '_' + str(i)
                port_2_mac[port]=sdx.sdx_ports[participant_name][i].mac
                i += 1
                
    # print port_2_state
    # Create the rules to change the state
    pol = drop
    for port in port_2_state:
        if 'out' in port_2_state[port]:
            pol = pol + (match(outport=port) >> modify(state=port_2_state[port],dstmac=port_2_mac[port]))
        else:
            pol = pol + (match(outport=port) >> modify(state=port_2_state[port]))

    return policy >> pol

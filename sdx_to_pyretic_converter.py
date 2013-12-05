# Author: Laurent Vanbever (vanbever@cs.princeton.edu)
# Create date: December, 2

## Pyretic-specific imports
from pyretic.lib.corelib import *
from pyretic.lib.std import *

## SDX-specific imports
from pyretic.sdx.lib.language import *

## Generic imports
from ipaddr import IPv4Network

##
## SDX high-level policy, written by the participant
##
A_policy = (
            (match(dstport=80) >> match(srcport=22) >> fwd(2)) +
            (match(dstport=6666) >> fwd(3)) +
            (match_prefixes_set({IPv4Network('11.0.0.0/8')}) >> fwd(2))
         )
##
## Data structures. Eventually, will be filled dynamically trough ExaBGP
##
participants_announcements = {
    1 : {
        2 : [
                IPv4Network('11.0.0.0/8'),
                IPv4Network('12.0.0.0/8'),
                IPv4Network('14.0.0.0/8')
            ],
        3 : [
                IPv4Network('11.0.0.0/8'),
                IPv4Network('12.0.0.0/8'),
                IPv4Network('13.0.0.0/8')
            ]
    }
}

prefix_to_vnhop_assigned = {
    1 : {
        IPv4Network('11.0.0.0/24') : EthAddr('A1:A1:A1:A1:A1:A1'),
        IPv4Network('12.0.0.0/24') : EthAddr('B1:B1:B1:B1:B1:B1'),
        IPv4Network('13.0.0.0/24') : EthAddr('C1:C1:C1:C1:C1:C1'),
        IPv4Network('14.0.0.0/24') : EthAddr('D1:D1:D1:D1:D1:D1')
    },
    2 : {
        IPv4Network('11.0.0.0/24') : EthAddr('A2:A2:A2:A2:A2:A2'),
        IPv4Network('12.0.0.0/24') : EthAddr('B2:B2:B2:B2:B2:B2'),
        IPv4Network('13.0.0.0/24') : EthAddr('C2:C2:C2:C2:C2:C2'),
        IPv4Network('14.0.0.0/24') : EthAddr('D2:D2:D2:D2:D2:D2')
    },
    3 : {
        IPv4Network('11.0.0.0/24') : EthAddr('A3:A3:A3:A3:A3:A3'),
        IPv4Network('12.0.0.0/24') : EthAddr('B3:B3:B3:B3:B3:B3'),
        IPv4Network('13.0.0.0/24') : EthAddr('C3:C3:C3:C3:C3:C3'),
        IPv4Network('14.0.0.0/24') : EthAddr('D3:D3:D3:D3:D3:D3')
    }
}

# Warning: must be ordered by prefix-length, with shorter prefix before
participant_to_ebgp_nh_received = {
    1 : {
        IPv4Network('11.0.0.0/24') : 3,
        IPv4Network('12.0.0.0/24') : 2,
        IPv4Network('13.0.0.0/24') : 3,
        IPv4Network('14.0.0.0/24') : 2,
    }
}


##
## Acces methods to data structures
##


# Warning: Linear Search. Inefficient and incorrect as we need to do longuest-match.
# Change to a binary tree.
def return_ebgp_nh(prefix, participant_id):
    global prefix_received_to_participant

    for candidate_prefix in prefix_received_to_participant[participant_id]:
        if IPv4Network(prefix.__repr__()) in candidate_prefix:
            return prefix_received_to_participant[participant_id][candidate_prefix]

def return_vnhop(prefix, participant_id):
    global prefix_to_vnhop_assigned
    
    for candidate_prefix in prefix_to_vnhop_assigned[participant_id]:
        if IPv4Network(prefix.__repr__()) in candidate_prefix:
            return prefix_to_vnhop_assigned[participant_id][candidate_prefix]


##
## Compilation stages
##

def step1(policy, participant_id, include_default_policy=False):
    p1 = step1a_expand_policy_with_prefixes(policy, participant_id)
    if include_default_policy:
        p1 = p1 >> get_default_forwarding_policy(participant_id)
    return p1

def step1a_expand_policy_with_prefixes(policy, participant_id, acc=[]):
    global participants_announcements
    
    # Recursive call
    if isinstance(policy, parallel):
        return parallel(map(lambda p: step1a_expand_policy_with_prefixes(p, participant_id), policy.policies))
    elif isinstance(policy, sequential):
        acc = []
        return sequential(map(lambda p: step1a_expand_policy_with_prefixes(p, participant_id, acc), policy.policies))
    elif isinstance(policy, if_):
        return if_(step1a_expand_policy_with_prefixes(policy.pred, participant_id), step1a_expand_policy_with_prefixes(policy.t_branch, participant_id), step1a_expand_policy_with_prefixes(policy.f_branch, participant_id))
    else:
        # Base call
        if isinstance(policy, match):
            if 'dstip' in policy.map:
                acc.append('dstip')
        elif isinstance(policy, match_prefixes_set):
            acc.append('dstip')
        elif isinstance(policy, fwd):
            if 'dstip' not in acc:    
                return match_prefixes_set(participants_announcements[participant_id][policy.outport]) >> policy
        return policy

def get_default_forwarding_policy(participant_id):
    global participant_to_ebgp_nh_received
    return parallel([match(dstip=IPPrefix(str(pfx))) >> fwd(nh) for (pfx, nh) in participant_to_ebgp_nh_received[participant_id].items()])

def extract_all_matches_from_policy(policy, acc=[]):
    # Recursive call
    if isinstance(policy, parallel):
        p = extract_all_matches_from_policy(policy.policies[0])
        for sub_policy in policy.policies[1:]:
            p = p | extract_all_matches_from_policy(sub_policy);
        return p
    elif isinstance(policy, sequential):
        p = extract_all_matches_from_policy(policy.policies[0])
        for sub_policy in policy.policies[1:]:
            p = p & extract_all_matches_from_policy(sub_policy);
        return p
    elif isinstance(policy, if_):
        print "Error: Not supported right now"
        sys.exit(-1)
    else:
        # Base call
        if isinstance(policy, fwd):
            return match()
        else:
            return policy

def step5(policy, participant_id):
    policy_matches = extract_all_matches_from_policy(policy)
    expanded_vnhop_policy = step5a_expand_policy_with_vnhop(policy, participant_id)
    bgp = get_default_forwarding_policy(participant_id)
        
    return if_(policy_matches)(expanded_vnhop_policy)(bgp)

def step5a_expand_policy_with_vnhop(policy, participant_id, acc=[]):
    # Recursive call
    if isinstance(policy, parallel):
        return parallel(map(lambda p: step5_expand_policy_with_vnhop(p, participant_id), policy.policies))
    elif isinstance(policy, sequential):
        a = []
        return sequential(map(lambda p: step5_expand_policy_with_vnhop(p, participant_id, a), policy.policies))
    elif isinstance(policy, if_):
        return if_(step5_expand_policy_with_vnhop(policy.pred, participant_id), step5_expand_policy_with_vnhop(policy.t_branch, participant_id), step5_expand_policy_with_vnhop(policy.f_branch, participant_id))
    else:
        # Base call
        if isinstance(policy, match):
            if 'dstip' in policy.map:
                pfx = policy.map['dstip']
                ebgp_nh = return_ebgp_nh(pfx, participant_id)
                acc.append((pfx, ebgp_nh))
                vnhop = return_vnhop(pfx, ebgp_nh)
                return match({'dstmac':vnhop})
        elif isinstance(policy, fwd):
            if policy.outport not in [ebgp_nh for (pfx, ebgp_nh) in acc]:
                return modify({'dstmac': return_vnhop(acc[0][0], policy.outport)}) >> policy
        return policy


def main():
    print "Original policy:", A_policy
    
    A_expanded = step1(A_policy, 1)
    print "Step 1:", A_expanded
    
    print "Pouet", extract_all_matches_from_policy(A_policy)
    
    #A_vnhop = step5_expand_policy_with_vnhop(A_expanded, 1)
    #print "Step 5:", A_vnhop
    
    return flood()
# Author: Laurent Vanbever (vanbever@cs.princeton.edu)
# Create date: December, 2

from pyretic.lib.corelib import *
from pyretic.lib.std import *
from ipaddr import IPv4Network

A_policy = (
            (match(dstport=80) >> fwd(2)) +
            (match(dstport=6666) >> fwd(3))
         )

A_expanded = (
            (match(dstip=IPAddr('11.0.0.1')) >> match(dstport=80) >> fwd(2)) +
            (match(dstip=IPAddr('12.0.0.1')) >> match(dstport=80) >> fwd(2)) +
            (match(dstip=IPAddr('14.0.0.1')) >> match(dstport=80) >> fwd(2)) +
            
            (match(dstip=IPAddr('11.0.0.1')) >> match(dstport=6666) >> fwd(3)) +
            (match(dstip=IPAddr('12.0.0.1')) >> match(dstport=6666) >> fwd(3)) +
            (match(dstip=IPAddr('13.0.0.1')) >> match(dstport=6666) >> fwd(3)) +
            
            (match(dstip=IPAddr('11.0.0.1')) >> fwd(3)) +
            (match(dstip=IPAddr('12.0.0.1')) >> fwd(2)) +
            (match(dstip=IPAddr('13.0.0.1')) >> fwd(3)) +
            (match(dstip=IPAddr('14.0.0.1')) >> fwd(2))
          )

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
prefix_received_to_participant = {
    1 : {
        IPv4Network('11.0.0.0/24') : 3,
        IPv4Network('12.0.0.0/24') : 2,
        IPv4Network('13.0.0.0/24') : 3,
        IPv4Network('14.0.0.0/24') : 2,
    }
}

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

def expanded_policy_to_vnhop_policy(policy, participant_id, bgp_neighbor=[]):
    # Recursive call
    if isinstance(policy, parallel):
        return parallel(map(lambda p: expanded_policy_to_vnhop_policy(p, participant_id), policy.policies))
    elif isinstance(policy, sequential):
        a = []
        return sequential(map(lambda p: expanded_policy_to_vnhop_policy(p, participant_id, a), policy.policies))
    elif isinstance(policy, if_):
        return if_(expanded_policy_to_vnhop_policy(policy.pred, participant_id), expanded_policy_to_vnhop_policy(policy.t_branch, participant_id), expanded_policy_to_vnhop_policy(policy.f_branch, participant_id))
    else:
        # Base call
        if isinstance(policy, match):
            if 'dstip' in policy.map:
                pfx = policy.map['dstip']
                ebgp_nh = return_ebgp_nh(pfx, participant_id)
                bgp_neighbor.append((pfx, ebgp_nh))
                vnhop = return_vnhop(pfx, ebgp_nh)
                return match({'dstmac':vnhop})
        elif isinstance(policy, fwd):
            if policy.outport not in [ebgp_nh for (pfx, ebgp_nh) in bgp_neighbor]:
                return modify({'dstmac': return_vnhop(bgp_neighbor[0][0], policy.outport)}) >> policy
        return policy

def main():
    print A_expanded
    print "rewritten: ", expanded_policy_to_vnhop_policy(A_expanded, 1)
    return expanded_policy_to_vnhop_policy(A_expanded, 1)
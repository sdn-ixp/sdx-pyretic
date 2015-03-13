#############################################
# Policy Composition                        #
# author: Arpit Gupta (glex.qsd@gmail.com)  #
#############################################

###
### SDX high-level functions
###
from pyretic.sdx.lib.corelib import *
from pyretic.sdx.lib.pyreticlib import *




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

def sdx_restrict_state(sdx, participant):
    '''
        Check if the state is not an end state (i.e., output port). 
        If so return a passthrough policy otherwise 
        prefix a match on the participant's state variable
        before any of the participant's policy to ensure that
        it cannot match on other participant's flowspace
    '''
    match_all_output_var = no_packets
    for output_var in sdx.out_var_to_port:
        match_all_output_var = match_all_output_var | match(state=output_var)
    return if_(match_all_output_var, 
               passthrough, 
               match(state=sdx.participant_id_to_in_var[participant.id_]) >> 
                    #parallel([sdx_from(participant.peers[peer_name]) for peer_name in participant.peers]) & '''Might not happen, as we are providing limited view to the participants''' 
                        participant.policies
              )


def get_forwardports(policy, sdx, id):
    """ Extract all the forwarding ports from input policy excluding participant's own"""
    fwdports = extract_all_forward_actions_from_policy(
                policy)
    
    """ Remove participant's own ports from the fwdport list """
    fwdports = filter(
        lambda port: port not in sdx.participant_2_port[id][id], fwdports)
    
    return fwdports
    

def get_inboundPorts(sdx, part_id):
    match_outports = no_packets
    for tmp in sdx.participant_2_port[part_id][part_id]:
        match_outports |= match(outport=tmp)
    match_outports.policies = filter(
        lambda x: x != drop,
        match_outports.policies)
    selfPorts = sdx.participant_2_port[part_id][part_id]
    
    return match_outports, selfPorts


def get_matchPorts(sdx, part_id, peer_id):
    match_inports = no_packets
    for tmp in sdx.participant_2_port[part_id][part_id]:
        match_inports |= match(inport=tmp)
    match_inports.policies = filter(
        lambda x: x != drop,
        match_inports.policies)

    match_outports = no_packets
    for tmp in sdx.participant_2_port[peer_id][peer_id]:
        match_outports |= match(outport=tmp)
    match_outports.policies = filter(
        lambda x: x != drop,
        match_outports.policies)
    
    return match_inports, match_outports


def isDefault(sdx, participant):
    policy = participant.policies
    if policy == identity:
        return True
    else:
        return False


def extract_all_forward_actions_from_policy(policy, acc=[]):
    # Recursive call
    if policy==drop:
        return set()
    elif isinstance(policy, parallel) or isinstance(policy, sequential):
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
            return set([policy.outport])
        else:
            return None
        
        
def naive_compose(sdx):
    """ 
        This is the Simple State Machine Policy Composition approach.
        P = (p1+p2+p3+...pn) >> (p1+p2+p3+...)
    """
    debug = True
    
    naivePolicies = []
    if debug:
        print "naiveCompose called"
    lowerPolicies = []
    # take into consideration the participants with inbound policies
    # They need to be composed in parallel with other policies
    print sdx.participants
    for participant in sdx.participants.values():
        if (isDefault(sdx, participant) == False):
            match_outports = no_packets
            for tmp in sdx.participant_2_port[participant.id_][participant.id_]:
                match_outports |= match(outport=tmp)
            match_outports.policies = filter(
                lambda x: x != drop,
                match_outports.policies)
            tmp_policy_participant = match_outports >> participant.policies >> match_outports
            lowerPolicies.append(tmp_policy_participant)

    for participant in sdx.participants.values():

        if debug:
            print "Participant", participant.id_, participant.policies
        # get list of all participants to which it forwards
        fwdports = get_forwardports(participant.policies, 
                                       sdx, participant.id_)         
        tmp_policy_participant = drop
        pdict = {}
        if debug:
            print participant.policies.compile()
        for port in fwdports:
            peer_id = sdx.port_2_participant[
                int(port)]  # Name of fwding participant
            # Instance of fwding participant
            peer = sdx.participants[peer_id]

            if debug:
                print "Seq compiling policies of part: ", participant.id_, " with peer: ", peer_id
            match_inports, match_outports = get_matchPorts(sdx, participant.id_, peer_id)
            
            """ 
                Compiling: A(outbound) >> B (inbound):
                Match for inport of to filter flows entering from other inports.
                Apply A's policies and filter out flows going out to B matching on B's outports. 
                Then apply B's policies and filter for flows entering B's physical ports.
            """
            tmp_policy_participant += (match_inports >> participant.policies >>
                           match_outports >> peer.policies >> match_outports)

        print tmp_policy_participant
        if debug:
            print tmp_policy_participant.compile()
        naivePolicies.append(tmp_policy_participant)
    
    #naivePolicies += lowerPolicies
    lPolicy = parallel(naivePolicies)
    
    if debug:
        print "Compile the naive policies"
    start_comp = time.time()
    lclassifier = lPolicy.compile()
    if debug:
        print lclassifier
    nRules = len(lclassifier)
    if debug:
        print nRules
    compileTime = time.time() - start_comp
    if debug:
        print 'Completed naive Compilation ', compileTime, "seconds"
    #return nRules, compileTime
    return lPolicy


def simple_compose(sdx):
    '''
        Defines the SDX platform workflow
    '''
    
    def sdx_preprocessing(sdx):
        '''
            Map incoming packets on participant's ports to the corresponding
            incoming state
        '''
        preprocessing_policies = []
        for participant in sdx.participants:
            for port in sdx.participants[participant].phys_ports:
                preprocessing_policies.append((match(inport=port.id_) >> 
                    modify(state=sdx.participant_id_to_in_var[sdx.participants[participant].id_])))
        return parallel(preprocessing_policies)
    
    def sdx_postprocessing(sdx):
        '''
            Forward outgoing packets to the appropriate participant's ports
            based on the outgoing state
        '''
        postprocessing_policies = []
        for output_var in sdx.out_var_to_port:
            postprocessing_policies.append((match(state=output_var) >> modify(state=None) >> 
                fwd(sdx.out_var_to_port[output_var].id_)))
        return parallel(postprocessing_policies)
    
    def sdx_participant_policies():
        '''
            Sequentially compose the || composition of the participants policy 
            k-times where k is the number of participants
        '''
        sdx_policy = passthrough
        for k in [0,1]:
            sdx_policy = sequential([
                    sdx_policy,
                    parallel(
                        [sdx_restrict_state(sdx, sdx.participants[participant]) for participant in sdx.participants]
                    )])
        return sdx_policy
    
    
    return (
        sdx_preprocessing(sdx) >>
        sdx_participant_policies() >>
        sdx_postprocessing(sdx)
    )

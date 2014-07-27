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
